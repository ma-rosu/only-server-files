import time
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import base64
import numpy as np
import cv2
from agents import fire_agent, fall_agent, human_interaction_agent, sns_agent, reminders_agent
from datetime import datetime

fall = fall_agent.FallAgent()
fire = fire_agent.FireAgent()
human_interaction_agent = human_interaction_agent.HumanInteractionAgent()

last_fall_time = 0
last_sleep_time = 0
last_move_time = 0
last_fire_time = 0
last_minute = -1

fall_cooldown = 60
time_cooldown = 300
fire_cooldown = 30

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global interaction, human_interaction_agent, last_sleep_time, last_move_time, last_fall_time, last_fire_time, fall_cooldown, fire_cooldown, last_minute
    await websocket.accept()
    try:
        while True:
            base64_frame = await websocket.receive_text()

            image_data = base64.b64decode(base64_frame)
            nparr = np.frombuffer(image_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if frame is None:
                await websocket.send_text("ERROR: Decode failed")
                continue

            resized_frame = cv2.resize(frame, (224, 224))
            norm_frame = resized_frame / 255.0  
            human_interaction_agent.init_bbox(frame)
            current_time = time.time()

            fall_int = 0
            if fall.check(frame) and current_time - last_fall_time > fall_cooldown:
                last_fall_time = current_time
                fall_int = 1
                sns_agent.SNSAgent('FALL DETECTED', 'THERE WAS A FALL DETECTED')

            fire_int = 0
            if fire.check(norm_frame) and current_time - last_fire_time > fire_cooldown:
                last_fire_time = current_time
                fire_int = 1
                sns_agent.SNSAgent('FIRE DETECTED', 'THERE WAS FIRE DETECTED')

            sleep_int = 0
            if human_interaction_agent.should_sleep() and current_time - last_sleep_time > time_cooldown:
                last_sleep_time = current_time
                sleep_int = 1

            move_int = 0
            if human_interaction_agent.should_move() and current_time - last_move_time > time_cooldown:
                last_move_time = current_time
                move_int = 1
            
            current_minute = datetime.now().minute

            if current_minute != last_minute:
                last_minute = current_minute
                list_with_reminders = reminders_agent.check()             
            else:
                list_with_reminders = []

            result = {
                "fall": fall_int,
                "fire": fire_int,
                'move': move_int,
                'sleep': sleep_int,
                'reminders': list_with_reminders
            }

            await websocket.send_json(result)

    except Exception as e:
        print("WebSocket error:", e)
        await websocket.close()
