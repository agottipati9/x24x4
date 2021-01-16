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
make
make test
sudo make install
echo "Finished install. Copying cofigs to ~/.config..."
sudo srslte_install_configs.sh user
#sudo cp ~/enb.conf ~/.config/srslte/enb.conf
#sudo cp ~/rr.conf ~/.config/srslte/rr.conf
