
import random
from loguru import logger
import asyncio

from tools.gas_boss import GasBoss
from tools.helpers import async_sleeping, get_contract_hl_erc20
from settings import (DELAY_SLEEP, RETRY, ClaimSettingsHL)

class ClaimHL:
    def __init__(self, number, key, chain, claim_count) -> None:
        self.number = number
        self.key = key
        self.chain = chain
        self.claim_count = claim_count
        self.claim_amount=  random.uniform(*ClaimSettingsHL.amount_claim)
        self.manager = GasBoss(self.key, self.chain)
        self.module_str = f'{self.number} {self.manager.address} | claim {self.claim_amount} tokens ({self.chain})'

    async def main(self, retry=0):
        contract_txn = await self.get_txn()
        if not contract_txn:
            logger.error(f'{self.module_str} | error getting contract_txn')
            return False
        
        #status, tx_link = await self.manager.send_tx(contract_txn)
        status, tx_link = 1, 'https://etherscan.io/tx/0x1b1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1'

        if status == 1:
            logger.success(f'{self.module_str} | {tx_link}')
        else:
            logger.error(f'{self.number} {self.manager.address} | tx is failed | {tx_link}')
            if retry < RETRY:
                logger.info(f'try again in 10 sec.')
                await asyncio.sleep(10)
                return await self.main(retry+1)
            else:
                logger.error(f'{self.number} {self.manager.address} | claim is failed for this address, moving to next wallet | {tx_link}')

    async def run(self):
        for i in range(self.claim_count):
            await self.main()
            if i+1 != self.claim_count:
                await async_sleeping(*DELAY_SLEEP)

    async def get_txn(self):
        try:
            self.contract = await get_contract_hl_erc20(self.chain)
            claim_fee = await self.contract.functions.mintFee().call()
            
            tokens = self.manager.web3.to_wei(self.claim_amount, 'ether')
            

            contract_txn = await self.contract.functions.mint(tokens).build_transaction(
                {
                    "from": self.manager.address,
                    "value": claim_fee,
                    "nonce": await self.manager.web3.eth.get_transaction_count(self.manager.address),
                    'gasPrice': 0,
                    'gas': 0,
                }
            )

            contract_txn = await self.manager.add_gas_price(contract_txn)
            contract_txn = await self.manager.add_gas_limit_layerzero(contract_txn)

            return contract_txn
        
        except Exception as error:
            logger.warning(error)
            return False
    
    async def calculate_cost(self):
        if await self.has_balance():
            contract_txn =  await self.get_txn()
            if not contract_txn: 
                return False
            claim_cost = contract_txn['value'] + contract_txn['gasPrice']*contract_txn['gas']*1.2
            total_cost = claim_cost * self.claim_count
            return total_cost
        else:
            return False
    
    async def has_balance(self):
        balance = await self.manager.get_balance_native()
        balance_native = self.manager.web3.from_wei(balance,'ether')
        if  balance_native == 0:
            logger.warning("Not enough balance")
            return False
        return True

    def get_base_chains():
        return ClaimSettingsHL.chains