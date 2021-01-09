#!/bin/bash
echo "installing FlexRAN..."
sudo apt update
sudo apt install snapd -y
sudo snap install flexran --channel=edge --devmode
