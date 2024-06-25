import os
import time
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime
import win32netcon
import win32wnet

# ตั้งค่า Access Token ของ LINE Notify
LINE_NOTIFY_TOKENS = [
    'Mq3mpiPFTpcxJQ7aIM9529WtPXT1sE30iD9qJguzeLJ'
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
                    print(f"Notification sent successfully for token {token}")
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

# ฟังก์ชันสำหรับเชื่อมต่อกับโฟลเดอร์เครือข่าย
# def connect_to_network_path(path, username, password):
#     net_resource = {
#         'lpRemoteName': path,
#         'dwType': win32netcon.RESOURCETYPE_DISK,
#     }
#     try:
#         win32wnet.WNetAddConnection2(net_resource, password, username)
#         print(f"Connected to network path: {path}")
#     except Exception as e:
#         print(f"Failed to connect to network path: {e}")

# ฟังก์ชันสำหรับสร้างโฟลเดอร์ตามวันที่ปัจจุบัน
def get_folder_to_watch():
    today_date = datetime.now().strftime('%Y-%m-%d')
    network_share_base_path = '\\\\10.20.9.33\\ptm\\AIAA\\10.20.121.4'
    # folder_to_watch = f'C:\\Users\\NitipoomSa\\Desktop\\{today_date}'
    folder_to_watch = f'{network_share_base_path}\\{today_date}'

    # เชื่อมต่อกับเครือข่ายโดยใช้ชื่อผู้ใช้และรหัสผ่าน
    # connect_to_network_path(network_share_base_path, 'administrator', 'L@c!iT')

    # ตรวจสอบว่ามีโฟลเดอร์หรือไม่ ถ้าไม่มีให้สร้างใหม่
    if not os.path.exists(folder_to_watch):
        os.makedirs(folder_to_watch)
        print(f"Created directory: {folder_to_watch}")
    return folder_to_watch

# สร้าง observer และ event handler
event_handler = FileEventHandler()
observer = Observer()

# เริ่มการตรวจสอบ
def start_observer():
    folder_to_watch = get_folder_to_watch()
    observer.schedule(event_handler, folder_to_watch, recursive=False)
    observer.start()
    print(f"Started observing: {folder_to_watch}")

start_observer()

try:
    # current_day = datetime.now().day
    current_day_time = "00:00:01"
    while True:
        time.sleep(1)
        # new_day = datetime.now().day
        new_day_time = datetime.now().strftime("%H:%M:%S")
        if current_day_time == new_day_time:
            # current_day = new_day
            observer.stop()
            observer.join()
            observer = Observer()
            start_observer()
except KeyboardInterrupt:
    observer.stop()
    observer.join()
    print("Observer stopped.")
