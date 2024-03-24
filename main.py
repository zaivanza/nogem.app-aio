import random
import sys
import asyncio
from modules.bridge import Bridge
from modules.filler import Filler

import questionary
from questionary import Choice

from config import WALLETS
from modules.auto_filler import AutoFiller
from modules.mint import Mint
from modules.mint_bridge import MintBridge
from modules.refuel import Refuel
from settings import SHUFFLE_WALLETS
from tools.runner import process_module

def get_module():
    result = questionary.select(
        "Choose a module (more coming soon!) :",
        choices=[
            Choice("1) Auto Filler", AutoFiller),
            Choice("2) Filler", Filler),
            Choice("3) Mint + Bridge", MintBridge),
            Choice("4) Mint", Mint),
            Choice("5) Bridge", Bridge),
            Choice("6) Refuel", Refuel),
            Choice("7) Exit", "exit"),
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