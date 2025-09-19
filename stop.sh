#!/bin/bash
if [ -f logs/app.pid ]; then
    kill $(cat logs/app.pid)
    rm logs/app.pid
    echo "App stopped."
else
    echo "No PID file found."
fi

