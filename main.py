import random
import sys
import asyncio
from modules.hyperlane.bridge_hl import BridgeHL
from modules.hyperlane.bridge_tokens_hl import BridgeTokenHL
from modules.hyperlane.claim_bridge_hl import ClaimBridgeTokenHL
from modules.hyperlane.claim_hl import ClaimHL
from modules.hyperlane.mint_bridge_hl import MintBridgeHL
from modules.layerzero.bridge import Bridge
from modules.layerzero.filler import Filler

import questionary
from questionary import Choice

from config import WALLETS
from modules.layerzero.auto_filler import AutoFiller
from modules.layerzero.mint import Mint
from modules.layerzero.mint_bridge import MintBridge
from modules.hyperlane.mint_hl import MintHL
from modules.layerzero.refuel import Refuel
from settings import SHUFFLE_WALLETS
from tools.runner import process_module

def get_project():
    result = questionary.select(
        "Choose project ",
        choices=[
            Choice("1) Hyperlane", "hyperlane"),
            Choice("2) LayerZero", "layerzero"),
            Choice("3) Exit", "exit")
        ],
        pointer="💠 "
    ).ask()
    if result == "exit":
        sys.exit()
    return result
    

def get_lz_module():    
    result = questionary.select(
        "Choose a module :",
        choices=[
            Choice("1) Auto Filler", AutoFiller),
            Choice("2) Filler", Filler),
            Choice("3) Mint + Bridge NFT", MintBridge),
            Choice("4) Mint NFT", Mint),
            Choice("5) Bridge NFT", Bridge),
            Choice("6) Refuel", Refuel),
            Choice("7) <- Back", "back"),
        ],
        pointer="💠 "
    ).ask()
    return result


def get_hl_module():    
    result = questionary.select(
        "Choose a module :",
        choices=[
            Choice("1) Mint NFT", MintHL),
            Choice("2) Bridge NFT", BridgeHL),
            Choice("3) Mint + Bridge NFT", MintBridgeHL),
            Choice("4) Claim tokens", ClaimHL), 
            Choice("5) Bridge tokens", BridgeTokenHL),
            Choice("6) Claim + Bridge tokens", ClaimBridgeTokenHL),
            Choice("7) <- Back", "back"),
        ],
        pointer="💠 "
    ).ask()
    return result


def get_module():
    while True:
        project = get_project()
        module = get_hl_module() if project == "hyperlane" else get_lz_module()
        if module != "back":
            return module


async def main(module):
    if SHUFFLE_WALLETS:
        random.shuffle(WALLETS)
    await process_module(module, WALLETS)

if __name__ == "__main__":
    module = get_module()
    asyncio.run(main(module))