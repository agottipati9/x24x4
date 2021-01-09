#!/bin/bash
echo "installing OAI eNB..."
git clone https://gitlab.eurecom.fr/oai/openairinterface5g
cd ~/openairinterface5g
source oaienv
cd ~/openairinterface5g/cmake_targets
sudo cp /local/repository/etc/OAI/rrc_eNB.c ~/openairinterface5g/openair2/RRC/LTE/rrc_eNB.c
sudo ./build_oai -I -c -C --eNB -w USRP
sudo cp /local/repository/etc/OAI/enb1.conf ~/openairinterface5g/targets/PROJECTS/GENERIC-LTE-EPC/CONF/enb.band7.tm1.50PRB.usrpb210.conf
