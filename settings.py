# --- Settings ---
IS_SLEEP = True         # Enable/disable delay between wallets
DELAY_SLEEP = [30, 60]  # Delay range between wallets (seconds)
SHUFFLE_WALLETS = True  # Enable/disable random wallet shuffling
RETRY = 0               # Number of retries on errors/failures
MAX_WAITING_NFT = 200   # Maximum duration (in seconds) to await the arrival of the NFT in the destination network before timing out.


class MintSettings:
    '''
    Minting operation
    Chains : arbitrum | optimism | bsc | polygon | base | avalanche | ethereum | scroll | zksync | linea | nova | zora | polygon_zkevm | fantom | core | celo | harmony | canto | starknet | mantle
    '''

    chains = ['scroll','bsc', 'avalanche']  # The networks where NFTs will be minted.
    amount_mint = [1, 1]  # The exact number of NFTs to mint.


class BridgeSettings:
        '''
        Bridging operation
        This function locates NFTs in the source chain and bridges them to a randomly selected destination chain.
        Chains : arbitrum | optimism | bsc | polygon | base | avalanche | ethereum | scroll | zksync | linea | nova | zora | polygon_zkevm | fantom | core | celo | harmony | canto | starknet | mantle
        '''

        # The source network where NFTs will be searched; the final choice is random.
        from_chain = ['optimism', 'zksync']
        # Potential destination networks; the final choice is random.
        to_chain = ['celo','scroll']

        amount = 1  # The number of NFTs to bridge.
        # If True, all available NFTs will be bridged if they exceed the specified 'amount'.
        bridge_all = False

class MintBridgeSettings:
        '''Combination of minting and bridging operations'''

        # Preferred source networks due to lower costs; selection is random if list is empty.
        from_chain = ['optimism', 'zksync', 'ethereum', 'linea', 'polygon']
        # Preferred destination networks due to lower costs; selection is random if list is empty.
        to_chain = ['base', 'nova']
        # Maximum acceptable cost for the process in dollars ($).
        max_price = 3
        # Range defining the minimum and maximum number of NFTs to be minted and bridged.
        amount = [1, 2]

class RefuelSettings:

    '''
    Gas refuel via nogem

    from_chains : optimism | bsc | polygon | arbitrum | avalanche | fantom | linea | celo | zksync | polygon_zkevm | nova | canto | zora | scroll | harmony | gnosis | core | base | mantle
    to_chains   : avalanche | bsc | arbitrum | optimism | fantom | harmony | celo | moonbeam | gnosis | metis | core | polygon_zkevm | canto | zksync | nova | zora | base | scroll | mantle
    '''

    # Networks from which you want to perform refuel (>= 1 network)
    from_chain = ['fantom']
    # Networks to which you want to perform refuel (>= 1 network)
    to_chain = ['mantle']

    # Obtain from a certain amount of native token of the to_chain network
    amount_from = 0.0000001
    # Obtain up to a certain amount of native token of the to_chain network
    amount_to = 0.000002

    swap_all_balance = False  # True / False. If True, then refuel the entire balance
    min_amount_swap = 0  # If the balance is less than this amount, no refuel will be made
    # How many coins to keep on the wallet (only works when: swap_all_balance = True)
    keep_value_from = 0
    # Up to how many coins to keep on the wallet (only works when: swap_all_balance = True)
    keep_value_to = 0

    # True if you want to check the gas. False if you want to perform refuel
    get_layerzero_fee = False

class FillerSettings:
    '''
    Gas filler via nogem

    from_chains : optimism | bsc | polygon | arbitrum | avalanche | fantom | linea | celo | nova | canto | zora | scroll | gnosis | core | base | mantle | astar |
                  conflux | fuse | gnosis | kava | klaytin | manta | metis | opbnb | telos | tenet | horizen | okt | orderly | rari | viction | xpla | 
    to_chains   : avalanche | bsc | arbitrum | optimism | fantom  | celo | gnosis | metis | core | canto  | nova | zora | base | scroll | mantle | polygon |
                  astar | conflux | fuse | gnosis | kava | klaytin | manta | metis | opbnb | telos | tenet | horizen | okt | orderly | rari | viction | xpla |
    '''

    # Networks from which you want to perform refill
    from_chain = ['optimism', 'polygon', 'arbitrum', 'fantom', 'bsc']  
    # Networks to which you want to perform refuel (will pick up random amount of networks based on to_chains_count)
    to_chains = ['gnosis', 'fuse', 'core', 'klaytn', 'celo', 'opbnb', 'viction']
    # Count of destination chains (min and max)
    to_chains_count = [2, 3]
    # If True, will choose destination chains based on cost (cost_to_chains value), if False will pick up random chains from to_chains
    is_cheap_to_chains = True  
    # Min and max price in $ for one fill
    cost_to_chains = [2, 3]