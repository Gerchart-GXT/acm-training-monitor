import nonebot
import requests
import asyncio
import datetime
import pytz
from nonebot import on_command, CommandSession


rank_info_group = [947400127]
submission_info_group = [947400127]
# rank_info_group = [788384992, 881680835]
# submission_info_group = [788384992, 881680835]
init_timestamp = "20240716000000"

user_submissions_update_locker = asyncio.Lock()

@nonebot.scheduler.scheduled_job('cron', minute="*", misfire_grace_time=60)
async def user_submissions_update():
    if user_submissions_update_locker.locked():
        return
    async with user_submissions_update_locker:
        params = {
            "action" : "get_monitored_contest"
        }
        r = requests.get(url="http://127.0.0.1:6060/api/nowcoder", params=params, timeout=60)
        
        if r.status_code != 200:
            return
        if r.json()["status"] != True :
            return 

        contests = r.json()["contest_info"]
        params = {
            "action" : "user_submissions_update",
            "latest_timestamp" : init_timestamp
        }

        r = requests.get(url="http://127.0.0.1:6060/api/nowcoder", params=params, timeout=60)
        
        if r.status_code != 200:
            return
        if r.json()["status"] != True :
            return 
        if r.json()["success"] != True:
            return
        
        out_contest_submissions = []
        for sub in r.json()["submissions"]:
            is_contest_sub = False
            for contest in contests:
                sub_time = sub["sub_time"]
                if (datetime.datetime.strptime(contest["start_time"], "%Y-%m-%d %H:%M:%S%z").strftime("%Y%m%d%H%M%S")) <= sub_time <= (datetime.datetime.strptime(contest["end_time"], "%Y-%m-%d %H:%M:%S%z").strftime("%Y%m%d%H%M%S")):
                    is_contest_sub = True
                    break
            if not is_contest_sub:
                out_contest_submissions.append(sub)

        result = "Nowcoder submission:\n"
        line_cnt = 0
        for sub in sorted(out_contest_submissions, key=lambda x : x["sub_time"]) : 
            result += f'{sub["user_name"]} submits {sub["pro_name"]} return {sub["status"]} at {datetime.datetime.strptime(sub["sub_time"], "%Y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S")}\n'
            line_cnt += 1
            if line_cnt % 10 == 0:
                for gp in submission_info_group :
                    await nonebot.get_bot().send_group_msg(group_id=gp,message=result)
                result = "Nowcoder submission:\n"
        if result != "Nowcoder submission:\n":
            await nonebot.get_bot().send_group_msg(group_id=gp,message=result)

contest_submissions_update_locker = asyncio.Lock()

@nonebot.scheduler.scheduled_job('cron', minute="*", misfire_grace_time=60)
async def contest_submissions_update():
    if contest_submissions_update_locker.locked():
        return
    async with contest_submissions_update_locker:
        params = {
            "action" : "get_monitored_contest"
        }
        r = requests.get(url="http://127.0.0.1:6060/api/nowcoder", params=params, timeout=60)
        
        if r.status_code != 200:
            return
        if r.json()["status"] != True :
            return 

        contests = r.json()["contest_info"]

        for contest in contests:
            params = {
                "action" : "contest_submission_update",
                "contest_id" : contest["contest_id"]
            }
            r = requests.get(url="http://127.0.0.1:6060/api/nowcoder", params=params, timeout=60)
            if r.status_code != 200:
                return
            if r.json()["status"] != True :
                return 
            if r.json()["success"] != True:
                continue
            result = "Nowcoder Contest Submission:\n"
            line_cnt = 0
            for sub in sorted(r.json()["submissions"], key=lambda x : x["sub_time"]) : 
                result +=f'{sub["user_name"]} submits {sub["pro_name"]} return {round(float(sub["status"]) * 100)}% Accepted at {datetime.datetime.fromtimestamp(int(sub["sub_time"]) / 1000).strftime("%Y-%m-%d %H:%M:%S")}\n'
                line_cnt += 1
                if line_cnt % 10 == 0:
                    for gp in submission_info_group :
                        await nonebot.get_bot().send_group_msg(group_id=gp,message=result)
                    result = "Nowcoder Contest Submission:\n"
            if result != "Nowcoder Contest Submission:\n":
                await nonebot.get_bot().send_group_msg(group_id=gp,message=result)

contest_rank_update_locker = asyncio.Lock()

@nonebot.scheduler.scheduled_job('cron', minute="*", misfire_grace_time=60)
async def contest_rank_update():
    if contest_rank_update_locker.locked():
        return
    async with contest_rank_update_locker:
        params = {
            "action" : "get_monitored_contest",
        }
        r = requests.get(url="http://127.0.0.1:6060/api/nowcoder", params=params, timeout=10)
        if r.status_code != 200:
            return
        if r.json()["status"] != True :
            return 
        contests = r.json()["contest_info"]
        for contest in contests:
            params = {
                "action" : "contest_rank_update",
                "contest_id" : contest["contest_id"]
            }
            r = requests.get(url="http://127.0.0.1:6060/api/nowcoder", params=params, timeout=60)
            if r.status_code != 200:
                return 
            if r.json()["status"] != True :
                return 
            if r.json()["success"] != True:
                return
            if r.json()["change"] != True:
                continue
            rank_info = r.json()["ranking"]

            result = f"<--Contest: {contest['contest_name']}-->\n"
            for rk in sorted(rank_info, key=lambda x: int(x["ranking"])):
                if str(rk["ranking"]) == "-1":
                    continue
                result = result + f'User Name: {rk["user_name"]}\nRanking: {"Not Attend" if str(rk["ranking"]) == "-1" else rk["ranking"]}\nAccept Count: {rk["accept_cnt"]}\n\n'
            for gp in rank_info_group :
                await nonebot.get_bot().send_group_msg(group_id=gp,message=result)