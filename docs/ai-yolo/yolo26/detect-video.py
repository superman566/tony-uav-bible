"""
用 best.pt 在一段视频上跑检测,输出「带框标注的新视频」+ 一份检测统计报告,
用来直观评估这个 wildfire 模型到底怎么样。

输入 : docs/ai-yolo/yolo26/Canada-wildfires.mp4
模型 : docs/ai-yolo/yolo26/runs/detect/train/weights/best.pt
输出 : docs/ai-yolo/yolo26/Canada-wildfires_detected.mp4   (+ 同名 .summary.txt)

标注说明:
    框上的 label 直接就是模型的类别名 —— 野火 = wildfire、烟 = smoke、
    明火 = fire、云 = cloud、森林 = forest、火星 = spark,后面数字是置信度(0~1)。
    这些类别名是训练时就定好的,不需要额外映射。

运行:
    cd docs/ai-yolo/yolo26
    python detect-video.py
    # 常用可选项:
    python detect-video.py --conf 0.15                 # 模型偏弱,调低阈值能多出框
    python detect-video.py --layout sidebyside         # 左原图 | 右标注,方便对比
    python detect-video.py --classes wildfire smoke    # 只画这两类

依赖:
    pip install ultralytics opencv-python torch
"""

import argparse
import time
from collections import Counter
from pathlib import Path

import cv2
import numpy as np
import torch

from ultralytics import YOLO

HERE = Path(__file__).resolve().parent

# ============================ 默认配置 ============================
MODEL_PATH = HERE / 'runs/detect/train/weights/best.pt'
INPUT_VIDEO = HERE / 'Canada-wildfires.mp4'
OUTPUT_VIDEO = HERE / 'Canada-wildfires_detected.mp4'

CONF = 0.25          # 置信度阈值。这个模型 F1 最优约 0.185,想多出框就调到 0.15 / 0.1
IMGSZ = 640          # 和训练一致
LAYOUT = 'overlay'   # 'overlay' = 框画在原视频上;'sidebyside' = 左原图 | 右标注
SHOW_CONF = True     # label 里是否带置信度数字(关掉就只显示 wildfire / smoke)
KEEP_CLASSES = None  # 只保留这些类别名的框;None = 全部。例: ['wildfire', 'smoke']
# ==============================================================


def parse_args():
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--model', default=str(MODEL_PATH))
    p.add_argument('--input', default=str(INPUT_VIDEO))
    p.add_argument('--output', default=str(OUTPUT_VIDEO))
    p.add_argument('--conf', type=float, default=CONF)
    p.add_argument('--imgsz', type=int, default=IMGSZ)
    p.add_argument('--layout', choices=['overlay', 'sidebyside'], default=LAYOUT)
    p.add_argument('--no-conf', dest='show_conf', action='store_false', default=SHOW_CONF)
    p.add_argument('--classes', nargs='*', default=KEEP_CLASSES,
                   help='只保留这些类别名,例如 --classes wildfire smoke')
    return p.parse_args()


def pick_device():
    if torch.cuda.is_available():
        return 'cuda'
    if torch.backends.mps.is_available():
        return 'mps'
    return 'cpu'


def fmt_ts(frame_index, fps):
    """帧号 → mm:ss.xx 时间戳。"""
    s = frame_index / fps
    return f'{int(s // 60):02d}:{s % 60:05.2f}'


def main():
    args = parse_args()

    device = pick_device()
    print(f'[device] {device}')
    print(f'[model]  {args.model}')
    model = YOLO(args.model)
    names = model.names                       # {0: 'cloud', 1: 'fire', ...}
    name2id = {v: k for k, v in names.items()}
    print(f'[model]  类别: {names}')

    keep_ids = None
    if args.classes:
        keep_ids = []
        for c in args.classes:
            if c not in name2id:
                raise SystemExit(f'[classes] 模型里没有类别 {c!r};可用: {list(name2id)}')
            keep_ids.append(name2id[c])
        print(f'[filter] 只保留 {args.classes} -> id {keep_ids}')

    cap = cv2.VideoCapture(args.input)
    if not cap.isOpened():
        raise SystemExit(f'[input] 打不开视频: {args.input}')

    fps = cap.get(cv2.CAP_PROP_FPS)
    if not fps or fps != fps or fps < 1:     # 0 / NaN / 异常值兜底
        fps = 25.0
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    out_w = w * 2 if args.layout == 'sidebyside' else w
    print(f'[input]  {w}x{h} @ {fps:.2f}fps, {total} 帧, 布局={args.layout}')

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(args.output, fourcc, fps, (out_w, h))
    if not writer.isOpened():
        raise SystemExit(f'[output] 无法创建输出视频: {args.output}')

    # ---------------- 统计量 ----------------
    cls_counter = Counter()          # 每类累计框数
    best_conf = {}                   # 每类最高置信度
    conf_sum, conf_n = 0.0, 0
    frames_with_det = 0
    segments = []                    # 连续「有检测」的时间段 [(起始帧, 结束帧), ...]
    seg_start = None
    idx = 0
    t0 = time.time()
    t_log = t0

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        kw = dict(conf=args.conf, imgsz=args.imgsz, verbose=False, device=device)
        if keep_ids is not None:
            kw['classes'] = keep_ids
        r = model(frame, **kw)[0]
        det = r.boxes
        n = len(det)

        if n:
            frames_with_det += 1
            for cid, cf in zip(det.cls.int().tolist(), det.conf.tolist()):
                nm = names[cid]
                cls_counter[nm] += 1
                conf_sum += cf
                conf_n += 1
                if cf > best_conf.get(nm, 0.0):
                    best_conf[nm] = cf

        # 连续检测段
        if n and seg_start is None:
            seg_start = idx
        elif not n and seg_start is not None:
            segments.append((seg_start, idx - 1))
            seg_start = None

        # 画框:label = 类别名(+ 置信度)
        ann = r.plot(conf=args.show_conf)
        out_frame = np.hstack([frame, ann]) if args.layout == 'sidebyside' else ann
        writer.write(out_frame)

        idx += 1
        now = time.time()
        if now - t_log >= 1.0:
            t_log = now
            speed = idx / (now - t0)
            pct = 100 * idx / total if total > 0 else 0.0
            print(f'[run] {idx}/{total} ({pct:4.1f}%)  {speed:4.1f} fps  '
                  f'有框帧={frames_with_det}  累计框={sum(cls_counter.values())}')

    if seg_start is not None:
        segments.append((seg_start, idx - 1))

    cap.release()
    writer.release()

    # ---------------- 汇总报告 ----------------
    frames_done = idx
    dur = time.time() - t0
    mean_conf = conf_sum / conf_n if conf_n else 0.0
    hit_rate = 100 * frames_with_det / max(frames_done, 1)

    L = []
    L.append('==================== 检测汇总 ====================')
    L.append(f'输入视频      : {args.input}')
    L.append(f'输出视频      : {args.output}')
    L.append(f'模型          : {args.model}')
    L.append(f'参数          : conf={args.conf}  imgsz={args.imgsz}  device={device}')
    L.append('')
    L.append(f'总帧数        : {frames_done}')
    L.append(f'有检测框的帧  : {frames_with_det}  ({hit_rate:.1f}%)')
    L.append(f'检测框总数    : {sum(cls_counter.values())}')
    L.append(f'平均置信度    : {mean_conf:.3f}')
    L.append('')
    L.append('按类别(框数 / 该类最高置信度):')
    if cls_counter:
        for nm, cnt in cls_counter.most_common():
            L.append(f'  {nm:10s} {cnt:6d}   max_conf={best_conf.get(nm, 0.0):.2f}')
    else:
        L.append('  整段视频没有任何检测框 —— 试试 --conf 0.15 甚至 0.1')
    L.append('')
    L.append('检测到目标的时间段:')
    if segments:
        for a, b in segments:
            L.append(f'  {fmt_ts(a, fps)} - {fmt_ts(b, fps)}   ({(b - a + 1) / fps:.1f}s)')
    else:
        L.append('  无')
    L.append('')
    L.append(f'处理耗时      : {dur:.1f}s  ({frames_done / max(dur, 1e-6):.1f} fps)')
    L.append('================================================')
    report = '\n'.join(L)
    print('\n' + report)

    summary_path = Path(args.output).with_suffix('.summary.txt')
    summary_path.write_text(report + '\n', encoding='utf-8')
    print(f'\n[done] 视频: {args.output}')
    print(f'[done] 报告: {summary_path}')


if __name__ == '__main__':
    main()
