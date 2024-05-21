@echo off

start /B docker-compose up --build -d

start http://127.0.0.1:8000
