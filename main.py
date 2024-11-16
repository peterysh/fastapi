from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import threading
import time
import uvicorn


class blinker:
    def __init__(self, id, green_total_time, red_total_time, longitude, latitude, color, time_remaining, non_blinker=False):
        self.id = id
        self.color = color
        self.time_remaining = time_remaining
        self.longitude = longitude
        self.latitude = latitude
        self.green_total_time = green_total_time
        self.red_total_time = red_total_time
        self.non_blinker = non_blinker
        self.car_approaching = False
        self.clear_to_board = True

    def get_non_blinker(self):
        return self.non_blinker

    def update_light(self, color, time_remaining):
        self.color = color
        self.time_remaining = time_remaining

    def detect_car(self, detect_car_):
        self.car_approaching = detect_car_
        if detect_car_ == False:
            self.clear_to_board = True

    def detect_running_car(self):
        self.detect_car(True)
        self.clear_to_board = False

    def countdown(self):
        while True:
            while self.time_remaining > 0:
                time.sleep(1)
                self.time_remaining -= 1

            if self.color == "red":
                self.update_light("green", self.green_total_time)
            else:
                self.update_light("red", self.red_total_time)

    def start_countdown_thread(self):
        thread = threading.Thread(target=self.countdown)
        thread.start()


app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 신호등 객체 생성
traffic_light = [
    blinker(id=0, color="red", time_remaining=10, longitude=0, latitude=20, green_total_time=10, red_total_time=5, non_blinker=False),
    blinker(id=1, color="green", time_remaining=15, longitude=50, latitude=70, green_total_time=7, red_total_time=8, non_blinker=False),
    blinker(id=2, color="", time_remaining=0, longitude=2, latitude=30, green_total_time=0, red_total_time=0, non_blinker=True)
]
main_id = 0

@app.get("/confirm/string")
def confirm_str():
    return "hello"

@app.get("/confirm/json")
def confirm_json():
    return {"message": "hello"}

@app.get("/main_crossboard")
def show_blinker_info():
    return traffic_light[main_id]

@app.get("/set_crossboard")
def set_main_crossboard(id: int):
    global main_id
    for blinker in traffic_light:
        if blinker.id == id:
            main_id = id
            return traffic_light[main_id]

@app.get("/caution")
def set_caution(id: int):
    for blinker in traffic_light:
        if blinker.id == id:
            blinker.detect_running_car()
            return blinker

@app.get("/incaution")
def set_uncaution(id: int):
    for blinker in traffic_light:
        if blinker.id == id:
            blinker.detect_car(False)
            return blinker

@app.get("/unmoving")
def set_uncaution(id: int):
    for blinker in traffic_light:
        if blinker.id == id:
            blinker.detect_car(True)
            return blinker


# 카운트다운을 별도의 쓰레드에서 시작
for blinker in traffic_light:
    if blinker.get_non_blinker() == False:
        blinker.start_countdown_thread()

# HTTP와 HTTPS 서버를 동시에 실행
def run_servers():
    def run_http():
        uvicorn.run(app, host="0.0.0.0", port=80)

    def run_https():
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=443,
            ssl_keyfile="path/to/your/private.key",
            ssl_certfile="path/to/your/certificate.crt",
        )

    http_thread = threading.Thread(target=run_http)
    https_thread = threading.Thread(target=run_https)

    http_thread.start()
    https_thread.start()
    http_thread.join()
    https_thread.join()


if __name__ == "__main__":
    run_servers()
