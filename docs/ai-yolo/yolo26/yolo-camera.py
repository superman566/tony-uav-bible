import torch
import cv2

from ultralytics import YOLO

import time

# 定义变量
MODEL_PATH='yolo26l.pt'
CAMERA_ID=0
SHOW_FPS=True

DEVICE='cpu'
if torch.cuda.is_available():
    DEVICE='cuda'
elif torch.backends.mps.is_available():
    DEVICE='mps'

print('DEVICE:', DEVICE)

# 加载模型
print('Loading model...')
model = YOLO(MODEL_PATH)
print('Model loaded.')

# 打开摄像头
cap = cv2.VideoCapture(CAMERA_ID)
if not cap.isOpened():
    print('Failed to open camera.')
    exit()

current_time = 0
prev_time = 0

# 从摄像头获取帧
while True:
    ret, frame = cap.read()
    if not ret:
        print('Failed to get frame.')
        break

    # 进行目标检测
    results = model(frame,
                    device=DEVICE,
                    verbose=False)

    # 显示结果
    ann_frame = results[0].plot()

    if SHOW_FPS:
        current_time = time.time()
        fps = 1/(current_time-prev_time)
        prev_time = current_time
        cv2.putText(ann_frame, f'FPS: {fps:.1f}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow('frame', ann_frame)

    # 按 'q' 键退出
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 释放资源
cap.release()
cv2.destroyAllWindows()
print('Done.')

