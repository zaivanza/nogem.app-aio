import asyncio
from tools.helpers import read_txt,load_json,get_chain_prices

MAX_TX_WAITING_TIME = 200

WALLETS = read_txt("data/wallets.txt")
ERC20_ABI = load_json("tools/contracts/erc20.json")

FILLER_VALUE = [0.0000051234, 0.00000051234, 8, 11] 

PRICES_NATIVE = asyncio.run(get_chain_prices())