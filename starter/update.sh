# !/bin/bash
## purpose: copies over the code from our directory to the 

base=/home/serialguitarist/Development/bomberland/bomberland/agents/dsci
our=/home/serialguitarist/Development/bomberland/dsci/bomberland/src

for py in $our/*.py; do
    echo $(basename $py)
    cp $py $base/$(basename $py)

done

# cp $base/bak.agent.py $base/agent.py
# cp $base/bak.game_state.py $base/game_state.py
