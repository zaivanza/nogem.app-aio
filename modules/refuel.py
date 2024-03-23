import asyncio
import sys
from config import PRICES_NATIVE
from eth_account import Account
from settings import RETRY, RefuelSettings
from tools.contracts.abi import ABI_REFUEL
from tools.contracts.contract import EXCLUDED_LZ_PAIRS, LAYERZERO_CHAINS_ID, NOGEM_REFUEL_CONTRACTS
from tools.gas_boss import GasBoss
from web3 import Web3
from eth_abi.packed import encode_packed

from loguru import logger

class Refuel:
    
    def __init__(self, number, key, from_chain, dest_chain):
            self.number = number
            self.key = key
            self.from_chain = from_chain
            self.to_chain = dest_chain
            self.amount_from = RefuelSettings.amount_from
            self.amount_to = RefuelSettings.amount_to
            self.swap_all_balance = RefuelSettings.swap_all_balance
            self.min_amount_swap = RefuelSettings.min_amount_swap
            self.keep_value_from = RefuelSettings.keep_value_from
            self.keep_value_to = RefuelSettings.keep_value_to
            self.manager = GasBoss(self.key, self.from_chain)
            self.module_str = f'{self.number} {self.manager.address} | refuel : {self.from_chain} => {self.to_chain}'
            

    async def run(self, retry=0):
        logger.info(f'{self.module_str}')

        if (LAYERZERO_CHAINS_ID[self.from_chain], LAYERZERO_CHAINS_ID[self.to_chain]) in EXCLUDED_LZ_PAIRS or (LAYERZERO_CHAINS_ID[self.to_chain], LAYERZERO_CHAINS_ID[self.from_chain]) in EXCLUDED_LZ_PAIRS:
                    logger.error(f'{self.module_str} | this pair of networks is not available for bridge')
                    return False
        
        contract_txn = await self.get_txn()

        if not contract_txn:
            logger.error(f'{self.module_str} | error getting contract_txn')
            return False
        
        status, tx_link = await self.manager.send_tx(contract_txn)

        if status == 1:
            logger.success(f'{self.module_str} | {tx_link}')
        else:
            logger.error(f'{self.number} {self.manager.address} | tx is failed | {tx_link}')
            if retry < RETRY:
                logger.info(f'try again in 10 sec.')
                await asyncio.sleep(10)
                return await self.run(retry+1)
            else:
                logger.error(f'{self.number} {self.manager.address} | filler is failed for this address, moving to next wallet | {tx_link}')
        


    async def setup(self):
        self.manager = GasBoss(self.key, self.from_chain)
        self.contract = self.manager.web3.eth.contract(address=Web3.to_checksum_address(NOGEM_REFUEL_CONTRACTS[self.from_chain]), abi=ABI_REFUEL)
        self.amount = await self.manager.get_amount_in(self.keep_value_from, self.keep_value_to, self.swap_all_balance, '', self.amount_from, self.amount_to)
        self.token_data = await self.manager.get_token_info('')
        self.value = Web3.to_wei(self.amount, 'ether')
        self.adapterParams = await self.get_adapterParams(self.value)
        self.module_str = f'{self.number} {self.manager.address} | refuel : {self.from_chain} => {self.to_chain}'

    async def get_adapterParams(self, amount: int):
        minDstGas = await self.get_min_dst_gas_lookup(LAYERZERO_CHAINS_ID[self.to_chain], 0)   
        addressOnDist = Account().from_key(self.key).address
        return encode_packed(
            ["uint16", "uint256", "uint256", "address"],
            [2, minDstGas, amount, addressOnDist] 
        )
    
    async def get_min_dst_gas_lookup(self, dstChainId, funcType):
        return await self.contract.functions.minDstGasLookup(dstChainId, funcType).call()

    async def get_txn(self):
        try:
            if (LAYERZERO_CHAINS_ID[self.from_chain], LAYERZERO_CHAINS_ID[self.to_chain]) in EXCLUDED_LZ_PAIRS or (LAYERZERO_CHAINS_ID[self.to_chain], LAYERZERO_CHAINS_ID[self.from_chain]) in EXCLUDED_LZ_PAIRS:
                logger.warning(f'{self.module_str} | this pair of networks is not available for bridge')
                return False

            await self.setup()

            dst_contract_address = encode_packed(["address"], [NOGEM_REFUEL_CONTRACTS[self.to_chain]])
            send_value = await self.contract.functions.estimateSendFee(LAYERZERO_CHAINS_ID[self.to_chain], dst_contract_address, self.adapterParams).call()
            contract_txn = await self.contract.functions.refuel(
                    LAYERZERO_CHAINS_ID[self.to_chain],
                    dst_contract_address,
                    self.adapterParams
                ).build_transaction(
                {
                    "from": self.manager.address,
                    "value": send_value[0],
                    "nonce": await self.manager.web3.eth.get_transaction_count(self.manager.address),
                    'gasPrice': 0,
                    'gas': 0,
                }
            )

            contract_txn = await self.manager.add_gas_price(contract_txn)
            contract_txn = await self.manager.add_gas_limit_layerzero(contract_txn)

            if self.swap_all_balance:
                gas_gas = int(contract_txn['gas'] * contract_txn['gasPrice'])
                contract_txn['value'] = contract_txn['value'] - gas_gas

            if self.amount >= self.min_amount_swap:
                return contract_txn
            else:
                logger.warning(f"{self.module_str} | {self.amount} (amount) < {self.min_amount_swap} (min_amount_swap)")
                return False
            
        except Exception as error:
            logger.warning(error)
            return False

    async def calculate_cost(self):
        contract_txn = await self.get_txn()

        if not contract_txn:
            return False        
        
        total_cost = contract_txn['value'] + contract_txn['gasPrice']*contract_txn['gas']*1.2
        return total_cost
    
    def get_base_chains():
        return RefuelSettings.from_chain
    
    def get_dest_chains():
        return RefuelSettings.to_chain 
    
    def print_chains():
        chains_list = list(NOGEM_REFUEL_CONTRACTS.keys())
        for chain in chains_list:
            print(chain, end=" | ")