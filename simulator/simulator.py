#!/usr/bin/env python3 -u
import os
import time
import random
import json
import sys
import numpy as np
import redis

# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True)

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
STREAM_NAME = os.getenv("STREAM_NAME", "bio-signals")

print(f"Connecting to Redis at {REDIS_HOST}:{REDIS_PORT}", flush=True)
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

# Test Redis connection
try:
    r.ping()
    print("Redis connection successful!", flush=True)
except Exception as e:
    print(f"Redis connection failed: {e}", flush=True)
    sys.exit(1)

def generate_sample():
    rate = random.uniform(12, 20)
    if random.random() < 0.1:
        rate = random.choice([random.uniform(25, 35), random.uniform(4, 8)])
    anomaly = rate > 24 or rate < 8
    audio_spectrum = np.random.rand(64).tolist()
    return {
        "patient_id": f"P{random.randint(1,100)}",
        "timestamp": time.time(),
        "breathing_rate": round(rate, 1),
        "anomaly": anomaly,
        "audio_spectrum": audio_spectrum
    }

def main():
    print(f"Simulator started. Writing to Redis stream '{STREAM_NAME}'", flush=True)
    count = 0
    while True:
        data = generate_sample()
        stream_data = {k: json.dumps(v) for k, v in data.items()}
        try:
            r.xadd(STREAM_NAME, stream_data, maxlen=1000)
            count += 1
            print(f"[{count}] Sent: {data['patient_id']} rate={data['breathing_rate']} anomaly={data['anomaly']}", flush=True)
        except Exception as e:
            print(f"Error sending to Redis: {e}", flush=True)
        time.sleep(1)

if __name__ == "__main__":
    main()
