
import asyncio
from modules.mint import get_contract
from tools.contracts.contract import ZERO_ADDRESS,LAYERZERO_CHAINS_ID, EXCLUDED_LZ_PAIRS
from settings import BridgeSettings
from settings import DELAY_SLEEP, RETRY
from tools.gas_boss import GasBoss
from tools.helpers import async_sleeping, get_balance_nfts_amount, get_balance_nfts_id
from loguru import logger
from eth_abi.packed import encode_packed

class Bridge:
    def __init__(self, number, key, from_chain, dest_chain, count=0):
        self.number = number
        self.key = key
        self.from_chain = from_chain
        self.to_chain = dest_chain
        self.count = count
        self.manager = GasBoss(self.key, self.from_chain)
        self.module_str = f'{self.number} {self.manager.address} | bridge nft {self.from_chain} => {self.to_chain}'

    async def run(self, retry=0):

        if (LAYERZERO_CHAINS_ID[self.from_chain], LAYERZERO_CHAINS_ID[self.to_chain]) in EXCLUDED_LZ_PAIRS or (LAYERZERO_CHAINS_ID[self.to_chain], LAYERZERO_CHAINS_ID[self.from_chain]) in EXCLUDED_LZ_PAIRS:
            logger.warning(f'{self.module_str} | this pair of networks is not available for bridge')
            return False

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
    
    def get_base_chains():
        return BridgeSettings.from_chain
    
    def get_dest_chains():
        return BridgeSettings.to_chain

    async def estimateSendFee(
            self,
            toDstLzChainId: int,
            token_id: int, 
            toDstAddress: str,
            useZro: bool,
            adapterParams: bytes
        ) -> (int, int):
        return await self.contract.functions.estimateSendFee(
            toDstLzChainId,
            toDstAddress,
            token_id,
            useZro,
            adapterParams
        ).call()
    
    async def get_min_dst_gas_lookup(self, dstChainId, funcType):
        return await self.contract.functions.minDstGasLookup(dstChainId, funcType).call()

    async def get_txn(self):
            adapterParams = encode_packed(
                ["uint16", "uint256"],
                [1, await self.get_min_dst_gas_lookup(LAYERZERO_CHAINS_ID[self.to_chain], 1)] # lzVersion, gasLimit - extra for minting
            )

            nativeFee, _ = await self.estimateSendFee(
                LAYERZERO_CHAINS_ID[self.to_chain],
                self.token_id,
                self.manager.address,
                False,
                adapterParams
            )

            gas = await self.contract.functions.sendFrom(
                self.manager.address,
                LAYERZERO_CHAINS_ID[self.to_chain],
                self.manager.address,
                self.token_id,
                self.manager.address,
                ZERO_ADDRESS,
                adapterParams
            ).estimate_gas(
                {
                    "from": self.manager.address,
                    "value": nativeFee,
                    "nonce": await self.manager.web3.eth.get_transaction_count(self.manager.address),
                    'gasPrice': 0,
                    'gas': 1,
                }
            )
            contract_txn = await self.contract.functions.sendFrom(
                self.manager.address,
                LAYERZERO_CHAINS_ID[self.to_chain],
                self.manager.address,
                self.token_id,
                self.manager.address,
                ZERO_ADDRESS,
                adapterParams
            ).build_transaction(
                {
                    "from": self.manager.address,
                    "value": nativeFee,
                    "nonce": await self.manager.web3.eth.get_transaction_count(self.manager.address),
                    'gasPrice': 0,
                    'gas': gas,
                }
            )

            contract_txn = await self.manager.add_gas_price(contract_txn)
            contract_txn = await self.manager.add_gas_limit_layerzero(contract_txn)
            return contract_txn
    
    async def get_bridge_details(self):
        self.contract = await get_contract(self.from_chain)
        nft_count = await get_balance_nfts_amount(self.contract, self.manager.address) 
        tokens_ids = [await get_balance_nfts_id(self.contract, self.manager.address, i) for i in range(nft_count)]
        return(nft_count, tokens_ids)
    
    def get_bridge_count(self, nft_count):
        if self.count !=0:
            return self.count
        elif BridgeSettings.bridge_all:
            return nft_count
        else:
            return BridgeSettings.amount
            
        
    async def calculate_cost(self):
        total_cost = 0
        nft_count, tokens_ids = await self.get_bridge_details()
        if nft_count == 0 or tokens_ids == 0:
            logger.warning(f'{self.module_str} | nft balance = 0')
            return False

        bridge_count = self.get_bridge_count(nft_count)  

        for i in range(bridge_count):
            self.token_id = tokens_ids[i]
            contract_txn = await self.get_txn()
            if not contract_txn:
                return False
            total_cost += contract_txn['value'] + contract_txn['gasPrice']*contract_txn['gas']*1.2
        
        return total_cost

