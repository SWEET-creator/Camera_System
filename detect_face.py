from config import token
import cv2
import requests
import time
import csv
import datetime

# ログファイルの名前と初期化
log_file_name = 'system_log.csv'
with open(log_file_name, mode='w', newline='') as file:
    writer = csv.writer(file)
    # CSVのヘッダー
    writer.writerow(['Timestamp', 'Event', 'Duration'])

def write_log(event, duration):
    """
    ログをCSVに書き込む関数
    """
    with open(log_file_name, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([datetime.datetime.now(), event, duration])

# カメラの初期化
cap = cv2.VideoCapture(0)

# 顔検出用の分類器の読み込み
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

url = "https://notify-api.line.me/api/notify" 
headers = {"Authorization" : "Bearer "+ token} 
message =  "座りすぎです" 
payload = {"message" :  message} 

buffer_stat_time = time.time() #誤検出を防ぐためのタイマー（）
sit_start_time = time.time()
start_time = time.time()
walk_flag = False
notify_walk = False
face_detection = False

while True:
    # フレームの取得
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 顔の検出
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)

    # 検出された顔に枠を描画
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

    # 結果の表示
    #cv2.imshow('frame', frame)
    if len(faces) > 0:
        if  time.time() - buffer_stat_time > 10:
            face_detection = True
            walk_flag = False
            start_time = time.time()
    else:
        face_detection = False
        buffer_stat_time = time.time()
        if time.time() - start_time > 1 * 60:
            if not notify_walk:
                #message =  "運動しててえらい" 
                #payload = {"message" :  message} 
                #r = requests.post(url, headers = headers, params=payload)
                #write_log('Exercise Notification Sent', time.time() - start_time)
                notify_walk = True
            walk_flag = True
    if walk_flag:
        sit_start_time = time.time()
    else:
        notify_walk = False
        if time.time() - sit_start_time > 10 * 60:
            message =  "座りすぎです" 
            payload = {"message" :  message} 
            r = requests.post(url, headers = headers, params=payload)
            write_log('Sitting Too Long Notification Sent', time.time() - sit_start_time)
            walk_flag = True
    
    print("連続検出",  (time.time() - buffer_stat_time))
    print("検出されていない時間:", (time.time() - start_time))
    print("座っている時間",(time.time() - sit_start_time))

    # qを押したら終了
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
    if walk_flag:
        write_log('Walk', time.time() - start_time)
    elif face_detection:
        write_log('Sit', time.time() - sit_start_time)
    else:
        write_log('Undefine', time.time() - sit_start_time)

    time.sleep(1)

cap.release()
cv2.destroyAllWindows()
