import random
import sys
import asyncio
from modules.filler import Filler

import questionary
from questionary import Choice

from config import WALLETS
from settings import SHUFFLE_WALLETS
from tools.runner import process_module

def get_module():
    result = questionary.select(
        "Choose a module (more coming soon!) :",
        choices=[
            Choice(" Filler", Filler),
            #Choice("2) Mint + Bridge", MintBridge),
            #Choice("3) Mint", Mint),
            #Choice("4) Bridge", Bridge),
            #Choice("5) Refuel", Refuel),
            Choice(" Exit", "exit"),
        ],
        pointer="💠 "
    ).ask()
    if result == "exit":
        sys.exit()
    return result


async def main(module):
    if SHUFFLE_WALLETS:
        random.shuffle(WALLETS)
    await process_module(module, WALLETS)

if __name__ == "__main__":
    module = get_module()
    asyncio.run(main(module))