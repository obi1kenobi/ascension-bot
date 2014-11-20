#!/bin/bash

./server/main.py &

sleep 0.5
./client/client.py &
./client/client.py &

sleep 3
echo ""
echo "**************************************************"
echo "Killing all clients and servers..."
echo ""

killall main.py
killall client.py

echo ""
echo "**************************************************"
echo "All clients and servers killed."
echo ""
