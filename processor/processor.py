import os
import json
import threading
import numpy as np
import onnxruntime as ort
import redis
from fastapi import FastAPI
import uvicorn

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
INPUT_STREAM = os.getenv("INPUT_STREAM", "bio-signals")
OUTPUT_STREAM = os.getenv("OUTPUT_STREAM", "processed-signals")

print(f"Connecting to Redis at {REDIS_HOST}:{REDIS_PORT}")
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

try:
    r.ping()
    print("Redis connection successful!")
except Exception as e:
    print(f"Redis connection failed: {e}")
    exit(1)

print("Loading ONNX model...")
session = ort.InferenceSession("breathing_model.onnx")
print("ONNX model loaded successfully!")

def process_loop():
    last_id = "0"
    print("Processor started, waiting for data...")
    while True:
        messages = r.xread({INPUT_STREAM: last_id}, count=10, block=1000)
        for stream, msgs in messages:
            for msg_id, fields in msgs:
                data = {k: json.loads(v) for k, v in fields.items()}
                features = np.array(data['audio_spectrum']).astype(np.float32).reshape(1, -1)
                output = session.run(None, {'float_input': features})[0][0]
                value = output.item()
                prediction = int(round(value))
                result = {
                    "patient_id": data['patient_id'],
                    "timestamp": data['timestamp'],
                    "raw_breathing_rate": data['breathing_rate'],
                    "is_abnormal": prediction
                }
                stream_data = {k: json.dumps(v) for k, v in result.items()}
                r.xadd(OUTPUT_STREAM, stream_data, maxlen=1000)
                print(f"Processed {data['patient_id']} (rate={data['breathing_rate']}) -> abnormal={prediction}")
                last_id = msg_id

# Start the background processor
threading.Thread(target=process_loop, daemon=True).start()

app = FastAPI()
@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
