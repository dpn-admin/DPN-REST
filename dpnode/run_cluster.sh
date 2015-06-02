#!/bin/bash
#
# run_cluster.sh
#
# Runs a cluster of DPN nodes for integration testing.
#
# ----------------------------------------------------------------------

echo "Deleting dbs for foreign nodes"
rm dpnrest_chron.db
rm dpnrest_hathi.db
rm dpnrest_tdr.db
rm dpnrest_sdr.db

echo "Creating dbs and applying migrations for foreigh nodes"
IMPERSONATE_DPN_NODE=chron python manage.py migrate
IMPERSONATE_DPN_NODE=hathi python manage.py migrate
IMPERSONATE_DPN_NODE=tdr python manage.py migrate
IMPERSONATE_DPN_NODE=sdr python manage.py migrate

echo "Loading data for foreign nodes"
IMPERSONATE_DPN_NODE=chron python manage.py loaddata ../data/TestServerData.json
IMPERSONATE_DPN_NODE=hatni python manage.py loaddata ../data/TestServerData.json
IMPERSONATE_DPN_NODE=tdr python manage.py loaddata ../data/TestServerData.json
IMPERSONATE_DPN_NODE=sdr python manage.py loaddata ../data/TestServerData.json

echo "Starting chron node on http://127.0.0.1:8001"
IMPERSONATE_DPN_NODE=chron python manage.py runserver 127.0.0.1:8001 &
CHRON_PID=$!

echo "Starting hathi node on http://127.0.0.1:8002"
IMPERSONATE_DPN_NODE=hathi python manage.py runserver 127.0.0.1:8002 &
HATHI_PID=$!

echo "Starting tdr node on http://127.0.0.1:8003"
IMPERSONATE_DPN_NODE=tdr python manage.py runserver 127.0.0.1:8003 &
TDR_PID=$!

echo "Starting sdr node on http://127.0.0.1:8004"
IMPERSONATE_DPN_NODE=sdr python manage.py runserver 127.0.0.1:8004 &
SDR_PID=$!

echo "--------------------------------------------------"
echo $CHRON_PID
echo $(pgrep -P $CHRON_PID)
echo "--------------------------------------------------"

# Shut down all servers in response to CTRL-C.
# The django servers start child processes, and
# we want to make sure to kill them all.
# SIGINT doesn't work here, so we're using SIGTERM.
# http://stackoverflow.com/questions/392022/best-way-to-kill-all-child-processes
kill_all() {
    echo "Shutting down Chron on http://127.0.0.1:8001"
    CPIDS=$(pgrep -P $CHRON_PID); (sleep 10 && kill -TERM $CPIDS &); kill -INT $CPIDS
    kill -TERM $CHRON_PID

    echo "Shutting down Hathi on http://127.0.0.1:8002"
    CPIDS=$(pgrep -P $HATHI_PID); (sleep 10 && kill -TERM $CPIDS &); kill -INT $CPIDS
    kill -TERM $HATHI_PID

    echo "Shutting down TDR on http://127.0.0.1:8003"
    CPIDS=$(pgrep -P $TDR_PID); (sleep 10 && kill -TERM $CPIDS &); kill -INT $CPIDS
    kill -TERM $TDR_PID

    echo "Shutting down SDR  on http://127.0.0.1:8004"
    CPIDS=$(pgrep -P $SDR_PID); (sleep 10 && kill -TERM $CPIDS &); kill -INT $CPIDS
    kill -TERM $SDR_PID

    echo "Sent SIGINT to all the Django processes"
    echo "It may take up to 30 seconds for them all to disappear"
}

trap kill_all SIGINT
wait $SDR_PID
