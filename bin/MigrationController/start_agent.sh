#!/bin/bash

sudo python3 /local/repository/bin/MigrationController/eNB_agent.py target
sudo -E ~/openairinterface5g/targets/bin/lte-softmodem.Rel14 -O ~/openairinterface5g/targets/PROJECTS/GENERIC-LTE-EPC/CONF/enb.band7.tm1.50PRB.usrpb210.conf
