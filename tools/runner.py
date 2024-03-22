import random
from modules.bridge import Bridge
from modules.filler import Filler
from modules.filler_ultra import FillerUltra
from modules.mint import Mint
from modules.mint_bridge import MintBridge
from modules.refuel import Refuel
from settings import MintSettings
from settings import IS_SLEEP, DELAY_SLEEP, FillerSettings

from tools.helpers import async_sleeping, is_private_key

from loguru import logger

async def process_module(func, wallets):
    number = 0
    try:
        for key in wallets:
            number += 1
            dest_chain = await get_dest_chain(func)
            if is_private_key:
                if dest_chain is not False:
                    wallet_number =  f'[{number}/{len(wallets)}]'
                    mint_count = random.randint(*MintSettings.amount_mint)
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
    if func == Bridge or func == MintBridge or func == Refuel:
        return random.choice(func.get_dest_chains())
    elif func == Filler:
        if not FillerSettings.use_random_chains:
            return func.get_dest_chains()
        else:
            return None

async def find_chain_with_balance(func, key, number, dest_chain, mint_count): 
    base_chains = func.get_base_chains()
    random.shuffle(base_chains)

    for chain in base_chains:
        logger.info(f"{number} Checking balance in {chain}")
        to_chain = dest_chain

        if func == Filler and FillerSettings.use_random_chains:
            to_chain = await func.get_cheap_chains(number, key, chain)

        # if func == FillerUltra:
        #     to_chain = await func.get_max_chains(number, key, chain)
        #     return chain, to_chain

        if to_chain is not False:
            function = get_func(func, key, number, chain, to_chain, mint_count)
            total_cost = await function.calculate_cost()
            if total_cost is not False:
                balance = await function.manager.get_balance_native()
                if balance >= total_cost:
                    return chain, to_chain
    logger.error(f'Execution is failed in all base chains {base_chains}. Please, check warnings from logs above to identify the issue.')               
    return None, dest_chain

def get_func(func, key, number, base_chain, dest_chain, mint_count=0):
    function_instance = func(number, key, base_chain, dest_chain) if func != Mint else func(number, key, base_chain, mint_count)
    return function_instance