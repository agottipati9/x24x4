#!/bin/bash
echo "Updating packages..."
sudo apt update
sudo apt install cmake libfftw3-dev libmbedtls-dev libboost-program-options-dev libconfig++-dev libsctp-dev -y
echo "Installing srsLTE..."
cd ~ && git clone https://github.com/srsLTE/srsLTE
cd ~/srsLTE
mkdir build
cd build
cmake ../
cp /local/repository/etc/srsLTE/main.cc ~/srsLTE/srsenb/src/main.cc
cp /local/repository/etc/srsLTE/rrc_mobility.cc ~/srsLTE/srsenb/src/stack/rrc/rrc_mobility.cc
make
make test
sudo make install
echo "Finished install. Copying cofigs to ~/.config..."
sudo srslte_install_configs.sh user
sudo cp /local/repository/etc/srsLTE/enb2.conf ~/.config/srslte/enb.conf
sudo cp /local/repository/etc/srsLTE/rr2.conf ~/.config/srslte/rr.conf
