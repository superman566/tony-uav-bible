"""
Local webcam -> YOLO inference (draw boxes) -> push the stream to ZLMediaKit on EC2

Difference from yolo-camera.py:
    yolo-camera.py only shows the annotated frames in a local window;
    this script feeds the annotated frames to an ffmpeg subprocess for encoding,
    then publishes them via RTSP / RTMP to ZLMediaKit on EC2, which re-serves the
    stream as RTSP / RTMP / HTTP-FLV / HLS / WebRTC.

Data flow:
    webcam --> OpenCV read --> YOLO(best.pt) --> results.plot() draw boxes
              |
              v  raw BGR frames written to ffmpeg.stdin
         ffmpeg subprocess (libx264 low-latency encode)
              |
              v  RTSP(TCP) or RTMP publish
         EC2: ZLMediaKit --> other clients pull the stream

Run:
    # The push URL usually carries an auth token, and this repo is public
    # (it is deployed to GitHub Pages), so pass it via an env var instead of
    # committing the token into the code.
    export EC2_PUSH_URL='rtsp://<EC2_IP>:554/live/cam-4385f1df?token=xxxx'
    python yolo-camera-push.py

Dependencies:
    pip install ultralytics opencv-python torch
    ffmpeg installed and on PATH (macOS: brew install ffmpeg)

Common ZLMediaKit playback URLs (app=live, stream=cam-4385f1df as an example):
    RTSP     rtsp://<EC2_IP>:554/live/cam-4385f1df
    RTMP     rtmp://<EC2_IP>:1935/live/cam-4385f1df
    HTTP-FLV http://<EC2_IP>/live/cam-4385f1df.live.flv      # low latency, ~1s
    HLS      http://<EC2_IP>/live/cam-4385f1df/hls.m3u8      # high latency, ~5-10s
"""

import os
import signal
import subprocess
import sys
import time

import cv2
import numpy as np
import torch

from ultralytics import YOLO

# ============================ config ============================
MODEL_PATH = '/Users/guochaohe/projects/drones/tony-uav-bible/docs/ai-yolo/yolo26/runs/detect/train/weights/best.pt'
CAMERA_ID = 0

# Capture / output resolution (falls back to the actual first frame if the
# camera does not support this mode).
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720

# Push frame rate: set this to the inference FPS you can actually sustain.
# The ffmpeg side uses wallclock timestamps + constant frame rate (cfr), so when
# inference is slow it duplicates frames and when it is fast it drops them,
# keeping the output at a stable rate instead of drifting further behind.
TARGET_FPS = 15

# YOLO inference params
IMGSZ = 640          # match the training size
CONF = 0.25          # this wildfire model is weak (F1-optimal conf ~0.185); lower as needed

# Encoder bitrate (lower it if uplink bandwidth is tight, e.g. BITRATE='1500k' + smaller resolution)
BITRATE = '2500k'
BUFSIZE = '500k'

# Push protocol: 'rtsp' or 'rtmp'
PROTOCOL = 'rtsp'

# ZLMediaKit push URL. Prefer reading it from an env var (the URL usually carries a token).
#   RTSP:  rtsp://<EC2_IP>:554/<app>/<stream>?token=xxxx
#   RTMP:  rtmp://<EC2_IP>:1935/<app>/<stream>?token=xxxx
# PUSH_URL = os.environ.get(
#     'EC2_PUSH_URL',
#     'rtsp://YOUR_EC2_IP:554/live/cam-4385f1df?token=REPLACE_ME',
# )
PUSH_URL = "rtsp://15.223.56.153:554/live/cam-4385f1df?token=d47af076e80a46c895ea76bb23a4cdf7f5806f80c8de49ce838e9a72fccc2658e"

SHOW_LOCAL = os.environ.get('SHOW_LOCAL', '0') == '1'   # local preview window is off by default (saves CPU); enable with: SHOW_LOCAL=1 python yolo-camera-push.py
FFMPEG_LOGLEVEL = 'warning'   # set to 'info' or 'verbose' when debugging the push
RECONNECT_DELAY = 3.0         # seconds to wait before restarting ffmpeg after it drops
# ==============================================================


def pick_device():
    if torch.cuda.is_available():
        return 'cuda'
    if torch.backends.mps.is_available():
        return 'mps'
    return 'cpu'


def build_ffmpeg_cmd(width, height):
    """Read raw BGR frames from stdin -> libx264 low-latency encode -> push to ZLMediaKit."""
    cmd = [
        'ffmpeg', '-hide_banner', '-loglevel', FFMPEG_LOGLEVEL,
        # ---- input: raw BGR frames from stdin, timestamped by arrival time ----
        '-f', 'rawvideo',
        '-pix_fmt', 'bgr24',
        '-s', f'{width}x{height}',
        '-use_wallclock_as_timestamps', '1',
        '-i', '-',
        # ---- encode: low-latency live profile, same as the ffmpeg command tested earlier ----
        '-an',
        '-c:v', 'libx264',
        '-preset', 'ultrafast',
        '-tune', 'zerolatency',
        '-profile:v', 'baseline',
        '-pix_fmt', 'yuv420p',
        '-r', str(TARGET_FPS),
        '-vsync', 'cfr',                 # newer ffmpeg: -fps_mode cfr
        '-g', str(TARGET_FPS),           # one keyframe per second
        '-keyint_min', str(TARGET_FPS),
        '-sc_threshold', '0',
        '-bf', '0',
        '-b:v', BITRATE, '-maxrate', BITRATE, '-bufsize', BUFSIZE,
    ]
    if PROTOCOL == 'rtsp':
        cmd += [
            '-f', 'rtsp',
            '-rtsp_transport', 'tcp',
            '-muxdelay', '0.1',
            PUSH_URL,
        ]
    elif PROTOCOL == 'rtmp':
        cmd += [
            '-f', 'flv',
            '-flvflags', 'no_duration_filesize',
            PUSH_URL,
        ]
    else:
        sys.exit(f'PROTOCOL must be rtsp or rtmp, got: {PROTOCOL!r}')
    return cmd


def start_ffmpeg(width, height):
    cmd = build_ffmpeg_cmd(width, height)
    print('[ffmpeg] starting:', ' '.join(cmd))
    try:
        return subprocess.Popen(cmd, stdin=subprocess.PIPE)
    except FileNotFoundError:
        sys.exit('[ffmpeg] ffmpeg not found; install it and add to PATH (macOS: brew install ffmpeg)')


def main():
    if 'REPLACE_ME' in PUSH_URL or 'YOUR_EC2_IP' in PUSH_URL:
        sys.exit(
            '[config] Set the push URL first:\n'
            "  export EC2_PUSH_URL='rtsp://<EC2_IP>:554/live/cam-4385f1df?token=xxxx'\n"
            '  or edit PUSH_URL in this script'
        )

    device = pick_device()
    print('[device]', device)

    print('[model] loading...', MODEL_PATH)
    model = YOLO(MODEL_PATH)
    print('[model] loaded')

    # open the camera
    cap = cv2.VideoCapture(CAMERA_ID)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, 30)
    if not cap.isOpened():
        sys.exit('[camera] failed to open')

    ok, frame = cap.read()  # use the first frame to get the real resolution
    if not ok:
        sys.exit('[camera] failed to read first frame')
    height, width = frame.shape[:2]
    print(f'[camera] actual resolution {width}x{height}')

    ffmpeg = start_ffmpeg(width, height)

    stop = {'flag': False}

    def handle_sig(signum, _frame):
        print(f'\n[signal] got {signum}, shutting down...')
        stop['flag'] = True

    signal.signal(signal.SIGINT, handle_sig)
    signal.signal(signal.SIGTERM, handle_sig)

    prev = time.time()
    log_t = prev
    fps = 0.0
    last_restart = 0.0
    names = model.names

    try:
        while not stop['flag']:
            ok, frame = cap.read()
            if not ok:
                print('[camera] dropped frame, retrying...')
                time.sleep(0.05)
                continue

            # object detection
            results = model(frame, device=device, imgsz=IMGSZ, conf=CONF, verbose=False)
            det = results[0].boxes
            ann = results[0].plot(labels=True, conf=True)

            # FPS (moving average)
            now = time.time()
            inst = 1.0 / max(now - prev, 1e-6)
            prev = now
            fps = 0.9 * fps + 0.1 * inst if fps else inst
            cv2.putText(ann, f'FPS: {fps:.1f}', (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # status line once per second: with no local window, this confirms the model is still producing boxes
            if now - log_t >= 1.0:
                log_t = now
                if len(det):
                    tally = {}
                    for c in det.cls.int().tolist():
                        tally[names[c]] = tally.get(names[c], 0) + 1
                    summary = ', '.join(f'{k}x{v}' for k, v in tally.items())
                    print(f'[yolo] fps={fps:4.1f}  dets={len(det):2d}  {summary}  max_conf={max(det.conf.tolist()):.2f}')
                else:
                    print(f'[yolo] fps={fps:4.1f}  dets= 0  (no detections, current CONF={CONF})')

            # size guard + ensure contiguous memory before handing to ffmpeg
            if ann.shape[1] != width or ann.shape[0] != height:
                ann = cv2.resize(ann, (width, height))
            ann = np.ascontiguousarray(ann)

            try:
                ffmpeg.stdin.write(ann.tobytes())
            except (BrokenPipeError, OSError):
                print(f'[ffmpeg] pipe broke (exit={ffmpeg.poll()}), restarting in {RECONNECT_DELAY}s')
                if time.time() - last_restart < RECONNECT_DELAY:
                    time.sleep(RECONNECT_DELAY)
                last_restart = time.time()
                try:
                    ffmpeg.kill()
                except OSError:
                    pass
                ffmpeg = start_ffmpeg(width, height)
                continue

            # local preview (after the push, so preview lag does not affect the stream)
            if SHOW_LOCAL:
                cv2.imshow('yolo-push (q to quit)', ann)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
    finally:
        print('[cleanup] releasing resources')
        cap.release()
        cv2.destroyAllWindows()
        if ffmpeg.stdin:
            try:
                ffmpeg.stdin.close()
            except OSError:
                pass
        try:
            ffmpeg.wait(timeout=5)
        except subprocess.TimeoutExpired:
            ffmpeg.kill()
        print('[cleanup] done')


if __name__ == '__main__':
    main()
