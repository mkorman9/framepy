#!/bin/bash

cd "$(dirname "$0")"
echo 'Running smoke tests...'

echo 'Installing test requirements...'
pip install behave requests

echo 'Running test application...'
(cd app/; python app_starter.py &)

echo 'Waiting for test application to wake up...'
timeout_counter="0"
while [ "$(curl -s "http://127.0.0.1:8080/")" == '' ]; do
    echo "Trying http://127.0.0.1:8080/"
    if [[ $timeout_counter == "30" ]]; then
        echo "Wake up phase timed out!"
        exit 1
    fi

    sleep 2
    timeout_counter=$[$timeout_counter+1]
done

echo 'Executing tests...'
python -m behave .

if [ $? != 0 ]; then
    echo 'Smoke tests failed!'
    exit 1
fi

echo 'Smoke tests OK'
exit 0
