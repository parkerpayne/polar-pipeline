import configparser
import subprocess
import signal
import time
import sys
import os

config = configparser.ConfigParser()
config.read('./config.ini')
server_ip = config.get('Configuration', 'SERVER_IP')
os.environ.setdefault("SERVER_IP", server_ip)

def sigint_handler(signal, frame):
    print("", end='')

signal.signal(signal.SIGINT, sigint_handler)

subprocess.run(['celery', '-A', 'tasks', 'worker', '--concurrency=1', '--prefetch-multiplier=1', '--loglevel=INFO'], cwd='services')