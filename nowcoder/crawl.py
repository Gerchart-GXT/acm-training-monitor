import json
import requests
import datetime
import time
import pytz
import html
import re
from bs4 import BeautifulSoup

class crawl_nowcoder_exception(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class crawl_nowcoder_contest :
    def __init__(self, contest_id, contest_name, start_time, end_time, contest_link) :
        local_tz = pytz.timezone('Asia/Shanghai')
        self.contest_id = str(contest_id)
        self.contest_name = str(html.unescape(contest_name))
        self.start_time = str(datetime.datetime.fromtimestamp(start_time / 1000, pytz.UTC).astimezone(local_tz))
        self.end_time = str(datetime.datetime.fromtimestamp(end_time / 1000, pytz.UTC).astimezone(local_tz))
        self.contest_link = str(contest_link[:-18])
        self.length = str((end_time - start_time) / 1000 / 60)   

class crawl_nowcoder_submission : 
    def __init__(self, user_name, user_id, sub_id, pro_id, pro_name, status, sub_time) :
        self.user_name = str(user_name)
        self.user_id = str(user_id)
        self.sub_id = str(sub_id)
        self.pro_id = str(pro_id)
        self.pro_name = str(pro_name)
        self.status = str(status)
        self.sub_time = str(sub_time)
          
class crawl_nowcoder_contest_rank : 
    def __init__(self, contest_id, user_name, user_id, accept_cnt, ranking) : 
        self.contest_id = str(contest_id)
        self.user_name = str(user_name)
        self.user_id = str(user_id)
        self.accept_cnt = str(accept_cnt)
        self.ranking = str(ranking)

class crawl_nowcoder :
    def __init__(self, requests_header, requests_timeout = 3):
        with open(file="./nowcoder/urls.json", mode="r") as file:
            self.urls = json.load(file)
        self.requests_header = requests_header
        self.requests_timeout = requests_timeout
        
    def get_recent_contest_info(self):
        try:
            now_timestap = int('{:.0f}'.format(time.time()) + "000")
            date = str(datetime.datetime.now().year) + "-" + str(datetime.datetime.now().month)
            second = '{:.0f}'.format(time.time())
            params = {
                'token': '',
                'month': date,
                '_': second
            }
            r = requests.get(url=self.urls["contest_calendar"], headers=self.requests_header, params=params, timeout=self.requests_timeout)
            if r.status_code != 200:
                raise crawl_nowcoder_exception(f"Failed to retrieve the page. Status code: {r.status_code}")
            data = r.json()["data"]

            contest_info = []
            for i in data : 
                if int(i["startTime"]) < int(now_timestap) :
                    continue
                contest_info.append(crawl_nowcoder_contest(i["link"].split('/')[-1].split('?')[0], i["contestName"], i["startTime"], i["endTime"], i["link"]))
           
            if(datetime.datetime.now().month == 12) :
                date = str(datetime.datetime.now().year + 1) + "-" + "01"
            else :
                date = str(datetime.datetime.now().year) + "-" + str(datetime.datetime.now().month + 1)
                
            second = '{:.0f}'.format(time.time())
            params = {
                'token': '',
                'month': date,
                '_': second
            }
            r = requests.get(url=self.urls["contest_calendar"], headers=self.requests_header, params=params, timeout=self.requests_timeout)
            if r.status_code != 200:
                raise crawl_nowcoder_exception(f"Failed to retrieve the page. Status code: {r.status_code}")
            
            data = r.json()["data"]
            for i in data : 
                if int(i["startTime"]) < now_timestap :
                    continue
                contest_info.append(crawl_nowcoder_contest(i["link"].split('/')[-1].split('?')[0], i["contestName"], i["startTime"], i["endTime"], i["link"]))
            
            return contest_info
        except Exception as e:
            print(e)

    def get_user_info(self, user_id) :
        url = self.urls["user_info"]["prefix"] + str(user_id)
        r = requests.get(url=url, headers=self.requests_header, timeout=self.requests_timeout)
        soup = BeautifulSoup(r.text, 'html.parser')
        if soup.select("div.null") or r.history:
            return None   
        user_name = soup.select("div.nk-container div.coder-info-detail a")[0].text
        user_rank = soup.select("div.my-state-main div.my-state-item div")[0].text
        return {
            "user_id" : user_id,
            "user_name" : user_name,
            "user_rank" : user_rank
        }

    
    def get_user_submission(self, user_id, user_name, latest_timestamp=0) :
        try : 
            result = {
                "user_id" : str(user_id),
                "user_name" : str(user_name),
                "submissions" : []
            }
            params = {
                "pageSize" : 200,
                "page" : 1
            }

            url = self.urls["user_info"]["prefix"] + str(user_id) + self.urls["user_info"]["submission"]
            r = requests.get(url=url, headers=self.requests_header, params=params, timeout=self.requests_timeout)

            if r.status_code != 200:
                raise crawl_nowcoder_exception(f"Failed to retrieve the page. Status code: {r.status_code}")
            soup = BeautifulSoup(r.text, 'html.parser')
            if soup.select("div.pagination") :
                page_cnt = int(soup.select("div.pagination ul li")[-1].select("a")[0].get("data-page"))
            else :
                page_cnt = 1
            for page_id in range(1, page_cnt + 1) :
                params = {
                    "pageSize" : 200,
                    "page" : page_id
                }
                
                url = self.urls["user_info"]["prefix"] + str(user_id) + self.urls["user_info"]["submission"]

                r = requests.get(url=url, headers=self.requests_header, params=params, timeout=self.requests_timeout)
                
                if r.status_code != 200:
                    raise crawl_nowcoder_exception(f"Failed to retrieve the page. Status code: {r.status_code}")
                soup = BeautifulSoup(r.text, 'html.parser')
                submissions = soup.select("section table tbody tr")
                if submissions[0].select("div.empty-tip-mod") :
                    return result
                for i in submissions: 
                    line = i.select("td")
                    sub_id = line[0].text
                    pro_id = line[1].get("href")
                    pro_name = line[1].text
                    status = line[2].text
                    sub_time = re.sub(r'\D', '', line[-1].text)
                    if int(sub_time) <= int(latest_timestamp) :
                        return result
                    if status == "正在判题" :
                        continue
                    result["submissions"].append(crawl_nowcoder_submission(user_name, user_id, sub_id, pro_id, pro_name, status, sub_time))

            return result


        except Exception as e:
            print(e)
        
    def get_contest_submission_by_name(self, contest_id, search_name, latest_timestamp=0) :
        try : 
            result = {
                "search_name" : str(search_name),
                "submissions" : []
            }
            url = self.urls["contest"]["submission"]
            params = {
                "id" : contest_id,
                "pageSize" : 50,
                "page" : 1,
                "searchUserName" : search_name
            }
            r = requests.get(url=url, headers=self.requests_header, params=params, timeout=self.
            requests_timeout)
            if r.status_code != 200:
                raise crawl_nowcoder_exception(f"Failed to retrieve the page. Status code: {r.status_code}")

            page_cnt = r.json()["data"]["basicInfo"]["pageCount"]

            for page_id in range(1, page_cnt + 1) :
                params = {
                    "id" : contest_id,
                    "pageSize" : 50,
                    "page" : page_id,
                    "searchUserName" : search_name
                }
                r = requests.get(url=url, headers=self.requests_header, params=params, timeout=self.requests_timeout)
                if r.status_code != 200:
                    raise crawl_nowcoder_exception(f"Failed to retrieve the page. Status code: {r.status_code}")
                for sub in r.json()["data"]["data"] : 
                    user_name = sub["userName"]
                    user_id = sub["userId"]
                    sub_id = sub["submissionId"]
                    pro_id = sub["problemId"]
                    pro_name = ""
                    status = sub["statusMessage"]
                    sub_time = sub["submitTime"]
                    if int(sub_time) <= int(latest_timestamp) : 
                        return result
                    if status == "正在判题" :
                        continue
                    result["submissions"].append(crawl_nowcoder_submission(user_name, user_id, sub_id, pro_id, pro_name, status, sub_time))
                    
            return result
            
        except Exception as e:
            print(e)
        
    def get_contest_rank_by_name(self, contest_id, search_name) : 
        result = {
            "search_name" : search_name,
            "rank" : []
        }
        url = self.urls["contest"]["rank"]
        params = {
            "id" : contest_id,
            "page" : 1,
            "limit" : 0,
            "searchUserName" : search_name
        }
        r = requests.get(url=url, headers=self.requests_header, params=params, timeout=self.requests_timeout)
        if r.status_code != 200:
            raise crawl_nowcoder_exception(f"Failed to retrieve the page. Status code: {r.status_code}")
        params["pageSize"] = r.json()["data"]["basicInfo"]["rankCount"]
        if params["pageSize"] == 0 :
            return result
        r = requests.get(url=url, headers=self.requests_header, params=params, timeout=self.requests_timeout)
        if r.status_code != 200:
            raise crawl_nowcoder_exception(f"Failed to retrieve the page. Status code: {r.status_code}")
        for par in r.json()["data"]["rankData"] : 
            user_name = par["userName"]
            user_id = par["uid"]
            accept_cnt = par["acceptedCount"]
            ranking = par["ranking"]
            result["rank"].append(crawl_nowcoder_contest_rank(contest_id, user_name, user_id, 
            accept_cnt, ranking))

        return result
