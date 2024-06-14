import asyncio
import random
from loguru import logger
from modules.layerzero.bridge import Bridge
from settings import RETRY, BridgeTokenSettingsHL
from tools.contracts.contract import HYPERLANE_CHAINS_ID
from tools.helpers import address_to_bytes32
from modules.hyperlane.claim_hl import get_contract_hl_erc20

class BridgeTokenHL(Bridge):
    async def run(self, retry=0):
        tokens_amount = await self.get_all_tokens_amount()

        if tokens_amount == 0:
            logger.warning(f'{self.module_str} | tokens balance = 0')
            return False
        elif not tokens_amount:
            logger.warning(f'{self.module_str} | error getting tokens balance')
            return False
        elif tokens_amount < BridgeTokenSettingsHL.amount[1]:
            logger.warning(f'{self.module_str} | token balance is less than bridge amount in settings.py')
            return False

        self.count = self.get_bridge_amount(tokens_amount)

        contract_txn = await self.get_txn()
        if not contract_txn:
            logger.warning(f'{self.module_str} | error getting contract_txn')
            return False
        status, tx_link = await self.manager.send_tx(contract_txn)

        if status == 1:
            logger.success(f'{self.module_str} | {tx_link}')
        else:
            logger.warning(f'{self.number} {self.manager.address} | tx is failed | {tx_link}')
            if retry < RETRY:
                logger.info(f'try again in 10 sec.')
                await asyncio.sleep(10)
                return await self.run(retry+1)
            else:
                logger.warning(f'{self.number} {function.manager.address} | bridge is failed for this address, moving to next wallet | {tx_link}')


    async def get_txn(self):
            try:
                address_bytes32 = address_to_bytes32(self.manager.address)
                tokens_amount = self.manager.web3.to_wei(self.count, 'ether') 

                nativeFee = await self.contract.functions.bridgeFee().call()
                gas = await self.contract.functions.getQuoteDispatchFee(
                    HYPERLANE_CHAINS_ID[self.to_chain],    
                    tokens_amount,
                    address_bytes32
                ).call()
                
                contract_txn = await self.contract.functions.transferRemote(
                    HYPERLANE_CHAINS_ID[self.to_chain],
                    self.manager.address,
                    tokens_amount
                ).build_transaction(
                    {
                        "from": self.manager.address,
                        "value": nativeFee + gas,
                        "nonce": await self.manager.web3.eth.get_transaction_count(self.manager.address),
                        'gasPrice': 0,
                        'gas': gas,
                    }
                )
                
                contract_txn = await self.manager.add_gas_price(contract_txn)
                contract_txn = await self.manager.add_gas_limit_layerzero(contract_txn)
                return contract_txn
            
            except Exception as error:
                logger.warning(error)
            return False

    async def get_all_tokens_amount(self):
            self.contract = await get_contract_hl_erc20(self.from_chain)
            tokens = await self.contract.functions.balanceOf(self.manager.address).call()
            return(tokens)

    def get_bridge_amount(self, all_tokens_amount):
            if BridgeTokenSettingsHL.bridge_all:
                return all_tokens_amount
            else:
                return random.uniform(*BridgeTokenSettingsHL.amount)
            
    async def calculate_cost(self):
        total_cost = 0

        tokens_amount = await self.get_all_tokens_amount()
        if tokens_amount == 0:
            logger.warning(f'{self.module_str} | tokens balance = 0')
            return False
        elif not tokens_amount:
            logger.warning(f'{self.module_str} | error getting tokens balance')
            return False
        elif tokens_amount < BridgeTokenSettingsHL.amount[1]:
            logger.warning(f'{self.module_str} | token balance is less than bridge amount in settings.py')
            return False

        bridge_amount = self.get_bridge_amount(tokens_amount)  
        
        self.count = bridge_amount
        contract_txn = await self.get_txn()
        if not contract_txn:
            return False
        total_cost += contract_txn['value'] + contract_txn['gasPrice']*contract_txn['gas']*1.2

        return total_cost
            
    def get_base_chains():
        return BridgeTokenSettingsHL.from_chain

    def get_dest_chains():
        return BridgeTokenSettingsHL.to_chain