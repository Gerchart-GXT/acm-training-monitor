from nowcoder.api import API_Nowcoder
from flask import Flask
from flask_cors import CORS

if __name__ == "__main__" :
    app = Flask(__name__)
    CORS(app)
    app.add_url_rule('/api/nowcoder', view_func=API_Nowcoder.as_view("now_coder"), methods=['GET', 'POST'])
    app.run(host='127.0.0.1', port=6060)
    # app.run(host="0.0.0.0", port=6060)




