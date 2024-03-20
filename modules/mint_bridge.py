import random

from loguru import logger
from config import PRICES_NATIVE
from modules.bridge import Bridge
from modules.mint import Mint

from settings import MintBridgeSettings
from tools.gas_boss import GasBoss

class MintBridge:
    def __init__(self, number, key, from_chain, dest_chain) -> None:
        self.number = number
        self.key = key
        self.from_chain = from_chain
        self.to_chain = dest_chain
        self.maxPrice = MintBridgeSettings.max_price
        self.amount = random.randint(*MintBridgeSettings.amount)
        self.manager = GasBoss(key, self.from_chain)
        self.module_str = f'{self.number} {self.manager.address} | mint&bridge | {self.from_chain} => {self.to_chain}'

    async def run(self):
        mint_func = Mint(self.number, self.key, self.from_chain, self.amount)
        await mint_func.run()
        
        bridge_func = Bridge(self.number, self.key, self.from_chain, self.to_chain, self.amount)
        await bridge_func.run()

    async def calculate_cost(self):
        mint_func = Mint(self.number, self.key, self.from_chain, self.amount)
        mint_cost = await mint_func.calculate_cost()
        bridge_func = Bridge(self.number, self.key, self.from_chain, self.to_chain, self.amount)
        bridge_cost = await bridge_func.calculate_cost()

        if not mint_cost or not bridge_cost:
            return False
        
        total_cost = mint_cost + bridge_cost
        total_cost_native = self.manager.web3.from_wei(total_cost,'ether')
        total_cost_usd = float(total_cost_native) * PRICES_NATIVE[self.from_chain]
        if total_cost_usd > MintBridgeSettings.max_price:  
            logger.info(f'Total cost for mint + bridge > {MintBridgeSettings.max_price}$') 
            return False

        return total_cost
    
    def get_base_chains():
        return MintBridgeSettings.from_chain
    
    def get_dest_chains():
        return MintBridgeSettings.to_chain