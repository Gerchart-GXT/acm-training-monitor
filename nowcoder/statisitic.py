from .crawl import *
import json
import os

class statistic_nowcoder : 
    def __init__(self) :
        header = {
            'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        }
        self.crawler = crawl_nowcoder(requests_header=header, requests_timeout=3)
        with open(file="./nowcoder/data/user_info.json", mode="r") as file:
            self.users_info = json.load(file) 
        for user in self.users_info["users"] : 
            submission_file = f"./nowcoder/data/submission/{user['user_id']}.json"
            with open(file=submission_file, mode="a") as file :
                pass
            with open(file=submission_file, mode="r+") as file:
                if file.read() == "" :
                    with open(file="./nowcoder/data/submission/example.json", mode="r") as example :
                        for line in example :
                            file.write(line)

    def add_user(self, user_name, user_id):
        with open(file="./nowcoder/data/user_info.json", mode="r") as file:
            self.users_info = json.load(file) 
        for user in self.users_info["users"] :
            if str(user_id) == user["user_id"]:
                return False
        self.users_info["users"].append({
            "user_id" : str(user_id),
            "user_name" : str(user_name)
        })
        submission_file = f"./nowcoder/data/submission/{user_id}.json"
        with open(file=submission_file, mode="a") as file :
            pass
        with open(file=submission_file, mode="r+") as file:
            if file.read() == "" :
                with open(file="./nowcoder/data/submission/example.json", mode="r") as example :
                    for line in example :
                        file.write(line)
        with open(file="./nowcoder/data/user_info.json", mode='w', encoding='utf-8') as json_file:
            json.dump(self.users_info, json_file, ensure_ascii=False, indent=4)
        return True

    def user_submissions_update(self, latest_timestamp = 0) :
        newest_submissions = []
        for user in self.users_info["users"] : 
            submission_file = f"./nowcoder/data/submission/{user['user_id']}.json"
            with open(file=submission_file, mode="r") as file:
                submission_info = json.load(file)
            latest_timestamp = max(int(submission_info["latest_timestamp"]), int(latest_timestamp))
            result = self.crawler.get_user_submission(user_id=user["user_id"], user_name=user["user_name"], latest_timestamp=int(latest_timestamp))
            submission_info["user_id"] = user["user_id"]
            submission_info["user_name"] = user['user_name']
            if len(result["submissions"]) != 0 : 
                submission_info["latest_timestamp"] = result["submissions"][0].sub_time
                for sub in reversed(result["submissions"]) : 
                    newest_submissions.append(sub.__dict__)
                    submission_info["submissions"].insert(0, sub.__dict__)
            with open(file=submission_file, mode='w', encoding='utf-8') as json_file:
                json.dump(submission_info, json_file, ensure_ascii=False, indent=4)
        return newest_submissions

    def contest_submission_update(self, contest_id):
        newest_submissions = []
        contest_dir = f"./nowcoder/data/contest/{contest_id}"
        os.makedirs(contest_dir, exist_ok=True)

        for user in self.users_info["users"] : 
            submission_file = f"./nowcoder/data/contest/{contest_id}/{user['user_id']}.json"
            with open(file=submission_file, mode="a") as file :
                pass
            with open(file=submission_file, mode="r+") as file :
                if file.read() == "" :
                    with open(file="./nowcoder/data/submission/example.json", mode="r") as example :
                        for line in example :
                            file.write(line)
            with open(file=submission_file, mode="r") as file:
                submission_info = json.load(file)
            submission_info["user_id"] = user["user_id"]
            submission_info["user_name"] = user['user_name']
            result = self.crawler.get_contest_submission_by_name(contest_id, user["user_name"], int(submission_info["latest_timestamp"]))
            if len(result["submissions"]) != 0 : 
                submission_info["latest_timestamp"] = result["submissions"][0].sub_time
                for sub in reversed(result["submissions"]) : 
                    newest_submissions.append(sub.__dict__)
                    submission_info["submissions"].insert(0, sub.__dict__)
            with open(file=submission_file, mode='w', encoding='utf-8') as json_file:
                json.dump(submission_info, json_file, ensure_ascii=False, indent=4)
        return newest_submissions
    def contest_rank_update(self, contest_id) :
        contest_dir = f"./nowcoder/data/contest/{contest_id}"
        os.makedirs(contest_dir, exist_ok=True)
        rank_file = f"./nowcoder/data/contest/{contest_id}/rank.json"
        rank_info = {
            "contest_id" : str(contest_id),
            "ranking" : []
        }
        for user in self.users_info["users"] : 
            result = self.crawler.get_contest_rank_by_name(contest_id, user["user_name"])
            if result["rank"] : 
                for par in result["rank"] :
                    rank_info["ranking"].append(par.__dict__)
            else :
                rank_info["ranking"].append(crawl_nowcoder_contest_rank(contest_id, user["user_name"], user["user_id"], -1, -1).__dict__)
        rank_info["ranking"].sort(key=lambda x: int(x["ranking"]))
        with open(file=rank_file, mode='w', encoding='utf-8') as json_file:
            json.dump(rank_info, json_file, ensure_ascii=False, indent=4)
        return rank_info
        
    def get_recent_contest(self) :
        return {
            "contest" : [contest.__dict__ for contest in self.crawler.get_recent_contest_info()]
        }