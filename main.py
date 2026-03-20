import os
import requests
from time import sleep
from telethon import TelegramClient, sync, functions
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.functions.messages import GetMessagesViewsRequest
from telethon.sessions import StringSession

API_ID = 32030400
API_HASH = '4c3fae71d5765498f8c691a5b33ddf31'
SESSION_STRING = os.environ.get("SESSION_STRING")
BOT_USERNAME = os.environ.get("BOT_USERNAME")

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

async def start_process():
    await client.connect()
    if not await client.is_user_authorized():
        print("- Session Invalid")
        return

    me = await client.get_me()
    user_id = me.id
    
    response = requests.get(f"https://bot.keko.dev/api/?login={user_id}&bot_username={BOT_USERNAME}").json()
    
    if response.get("ok"):
        echo_token = response["token"]
        print(f"- Logged in. Token: {echo_token}")
    else:
        print(f"- Login Error: {response.get('msg')}")
        return

    while True:
        try:
            res = requests.get(f"https://bot.keko.dev/api/?token={echo_token}").json()
            
            if not res.get("ok"):
                print(f"- API Error: {res.get('msg')}")
                sleep(60)
                continue

            target = res.get("return")
            print(f"- Processing: {res.get('type')} -> {target}")

            if res.get("type") == "link":
                await client(ImportChatInviteRequest(res["tg"]))
            else:
                await client(JoinChannelRequest(target))
            
            sleep(2)
            entity = await client.get_entity(target)
            messages = await client.get_messages(entity, limit=10)
            msg_ids = [m.id for m in messages]
            
            await client(GetMessagesViewsRequest(peer=target, id=msg_ids, increment=True))
            
            done_res = requests.get(f"https://bot.keko.dev/api/?token={echo_token}&done={target}").json()
            if done_res.get("ok"):
                print(f"- Points: {done_res.get('c')}")
            
            sleep(30)
            
        except Exception as e:
            print(f"- Error: {e}")
            sleep(100)

with client:
    client.loop.run_until_complete(start_process())
