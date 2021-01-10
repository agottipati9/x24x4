# About This Profile

Use this profile to instantiate an experiment of SigFlow using Open Air Interface,
FlexRAN, and NextEPC to realize an end-to-end SDR-based mobile network. This profile includes
the following resources:

    * Off-the-shelf Nexus 5 UE running Android 4.4.4 KitKat ('rue1')
    * SDR eNodeB (Intel NUC + USRP B210) running OAI on Ubuntu 16 ('enb1')
    * SDR eNodeB (Intel NUC + USRP B210) running OAI on Ubuntu 16 ('enb2')
    * NextEPC EPC (HSS, MME, SPGW), FlexRAN Ran Controller, and SigFlow running on Ubuntu 18 ('epc')
    * A node providing out-of-band ADB access to the UE ('adb-tgt')

# Finishing the Install

After booting is complete (all nodes have a Startup status of **Finished** aside from the UE), run the following commands
to finish setting up the experiment:

Log into the `enb1` node and run: 

    sudo /local/repository/bin/OAI/install_OAI_eNB1.sh

Log into the `enb2 ` node and run:

    sudo /local/repository/bin/OAI/install_OAI_eNB2.sh
    
Log into the `epc` node and do:

   Navigate to this [guide](https://gitlab.flux.utah.edu/powderrenewpublic/mww2019/blob/master/4G-LTE.md) and follow the instructions
   in the **Add the simulated UE subscriber information to the HSS database** section to add the UE subscriber information. Enter in the following:
    
    * IMSI: 998981234560300
    * Key: 00112233445566778899aabbccddeeff
    * OP_Type: OP
    * OP: 01020304050607080910111213141516
    
After adding the UE subscriber information, run the following command to install python3.8:

    sudo /local/repository/bin/MigrationController/install_python.sh     
        
**NOTE: Press enter when prompted to add the python repository**
        
Log into the `adb` node and run:

    sudo /local/repository/bin/UE/install_UE_iPerf.sh

# Getting Started
After installing all the dependencies, you can start SigFlow with following commands:

Log into the `epc` node and run the following commands in separate windows:

    sudo /opt/nextepc/install/bin/nextepc-epcd
    sudo /snap/bin/flexran
    sudo python3.8 /local/repository/bin/MigrationController/mano_controller.py
    
**NOTE: If there is an error starting FlexRAN, try running:** 

    sudo snap connect flexran:process-control
    
Log into the `enb1` node and run the following commands in separate windows: 

    sudo -E ~/openairinterface5g/targets/bin/lte-softmodem.Rel14 -O ~/openairinterface5g/targets/PROJECTS/GENERIC-LTE-EPC/CONF/enb.band7.tm1.50PRB.usrpb210.conf
    sudo python3 /local/repository/bin/MigrationController/eNB_agent.py source
    
**NOTE: Wait for the UE to attach to the base station before preceeding. The UE device will typically connect on its own, but if it doesn't, you can reboot the phone from `adb` node with the following:**

    pnadb -a
    adb reboot
      
Log into the `enb2 ` node and run:

    sudo /local/repository/bin/MigrationController/start_agent.sh
    
This will start migration process. To restart SigFlow, simply kill the previous commands and restart the services in this section.
 
**NOTE: Due to stability issues with OAI, the handover may fail, causing the base stations to crash. Example errors are listed below. If this happens, try restarting SigFlow.**

**Common Errors:** 
   * LTE_RRCConnectionReestablishmentRequest ue_Identity.physCellId(0) is not equal to current physCellId(1), let's reject the UE.

# Conducting Bandwidth Tests
## Configuring the Source Agent
Due to the OAI's X2 protocol implementation, when the source base station is removed, the target base station will
also stop. To circumvent this for measurement purposes, on `enb1` run:

    sudo python3 /local/repository/bin/MigrationController/eNB_agent.py source -t X

where X is the number of seconds to delay the removal of the source base station.

## Setting up the UE for iPerf
To conduct bandwidth measurements, run the following commands on the `adb` node prior to starting the agent on `enb2`:

To access the UE GUI, run: 

    culebra -s pc599.emulab.net:8001 -uG -P 0.25
 
This will open up a GUI to access the COTS UE. 

**NOTE: If there is an error when opening the GUI, try running:**

    pnadb -a

To access iPerf on UE, do the following:
* **NOTE: Please carry out only one action at a time, as the GUI is very slow.**
* If the screen is black, right click on the screen (may have to hold right click) and select wake up device.
* Click on the menu towards the bottom of the GUI and open the magic iPerf application.
* In the upper left, ensure that iPerf2 is displayed.
* Select the input box and enter in an iPerf command.

* For Uplink:

        -c 192.168.0.1 -p 8000 -t 120 -i 1 -u
    
* For Downlink:

        -s -u -p 5000 -i 1
    
     **NOTE: During the handover, iPerf may fail, when testing downlink traffic.**

     If this is the case, try: 

        -c 192.168.0.1 -p 8000 -t 120 -i 1 -u -R 

    * This causes the UE to act as a client, but the server will send packets downstream.

* In the upper right, flip the button that says ``stopped``. This will start the iPerf process. 
   
   **NOTE: For uplink and the reversed downlink (-R), please ensure that the iPerf server is running on the `epc` before starting the client.**
   
For trouble shooting the GUI, please refer to this [guide](https://wiki.phantomnet.org/wiki/phantomnet/tutorial-interacting-and-scripting-on-the-ue-with-culebra).

## Setting up the EPC for iPerf
On the `epc` node, run the following command:

* For Uplink:

        iperf -s -u -p 8000 -i 1
        
* For Downlink:

        iperf -c 192.168.0.2 -p 5000 -t 120 -i 1 -u
    If you are using the **-R** flag on the UE, run:
    
        iperf -s -u -p 8000 -i 1
