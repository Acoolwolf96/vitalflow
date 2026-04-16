#!/bin/bash
# Clean up the entire stack

echo "Deleting all deployments in vitalflow namespace..."
kubectl delete deployment --all -n vitalflow
kubectl delete service --all -n vitalflow
kubectl delete configmap --all -n vitalflow
kubectl delete pvc --all -n vitalflow

echo "Deleting namespace..."
kubectl delete namespace vitalflow

echo "Cleanup complete!"
