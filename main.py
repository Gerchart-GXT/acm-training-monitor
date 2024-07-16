from nowcoder.api import API_now_coder
from nowcoder.statistic import *
from flask import Flask
import requests

if __name__ == "__main__" :
    app = Flask(__name__)
    app.add_url_rule('/api/nowcoder', view_func=API_now_coder.as_view("now_coder"), methods=['GET', 'POST'])
    app.run(host='0.0.0.0', port=6060)
    # header = {
    #     'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    # }
    # test = crawl_nowcoder(requests_header=header, requests_timeout=60)
    # print([i.__dict__ for i in test.get_contest_submission(81596)["submissions"]])
    # test = statistic_nowcoder()
    # print(test.user_submissions_update())



