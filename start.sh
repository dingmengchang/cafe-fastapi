#!/bin/bash
echo "--- STARTING APP VIA SCRIPT ---"
# 确保在当前目录下运行
export PYTHONPATH=$PYTHONPATH:.
python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}
