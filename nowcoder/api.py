from flask.views import MethodView
from flask import jsonify, request

from nowcoder.statistic import statistic_nowcoder

from flask.views import MethodView
from flask import jsonify, request

class API_Nowcoder(MethodView):
    def __init__(self):
        super().__init__()
        self.nowcoder = statistic_nowcoder(100)

    def get(self):
        action = request.args.get('action')
        if action == 'get_latest_contest':
            return self.get_latest_contest()
        elif action == 'get_contest_datas':
            return self.get_contest_datas()
        elif action == 'get_monitored_contest':
            return self.get_monitored_contest()
        elif action == 'add_contest':
            return self.add_contest()
        elif action == 'delete_contest':
            return self.delete_contest()
        elif action == 'get_user_info':
            return self.get_user_info()
        elif action == 'add_user':
            return self.add_user()
        elif action == 'delete_user':
            return self.delete_user()
        elif action == 'get_monitored_user':
            return self.get_monitored_user()
        elif action == 'user_submissions_update':
            return self.user_submissions_update()
        elif action == 'contest_submission_update':
            return self.contest_submission_update()
        elif action == 'contest_rank_update':
            return self.contest_rank_update()
        elif action == 'get_contest_rank':
            return self.get_contest_rank()
        else:
            return jsonify({"status": False, "message": "Invalid action"})

    def post(self):
        return jsonify({"status": False, "message": "Invalid action"})

    def get_latest_contest(self):
        msg = {
            "status": True,
            "contest": self.nowcoder.get_recent_contest()["contest"]
        }
        return jsonify(msg)

    def get_contest_datas(self):
        contest_id = request.args.get('contest_id')
        msg = {
            "status":True,
            "contest_datas": self.nowcoder.crawler.get_contest_datas(contest_id)
        }
        return jsonify(msg)

    def get_user_info(self, user_id):
        msg = {
            "status": True,
            "user_info": self.nowcoder.crawler.get_user_info(user_id)
        }
        return jsonify(msg)

    def add_user(self):
        user_id = request.args.get('user_id')
        user_name = request.args.get('user_name').strip('"')
        msg = {
            "status": True,
            "success": False,
            "user_info": {
                "user_name": user_name,
                "user_id": user_id
            }
        }
        if str(user_id) == "-1" :
            res = self.nowcoder.crawler.get_user_id_by_name(user_name) 
            msg["user_info"] = {
                "user_name": res["user_name"],
                "user_id": res["user_id"],
            }
            if msg["user_info"]["user_id"] == None :
                return jsonify(msg)
            
        msg["user_info"] = self.nowcoder.crawler.get_user_info(msg["user_info"]["user_id"])

        if not msg["user_info"]:
            return jsonify(msg)
        
        msg["success"] = self.nowcoder.add_user(msg["user_info"]["user_name"], msg["user_info"]["user_id"], msg["user_info"]["is_team"])
        return jsonify(msg)
    
    def delete_user(self):
        user_id = request.args.get('user_id')
        user_name = request.args.get('user_name').strip('"')
        msg = {
            "status": True,
            "success": False,
            "user_info": {
                "user_name": user_name,
                "user_id": user_id
            }
        }
        if str(user_id) == "-1" :
            res = self.nowcoder.crawler.get_user_id_by_name(user_name) 
            msg["user_info"] = {
                "user_name": res["user_name"],
                "user_id": res["user_id"],
            }
            if msg["user_info"]["user_id"] == None :
                return jsonify(msg)
            
        msg["user_info"] = self.nowcoder.crawler.get_user_info(msg["user_info"]["user_id"])

        if not msg["user_info"]:
            return jsonify(msg)
        
        msg["success"] = self.nowcoder.delete_user(msg["user_info"]["user_name"], msg["user_info"]["user_id"])
        return jsonify(msg)

    def get_monitored_user(self) :
        msg = {
            "status": True,
            "user_info": self.nowcoder.get_user_list()["users"]
        }
        return jsonify(msg)

    def user_submissions_update(self):
        newest_submissions = self.nowcoder.user_submissions_update(int(request.args.get('latest_timestamp')))
        msg = {
            "status": True,
            "success": False,
            "submissions": None
        }
        if newest_submissions:
            msg["submissions"] = newest_submissions
            msg["success"] = True
        return jsonify(msg)

    def contest_submission_update(self):
        contest_id = request.args.get("contest_id")
        newest_submissions = self.nowcoder.contest_submission_update(contest_id)
        msg = {
            "status": True,
            "success": False,
            "submissions": None
        }
        if newest_submissions:
            msg["submissions"] = newest_submissions
            msg["success"] = True
        return jsonify(msg)

    def contest_rank_update(self):
        contest_id = request.args.get("contest_id")
        rank_info = self.nowcoder.contest_rank_update(contest_id)
        msg = {
            "status": True,
            "success": False,
            "change" : False,
            "ranking": None
        }
        if rank_info:
            msg["success"] = True
            msg["ranking"] = rank_info["ranking"]
            msg["change"] = rank_info["change"]
        return jsonify(msg)

    def get_contest_rank(self):
        contest_id = request.args.get('contest_id')
        contest_list = self.nowcoder.get_contest_list()["contest"]
        msg = {
            "status": True,
            "success": False,
            "contest_info" : None, 
            "contest_rank": None
        }
        for con in contest_list :
            if str(con["contest_id"]) == str(contest_id):
                msg["success"] = True
                msg["contest_info"] = con
                msg["contest_rank"] = self.nowcoder.get_contest_rank(contest_id)
                return jsonify(msg)
        return jsonify(msg)

    def get_monitored_contest(self):
        msg = {
            "status": True,
            "contest_info": self.nowcoder.get_contest_list()["contest"]
        }
        return jsonify(msg)
    
    def add_contest(self):
        contest_id = request.args.get('contest_id')
        contest_info = self.nowcoder.crawler.get_contest_datas(contest_id)["contest_info"]
        msg = {
            "status": True,
            "success": False,
            "contest_info": contest_info
        }
        if not contest_info:
            return jsonify(msg)
        msg = {
            "status": True,
            "success": self.nowcoder.add_contest(contest_info),
            "contest_info": contest_info
        }
        return jsonify(msg)
    
    def delete_contest(self):
        contest_id = request.args.get('contest_id')
        contest_info = self.nowcoder.crawler.get_contest_datas(contest_id)["contest_info"]
        msg = {
            "status": True,
            "success": False,
            "contest_info": contest_info
        }
        if not contest_info:
            return jsonify(msg)
        msg = {
            "status": True,
            "success": self.nowcoder.delete_contest(contest_info),
            "contest_info": contest_info
        }
        return jsonify(msg)



        
    