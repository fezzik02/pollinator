set -m
date
/opt/bin/entry_point.sh &
sleep 5
echo "Selenium Started"
python3 /opt/pollinator/src/pollinator.py
