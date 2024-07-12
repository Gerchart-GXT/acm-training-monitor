from flask.views import MethodView
from flask import jsonify, request

from nowcoder.statistic import statistic_nowcoder

from flask.views import MethodView
from flask import jsonify, request

class API_now_coder(MethodView):
    def __init__(self):
        super().__init__()
        self.now_coder = statistic_nowcoder()

    def get(self):
        action = request.args.get('action')
        if action == 'get_latest_contest':
            return self.get_latest_contest()
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
        else:
            return jsonify({"status": False, "message": "Invalid action"})

    def post(self):
        return jsonify({"status": False, "message": "Invalid action"})

    def get_latest_contest(self):
        msg = {
            "status": True,
            "contest": self.now_coder.get_recent_contest()["contest"]
        }
        return jsonify(msg)

    def get_user_info(self, user_id):
        msg = {
            "status": True,
            "user_info": self.now_coder.crawler.get_user_info(user_id)
        }
        return jsonify(msg)

    def add_user(self):
        user_id = request.args.get('user_id')
        user_info = self.now_coder.crawler.get_user_info(user_id)
        msg = {
            "status": True,
            "success": False,
            "user_info": user_info
        }
        if not user_info:
            return jsonify(msg)
        self.now_coder.add_user(user_info["user_name"], user_info["user_id"])
        msg["success"] = True
        return jsonify(msg)
    
    def delete_user(self):
        user_id = request.args.get('user_id')
        user_info = self.now_coder.crawler.get_user_info(user_id)
        msg = {
            "status": True,
            "success": False,
            "user_info": user_info
        }
        if not user_info:
            return jsonify(msg)
        
        msg["success"] = self.now_coder.delete_user(user_info["user_name"], user_info["user_id"])
        return jsonify(msg)
    
    def get_monitored_user(self) :
        msg = {
            "status": True,
            "user_info": self.now_coder.get_user_list()["users"]
        }
        return jsonify(msg)


    def user_submissions_update(self):
        newest_submissions = self.now_coder.user_submissions_update(int(request.args.get('latest_timestamp')))
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
        contest_id = int(request.args.get('contest_id'))
        newest_submissions = self.now_coder.user_submissions_update()
        msg = {
            "status": True,
            "success": False,
            "contest_id": contest_id,
            "submissions": None
        }
        if newest_submissions:
            msg["submissions"] = newest_submissions
            msg["success"] = True
        return jsonify(msg)

    def contest_rank_update(self):
        contest_id = int(request.args.get('contest_id'))
        rank_info = self.now_coder.user_submissions_update(contest_id)
        msg = {
            "status": True,
            "success": False,
            "contest_id": contest_id,
            "ranking": None
        }
        if rank_info:
            msg["ranking"] = rank_info["ranking"]
            msg["success"] = True
        return jsonify(msg)
    