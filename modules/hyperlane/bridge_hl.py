import asyncio
from loguru import logger
from modules.layerzero.bridge import Bridge
from settings import DELAY_SLEEP, RETRY, BridgeNFTSettingsHL
from tools.contracts.contract import HYPERLANE_CHAINS_ID
from tools.helpers import address_to_bytes32, async_sleeping, get_balance_hl_nfts_id
from modules.hyperlane.mint_hl import get_contract_hl_nft

class BridgeHL(Bridge):
    async def run(self, retry=0):
        nft_count, tokens_ids = await self.get_bridge_details()

        if nft_count == 0:
            logger.warning(f'{self.module_str} | nft balance = 0')
            return False
        
        bridge_count = self.get_bridge_count(nft_count)

        for i in range(bridge_count):
            self.token_id = tokens_ids[i]
            
            contract_txn = await self.get_txn()
            if not contract_txn:
                logger.warning(f'{self.module_str} | error getting contract_txn')
                continue
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

            if i+1 != bridge_count:
                await async_sleeping(*DELAY_SLEEP)


    async def get_txn(self):
            try:
                address_bytes32 = address_to_bytes32(self.manager.address)
                
                nativeFee = await self.contract.functions.bridgeFee().call()
                gas = await self.contract.functions.getQuoteDispatchFee(
                    HYPERLANE_CHAINS_ID[self.to_chain],    
                    self.token_id,
                    address_bytes32
                ).call()

                contract_txn = await self.contract.functions.transferRemote(
                    HYPERLANE_CHAINS_ID[self.to_chain],
                    self.manager.address,
                    self.token_id
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

    async def get_bridge_details(self):
            self.contract = await get_contract_hl_nft(self.from_chain)
            tokens_ids = await get_balance_hl_nfts_id(self.contract, self.manager.address)
            nft_count = len(tokens_ids) 
            return(nft_count, tokens_ids)

    def get_bridge_count(self, nft_count):
            if self.count !=0:
                return self.count
            if BridgeNFTSettingsHL.bridge_all:
                return nft_count
            else:
                return BridgeNFTSettingsHL.amount
            
    def get_base_chains():
        return BridgeNFTSettingsHL.from_chain

    def get_dest_chains():
        return BridgeNFTSettingsHL.to_chain