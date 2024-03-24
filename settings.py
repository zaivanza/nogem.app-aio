# --- Settings ---
IS_SLEEP = True         # Enable/disable delay between wallets
DELAY_SLEEP = [30, 60]  # Delay range between wallets (seconds)
SHUFFLE_WALLETS = True  # Enable/disable random wallet shuffling
RETRY = 0               # Number of retries on errors/failures
MAX_WAITING_NFT = 200   # Maximum duration (in seconds) to await the arrival of the NFT in the destination network before timing out.

class AutoFillerSettings:
    '''
    Gas auto filler via nogem

    Chains : arbitrum | polygon | bsc | optimism | fantom | core | nova | mantle | avalanche | base | linea | scroll | zora | astar | aurora | celo 
           | conflux | fuse | gnosis | kava | klaytn | manta | metis | opbnb | telos | tenet | horizen | okx | orderly | rari | viction | xpla | 
    '''

    # Networks from which you want to perform refill. Will choose one network with balance.
    from_chain =  ['optimism', 'arbitrum', 'fantom', 'bsc', 'polygon'] 
    # Min and max price in $ for one fill. Will pick up maximum amount of networks for your price range mentioned in 'cost_to_chains'.
    cost_to_chains = [1, 2]

class FillerSettings:
    '''
    Gas filler via nogem

    Chains : arbitrum | polygon | bsc | optimism | fantom | core | nova | mantle | avalanche | base | linea | scroll | zora | astar | aurora | celo 
           | conflux | fuse | gnosis | kava | klaytn | manta | metis | opbnb | telos | tenet | horizen | okx | orderly | rari | viction | xpla | 
    '''

    # Networks from which you want to perform refill.
    from_chain = ['optimism', 'arbitrum', 'fantom', 'bsc', 'polygon']  
    # Networks to which you want to perform refuel (will pick up random amount of networks based on 'to_chains_count').
    to_chains = ['gnosis', 'fuse', 'klaytn', 'opbnb', 'telos', 'orderly', 'rari', 'astar', 'aurora']
    # Count of destination chains (min and max).
    to_chains_count = [4, 9]

    #========================================Use Random Chains===========================================
    # if False, will pick up random amount of chains (within 'to_chains_count' range) from 'to_chain' list. 
    # if True, will use random cheap chains with total cost within 'cost_to_chains' range.
    use_random_chains = True  
    # Min amount of destination chains for random mode (when 'use_random_chains = True')
    min_chains_count = 3
    # Min and max price in $ for one fill.
    cost_to_chains = [1, 2]

class MintSettings:
    '''
    Minting operation

    Chains : bsc | celo | beam | manta | kava | linea | fantom | gnosis | tenet | aurora | core | polygon | opbnb 
           | nova | arbitrum | optimism | zora | okx | rari | loot | orderly | xpla | astar | viction | zksync | scroll
    '''
    # The networks where NFTs will be minted.
    chains = ['fantom']  
    # The networks where NFTs will be minted.
    amount_mint = [1, 1]  

class BridgeSettings:
        '''
        Bridging operation
        This function locates NFTs in the source chain and bridges them to a randomly selected destination chain.

        Chains : bsc | celo | beam | manta | kava | linea | fantom | gnosis | tenet | aurora | core | polygon | opbnb | nova | arbitrum 
               | optimism | zora | okx | rari | loot | orderly | xpla | astar | viction | zksync | scroll
        '''

        # The source network where NFTs will be searched; the final choice is random.
        from_chain = ['optimism', 'arbitrum', 'fantom', 'bsc', 'polygon']
        # Potential destination networks; the final choice is random.
        to_chain = ['metis', 'core', 'fuse', 'gnosis', 'tenet']
        # The number of NFTs to bridge.
        amount = 1  
        # If True, all available NFTs will be bridged, even if they exceed the specified 'amount' value.
        bridge_all = False

class MintBridgeSettings:
        '''
        Combination of minting and bridging operations

        Chains : bsc | celo | beam | manta | kava | linea | fantom | gnosis | tenet | aurora | core | polygon | opbnb | nova | arbitrum 
               | optimism | zora | okx | rari | loot | orderly | xpla | astar | viction | zksync | scroll
        '''

        # Preferred source networks, will randomly pick up network with money for mint+bridge.
        from_chain = ['zksync', 'linea', 'scroll']
        # Preferred destination networks, will randomly pick up one destination network.
        to_chain = ['optimism', 'nova', 'celo', 'core']
        # Maximum acceptable cost for the mint+bridge in dollars ($).
        max_price = 3
        # Range defining the minimum and maximum number of NFTs to be minted and bridged.
        amount = [1, 2]

class RefuelSettings:

    '''
    Gas refuel via nogem

     Chains : arbitrum | nova | bsc | avalanche | polygon | fantom | celo | fuse | gnosis | klaytn | core | tenet | kava | mantle 
            | beam | telos | opbnb | aurora | conflux | scroll | horizen | manta | xpla | okx | rari | zora | optimism | loot | orderly | 
    '''

    # Networks from which you want to perform refuel.
    from_chain = ['fantom', 'polygon']
    # Networks to which you want to perform refuel.
    to_chain = ['avalanche', 'rari', 'tenet', 'opbnb', 'manta']

    # Obtain from a certain amount of native token of the to_chain network.
    amount_from = 0.0000001
    # Obtain up to a certain amount of native token of the to_chain network.
    amount_to = 0.000002

    # True / False. If True, then refuel the entire balance.
    swap_all_balance = False
    # If the balance is less than this amount, no refuel will be made.
    min_amount_swap = 0  
    # How many coins to keep on the wallet (only works when: swap_all_balance = True).
    keep_value_from = 0
    # Up to how many coins to keep on the wallet (only works when: swap_all_balance = True).
    keep_value_to = 0