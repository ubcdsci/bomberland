# !/bin/bash
## purpose: restores the original agent from the backup file

base=/home/serialguitarist/Development/bomberland/bomberland/agents/dsci

cp $base/bak.agent.py $base/agent.py
cp $base/bak.game_state.py $base/game_state.py
