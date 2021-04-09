#!/bin/bash
echo "Updating srsLTE..."
cd ~/srsLTE/build
make
make test
sudo make install
echo "Finished update."
