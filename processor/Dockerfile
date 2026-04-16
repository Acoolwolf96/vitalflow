FROM python:3.9-slim
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Generate the ONNX model
COPY train_model.py .
RUN python train_model.py

# Copy processor code
COPY processor.py .
CMD ["python", "processor.py"]
