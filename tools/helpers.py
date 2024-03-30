import time
import json
from tqdm import tqdm
import asyncio, aiohttp
import random
from pathlib import Path
from data.rpc import RPC
from eth_account import Account
from tools.contracts.abi import ABI_NOGEM
from tools.contracts.contract import NOGEM_CONTRACTS
from web3 import AsyncHTTPProvider, Web3
from web3.eth import AsyncEth

from loguru import logger


def decimalToInt(qty, decimal):
    return float(qty * 10**decimal)

def load_json(filepath: Path | str):
    with open(filepath, "r") as file:
        return json.load(file)


def read_txt(filepath: Path | str):
    with open(filepath, "r") as file:
        return [row.strip() for row in file]


def call_json(result: list | dict, filepath: Path | str):
    with open(f"{filepath}.json", "w") as file:
        json.dump(result, file, indent=4, ensure_ascii=False)

def sleeping(from_sleep, to_sleep):
    x = random.randint(from_sleep, to_sleep)
    for i in tqdm(range(x), desc='sleep ', bar_format='{desc}: {n_fmt}/{total_fmt}'):
        time.sleep(1)

async def async_sleeping(from_sleep, to_sleep):
    x = random.randint(from_sleep, to_sleep)
    for i in tqdm(range(x), desc='sleep ', bar_format='{desc}: {n_fmt}/{total_fmt}'):
        await asyncio.sleep(1)

def is_private_key(key):
    try:
        return Account().from_key(key).address
    except:
        return False

async def get_contract(chain):
    web3 = Web3(AsyncHTTPProvider(RPC[chain]['rpc']), modules={
                "eth": (AsyncEth)}, middlewares=[])
    return web3.eth.contract(address=Web3.to_checksum_address(NOGEM_CONTRACTS[chain]), abi=ABI_NOGEM)

async def get_balance_nfts_amount(contract, owner):
    return await contract.functions.balanceOf(Web3.to_checksum_address(owner)).call()

async def get_balance_nfts_id(contract, owner, i):
    return await contract.functions.tokenOfOwnerByIndex(Web3.to_checksum_address(owner), i).call()

def get_web3(self, chain):
    web3 = Web3(AsyncHTTPProvider(RPC[chain]['rpc']), modules={"eth": AsyncEth}, middlewares=[])
    return web3

async def get_chain_prices():
    chains = {
        'avalanche': 'AVAX',
        'polygon': 'MATIC',
        'ethereum': 'ETH',
        'bsc': 'BNB',
        'arbitrum': 'ETH',
        'optimism': 'ETH',
        'fantom': 'FTM',
        'zksync': 'ETH',
        'nova': 'ETH',
        'gnosis': 'xDAI',
        'celo': 'CELO',
        'polygon_zkevm': 'ETH',
        'core': 'COREDAO',
        'harmony': 'ONE',
        'moonbeam': 'GLMR',
        'moonriver': 'MOVR',
        'linea': 'ETH',
        'base': 'ETH',
        'scroll': 'ETH',
        'zora': 'ETH',
        'mantle': 'MNT',
        'zeta': 'ZETA',
        'blast': 'ETH',
    }

    prices = {chain: 0 for chain in chains.keys()}
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_price(session, symbol) for symbol in chains.values()]
        fetched_prices = await asyncio.gather(*tasks)

        for chain, price in zip(chains.keys(), fetched_prices):
            prices[chain] = price
            if price == 0:
                price =  await fetch_price(session, chains[chain])
                if price != 0:
                    prices[chain] = price
                else:
                    logger.info(f'Failed to fetch price for {chain}. Setting price to 0.')

    return prices

async def fetch_price(session, symbol):
    url = f'https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USDT'
    try:
        async with session.get(url, timeout=10) as resp:
            if resp.status == 200:
                resp_json = await resp.json(content_type=None)
                return float(resp_json.get('USDT', 0))
            else:
                await asyncio.sleep(1)
                return await fetch_price(session, symbol)
    except Exception as error:
        await asyncio.sleep(1)
        return await fetch_price(session, symbol)