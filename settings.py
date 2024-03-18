# --- Settings ---
IS_SLEEP = True         # Enable/disable delay between wallets
DELAY_SLEEP = [30, 60]  # Delay range between wallets (seconds)
SHUFFLE_WALLETS = True  # Enable/disable random wallet shuffling
RETRY = 0               # Number of retries on errors/failures

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
    is_cheap_to_chains = False  
    # Min and max price in $ for one fill
    cost_to_chains = [2, 3]  