import googlemaps
from bs4 import BeautifulSoup
import re
from pprint import pprint
import json

gmaps = googlemaps.Client(key='AIzaSyCMPEdKQ3Mba49lHs1KaewavK08FSTbbTw')

# 做全聯list#############################

f_mxmart = open('mxmarthtml.txt','r',encoding='UTF-8')

mx_html = f_mxmart.read();

soup = BeautifulSoup(mx_html,"html.parser")

results = soup.find_all("div", class_="right")

content = ""

for result in results:
    result = str(result)
    content += result

address = re.findall("\"add\"><b>(.+)<\/b>", content)

shop = re.findall("前往全聯福利中心 (.+門市)", content)

pxmart_list = list(zip(shop, address))

# 做全聯list################################



f_tpx = open('tpxapi.txt','r',encoding='UTF-8');

tpxapi_data = f_tpx.readlines()[20];

data = json.loads(tpxapi_data)



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
