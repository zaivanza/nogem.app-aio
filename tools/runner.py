import random

from web3 import Web3
from data.rpc import RPC
from modules.hyperlane.bridge_hl import BridgeHL
from modules.hyperlane.bridge_tokens_hl import BridgeTokenHL
from modules.hyperlane.claim_bridge_hl import ClaimBridgeTokenHL
from modules.hyperlane.claim_hl import ClaimHL
from modules.hyperlane.mint_bridge_hl import MintBridgeHL
from modules.layerzero.bridge import Bridge
from modules.layerzero.filler import Filler
from modules.layerzero.auto_filler import AutoFiller
from modules.layerzero.mint import Mint
from modules.layerzero.mint_bridge import MintBridge
from modules.hyperlane.mint_hl import MintHL
from modules.layerzero.refuel import Refuel
from settings import ClaimBridgeSettingsHL, ClaimSettingsHL, MintBridgeSettingsHL, MintBridgeSettingsLZ, MintSettingsHL, MintSettingsLZ
from settings import IS_SLEEP, DELAY_SLEEP, FillerSettings

from tools.helpers import async_sleeping, is_private_key

from loguru import logger

async def process_module(func, wallets):
    if func == None:
        logger.info('Stopping application.')
    else:
        number = 0
        for key in wallets:
                try:
                    number += 1
                    dest_chain = await get_dest_chain(func)
                    if is_private_key(key):
                        if dest_chain is not False:
                            wallet_number =  f'[{number}/{len(wallets)}]'
                            mint_count = get_amount_mint(func)

                            base_chain, dest_chain = await find_chain_with_balance(func, key, wallet_number, dest_chain, mint_count) 

                            if base_chain is not None:
                                function = get_func(func, key, wallet_number, base_chain, dest_chain, mint_count)
                                await function.run()
                    else:
                        logger.error(f"{key} isn't private key")

                    if IS_SLEEP and number != len(wallets):
                        await async_sleeping(*DELAY_SLEEP)

                except Exception as error:
                    logger.error(error)

async def get_dest_chain(func):
    if func in (Bridge, MintBridge, Refuel, BridgeHL, MintBridgeHL, BridgeTokenHL, ClaimBridgeTokenHL):
        return random.choice(func.get_dest_chains())
    elif func == Filler:
        if not FillerSettings.use_random_chains:
            return func.get_dest_chains()
        else:
            return None

async def find_chain_with_balance(func, key, number, dest_chain, mint_count): 
    try:
        address = get_address(key)
        base_chains = func.get_base_chains()
        random.shuffle(base_chains)

        for chain in base_chains:
            logger.info(f"{number} {address} Checking balance in {chain}")
            to_chain = dest_chain

            if func == Filler and FillerSettings.use_random_chains:
                to_chain = await func.get_cheap_chains(number, key, chain)

            if func == AutoFiller:
                to_chain = await func.get_max_chains(number, key, chain)

            if to_chain is not False:
                function = get_func(func, key, number, chain, to_chain, mint_count)
                total_cost = await function.calculate_cost()
                if total_cost is not False:
                    balance = await function.manager.get_balance_native()
                    if balance >= total_cost:
                        return chain, to_chain
        logger.error(f'Execution is failed in all base chains {base_chains}. Please, check warnings from logs above to identify the issue.')               
        return None, dest_chain
    except Exception as error:
        logger.error(error)

def get_func(func, key, number, base_chain, dest_chain, mint_count=0):
    if func in (Mint, MintHL, ClaimHL):
        return func(number, key, base_chain, mint_count)
    elif func in (MintBridge, MintBridgeHL, ClaimBridgeTokenHL):
        return func(number, key, base_chain, dest_chain, mint_count)
    else:
        return func(number, key, base_chain, dest_chain)

def get_address(key):
    rpc = RPC['ethereum']['rpc']
    w3 = Web3(Web3.HTTPProvider(rpc))
    account = w3.eth.account.from_key(key)
    return account.address

def get_amount_mint(func):
    if func == MintHL:
        return  random.randint(*MintSettingsHL.amount_mint)
    elif func == MintBridgeHL:
        return random.randint(*MintBridgeSettingsHL.amount)
    elif func == ClaimHL:
        return random.randint(*ClaimSettingsHL.count_claim)
    elif func == ClaimBridgeTokenHL:
        return random.randint(*ClaimBridgeSettingsHL.amount)
    elif func == Mint:
        return random.randint(*MintSettingsLZ.amount_mint)
    elif func == MintBridge:
        return random.randint(*MintBridgeSettingsLZ.amount)