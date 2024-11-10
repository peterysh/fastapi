from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import threading
import time

class blinker:
    def __init__(self, name, green_total_time, red_total_time, longitude, latitude, color="red", time_remaining=0, car_approaching=False, non_blinker=False):
        self.name = name
        self.color = color
        self.time_remaining = time_remaining
        self.longitude = longitude
        self.latitude = latitude
        self.car_approaching = car_approaching
        self.green_total_time = green_total_time
        self.red_total_time = red_total_time
        self.non_blinker = non_blinker
        #신호등 없는 횡단보도

    def update_light(self, color, time_remaining):
        self.color = color
        self.time_remaining = time_remaining

    def detect_car(self, car_approaching):
        self.car_approaching = car_approaching
        
    def countdown(self):
        while True:
            while self.time_remaining > 0:
                time.sleep(1)
                self.time_remaining -= 1

            # 시간이 0이 되면 신호 변경
            if self.color == "red":
                self.update_light("green", self.green_total_time) 
            else:
                self.update_light("red", self.red_total_time)  
                
    
    def start_countdown_thread(self):
        # 별도 쓰레드로 카운트다운을 실행
        thread = threading.Thread(target=self.countdown)
        thread.start()
        
app = FastAPI()
main_crossboard=""

@app.get("/confirm/string")
async def confirm_str():
    return "hello"

@app.get("/confirm/json")
async def confirm_json():
    return {"message":"hello"}

@app.get("/main_crossboard")
async def show_blinker_info():
    return main_crossboard
        
@app.get("/set_crossboard")
async def set_main_crossboard(name: str):
    for blinker in traffic_light:
        if blinker.name == name:
            main_crossboard = blinker
            return main_crossboard

@app.get("/caution")
async def set_caution(name: str):
    for blinker in traffic_light:
        if blinker.name == name:
            blinker.detect_car(True)
            return blinker

@app.get("/incaution")
async def set_uncaution(name: str):
    for blinker in traffic_light:
        if blinker.name == name:
            blinker.detect_car(False)
            return blinker


# 신호등 객체 생성
traffic_light = [
    blinker(name="A", color="red", time_remaining=10, longitude=0, latitude=20, green_total_time=10, red_total_time=5, non_blinker=False),
    blinker(name="B", color="green", time_remaining=15, longitude=50, latitude=70, green_total_time=7, red_total_time=8, non_blinker=False),
    blinker(name="C", color="", time_remaining=0, longitude=2, latitude=30, green_total_time=7, red_total_time=8, non_blinker=True)
]
# 카운트다운을 별도의 쓰레드에서 시작
for blinker in traffic_light:
    blinker.start_countdown_thread()

