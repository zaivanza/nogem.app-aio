import time
import json
from tqdm import tqdm
import asyncio
import aiohttp
import random
from pathlib import Path
from data.rpc import RPC
from eth_account import Account
from tools.contracts.abi import ABI_NOGEM_HL_ERC20, ABI_NOGEM_HL_NFT, ABI_NOGEM_LZ
from tools.contracts.contract import HYPERLANE_ERC20, HYPERLANE_HNFT, LAYERZERO_ONFT
from web3 import AsyncHTTPProvider, Web3
from web3.eth import AsyncEth
import math

from loguru import logger


def round_to(num, digits=3):
    try:
        if num == 0:
            return 0
        scale = int(-math.floor(math.log10(abs(num - int(num))))) + digits - 1
        if scale < digits:
            scale = digits
        return round(num, scale)
    except:
        return num


def intToDecimal(qty, decimal):
    return int(qty * 10**decimal)


def decimalToInt(qty, decimal):
    return float(qty / 10**decimal)


def load_json(filepath: Path | str):
    with open(filepath, "r") as file:
        return json.load(file)


def read_txt(filepath: Path | str):
    with open(filepath, "r") as file:
        return [row.strip() for row in file]


def call_json(result: list | dict, filepath: Path | str):
    with open(f"{filepath}.json", "w") as file:
        json.dump(result, file, indent=4, ensure_ascii=False)


def address_to_bytes32(address: str):
    address = address[2:] if address.startswith('0x') else address
    address_bytes = bytes.fromhex(address)
    return address_bytes.rjust(32, b'\0')


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


async def get_contract_lz(chain):
    web3 = Web3(AsyncHTTPProvider(RPC[chain]['rpc']), modules={
                "eth": (AsyncEth)}, middlewares=[])
    return web3.eth.contract(address=Web3.to_checksum_address(LAYERZERO_ONFT[chain]), abi=ABI_NOGEM_LZ)


async def get_contract_hl_nft(chain):
    web3 = Web3(AsyncHTTPProvider(RPC[chain]['rpc']), modules={
                "eth": (AsyncEth)}, middlewares=[])
    return web3.eth.contract(address=Web3.to_checksum_address(HYPERLANE_HNFT[chain]), abi=ABI_NOGEM_HL_NFT)


async def get_contract_hl_erc20(chain):
    web3 = Web3(AsyncHTTPProvider(RPC[chain]['rpc']), modules={
                "eth": (AsyncEth)}, middlewares=[])
    return web3.eth.contract(address=Web3.to_checksum_address(HYPERLANE_ERC20[chain]), abi=ABI_NOGEM_HL_ERC20)


async def get_balance_nfts_amount(contract, owner):
    return await contract.functions.balanceOf(Web3.to_checksum_address(owner)).call()


async def get_balance_nfts_id(contract, owner, i):
    return await contract.functions.tokenOfOwnerByIndex(Web3.to_checksum_address(owner), i).call()


async def get_balance_hl_nfts_id(contract, owner):
    return await contract.functions.tokensOfOwner(Web3.to_checksum_address(owner)).call()


def get_web3(self, chain):
    web3 = Web3(AsyncHTTPProvider(RPC[chain]['rpc']), modules={
                "eth": AsyncEth}, middlewares=[])
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
        'mode': 'ETH',
    }

    prices = {chain: 0 for chain in chains.keys()}
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_price(session, symbol) for symbol in chains.values()]
        fetched_prices = await asyncio.gather(*tasks)

        for chain, price in zip(chains.keys(), fetched_prices):
            prices[chain] = price
            if price == 0:
                price = await fetch_price(session, chains[chain])
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