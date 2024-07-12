import nonebot
import requests
from datetime import datetime
import asyncio

group_id = [947400127]

user_submissions_update_locker = asyncio.Lock()

@nonebot.scheduler.scheduled_job('interval', minutes=0.5)
async def user_submissions_update():
    if user_submissions_update_locker.locked():
        return
    async with user_submissions_update_locker:
        params = {
            "action" : "user_submissions_update",
            "latest_timestamp" : "20240701000000"
        }
        r = requests.get(url="http://127.0.0.1:6060/api/nowcoder", params=params, timeout=45)
        if r.status_code != 200:
            return
        if r.json()["status"] != True :
            return 
        if r.json()["success"] != True:
            return
        for sub in r.json()["submissions"] : 
            for gp in group_id :
                await nonebot.get_bot().send_group_msg(group_id=gp,message=f'Nowcoder submission:\n{sub["user_name"]} submits {sub["pro_name"]} return {sub["status"]} at {datetime.strptime(sub["sub_time"], "%Y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S")}')
