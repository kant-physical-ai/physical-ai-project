def calculate_fps(prev_time: float, current_time: float):
    fps = 1 / (current_time - prev_time)
    return fps
