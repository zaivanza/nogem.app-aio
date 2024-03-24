import asyncio
import random
from config import FILLER_VALUE, PRICES_NATIVE
from settings import RETRY, FillerSettings
from tools.contracts.abi import ABI_FILLER
from tools.contracts.contract import EXCLUDED_LZ_PAIRS, LAYERZERO_CHAINS_ID, NOGEM_FILLER_CONTRACTS, NOGEM_REFUEL_CONTRACTS
from tools.gas_boss import GasBoss
from web3 import Web3
from eth_abi.packed import encode_packed

from loguru import logger

class Filler:
    
    def __init__(self, number, key, from_chain, dest_chains):
            self.number = number
            self.key = key
            self.from_chain = from_chain
            self.to_chains = dest_chains
            self.to_chains_count = FillerSettings.to_chains_count
            self.use_random_chains = FillerSettings.use_random_chains
            self.cost_to_chains = FillerSettings.cost_to_chains
            self.manager = GasBoss(self.key, self.from_chain)
            self.contract = self.manager.web3.eth.contract(address=Web3.to_checksum_address(NOGEM_FILLER_CONTRACTS[self.from_chain]), abi=ABI_FILLER)
            self.module_str = f'{self.number} {self.manager.address} | filler : {self.from_chain} => {self.to_chains}'

    async def run(self, retry=0):
        logger.info(f'{self.module_str}')
        
        if not self.is_supported_networks():
            logger.error(f'{self.module_str} | this pair of networks is not available for bridge')

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

    async def get_txn(self):
        try:
            to_chains_ids = [ids + 30000 for ids in self.get_dst_chain_ids()]
            filler_values_list = self.get_filler_values()
            filler_data = self.get_filler_data(to_chains_ids, filler_values_list)

            adapter_params = await asyncio.gather(*[self.contract.functions.createNativeDropOption(to_chains_ids[i], filler_values_list[i], self.manager.address).call() for i in range(len(self.to_chains))])
            list_message = ['0x' for _ in range(len(to_chains_ids))]
            fees = await asyncio.gather(*[self.contract.functions.estimateFees(to_chains_ids, list_message, adapter_params).call()])

            contract_txn = await self.contract.functions.sendDeposits(filler_data, self.manager.address).build_transaction(
                    {
                        "from": self.manager.address,
                        "value": sum(fees[0]),
                        "nonce": await self.manager.web3.eth.get_transaction_count(self.manager.address),
                        'gasPrice': 0
                    }
                )

            contract_txn = await self.manager.add_gas_price(contract_txn)
            contract_txn = await self.manager.add_gas_limit_layerzero(contract_txn)

            return contract_txn
        
        except Exception as error:
            logger.warning(error)
            return False
    
    async def get_test_txn(self):
        try:
            to_chains_ids = [ids + 30000 for ids in self.get_dst_chain_ids()]
            filler_values_list = self.get_filler_values()
            filler_data = self.get_filler_data(to_chains_ids, filler_values_list)

            adapter_params = await asyncio.gather(*[self.contract.functions.createNativeDropOption(to_chains_ids[i], filler_values_list[i], self.manager.address).call() for i in range(len(self.to_chains))])
            list_message = ['0x' for _ in range(len(to_chains_ids))]
            fees = await asyncio.gather(*[self.contract.functions.estimateFees(to_chains_ids, list_message, adapter_params).call()])

            contract_txn = await self.contract.functions.sendDeposits(filler_data, self.manager.address).build_transaction(
                    {
                        "from": self.manager.address,
                        "value": sum(fees[0]),
                        "nonce": await self.manager.web3.eth.get_transaction_count(self.manager.address),
                        'gasPrice': 0
                    }
                )

            contract_txn = await self.manager.add_gas_price(contract_txn)
            contract_txn = await self.manager.add_gas_limit_layerzero(contract_txn)

            return contract_txn, True
        
        except Exception as error:
            return error, False

    def get_filler_data(self, to_chains_ids, filler_values_list):
        data = []
        for i in range(len(to_chains_ids)):
            deposit_param = to_chains_ids[i] << 224
            value = filler_values_list[i]
            mask = (1 << 128) - 1
            modified_bytes = (deposit_param & ~mask) | (value & mask)
            data.append(modified_bytes)
        return data

    async def calculate_cost(self):
        contract_txn = await self.get_txn()

        if not contract_txn:
            return False        
        
        total_cost = contract_txn['value'] + contract_txn['gasPrice']*contract_txn['gas']*1.2
        return total_cost

    def get_dst_chain_ids(self):
        to_chain_ids = [LAYERZERO_CHAINS_ID[chain] for chain in self.to_chains]
        return to_chain_ids

    def get_filler_values(self):
        filler_values_list = [Web3.to_wei(round(random.uniform(FILLER_VALUE[0], FILLER_VALUE[1]), random.randint(FILLER_VALUE[2], FILLER_VALUE[3])), 'ether') for _ in self.to_chains]
        return filler_values_list

    def get_base_chains():
        return FillerSettings.from_chain
    
    def get_dest_chains():
        chains_count = random.randint(*FillerSettings.to_chains_count)
        if chains_count <= len(FillerSettings.to_chains):
            return random.sample(FillerSettings.to_chains, chains_count)
        else:
            logger.error(f"Error during destination chains selection: {chains_count} (to_chains_count) > {len(FillerSettings.to_chains)} (to_chains amount). You can't select more chains than you have in to_chains setting.")
            return False
    
    async def get_cheap_chains(number, key, from_chain):
        try:       
            result_chains = []
            total_cost = 0

            chains_list = list(NOGEM_FILLER_CONTRACTS.keys())
            chains_list.remove(from_chain)
            
            while len(chains_list) != 1:
                if result_chains == []:
                    to_chains = random.sample(chains_list, FillerSettings.min_chains_count)
                else:
                    to_chains = random.sample(chains_list, 1)
                    chains_list.remove(to_chains[0])

                chains_list = list(set(chains_list) - set(to_chains))
                to_chains.extend(result_chains)

                func = Filler(number, key, from_chain, to_chains)
                if not await func.has_balance():
                    return False
                
                if func.is_supported_networks():
                    contract_txn, txn_is_ok = await func.get_test_txn()
                    
                    if txn_is_ok:
                        cost = contract_txn['value'] + contract_txn['gasPrice']*contract_txn['gas']*1.2
                        if cost != 0:
                            cost_native = func.manager.web3.from_wei(cost,'ether')
                            cost_usd = float(cost_native) * PRICES_NATIVE[from_chain]

                            if  cost_usd < FillerSettings.cost_to_chains[1]:
                                result_chains = to_chains
                                total_cost = cost_usd
                            elif result_chains != []:
                                return result_chains
                    if 'insufficient' in str(contract_txn) and result_chains != [] and (FillerSettings.cost_to_chains[0] < total_cost < FillerSettings.cost_to_chains[1]):
                        return result_chains

            logger.warning('Cannot find random cheap chains. Please, decrease min_chains_count or adjust cost_to_chains value.')
            return False
                            
        except Exception as error:
            logger.warning(error)
            return False

    async def has_balance(self):
        balance = await self.manager.get_balance_native()
        balance_native = self.manager.web3.from_wei(balance,'ether')
        balance_usd = round(float(balance_native) * PRICES_NATIVE[self.from_chain])
        if balance_usd < FillerSettings.cost_to_chains[1]:
            logger.warning("Not enough balance")
            return False
        return True

    def is_supported_networks(self):
            for chain in self.to_chains:
                if (LAYERZERO_CHAINS_ID[self.from_chain], LAYERZERO_CHAINS_ID[chain]) in EXCLUDED_LZ_PAIRS or (LAYERZERO_CHAINS_ID[chain], LAYERZERO_CHAINS_ID[self.from_chain]) in EXCLUDED_LZ_PAIRS:
                    return False
            return True
    
    async def check_chains(number, key, from_chain):
            chains_list = list(NOGEM_FILLER_CONTRACTS.keys())
            chains_list.remove(from_chain)

            print(f'base chain: {from_chain}')
            for chain in chains_list:
                to_chains = []
                to_chains.append(chain)
                func = Filler(number, key, from_chain, to_chains)

                if not await func.has_balance():
                    return False
                
                contract_txn = await func.get_txn()

                if contract_txn is not False:
                    print('+', chain)
                else:
                    print('-', chain)

    def print_chains():
        chains_list = list(NOGEM_FILLER_CONTRACTS.keys())
        for chain in chains_list:
            print(chain, end=" | ")