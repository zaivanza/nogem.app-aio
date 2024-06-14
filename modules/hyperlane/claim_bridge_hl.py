import random

from loguru import logger
from config import PRICES_NATIVE
from modules.hyperlane.bridge_tokens_hl import BridgeTokenHL
from modules.hyperlane.claim_hl import ClaimHL
from modules.layerzero.mint_bridge import MintBridge
from settings import ClaimBridgeSettingsHL
from tools.gas_boss import GasBoss


class ClaimBridgeTokenHL(MintBridge):
    def __init__(self, number, key, from_chain, dest_chain, mint_amount) -> None:
        self.number = number
        self.key = key
        self.from_chain = from_chain
        self.to_chain = dest_chain
        self.maxPrice = ClaimBridgeSettingsHL.max_price
        self.amount = mint_amount
        self.manager = GasBoss(key, self.from_chain)
        self.module_str = f'{self.number} {self.manager.address} | claim&bridge | {self.from_chain} => {self.to_chain}'

    async def run(self):
        mint_func = ClaimHL(self.number, self.key, self.from_chain, self.amount)
        result = await mint_func.run()
        if result is not False:
            bridge_func = BridgeTokenHL(self.number, self.key, self.from_chain, self.to_chain, self.amount)
            await bridge_func.run()

    async def calculate_cost(self):
        mint_func = ClaimHL(self.number, self.key, self.from_chain, self.amount)
        
        mint_cost = await mint_func.calculate_cost()
        if mint_cost is not False:
            bridge_func = BridgeTokenHL(self.number, self.key, self.from_chain, self.to_chain, self.amount)
            bridge_cost = await bridge_func.calculate_cost()
        elif not mint_cost:
            return False
        
        if not bridge_cost:
            return False
        
        total_cost = mint_cost + bridge_cost
        total_cost_native = self.manager.web3.from_wei(total_cost,'ether')
        total_cost_usd = float(total_cost_native) * PRICES_NATIVE[self.from_chain]
        
        if total_cost_usd > ClaimBridgeSettingsHL.max_price:  
            logger.info(f'Total cost for claim + bridge > {ClaimBridgeSettingsHL.max_price}$') 
            return False

        return total_cost
    
    def get_base_chains():
        return ClaimBridgeSettingsHL.from_chain
    
    def get_dest_chains():
        return ClaimBridgeSettingsHL.to_chain