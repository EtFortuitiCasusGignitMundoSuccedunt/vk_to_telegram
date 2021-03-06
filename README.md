# vk_to_telegram
This scripts can help to forward messages from vk to Telegram

***

## Dependences and installation

This script tested with python 3.7

To install you should do next:

1. `pip3 intall vk_api; pip3 install pyTelegramBotAPI`
2. `git clone https://github.com/EtFortuitiCasusGignitMundoSuccedunt/vk_to_telegram.git`

## Configs
First of all you should generate config file. `config_maker.py` and `vk_token_get.py` help you. Or you can write it by yourself. Config should be in `~/.config/vk_to_telegram/config`.

### Manually
Example( comments in `<>` must be deleted):
```
[General]
bot_token = 00000000:AAAAAAAAAAAAAAAAAAAAAAAAAAAAA <telegram bot token>
user_ids = [0, 1, 2] <telegram users ids to which will forward messages>
vk_users = ['temp1','temp2'] <vk users headers>

[temp1]
token = 0a0a00a0a0aa00a0a0a0a0a00 <vk token>
chat_users = [0, 1, 3, 70] <users from which messages will be forwarded, or * for all private messages>
chats = [1, 34] <chats from which messages will be forwarded, * don't work with chats>

[temp2]
token = a0a00a0a0aa00a0a0a0a0a00
chat_users = *
chats = []
```

### By Scripts

1. Get vk_api token( it should have access to offline, notify, messages). Example:`./vk_token_get.py -s offline notify messages`
2. Generate configs and add vk account with token. `./config_maker.py`

## Usage

It will run on VPS/VDS. Not tested with heroku and same servises, but it should work, if you change config path( 7th line in `resender.py`).

To conntact with Bot you can use Telegram commands:
1. `/stop`  to pause bot
2. `/start` to resume
3. `/kill`  to kill bot( it kills bot's pid, doesn't work with Windows server). You can kill bot manually
