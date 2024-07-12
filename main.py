from nowcoder.statisitic import *
from codeforces.crawl import *

if __name__ == "__main__" :
    header = {
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        'Cookie':'70a7c28f3de=26sxivc9if2qxjk0h8; X-User-Sha1=984b5e8adb0c313bbd092edc1432ab342429c81a; JSESSIONID=3BC1D94DA2D377A9700768BC9E2E3B3A; 39ce7=CFpTMp5M; cf_clearance=gKCwgMX04WF_IorWwHhEXKCQYAiPv9z3RgMvXigDZWI-1720708617-1.0.1.1-l2acNycUrfTY2ezZEC6g2gC945TgEzfl.m3FuWTSxAvCV5foK.rys6dzSlSF5l3c_WGj5pa6FheWuI0Y2qTgHA'
    }
    test = crawl_codeforces(requests_header=header, requests_timeout=3)
    print(test.get_recent_contest_info())
    # test.get_user_submission("tourist")c