from nonebot import on_command, CommandSession
import requests

@on_command('help')
async def help(session: CommandSession):
    help_text = (
        "Available commands:\n"
        "- help: Show this help message\n"
        "\n"
        "Nowcoder Commends:\n"
        "- nc--contest: Get the latest Nowcoder contests\n"
        "- nc--add-user <user_id>: Add a Nowcoder user\n"
        "- nc--delete-user <user_id>: Delete a Nowcoder user\n"
        "- nc--user-list: Get the list of monitored Nowcoder users\n"
    )
    await session.send(help_text)

@on_command('nc--contest')
async def get_latest_contest(session: CommandSession):
    params = {
        "action" : "get_latest_contest",
    }
    await session.send("Getting Nowcoder latest contest...")
    r = requests.get(url="http://127.0.0.1:6060/api/nowcoder", params=params, timeout=10)
    if r.status_code != 200:
        await session.send("Server connect erro!")
        return
    if r.json()["status"] != True :
        await session.send("Nowcoder server erro!")
        return 
    contest = r.json()["contest"]
    result = "<-Coming Contests->\n"
    for con in contest :
        result = result + f'Contest Name: {con["contest_name"]}\nLink: {con["contest_link"]}\nStart time: {con["start_time"]}\nEnd time: {con["end_time"]}\nLength: {(con["length"])} mins\n\n'
    await session.send(result)

# @on_command('nc--add-contest')
# async def add_contest(session: CommandSession):
#     user_id = session.current_arg_text.strip()
#     if not user_id :
#         await session.send("Please input user ID !")
#         return
#     params = {
#         "action" : "add_contest",
#         "contest_id" : int(contest_id)
#     }
#     r = requests.get(url="http://127.0.0.1:6060/api/nowcoder", params=params, timeout=10)
#     if r.status_code != 200:
#         await session.send("Server connect erro!")
#         return
#     if r.json()["status"] != True :
#         await session.send("Nowcoder server erro!")
#         return 
#     if r.json()["success"] != True:
#         await session.send(f"user_id : {user_id} Not Found !")
#     user_info = r.json()["user_info"]
#     await session.send(f"NowCoder add user : {user_info['user_name']}(used id : {user_info['user_id']}, rank : {user_info['user_rank']}) successfully !")

@on_command('nc--add-user')
async def add_user(session: CommandSession):
    user_id = session.current_arg_text.strip()
    if not user_id :
        await session.send("Please input user ID!")
        return
    params = {
        "action" : "add_user",
        "user_id" : int(user_id)
    }
    r = requests.get(url="http://127.0.0.1:6060/api/nowcoder", params=params, timeout=10)
    if r.status_code != 200:
        await session.send("Server connect erro!")
        return
    if r.json()["status"] != True :
        await session.send("Nowcoder server erro!")
        return 
    if r.json()["success"] != True:
        await session.send(f"user_id : {user_id} Not Found!")
    user_info = r.json()["user_info"]
    await session.send(f"NowCoder add user : {user_info['user_name']}(used id : {user_info['user_id']}, rank : {user_info['user_rank']}) successfully!")

@on_command('nc--delete-user')
async def delete_user(session: CommandSession):
    user_id = session.current_arg_text.strip()
    if not user_id :
        await session.send("Please input user ID!")
        return
    params = {
        "action" : "delete_user",
        "user_id" : int(user_id)
    }
    r = requests.get(url="http://127.0.0.1:6060/api/nowcoder", params=params, timeout=10)
    if r.status_code != 200:
        await session.send("Server connect erro!")
        return
    if r.json()["status"] != True :
        await session.send("Nowcoder server erro!")
        return 
    user_info = r.json()["user_info"]
    if r.json()["success"] != True:
        await session.send(f"{user_info['user_name']}(used id : {user_info['user_id']}, rank : {user_info['user_rank']}) has been already deleted!")
        return 
    await session.send(f"NowCoder de user : {user_info['user_name']}(used id : {user_info['user_id']}, rank : {user_info['user_rank']}) successfully !")

@on_command('nc--user-list')
async def get_monitored_user(session: CommandSession):
    params = {
        "action" : "get_monitored_user",
    }
    r = requests.get(url="http://127.0.0.1:6060/api/nowcoder", params=params, timeout=10)
    if r.status_code != 200:
        await session.send("Server connect erro!")
        return
    if r.json()["status"] != True :
        await session.send("Nowcoder server erro!")
        return 
    user_info = r.json()["user_info"]
    result = "<-User List->\n"
    for user in user_info :
        result = result + f"{user['user_name']}\n"
    await session.send(result)




