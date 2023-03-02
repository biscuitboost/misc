#!/bin/bash

# Set the source and destination directories
SRC_DIR="USER@SERVER:FOLDER"
DEST_DIR="/path/to/local/destination/"

# Set the log file path
LOG_FILE="/path/to/local/destination/log.txt"

# Set the rsync options
RSYNC_OPTS="-avhe ssh --progress --log-file=${LOG_FILE} --stats --append --partial"

# Set the maximum runtime in seconds
MAX_RUNTIME=$((3 * 60 * 60))  # 3 hours

# Check if the script is already running
if pidof -o %PPID -x "$0"; then
   echo "Script is already running. Exiting."
   exit 1
fi

# Check the start/stop parameter
if [ "$1" == "start" ]; then
  # Start the rsync transfer
  rsync ${RSYNC_OPTS} ${SRC_DIR} ${DEST_DIR} &
  RSYNC_PID=$!
  echo "Rsync started with PID ${RSYNC_PID}."
  # Record the start time
  START_TIME=$(date +%s)
elif [ "$1" == "stop" ]; then
  # Stop the rsync transfer
  kill ${RSYNC_PID}
  echo "Rsync stopped."
  exit 0
else
  echo "Invalid parameter. Usage: $0 start|stop"
  exit 1
fi

# Check the maximum runtime
while [ $(($(date +%s) - ${START_TIME})) -lt ${MAX_RUNTIME} ]; do
  if ps -p ${RSYNC_PID} > /dev/null; then
    sleep 10
  else
    echo "Rsync completed successfully."
    exit 0
  fi
done

# Stop the rsync transfer if it has not completed within the maximum runtime
kill ${RSYNC_PID}
echo "Rsync stopped after reaching maximum runtime."
exit 1
