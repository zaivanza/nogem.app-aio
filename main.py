import random
import sys
import asyncio
from modules.bridge import Bridge
from modules.filler import Filler

import questionary
from questionary import Choice

from config import WALLETS
from modules.filler_ultra import FillerUltra
from modules.mint import Mint
from modules.mint_bridge import MintBridge
from modules.refuel import Refuel
from settings import SHUFFLE_WALLETS
from tools.runner import process_module

def get_module():
    result = questionary.select(
        "Choose a module (more coming soon!) :",
        choices=[
            Choice("1) Filler", Filler),
            Choice("2) Mint + Bridge", MintBridge),
            Choice("3) Mint", Mint),
            Choice("4) Bridge", Bridge),
            Choice("5) Refuel", Refuel),
            #Choice("6) FillerUltra", FillerUltra),
            Choice("6) Exit", "exit"),
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