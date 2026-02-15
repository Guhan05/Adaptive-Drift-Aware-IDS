from collections import deque
import time

# Store last 500 logs in memory
log_buffer = deque(maxlen=500)


def log_event(ip, risk, level, action):

    log_buffer.appendleft({
        "time": time.strftime("%H:%M:%S"),
        "ip": ip,
        "risk": risk,
        "level": level,
        "action": action
    })


def get_logs(limit=100):
    return list(log_buffer)[:limit]
