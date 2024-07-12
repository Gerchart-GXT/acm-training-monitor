import json
import requests
from datetime import datetime, timedelta
import time
import pytz
import html
import re
from bs4 import BeautifulSoup

class crawl_codeforces_exception(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class crawl_codeforces_contest :
    def __init__(self, contest_id, contest_name, start_time, end_time, length, contest_link) :
        self.contest_id = str(contest_id)
        self.contest_name = str(html.unescape(contest_name))
        self.start_time = str(start_time)
        self.end_time = str(end_time)
        self.contest_link = str(contest_link[:-18])
        self.length = length

class crawl_codeforces :
    def __init__(self, requests_header, requests_timeout = 3):
        with open(file="./codeforces/urls.json", mode="r") as file:
            self.urls = json.load(file)
        self.requests_header = requests_header
        self.requests_timeout = requests_timeout
    
    def get_recent_contest_info(self) :
        try:
            contest_info = []
            r = requests.get(url=self.urls["contest_calendar"], headers=self.requests_header, timeout=self.requests_timeout)
            soup = BeautifulSoup(r.text, 'html.parser')
            contest = soup.select("div.contestList div.datatable table tr ")[1:]
            if not contest : 
                return contest_info
            for _ in contest :
                contest_id = _.get("data-contestid")
                con = _.select("td")
                contest_name = con[0].text.strip()

                time_format = "%b/%d/%Y %H:%M"
                naive_datetime = datetime.strptime(con[2].text.strip(), time_format)
                moscow_tz = pytz.timezone("Europe/Moscow")
                moscow_datetime = moscow_tz.localize(naive_datetime)
                shanghai_tz = pytz.timezone("Asia/Shanghai")
                start_time = moscow_datetime.astimezone(shanghai_tz)
                
                contest_length = con[3].text.strip()
                routine_hour, routine_minute = map(int, contest_length.split(":"))
                contest_length = routine_hour * 60 + routine_minute

                end_time = start_time + timedelta(minutes=int(contest_length))

                contest_info.append(crawl_codeforces_contest(contest_id, contest_name, start_time, end_time, contest_length, self.urls["contest"]["problem"] + str(contest_id)))
            
            return contest_info

        except Exception as e:
            print(e)

    def get_user_submission(self, user_name, latest_timestamp=0) :
        try : 
            result = {
                "user_name" : str(user_name),
                "submissions" : []
            }

            url = self.urls["user_info"]["submission"] + user_name
            r = requests.post(url=url, headers=self.requests_header, timeout=self.requests_timeout)
            soup = BeautifulSoup(r.text, 'html.parser')
            print(soup)
            page_cnt = soup.select("div.pagination ul li")[-2].text
            print(page_cnt)
        except Exception as e:
            print(e)