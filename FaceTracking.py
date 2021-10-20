import cv2
import numpy as np
from djitellopy import tello
import time

me = tello.Tello()
me.connect()
print(me.get_battery())
me.streamoff()
me.streamon()

# 이륙하기
me.takeoff()
# 속도 초기값 설정ㅂ
me.send_rc_control(0, 0, 24, 0)


# 화면 사이즈 조정
w, h = 720, 680
#사이즈 조절이 중요하다
fbRange = [11000, 18000]
pid = [0.4, 0.4, 0]
pError = 0


def findFace(img):
    # classifier 이용해서 분류
    faceCasecade = cv2.CascadeClassifier("Resources/haarcascade_frontalface_default.xml")
    # eyeCaecade = cv2.CascadeClassifier("Resources/haarcascade_eye.xml")
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # 얼굴 검출
    faces = faceCasecade.detectMultiScale(imgGray, 1.2, 8)

    # center x ,y
    myFaceListC = []
    myFaceListArea = []

    # face 의 좌표정보를 받고 이용
    for (x, y, w, h) in faces:
        # 얼굴 위치 표시
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2, )
        cx = x + w // 2
        cy = y + h // 2
        area = w * h
        # 중앙점 표시
        cv2.circle(img, (cx, cy), 5, (0, 255, 0), cv2.FILLED)
        myFaceListC.append([cx, cy])
        myFaceListArea.append(area)
        # # 눈 찾기
        # eyes = eyeCaecade.detectMultiScale(myFaceListArea)
        # for (eye_x, eye_y, eye_w, eye_h) in eyes:
        #     #x ,y를 더해서 눈을 제대로 찾는다
        #     cv2.rectangle(img, (x + eye_x, y + eye_y, eye_w, eye_h), (0, 255, 0), 2)

    #     point 값 얻기 center,area
    if len(myFaceListArea) != 0:
        i = myFaceListArea.index(max(myFaceListArea))
        return img, [myFaceListC[i], myFaceListArea[i]]
    else:
        return img, [[0, 0], 0]


def trackFace(info, w, pid, pError):
    # 영역 벗어나면 드론 위치 수정하기
    area = info[1]
    x, y = info[0]
    fb = 0

    error = x - w // 2
    speed = pid[0] * error + pid[1] * (error - pError)
    speed = int(np.clip(speed, -30, 30))

    if area > fbRange[0] and area < fbRange[1]:
        fb = 0
    elif area > fbRange[1]:  # 6800
        fb = -10
    elif area < fbRange[0] and area != 0:  # 6200
        fb = 10

    # print(speed,fb)

    if x == 0:
        speed = 0
        error = 0

    me.send_rc_control(0, fb, 0, speed)
    return error


cap = cv2.VideoCapture(0)

while True:
    # _, img = cap.read()
    img = me.get_frame_read().frame
    img = cv2.resize(img, (w, h))
    img, info = findFace(img)
    pError = trackFace(info, w, pid, pError)
    # print("center",info[0],"Area",info[1])
    cv2.imshow("Output", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        me.land()
        break
