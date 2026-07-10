import threading

import cv2
import numpy as np
from typing import Callable, Optional, NamedTuple
from dataclasses import dataclass
import time
from .tot import *

class FrameData(NamedTuple):
    frame: np.ndarray
    videoCapture: cv2.VideoCapture
    ret: bool
    prevTime: float
    currentTime: float
    fps: float

# 프레임을 받아 아무것도 리턴하지 않는(None) 콜백 함수 타입 정의
def while_video_read_context(device_id: int, callback: Callable[[FrameData], None],
                       on_finish: Optional[Callable[[], None]] = None):
    cap = cv2.VideoCapture(device_id, cv2.CAP_ANY)
    prev_time = time.perf_counter()
    try:
        while cap.isOpened():
            ret, frame = cap.read()
            current_time = time.perf_counter()

            if not ret:
                break

            data = FrameData(
                frame=frame,
                ret=ret,
                videoCapture=cap,
                prevTime=prev_time,
                currentTime=current_time,
                fps=1 / (current_time - prev_time)
            )
            callback(data)
            prev_time = current_time
    finally:
        cap.release()
        # 만약 on_finish 함수가 제공되었다면 실행
        if on_finish is not None:
            on_finish()


def is_available_video_device(device_id: int, require_frame: bool = True) -> bool:
    cap = cv2.VideoCapture(device_id, cv2.CAP_ANY)
    try:
        if not cap.isOpened():
            return False
        ok = True
        if require_frame:
            # try to grab/read a single frame
            ret, frame = cap.read()
            ok = bool(ret and frame is not None)
        return ok
    finally:
        cap.release()


def first_video_capture() -> cv2.VideoCapture | None:
    device_id = detect_first_video_device()
    if device_id is None:
        return None
    return cv2.VideoCapture(device_id)


def video_captures(max_devices: int = 10) -> list[cv2.VideoCapture]:
    available = detect_video_devices(max_devices)
    return [cv2.VideoCapture(device_id) for device_id in available]


def detect_first_video_device() -> int | None:
    for i in range(10):
        if is_available_video_device(i):
            return i
    return None


def detect_video_devices(max_devices: int = 10, require_frame: bool = True) -> list[int]:
    available: list[int] = []
    for i in range(max_devices):
        if is_available_video_device(i, require_frame):
            available.append(i)
    return available
