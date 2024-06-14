from loguru import logger
from modules.layerzero.mint import Mint
from settings import MintSettingsHL
from tools.helpers import get_contract_hl_nft


class MintHL(Mint):
    async def get_txn(self):
        try:
            self.contract = await get_contract_hl_nft(self.chain)
            mint_fee = await self.contract.functions.mintFee().call()

            contract_txn = await self.contract.functions.mint().build_transaction(
                {
                    "from": self.manager.address,
                    "value": mint_fee,
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
        
    def get_base_chains():
        return MintSettingsHL.chains