from nonebot import on_command, CommandSession
import requests
import pytz
import datetime


# @on_command('test')
# async def asfsdfdssdfds(session: CommandSession):
#     params = {
#         "action" : "get_monitored_contest",
#     }
#     r = requests.get(url="http://127.0.0.1:6060/api/nowcoder", params=params, timeout=10)
#     if r.status_code != 200:
#         return
#     if r.json()["status"] != True :
#         return 
#     contests = r.json()["contest_info"]
#     for contest in contests:
#         params = {
#             "action" : "contest_rank_update",
#             "contest_id" : contest["contest_id"]
#         }
#         r = requests.get(url="http://127.0.0.1:6060/api/nowcoder", params=params, timeout=60)
#         if r.status_code != 200:
#             return 
#         if r.json()["status"] != True :
#             return 
#         if r.json()["success"] != True:
#             return
#         if r.json()["change"] != True:
#             continue

#         rank_info = r.json()["ranking"]
#         result = f'<--Contest: {contest["contest_name"]}-->\n'
#         for rk in sorted(rank_info, key=lambda x: int(x["ranking"])):
#             if str(rk["ranking"]) == "-1":
#                 continue
#             result = result + f'User Name: {rk["user_name"]}\nRanking: {"Not Attend" if str(rk["ranking"]) == "-1" else rk["ranking"]}\nAccept Count: {rk["accept_cnt"]}\n\n'
#         await session.send(result)
#     return 


@on_command('help')
async def help(session: CommandSession):
    help_text = (
        "Commands format:\n"
        "[commend <params>...]\n"
        "\n"
        "Available commands:\n"
        "- [help]: Show this help message\n"
        "\n"
        "Nowcoder Commands:\n"
        "- [nc--user-info <user_name>]: Get an Nowcoder user(team)'s information, especially the user ID, used for the following commands)\n"
        "\n"
        "- [nc--add-user <user_id>]: Add a Nowcoder user(team)\n"
        "- [nc--delete-user <user_id>]: Delete a Nowcoder user(team)\n"
        "- [nc--user-list]: Get the list of monitored Nowcoder user(team)\n"
        "- [nc--contest]: Get the latest Nowcoder contests\n"
        "- [nc--add-contest <contest_id>]: Add a Monitored Nowcoder contest\n"
        "- [nc--delete-contest <contest_id>]: Delete a Monitored Nowcoder contest\n"
        "- [nc--contest-list]: Get the list of monitored Nowcoder contests\n"
        "- [nc--contest-rank <contest_id>]: Get the rank of a Monitored Nowcoder contest\n"
    )
    await session.send(help_text)


@on_command('nc--add-contest')
async def add_contest(session: CommandSession):
    contest_id = session.current_arg_text.strip()
    if not contest_id :
        await session.send("Please input contest ID !")
        return
    params = {
        "action" : "add_contest",
        "contest_id" : int(contest_id)
    }
    r = requests.get(url="http://127.0.0.1:6060/api/nowcoder", params=params, timeout=10)
    if r.status_code != 200:
        await session.send("Server connect erro!")
        return
    if r.json()["status"] != True :
        await session.send("Nowcoder server erro!")
        return 
    if r.json()["success"] != True:
        await session.send(f"contest : {contest_id} Not Found!")
        return
    contest_info = r.json()["contest_info"]
    await session.send(f'NowCoder add contest :\nContest Name: {contest_info["contest_name"]}\nLink: {contest_info["contest_link"]}\nStart time: {contest_info["start_time"]}\nEnd time: {contest_info["end_time"]}\nLength: {(contest_info["length"])} mins\nContest ID: {contest_info["contest_id"]}\nsuccessfully!')

@on_command('nc--delete-contest')
async def delete_contest(session: CommandSession):
    contest_id = session.current_arg_text.strip()
    if not contest_id :
        await session.send("Please input contest ID !")
        return
    params = {
        "action" : "delete_contest",
        "contest_id" : int(contest_id)
    }
    r = requests.get(url="http://127.0.0.1:6060/api/nowcoder", params=params, timeout=10)
    if r.status_code != 200:
        await session.send("Server connect erro!")
        return
    if r.json()["status"] != True :
        await session.send("Nowcoder server erro!")
        return 
    if r.json()["success"] != True:
        await session.send(f"contest : {contest_id} Not Added!")
        return

    contest_info = r.json()["contest_info"]
    await session.send(f'NowCoder delete contest :\nContest Name: {contest_info["contest_name"]}\nLink: {contest_info["contest_link"]}\nStart time: {contest_info["start_time"]}\nEnd time: {contest_info["end_time"]}\nLength: {(contest_info["length"])} mins\nContest ID: {contest_info["contest_id"]}\nsuccessfully!')

@on_command('nc--contest-rank')
async def contest_rank_update(session: CommandSession):
    contest_id = session.current_arg_text.strip()
    if not contest_id :
        await session.send("Please input contest ID !")
        return
    params = {
        "action" : "get_contest_rank",
        "contest_id" : contest_id
    }
    r = requests.get(url="http://127.0.0.1:6060/api/nowcoder", params=params, timeout=10)
    if r.status_code != 200:
        await session.send("Server connect erro!")
        return
    if r.json()["status"] != True :
        await session.send("Nowcoder server erro!")
        return 
    if r.json()["success"] != True:
        await session.send(f"contest : {contest_id} Not Added!")
        return

    rank_info = r.json()["contest_rank"]
    contest_info = r.json()["contest_info"]

    result = f"<--Contest: {contest_info['contest_name']}-->\n"
    
    for rk in rank_info :
        if str(rk["ranking"]) == "-1":
            continue
        result = result + f'User Name: {rk["user_name"]}\nRanking: {"Not Attend" if str(rk["ranking"]) == "-1" else rk["ranking"]}\n Accept Count: {rk["accept_cnt"]}\n\n'
    await session.send(result)

@on_command('nc--add-user')
async def add_user(session: CommandSession):
    user_name = session.current_arg_text.strip()
    if not user_name :
        await session.send("Please input user ID/Name!")
        return
    params = {
        "action" : "add_user",
        "user_id" : -1,
        "user_name": user_name
    }
    r = requests.get(url="http://127.0.0.1:6060/api/nowcoder", params=params, timeout=10)
    if r.status_code != 200:
        await session.send("Server connect erro!")
        return
    if r.json()["status"] != True :
        await session.send("Nowcoder server erro!")
        return 
    if r.json()["success"] == True:
        user_info = r.json()["user_info"]
        await session.send(f"NowCoder add user : {user_info['user_name']}(used id : {user_info['user_id']}, rank : {user_info['user_rank']}) successfully!")
        return
    params = {
        "action" : "add_user",
        "user_id" : user_name,
        "user_name": ""
    }
    r = requests.get(url="http://127.0.0.1:6060/api/nowcoder", params=params, timeout=10)
    if r.status_code != 200:
        await session.send("Server connect erro!")
        return
    if r.json()["status"] != True :
        await session.send("Nowcoder server erro!")
        return 
    if r.json()["success"] == True:
        user_info = r.json()["user_info"]
        await session.send(f"NowCoder add user : {user_info['user_name']}(used id : {user_info['user_id']}, rank : {user_info['user_rank']}) successfully!")
        return
    await session.send(f"NowCoder add user : {user_name} Erro! User not exsist or never participate any contest with last 6 mouths.")

    
@on_command('nc--delete-user')
async def delete_user(session: CommandSession):
    user_name = session.current_arg_text.strip()
    if not user_name :
        await session.send("Please input user ID/Name!")
        return
    params = {
        "action" : "delete_user",
        "user_id" : -1,
        "user_name": user_name
    }
    r = requests.get(url="http://127.0.0.1:6060/api/nowcoder", params=params, timeout=10)
    if r.status_code != 200:
        await session.send("Server connect erro!")
        return
    if r.json()["status"] != True :
        await session.send("Nowcoder server erro!")
        return 
    if r.json()["success"] == True:
        user_info = r.json()["user_info"]
        await session.send(f"NowCoder delete user : {user_info['user_name']}(used id : {user_info['user_id']}, rank : {user_info['user_rank']}) successfully!")
        return
    params = {
        "action" : "delete_user",
        "user_id" : user_name,
        "user_name": ""
    }
    r = requests.get(url="http://127.0.0.1:6060/api/nowcoder", params=params, timeout=10)
    if r.status_code != 200:
        await session.send("Server connect erro!")
        return
    if r.json()["status"] != True :
        await session.send("Nowcoder server erro!")
        return 
    if r.json()["success"] == True:
        user_info = r.json()["user_info"]
        await session.send(f"NowCoder delete user : {user_info['user_name']}(used id : {user_info['user_id']}, rank : {user_info['user_rank']}) successfully!")
        return
    await session.send(f"NowCoder delete user : {user_name} Erro! User may not be added.")

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
    result = "<-NowCoder Users List->\n"
    for user in user_info :
        result = result + f"{user['user_name']}"
        if user["is_team"] :
            result = result + "(Team)"
        result = result + "\n"

    await session.send(result)


@on_command('nc--contest-list')
async def contest_update(session: CommandSession):
    params = {
        "action" : "get_monitored_contest",
    }
    r = requests.get(url="http://127.0.0.1:6060/api/nowcoder", params=params, timeout=10)
    if r.status_code != 200:
        await session.send("Server connect erro!")
        return
    if r.json()["status"] != True :
        await session.send("Nowcoder server erro!")
        return 
    
    monitored_contest = r.json()["contest_info"]
    shanghai_tz = pytz.timezone('Asia/Shanghai')
    current_time = datetime.datetime.now(shanghai_tz)
    finished_contest = [
        contest for contest in monitored_contest
        if current_time >= (datetime.datetime.fromisoformat(contest['end_time']))
    ]
    for contest in finished_contest:
        params = {
            "action" : "delete_contest",
            "contest_id" : int(contest["contest_id"])
        }
        requests.get(url="http://127.0.0.1:6060/api/nowcoder", params=params, timeout=10)
        if r.status_code != 200:
            await session.send("Server connect erro!")
            return
        if r.json()["status"] != True :
            await session.send("Nowcoder server erro!")
            return 

    params = {
        "action" : "get_latest_contest",
    }
    r = requests.get(url="http://127.0.0.1:6060/api/nowcoder", params=params, timeout=10)
    if r.status_code != 200:
        await session.send("Server connect erro!")
        return
    if r.json()["status"] != True :
        await session.send("Nowcoder server erro!")
        return 
    latest_contest = r.json()["contest"]
    for contest in latest_contest:
        params = {
            "action" : "add_contest",
            "contest_id" : int(contest["contest_id"])
        }
        requests.get(url="http://127.0.0.1:6060/api/nowcoder", params=params, timeout=10)
        if r.status_code != 200:
            await session.send("Server connect erro!")
            return
        if r.json()["status"] != True :
            await session.send("Nowcoder server erro!")
            return 

    params = {
        "action" : "get_monitored_contest",
    }
    r = requests.get(url="http://127.0.0.1:6060/api/nowcoder", params=params, timeout=10)
    if r.status_code != 200:
        await session.send("Server connect erro!")
        return
    if r.json()["status"] != True :
        await session.send("Nowcoder server erro!")
        return 

    result = "<-NowCoder Contests list>\n"
    for con in latest_contest :
        result = result + f'Contest Name: {con["contest_name"]}\nLink: {con["contest_link"]}\nStart time: {con["start_time"]}\nEnd time: {con["end_time"]}\nLength: {(con["length"])} mins\nContest ID: {con["contest_id"]}\n\n'
    await session.send(result)
