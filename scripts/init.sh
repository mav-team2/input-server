#!/bin/bash

# activate the virtual environment
python -m venv /home/ubuntu/venv
source /home/ubuntu/venv/bin/activate

# install the requirements
cd /home/ubuntu/input-server
pip install -r requirements.txt