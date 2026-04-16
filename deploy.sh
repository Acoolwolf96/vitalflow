#!/bin/bash
# Deploy the entire stack

echo "Creating namespace..."
kubectl apply -f namespace.yaml

echo "Deploying Redis..."
kubectl apply -f redis.yaml

echo "Waiting for Redis to be ready..."
sleep 10

echo "Deploying Simulator..."
kubectl apply -f simulator.yaml

echo "Deploying Processor..."
kubectl apply -f processor.yaml

echo "Deployment complete!"
echo "Check status with: kubectl get pods -n vitalflow"
