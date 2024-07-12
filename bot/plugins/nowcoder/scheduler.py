import nonebot
import requests
import asyncio
import datetime

group_id = [947400127]

user_submissions_update_locker = asyncio.Lock()

@nonebot.scheduler.scheduled_job('cron', minute="*", misfire_grace_time=60)
async def user_submissions_update():
    if user_submissions_update_locker.locked():
        return
    async with user_submissions_update_locker:
        params = {
            "action" : "user_submissions_update",
            "latest_timestamp" : "20240701000000"
        }
        r = requests.get(url="http://127.0.0.1:6060/api/nowcoder", params=params, timeout=60)
        if r.status_code != 200:
            return
        if r.json()["status"] != True :
            return 
        if r.json()["success"] != True:
            return
        for sub in r.json()["submissions"] : 
            for gp in group_id :
                await nonebot.get_bot().send_group_msg(group_id=gp,message=f'Nowcoder submission:\n{sub["user_name"]} submits {sub["pro_name"]} return {sub["status"]} at {datetime.strptime(sub["sub_time"], "%Y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S")}')

contest_submissions_update_locker = asyncio.Lock()

@nonebot.scheduler.scheduled_job('cron', minute="*", misfire_grace_time=60)
async def contest_submissions_update():
    if contest_submissions_update_locker.locked():
        return
    async with contest_submissions_update_locker:
        params = {
            "action" : "contest_submission_update",
        }
        r = requests.get(url="http://127.0.0.1:6060/api/nowcoder", params=params, timeout=60)
        if r.status_code != 200:
            return
        if r.json()["status"] != True :
            return 
        if r.json()["success"] != True:
            return
        print(r.json()["submissions"])
        for sub in r.json()["submissions"] : 
            for gp in group_id :
                await nonebot.get_bot().send_group_msg(group_id=gp,message=f'Nowcoder submission:\n{sub["user_name"]} submits {sub["pro_name"]} return {sub["status"]} at {datetime.datetime.fromtimestamp(int(sub["sub_time"]) / 1000).strftime("%Y-%m-%d %H:%M:%S")}')

contest_rank_update_locker = asyncio.Lock()

@nonebot.scheduler.scheduled_job('cron', minute="*", misfire_grace_time=60)
async def contest_rank_update():
    if contest_rank_update_locker.locked():
        return
    async with contest_rank_update_locker:
        params = {
            "action" : "contest_rank_update",
        }
        r = requests.get(url="http://127.0.0.1:6060/api/nowcoder", params=params, timeout=60)