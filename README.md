# About This Profile

Use this profile to instantiate an experiment of BoTM using srsLTE and NextEPC to realize an end-to-end SDR-based mobile network. This profile includes
the following resources:

      * Off-the-shelf Nexus 5 UE running Android 4.4.4 KitKat ('rue1')
      * SDR eNodeB (Intel NUC + USRP B210) running srsLTE on Ubuntu 18 ('enb1')
      * SDR eNodeB (Intel NUC + USRP B210) running srsLTE on Ubuntu 18 ('enb2')
      * NextEPC EPC (HSS, MME, SPGW) and BoTM running on Ubuntu 18 ('epc')
      * A node providing out-of-band ADB access to the UE ('adb-tgt')

# Finishing the Install

After booting is complete (all nodes have a Startup status of **Finished** aside from the UE), run the following commands
to finish setting up the experiment:
    
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
After installing all the dependencies, you can start BoTM with following commands:

Log into the `epc` node and run the following commands in separate windows:

    sudo /opt/nextepc/install/bin/nextepc-epcd
    sudo python3.8 /local/repository/bin/MigrationController/mano_controller.py
    
Log into the `enb1` node and run the following commands in separate windows: 

    n/a
    sudo python3 /local/repository/bin/MigrationController/eNB_agent.py source
    
**NOTE: Wait for the UE to attach to the base station before preceeding. The UE device will typically connect on its own, but if it doesn't, you can reboot the phone from `adb` node with the following:**

    pnadb -a
    adb reboot
      
Log into the `enb2 ` node and run:

    sudo /local/repository/bin/MigrationController/start_agent.sh
    
This will start migration process. To restart BoTM, simply kill the previous commands and restart the services in this section.

# Conducting Bandwidth Tests
## Setting up the EPC for iPerf
On the `epc` node, run the following command:

    iperf -s -u -p 8000 -i 1
        
## Setting up the UE for iPerf
To conduct bandwidth measurements, run the following commands on the `adb` node prior to starting the agent on `enb2`:

To access the UE GUI, run: 

    culebra -s pc599.emulab.net:8001 -uG -P 0.25
 
This will open up a GUI to access the COTS UE. 

**NOTE: If there is an error when opening the GUI, try running:**

    pnadb -a

To access iPerf on the UE, do the following:
* **NOTE: Please carry out only one action at a time, as the GUI is very slow.**
* If the screen is black, right click on the screen (may have to hold right click) and select ``Wake up``.
* Click on the menu (middle icon on the last row) and open the ``Magic iPerf`` application.
* In the upper left, ensure that iPerf2 is displayed.
* Select the input box and enter in an iPerf command.

      -c 192.168.0.1 -p 8000 -t 80 -i 1 -u -d

   * The ```-t``` flag specifies the duration of the iPerf test.
   * The ```-d``` flag allows uplink and downlink testing to be conducted in parallel.

* In the upper right, flip the button that says ``stopped``. This will start the iPerf process. 
   
   **NOTE: Please ensure that the iPerf server is running on the `epc` before starting the client.**

The GUI may freeze due to the iPerf updates, in this case, simply restart the ``culebra`` client.

For all other trouble shooting the GUI, please refer to this [guide](https://wiki.phantomnet.org/wiki/phantomnet/tutorial-interacting-and-scripting-on-the-ue-with-culebra).
