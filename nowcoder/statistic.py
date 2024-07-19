from .crawl import *
import json
import os
import threading
from concurrent.futures import ThreadPoolExecutor

class statistic_nowcoder : 
    def __init__(self, max_working_thread_count) :
        header = {
            'user-agent': "Mozilla/5.0 (Windows NT self.max_working_thread_count.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        }
        self.crawler = Crawl_Nowcoder(requests_header=header, requests_timeout=3)
        self.max_working_thread_count = max_working_thread_count
        self.user_example = {
            "latest_timestamp" : "0",
            "user_id" : "", 
            "user_name" : "",
            "submissions" : []
        }

        self.user_info_locker = threading.Lock()
        self.user_submission_locker = {}
        self.locker_of_user_submission_locker = threading.Lock()
        self.contest_submission_locker = {}
        self.locker_of_contest_submission_locker = threading.Lock()
        self.contest_rank_locker = {}
        self.locker_of_contest_rank_locker = threading.Lock()

        self.contest_monitor_locker = threading.Lock()

        # read user info
        with self.user_info_locker :
            with open(file="./nowcoder/data/user_info.json", mode="r") as file:
                users_info = json.load(file) 
        # check if submission locker for each user exsist
        with self.locker_of_user_submission_locker :
            for user in users_info["users"] : 
                if f"{user['user_id']}" not in self.user_submission_locker :
                    self.user_submission_locker[f"{user['user_id']}"] = threading.Lock()

        os.makedirs(f"./nowcoder/data/submission", exist_ok=True)
        for user in users_info["users"] : 
            # check if submission.json for each user exsist
            with self.user_submission_locker[f"{user['user_id']}"]:
                submission_file = f"./nowcoder/data/submission/{user['user_id']}.json"
                with open(file=submission_file, mode="a") as file :
                    pass
                with open(file=submission_file, mode="r+") as file:
                    if file.read() == "" :
                        json.dump(self.user_example, file, ensure_ascii=False, indent=4)

        with self.contest_monitor_locker :
            contest_file = "./nowcoder/data/contest.json"
            with open(file=contest_file, mode="r") as file:
                contest_info = json.load(file)

        for con in contest_info["contest"]:
            contest_id = con["contest_id"]
            os.makedirs(f"./nowcoder/data/contest/{contest_id}", exist_ok=True)

            # check if contest rank locker exsist
            with self.locker_of_contest_rank_locker : 
                if f"{contest_id}" not in self.contest_rank_locker :
                    self.contest_rank_locker[f"{contest_id}"] = threading.Lock()
            with self.contest_rank_locker[f"{contest_id}"]:
                rank_file = f"./nowcoder/data/contest/{contest_id}/rank.json"
                with open(file=rank_file, mode="a") as file :
                    pass
                with open(file=rank_file, mode="r+") as file :
                    if file.read() == "" :
                        json.dump([], file, ensure_ascii=False, indent=4)

    # insert designated user info to user_info.json ,if exsist return False, else retrun True
    def add_user(self, user_name, user_id, is_team):
        # update user_info.json
        with self.user_info_locker :
            user_file = "./nowcoder/data/user_info.json"
            with open(file=user_file, mode="r") as file:
                users_info = json.load(file) 
            for user in users_info["users"] :
                if str(user_id) == user["user_id"]:
                    return False
        
            users_info["users"].append({
                "user_id" : str(user_id),
                "user_name" : str(user_name),
                "is_team" : is_team
            })
            with open(file=user_file, mode='w', encoding='utf-8') as json_file:
                json.dump(users_info, json_file, ensure_ascii=False, indent=4)

        # create new user's submission locker
        with self.locker_of_user_submission_locker:
            self.user_submission_locker[f"{user_id}"] = threading.Lock()

        # create new user's submission.json
        with self.user_submission_locker[f"{user_id}"] : 
            submission_file = f"./nowcoder/data/submission/{user_id}.json"
            with open(file=submission_file, mode="a") as file :
                pass
            with open(file=submission_file, mode="r+") as file:
                if file.read() == "" :
                    json.dump(self.user_example, file, ensure_ascii=False, indent=4)
  
        return True

    # delete designated user info from user_info.json, if not exsist return False, else return True
    def delete_user(self, user_name, user_id) :
        with self.user_info_locker :
            user_file = "./nowcoder/data/user_info.json"
            with open(file=user_file, mode="r") as file:
                user_info = json.load(file)
            tmp = [i for i in user_info["users"] if str(user_id) != str(i["user_id"])]
            if len(tmp) == len(user_info["users"]) :
                return False
            user_info["users"] = [i for i in tmp]
            with open(file=user_file, mode='w', encoding='utf-8') as json_file:
                json.dump(user_info, json_file, ensure_ascii=False, indent=4)
        with self.locker_of_user_submission_locker:
            del self.user_submission_locker[f"{user_id}"]
        return True
    
    # return user_info.json
    def get_user_list(self) :
        with self.user_info_locker :
            with open(file="./nowcoder/data/user_info.json", mode="r") as file:
                users_info = json.load(file) 
        return users_info
        
    # get designated user's submissions, and restore in "./nowcoder/data/submission/{user_id}.json", simultaneously update its latest_timestamp
    # if supposed time_stamp greater than last lastest_timestamp, update nothing but update its latest_timestamp too
    # return the newest_submission updated this time
    def get_user_submissions(self, user, latest_timestamp = 0) :
        newest_submissions = []
        # update user's submission.json
        with self.user_submission_locker[f"{user['user_id']}"] : 
            submission_file = f"./nowcoder/data/submission/{user['user_id']}.json"
            with open(file=submission_file, mode="r") as file:
                submission_info = json.load(file)
            latest_timestamp = max(int(submission_info["latest_timestamp"]), int(latest_timestamp))
            result = self.crawler.get_user_submission(user_id=user["user_id"], user_name=user["user_name"], latest_timestamp=int(latest_timestamp))
            submission_info["user_id"] = user["user_id"]
            submission_info["user_name"] = user['user_name']
            if len(result["submissions"]) != 0 : 
                for sub in reversed(result["submissions"]) : 
                    newest_submissions.append(sub.__dict__)
                    submission_info["submissions"].insert(0, sub.__dict__)
                submission_info["latest_timestamp"] = max(str(newest_submissions[-1]["sub_time"]), str(latest_timestamp))

            with open(file=submission_file, mode='w', encoding='utf-8') as json_file:
                json.dump(submission_info, json_file, ensure_ascii=False, indent=4)
        return newest_submissions

    #update total user's submission by envoking get_user_submissions with multi thread
    def user_submissions_update(self, latest_timestamp = 0) :
        newest_submissions = []

        # read user_info
        users_info = self.get_user_list()
        
        # check if submission locker for each user exsist
        with self.locker_of_user_submission_locker :
            for user in users_info["users"] : 
                if f"{user['user_id']}" not in self.user_submission_locker :
                    self.user_submission_locker[f"{user['user_id']}"] = threading.Lock()

        for user in users_info["users"] : 
            # check if submission.json for each user exsist
            with self.user_submission_locker[f"{user['user_id']}"]:
                submission_file = f"./nowcoder/data/submission/{user['user_id']}.json"
                with open(file=submission_file, mode="a") as file :
                    pass
                with open(file=submission_file, mode="r+") as file:
                    if file.read() == "" :
                        json.dump(self.user_example, file, ensure_ascii=False, indent=4)

        def update_user_submission(user):
            submissions = self.get_user_submissions(user, latest_timestamp)
            if submissions:
                newest_submissions.extend(submissions)
        
        # start crawling for each user
        with ThreadPoolExecutor(max_workers=self.max_working_thread_count) as executor:
            executor.map(update_user_submission, users_info["users"])
        
        return newest_submissions

    # get designated user's submissions in suposed contest , and restore in "/nowcoder/data/contest/{contest_id}/{user_id}.json", simultaneously update its latest_timestamp
    # return the newest_submission updated this time
    def get_user_contest_submission(self, contest_id, user, all_submissions) :
        newest_submissions = []
        # update user's contest submission.json
        with self.contest_submission_locker[f"{contest_id}"][f"{user['user_id']}"]:
            submission_file = f"./nowcoder/data/contest/{contest_id}/{user['user_id']}.json"
            with open(file=submission_file, mode="r") as file:
                submission_info = json.load(file)
            submission_info["user_id"] = user["user_id"]
            submission_info["user_name"] = user['user_name']
            if len(all_submissions[user["user_id"]]) != 0 : 
                for sub in reversed(all_submissions[user["user_id"]]) : 
                    if int(sub.sub_time) <= int(submission_info["latest_timestamp"]):
                        break
                    newest_submissions.append(sub.__dict__)
                    submission_info["submissions"].insert(0, sub.__dict__)
                submission_info["latest_timestamp"] = all_submissions[user["user_id"]][-1].sub_time
            with open(file=submission_file, mode='w', encoding='utf-8') as json_file:
                json.dump(submission_info, json_file, ensure_ascii=False, indent=4)
        return newest_submissions
        
    #update total user's submission in all by envoking get_user_submissions with multi thread
    def contest_submission_update(self, contest_id):
        newest_submissions = []
        
        # read user info
        users_info = self.get_user_list()

        # check if contest dir exsist
        os.makedirs(f"./nowcoder/data/contest/{contest_id}", exist_ok=True)

        # check if contest locker for each user exsist
        with self.locker_of_contest_submission_locker :
            if f"{contest_id}" not in self.contest_submission_locker :
                self.contest_submission_locker[f"{contest_id}"] = {}
            for user in users_info["users"] : 
                if f"{user['user_id']}" not in self.contest_submission_locker[f"{contest_id}"] :
                    self.contest_submission_locker[f"{contest_id}"][f"{user['user_id']}"] = threading.Lock()
                    
        submissions = self.crawler.get_contest_submission(contest_id)["submissions"]
        all_submissions = {}
        for sub in submissions:
            if sub.user_id not in all_submissions:
                all_submissions[sub.user_id] = []
            all_submissions[sub.user_id].append(sub)

        for user in users_info["users"] : 
            # check if contest submission.json for each user exsist
            with self.contest_submission_locker[f"{contest_id}"][f"{user['user_id']}"]:
                submission_file = f"./nowcoder/data/contest/{contest_id}/{user['user_id']}.json"
                with open(file=submission_file, mode="a") as file :
                    pass
                with open(file=submission_file, mode="r+") as file :
                    if file.read() == "" :
                        json.dump(self.user_example, file, ensure_ascii=False, indent=4)

        def update_user_submission(user):
            submissions = self.get_user_contest_submission(contest_id, user, all_submissions)
            if submissions:
                newest_submissions.extend(submissions)
        
        with ThreadPoolExecutor(max_workers=self.max_working_thread_count) as executor:
            executor.map(update_user_submission, users_info["users"])

        return newest_submissions
    
    # get designated user's contest rank in supposed contest
    def get_user_contest_ranking(self, contest_id, user) :
        ranking = []
        result = self.crawler.get_contest_rank_by_name(contest_id, user["user_name"])

        if result["rank"] : 
            for par in result["rank"] :
                ranking.append(par.__dict__)
        else :
            ranking.append(Crawl_Nowcoder_Contest_Rank(contest_id, user["user_name"], user["user_id"], -1, -1).__dict__)

        return ranking

    #update total user's ranking in all by envoking get_user_contest_ranking with multi thread
    # return the newest_ranking if some user's accepted problems changed
    def contest_rank_update(self, contest_id) :
        ranking = []
        # read user info contest info
        users_info = self.get_user_list()

        os.makedirs(f"./nowcoder/data/contest/{contest_id}", exist_ok=True)

        # check if contest rank locker exsist
        with self.locker_of_contest_rank_locker : 
            if f"{contest_id}" not in self.contest_rank_locker :
                self.contest_rank_locker[f"{contest_id}"] = threading.Lock()

        def update_user_rank(user) :
            rank_info = self.get_user_contest_ranking(contest_id, user)
            ranking.extend(rank_info)
        
        with ThreadPoolExecutor(max_workers=self.max_working_thread_count) as executor:
            executor.map(update_user_rank, users_info["users"])

        change = False
        with self.contest_rank_locker[f"{contest_id}"]:
            rank_file = f"./nowcoder/data/contest/{contest_id}/rank.json"
            with open(file=rank_file, mode="r") as json_file:
                last_rank = json.load(json_file) 
            if not change:
                for now in ranking :
                    found = False
                    for last in last_rank:
                        if now["user_id"] == last["user_id"]:
                            found = True
                            if now["accept_cnt"] != last["accept_cnt"] :
                                change = True
                                break
                    if change :
                        break
                    if not found:
                        change = True
                        break
            with open(file=rank_file, mode='w', encoding='utf-8') as json_file:
                json.dump(ranking, json_file, ensure_ascii=False, indent=4)
        return {
            "change" : change,
            "ranking": ranking
        }
        
    # get contest.json
    def get_recent_contest(self) :
        return {
            "contest" : [contest.__dict__ for contest in self.crawler.get_recent_contest_info()]
        }
    
    # get designated contest's ranking
    def get_contest_rank(self, contest_id):
        with self.contest_rank_locker[f"{contest_id}"]:
            rank_file = f"./nowcoder/data/contest/{contest_id}/rank.json"
            with open(file=rank_file, mode='r') as file:
                rank_info = json.load(file)
        return rank_info

    # mannully add a monitored contest, if exsists return False
    def add_contest(self, contest) :
        with self.contest_monitor_locker :
            contest_file = "./nowcoder/data/contest.json"
            with open(file=contest_file, mode="r") as file:
                contest_info = json.load(file)
            for con in contest_info["contest"] :
                if str(contest["contest_id"]) == con["contest_id"]:
                    return False
            contest_info["contest"].append(contest)
            contest_info["contest"].sort(key=lambda x : x["start_time"])
            with open(file=contest_file, mode='w', encoding='utf-8') as json_file:
                json.dump(contest_info, json_file, ensure_ascii=False, indent=4)
        with self.locker_of_contest_rank_locker : 
            if f'{contest["contest_id"]}' not in self.contest_rank_locker:
                self.contest_rank_locker[f'{contest["contest_id"]}'] = threading.Lock()
        return True

    # mannully delete a monitored contest, if not exsists return False
    def delete_contest(self, contest) :
        with self.contest_monitor_locker :
            contest_file = "./nowcoder/data/contest.json"
            with open(file=contest_file, mode="r") as file:
                contest_info = json.load(file)
            tmp = [i for i in contest_info["contest"] if str(contest["contest_id"]) != str(i["contest_id"])]
            if len(tmp) == len(contest_info["contest"]) :
                return False
            contest_info["contest"] = [i for i in tmp]
            contest_info["contest"].sort(key=lambda x : x["start_time"])
            with open(file=contest_file, mode='w', encoding='utf-8') as json_file:
                json.dump(contest_info, json_file, ensure_ascii=False, indent=4)
        return True
    
    # get contest.json
    def get_contest_list(self) :
        with self.contest_monitor_locker :
            contest_file = "./nowcoder/data/contest.json"
            with open(file=contest_file, mode="r") as file:
                    contest_info = json.load(file)
        return contest_info