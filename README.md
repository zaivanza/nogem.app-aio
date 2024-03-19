[![Typing SVG](https://readme-typing-svg.herokuapp.com?color=%2336BCF7&lines=Nogem.app-AIO)](https://git.io/typing-svg)

Софт, в котором есть все модули, которые есть в https://nogem.app

# Настройка
1. Переименуй папку data_EXAMPLE в data.
2. Добавьте свои private keys в файл wallets.txt в папке data.
3. По желанию можно вставить свои rpc в файле rpc.py в папке data.
4. Вся настройка модулей происходит в файле settings.py:
    FillerSettings:
    - from_chains - список из сетей с которой будем бриджить, также циклом ищет сеть в которой есть деньги для бриджа в to_chains
    - to_chains - в какие сети будем бриджить
    - is_cheap_to_chains = True / False. если True, тогда скрипт будет собирать to_chains основываясь на cost_to_chains, если False, то берем сети из to_chains
    - to_chains_count - сколько сетей выберем из to_chains
    - cost_to_chains ($) - сколько долларов готовы выделить на бридж. скрипт будет считать стоимость бриджа в каждую сеть и рандомно собирать to_chains в пределах этих cost_to_chains в которые будем бриджить из from_chain.

# Запуск
1. Скачиваем библиотеки: `pip install -r requirements.txt`
2. Запускаем файл main.py

## Донаты (EVM): 
- `0xb7415DB78c886c67DBfB25D3Eb7fcd496dAf9021`
- `donates-for-hodlmod.eth`

## Links:
- https://t.me/links_hodlmodeth
- Code chat: [[ code ]](https://t.me/code_hodlmodeth)
- Ультимативный гайд по запуску скриптов на python : https://teletype.in/@hodlmod.eth/how-to-run-scripts