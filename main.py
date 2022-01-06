import googlemaps
from bs4 import BeautifulSoup
import requests
import re
from hashlib import sha1
import hmac
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime
import base64
from pprint import pprint

gmaps = googlemaps.Client(key='AIzaSyCMPEdKQ3Mba49lHs1KaewavK08FSTbbTw')

# 做全聯list#############################
url = "https://twcoupon.com/brandshopcity-%e5%85%a8%e8%81%af%e7%a6%8f%e5%88%a9%e4%b8%ad%e5%bf%83-%e6%96%b0%e7%ab%b9%e5%b8%82-%e9%9b%bb%e8%a9%b1-%e5%9c%b0%e5%9d%80.html"
html = requests.get(url)
html.encoding = "utf-8"

soup = BeautifulSoup(html.text, "html.parser")

results = soup.find_all("div", class_="right")

content = ""

for result in results:
    result = str(result)
    content += result

address = re.findall("\"add\"><b>(.+)<\/b>", content)

shop = re.findall("前往全聯福利中心 (.+門市)", content)

pxmart_list = list(zip(shop, address))

# 做全聯list################################

# 使用ptx api##################################
app_id = 'da1d9183c40a448f97dee657149d89ad'
app_key = 'N3tt25MgpC8rs8jp05HuyXop_yU'


class Auth():
    def __init__(self, app_id, app_key):
        self.app_id = app_id
        self.app_key = app_key

    def get_auth_header(self):
        xdate = format_date_time(mktime(datetime.now().timetuple()))
        hashed = hmac.new(self.app_key.encode('utf8'), ('x-date: ' + xdate).encode('utf8'), sha1)
        signature = base64.b64encode(hashed.digest()).decode()

        authorization = 'hmac username="' + self.app_id + '", ' + \
                        'algorithm="hmac-sha1", ' + \
                        'headers="x-date", ' + \
                        'signature="' + signature + '"'
        return {
            'Authorization': authorization,
            'x-date': format_date_time(mktime(datetime.now().timetuple())),
            'Accept - Encoding': 'gzip'
        }


if __name__ == '__main__':
    a = Auth(app_id, app_key)
    response = requests.get('https://ptx.transportdata.tw/MOTC/v2/Bike/Station/Hsinchu?$top=88888888&$format=JSON',
                       headers=a.get_auth_header())
    data = response.json()

# 使用ptx api###########################

try:
    input_station_name = input("請輸入youbike站名(新竹市)(格式為YouBikeX.0_站名):")

    for i in range(len(data)):  # 找出該站名在資料庫中的位置
        if data[i]["StationName"]["Zh_tw"] == input_station_name:
            index = i
            break

    # 取出該站的經緯座標
    youbike_station_coordinate = (
        data[index]["StationPosition"]["PositionLat"],
        data[index]["StationPosition"]["PositionLon"]
    )

    # 計算每一間全聯與該youbike站的距離
    distance_list = []
    time_list = []
    for j in range(len(pxmart_list)):
        geocode_result = gmaps.geocode(pxmart_list[j][1])
        A = geocode_result[0]["geometry"]["location"]
        pxmart_coordinate = (A["lat"], A["lng"])

        distance_matrix_result = gmaps.distance_matrix(youbike_station_coordinate, pxmart_coordinate, mode='bicycling')
        B = distance_matrix_result["rows"][0]["elements"][0]
        distance = B["distance"]["value"]
        time_ = B["duration"]["value"]

        distance_list.append(distance)
        time_list.append(time_)

    # 找出距離最短的全聯
    index2 = distance_list.index(min(distance_list))

    print("離你最近的全聯是：" + str(pxmart_list[index2][0]))
    print("地址為：" + str(pxmart_list[index2][1]))
    print("距離:" + str(distance_list[index2]) + "公尺")
    print("時間:" + str(time_list[index2] // 60) + "分" + str(time_list[index2] % 60) + "秒")


except NameError as err:
    print("請輸入正確站名")
except KeyboardInterrupt as err2:
    print("\n按到奇怪的鍵了，請再執行一次")
except Exception as other:
    print("發生了意想不到的錯誤", other, "，請再試一次吧")
