#!/bin/bash
echo "Building Docker image..."
docker build -t miles-optimizer .

echo ""
echo "Running Streamlit App on port 8501..."
docker run --rm -p 8501:8501 miles-optimizer
