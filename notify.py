import os
import time
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime

# ตั้งค่า Access Token ของ LINE Notify
LINE_NOTIFY_TOKENS = [
    'RNkb8ch08Hl6L6Z5DzfvTepq6RPiN18XKW4Z9ZGfVH6',
    # 'YOUR_LINE_NOTIFY_ACCESS_TOKEN_2',
    # เพิ่ม token อื่น ๆ ได้ตามต้องการ
]

# ฟังก์ชันสำหรับส่งการแจ้งเตือนผ่าน LINE Notify พร้อมรูปภาพ
def send_line_notify(image_path):
    url = 'https://notify-api.line.me/api/notify'
    current_time = datetime.now().strftime('%d-%m-%Y %H:%M:%S')  # เวลาปัจจุบัน
    data = {
        'message': current_time  # ส่งข้อความเป็นวันที่และเวลาปัจจุบัน
    }

    for token in LINE_NOTIFY_TOKENS:
        headers = {
            'Authorization': f'Bearer {token}'
        }

        files = {}

        if image_path:
            try:
                with open(image_path, 'rb') as image_file:
                    files['imageFile'] = image_file
                    response = requests.post(url, headers=headers, data=data, files=files)
                    response.raise_for_status()  # Raise an exception for HTTP errors
            except Exception as e:
                print(f"Failed to send image for token {token}: {e}")

# สร้างคลาสสำหรับจัดการเหตุการณ์การเปลี่ยนแปลงในโฟลเดอร์
class FileEventHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            file_path = event.src_path

            # ตรวจสอบว่าไฟล์เป็นรูปภาพหรือไม่
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                # ตรวจสอบว่าไฟล์พร้อมใช้งานหรือไม่
                time.sleep(1)  # รอให้ไฟล์เสร็จสิ้นการสร้าง
                send_line_notify(file_path)

# ฟังก์ชันสำหรับสร้างโฟลเดอร์ตามวันที่ปัจจุบัน
def get_folder_to_watch():
    today_date = datetime.now().strftime('%Y-%m-%d')
    folder_to_watch = f'C:/Users/NitipoomSa/Desktop/{today_date}'
    # ตรวจสอบว่ามีโฟลเดอร์หรือไม่ ถ้าไม่มีให้สร้างใหม่
    # if not os.path.exists(folder_to_watch):
    #     os.makedirs(folder_to_watch)
    return folder_to_watch

# สร้าง observer และ event handler
event_handler = FileEventHandler()
observer = Observer()

# เริ่มการตรวจสอบ
def start_observer():
    folder_to_watch = get_folder_to_watch()
    observer.schedule(event_handler, folder_to_watch, recursive=False)
    observer.start()

start_observer()

try:
    current_day = datetime.now().day
    while True:
        time.sleep(1)
        new_day = datetime.now().day
        if new_day != current_day:
            current_day = new_day
            observer.stop()
            observer.join()
            observer = Observer()
            start_observer()
except KeyboardInterrupt:
    observer.stop()
    observer.join()
