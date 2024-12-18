#!/bin/bash

LOG_FILE="/home/ubuntu/init.log"

# 로그 시작
echo "Init script started at $(date)" >> $LOG_FILE

# 가상 환경 생성 및 활성화
echo "Creating virtual environment..." >> $LOG_FILE
python -m venv /home/ubuntu/venv >> $LOG_FILE 2>&1
if [ $? -ne 0 ]; then
    echo "Error creating virtual environment" >> $LOG_FILE
    exit 1
fi

echo "Activating virtual environment..." >> $LOG_FILE
source /home/ubuntu/venv/bin/activate >> $LOG_FILE 2>&1
if [ $? -ne 0 ]; then
    echo "Error activating virtual environment" >> $LOG_FILE
    exit 1
fi

# requirements.txt 설치
echo "Installing requirements..." >> $LOG_FILE
cd /home/ubuntu/input-server >> $LOG_FILE 2>&1
pip install -r requirements.txt >> $LOG_FILE 2>&1
if [ $? -ne 0 ]; then
    echo "Error installing requirements" >> $LOG_FILE
    exit 1
fi

echo "Init script completed successfully at $(date)" >> $LOG_FILE
exit 0
