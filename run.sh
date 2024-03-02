#!/bin/bash

tmux list-sessions -F "#{session_name}" | xargs -I {} tmux kill-session -t {}

# Start a new tmux session
tmux new-session -d -s Skeleton

# Split the window horizontally
tmux split-window -h

# Select pane 0 (the left pane)
tmux select-pane -t 0

# Start Vue.js npm server in the left pane
tmux send-keys 'cd frontend/' C-m  # replace with your Vue.js project path
tmux send-keys 'npm start' C-m

# Select pane 1 (the right pane)
tmux select-pane -t 1

# Start Python server in the right pane
tmux send-keys 'cd backend/' C-m  # replace with your Python project path
tmux send-keys 'uvicorn main:app --reload' C-m  # or any other python server command

# Attach to the tmux session
tmux attach-session -t Skeleton

