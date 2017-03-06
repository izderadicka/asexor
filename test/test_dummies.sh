#! /bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export PYTHONPATH=$DIR/..
crossbar start &
sleep 1
python dummy_backend.py --use-raw --use-wamp &
BACKEND_PID=$!
sleep 1
RES=
python dummy_client.py -n 10 user
RES+=$?
python dummy_client.py -n 10 user --use-raw
RES+=$?
python dummy_client.py -n 10 user --use-raw
RES+=$?

kill $BACKEND_PID
crossbar stop
sleep 1
echo
if [[ $RES == "000" ]]; then
  echo All OK
else
  echo Some errors $RES
fi