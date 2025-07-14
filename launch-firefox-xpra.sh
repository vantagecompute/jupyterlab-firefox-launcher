#!/bin/bash

# Dynamically allocate port and display
PORT=$(shuf -i 15000-16000 -n 1)
DISPLAY_NUM=$(shuf -i 100-200 -n 1)

# Store for jupyter-server-proxy to read
echo "$PORT" > /tmp/xpra-port

# Start Xpra with Firefox
xpra start :$DISPLAY_NUM \
  --bind-tcp=0.0.0.0:$PORT \
  --html=on \
  --daemon=no \
  --start-child=firefox \
  --exit-with-children
