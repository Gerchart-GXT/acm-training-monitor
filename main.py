from nowcoder.api import API_now_coder
from codeforces.crawl import *
from flask import Flask


if __name__ == "__main__" :
    app = Flask(__name__)
    app.add_url_rule('/api/nowcoder', view_func=API_now_coder.as_view("now_coder"), methods=['GET', 'POST'])
    app.run(host='0.0.0.0', port=6060)
