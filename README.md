# nogem.app-aio

1. Добавьте свои private keys в файл wallets.txt в папке data.
2. По желанию можно вставить свои rpc в файле rpc.py в папке data.
3. Вся настройка модулей происходит в файле settings.py:
    FillerSettings:
    - from_chains - список из сетей с которой будем бриджить, также циклом ищет сеть в которой есть деньги для бриджа в to_chains
    - to_chains - в какие сети будем бриджить
    - is_cheap_to_chains = True / False. если True, тогда скрипт будет собирать to_chains основываясь на cost_to_chains, если False, то берем сети из to_chains
    - to_chains_count - сколько сетей выберем из to_chains
    - cost_to_chains ($) - сколько долларов готовы выделить на бридж. скрипт будет считать стоимость бриджа в каждую сеть и рандомно собирать to_chains в пределах этих cost_to_chains в которые будем бриджить из from_chain.
4. Запуск:
    pip install -r requirements.txt
    
    python main.py