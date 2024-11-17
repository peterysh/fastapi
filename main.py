from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import threading
import time
import uvicorn


class blinker:
    def __init__(self, id, green_total_time, red_total_time, green_blinking_time, longitude, latitude, color, time_remaining, non_blinker=False):
        self.id = id
        self.color = color
        self.time_remaining = time_remaining
        self.longitude = longitude
        self.latitude = latitude
        self.green_total_time = green_total_time
        self.green_blinking_time = green_blinking_time
        self.red_total_time = red_total_time
        self.non_blinker = non_blinker
        self.car_approaching = False
        self.clear_to_board = True
        self.is_counting = False

    def get_non_blinker(self):
        return self.non_blinker

    def update_light(self, color, time_remaining):
        self.color = color
        self.time_remaining = time_remaining

    def detect_car(self, detect_car_):
        self.car_approaching = detect_car_

    def countdown(self):
        while True:
            while self.time_remaining > 0:                
                time.sleep(1)
                self.time_remaining -= 1
                if self.is_counting == False:
                    break
                if self.time_remaining == 0:
                    if self.color == "red":
                        self.update_light("green", self.green_total_time)
                    elif self.color == "green":
                        self.update_light("blinking_green", self.green_blinking_time)
                    elif self.color == "blinking_green":
                        self.update_light("red", self.red_total_time)
            if self.is_counting == False:
                self.color = "red"
                self.time_remaining = self.red_total_time

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
traffic_lights = [
    blinker(id=0, color="red", time_remaining=10, longitude=0, latitude=20, green_total_time=10, red_total_time=5, green_blinking_time=10, non_blinker=False),
    blinker(id=1, color="red", time_remaining=15, longitude=50, latitude=70, green_total_time=7, red_total_time=8, green_blinking_time=10, non_blinker=False),
    blinker(id=2, color="red", time_remaining=12, longitude=50, latitude=70, green_total_time=10, red_total_time=12, green_blinking_time=6, non_blinker=False),
    blinker(id=3, color="", time_remaining=0, longitude=2, latitude=30, green_total_time=0, red_total_time=0, green_blinking_time=0, non_blinker=True)
]
main_id = 2
running = 0
is_start = False

@app.get("/")
def confirm_str():
    return "hello"

@app.get("/confirm/string")
def confirm_str():
    return "hello"

@app.get("/confirm/json")
def confirm_json():
    return {"message": "hello"}

@app.get("/main_crossboard")
def show_blinker_info():
    return traffic_lights[main_id]

@app.get("/set_crossboard")
def set_main_crossboard(id: int):
    global main_id
    for blinker in traffic_lights:
        if blinker.id == id:
            main_id = id
            return traffic_lights[main_id]

@app.get("/caution")
def set_caution():
    traffic_lights[3].detect_car(True)
    # for blinker in traffic_lights:
    #     if blinker.id == id:
    #         blinker.detect_running_car()
    #         return blinker
    return 1

@app.get("/incaution")
def set_uncaution():
    traffic_lights[3].detect_car(False)
    # for blinker in traffic_lights:
    #     if blinker.id == id:
    #         blinker.detect_car(False)
    #         return blinker
    return 0

@app.get("/setup")
def setup(red_time: int, green_time: int, green_blinking_time: int):
    traffic_lights[2].red_total_time = red_time
    traffic_lights[2].green_total_time = green_time
    traffic_lights[2].green_blinking_time = green_blinking_time
    traffic_lights[2].color = "red"
    traffic_lights[2].time_remaining = red_time
    return traffic_lights[2]

@app.get("/coloring")
def coloring(color: int):
    if color == 0:
        traffic_lights[2].color = "red"
        traffic_lights[2].time_remaining = traffic_lights[2].red_total_time
    elif color == 1:
        traffic_lights[2].color = "green"
        traffic_lights[2].time_remaining = traffic_lights[2].green_total_time
    elif color == 2:
        traffic_lights[2].color = "blinking_green"
        traffic_lights[2].time_remaining = traffic_lights[2].green_blinking_time
    return traffic_lights[2]

# /start 엔드포인트 추가
@app.get("/start")
def start_countdown():
    global is_start
    if is_start == True:
        return is_start
    
    global running
    for blinker in traffic_lights:
        if not blinker.get_non_blinker():
            blinker.is_counting = True
            blinker.start_countdown_thread()
    running = 1
    return running

# /start 엔드포인트 추가
@app.get("/continue")
def continue_countdown():
    global running
    for blinker in traffic_lights:
        if not blinker.get_non_blinker():
            blinker.is_counting = True
    running = 1
    return running

# /init 엔드포인트 추가
@app.get("/stop")
def init_countdown():
    global running
    for blinker in traffic_lights:
        if not blinker.get_non_blinker():
            blinker.is_counting = False
            
    running = 0
    return running

# /init 엔드포인트 추가
@app.get("/status")
def start_countdown():
    global running
    return running



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
