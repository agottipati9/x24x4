#!/usr/bin/env python

#
# Standard geni-lib/portal libraries
#
import geni.portal as portal
import geni.rspec.pg as rspec
import geni.rspec.emulab as elab
import geni.rspec.igext as IG
import geni.urn as URN

tourDescription = """
Use this profile to instantiate an experiment of BoTM using srsLTE and NextEPC to realize an end-to-end SDR-based mobile network. This profile includes
the following resources:
  * Off-the-shelf Nexus 5 UE running Android 4.4.4 KitKat ('rue1')
  * SDR eNodeB (Intel NUC + USRP B210) running srsLTE on Ubuntu 18 ('enb1')
  * SDR eNodeB (Intel NUC + USRP B210) running srsLTE on Ubuntu 18 ('enb2')
  * NextEPC EPC (HSS, MME, SPGW) and BoTM running on Ubuntu 18 ('epc')
  * A node providing out-of-band ADB access to the UE ('adb-tgt')
""";

tourInstructions = """
# Finishing the Install

After booting is complete (all nodes have a Startup status of **Finished** aside from the UE), run the following commands
to finish setting up the experiment:

    sudo /local/repository/bin/srsLTE/install_srsLTE_X.sh
    
where X is either 1 or 2.
    
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
      
Log into the `enb2` node and run:

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
""";

#
# PhantomNet extensions.
#
import geni.rspec.emulab.pnext as PN


#
# Globals
#
class GLOBALS(object):
    UE_IMG = URN.Image(PN.PNDEFS.PNET_AM, "PhantomNet:ANDROID444-STD")
    ADB_IMG = URN.Image(PN.PNDEFS.PNET_AM, "PhantomNet:UBUNTU14-64-PNTOOLS")
    SRS_ENB_IMG = "urn:publicid:IDN+emulab.net+image+PowderProfiles:U18LL-SRSLTE:1"
    EPC_IMG = "urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU18-64-STD"
    NEXTEPC_INSTALL_SCRIPT = "/usr/bin/sudo /local/repository/bin/NextEPC/install_nextEPC.sh"
    SRSLTE_INSTALL_SCRIPT = "/usr/bin/sudo /local/repository/bin/srsLTE/install_srsLTE.sh"
    SIM_HWTYPE = "d430"
    NUC_HWTYPE = "nuc5300"
    UE_HWTYPE = "nexus5"


#
# This geni-lib script is designed to run in the PhantomNet Portal.
#
pc = portal.Context()

#
# Profile parameters.
#
pc.defineParameter("FIXED_UE1", "Bind to a specific UE",
                   portal.ParameterType.STRING, "", advanced=True,
                   longDescription="Input the name of a PhantomNet UE node to allocate (e.g., 'ue1').  Leave blank to "
                                   "let the mapping algorithm choose.")

pc.defineParameter("FIXED_ENB1", "Bind to a specific eNodeB",
                   portal.ParameterType.STRING, "", advanced=True,
                   longDescription="Input the name of a PhantomNet eNodeB device to allocate (e.g., 'nuc1').  Leave "
                                   "blank to let the mapping algorithm choose.  If you bind both UE and eNodeB "
                                   "devices, mapping will fail unless there is path between them via the attenuator "
                                   "matrix.")
pc.defineParameter("FIXED_ENB2", "Bind to a specific eNodeB",
                   portal.ParameterType.STRING, "", advanced=True,
                   longDescription="Input the name of a PhantomNet eNodeB device to allocate (e.g., 'nuc1').  Leave "
                                   "blank to let the mapping algorithm choose.  If you bind both UE and eNodeB "
                                   "devices, mapping will fail unless there is path between them via the attenuator "
                                   "matrix.")

pc.defineParameter("TYPE", "Experiment type",
                   portal.ParameterType.STRING,"ota",[("atten","Real UE with attenuator"),("srsUE","srsUE with attenuator"),("ota","Over the air")],
                   longDescription="*Simulated UE*: OAI simulated UE connects to an OAI eNodeB and EPC. *Real "
                                   "UE/srsUE with attenuator*: Real RF devices will be connected via transmission "
                                   "lines with variable attenuator control. *Over the air*: Real RF devices with real "
                                   "antennas and transmissions propagated through free space will be selected.")


params = pc.bindParameters()
pc.verifyParameters()

#
# Create our in-memory model of the RSpec -- the resources we're going
# to request in our experiment, and their configuration.
#
request = pc.makeRequestRSpec()
hacklan = request.Link("s1-lan")

# Checking for COTS UE
if params.TYPE != "srsUE":
    # Add a node to act as the ADB target host
    adb_t = request.RawPC("adb-tgt")
    adb_t.disk_image = GLOBALS.ADB_IMG

# Add a NUC eNB node.
enb1 = request.RawPC("enb1")
if params.FIXED_ENB1:
    enb1.component_id = params.FIXED_ENB1
enb1.hardware_type = GLOBALS.NUC_HWTYPE
enb1.disk_image = GLOBALS.SRS_ENB_IMG
enb1.Desire("rf-radiated" if params.TYPE == "ota" else "rf-controlled", 1)
# enb1.addService(rspec.Execute(shell="bash", command=GLOBALS.SRSLTE_INSTALL_SCRIPT))
enb1_s1_if = enb1.addInterface("enb1_s1if")

# Add another NUC eNB node.
enb2 = request.RawPC("enb2")
if params.FIXED_ENB2:
    enb2.component_id = params.FIXED_ENB2
enb2.hardware_type = GLOBALS.NUC_HWTYPE
enb2.disk_image = GLOBALS.SRS_ENB_IMG
enb2.Desire("rf-radiated" if params.TYPE == "ota" else "rf-controlled", 1)
# enb2.addService(rspec.Execute(shell="bash", command=GLOBALS.SRSLTE_INSTALL_SCRIPT))
enb2_s1_if = enb2.addInterface("enb2_s1if")

# Add an OTS (Nexus 5) UE
if params.TYPE != 'srsUE':
    rue1 = request.UE("rue1")
else:
    rue1 = request.RawPC("rue1")
if params.FIXED_UE1:
    rue1.component_id = params.FIXED_UE1
if params.TYPE != "srsUE":
    rue1.hardware_type = GLOBALS.UE_HWTYPE
    rue1.disk_image = GLOBALS.UE_IMG
    rue1.Desire("rf-radiated" if params.TYPE == "ota" else "rf-controlled", 1)
    rue1.adb_target = "adb-tgt"
else:
    rue1.hardware_type = GLOBALS.NUC_HWTYPE
    rue1.disk_image = GLOBALS.SRS_ENB_IMG
    rue1.Desire("rf-radiated" if params.TYPE == "ota" else "rf-controlled", 1)

# Create the RF link between the Nexus 5 UE and eNodeB
# ue1---------------------------------------------------
enb1_rue1_rf = enb1.addInterface("rue1_rf")
rue1_enb1_rf = rue1.addInterface("enb1_rf")
rflink11 = request.RFLink("rflink11")
rflink11.addInterface(enb1_rue1_rf)
rflink11.addInterface(rue1_enb1_rf)

enb2_rue1_rf = enb2.addInterface("rue1_rf")
rue1_enb2_rf = rue1.addInterface("enb2_rf")
rflink21 = request.RFLink("rflink21")
rflink21.addInterface(enb2_rue1_rf)
rflink21.addInterface(rue1_enb2_rf)

# Add a link connecting the NUC eNB and the OAI EPC node.
hacklan.addInterface(enb1_s1_if)
hacklan.addInterface(enb2_s1_if)

# Add OAI EPC (HSS, MME, SPGW) node.
epc = request.RawPC("epc")
epc.disk_image = GLOBALS.EPC_IMG
epc.addService(rspec.Execute(shell="bash", command=GLOBALS.NEXTEPC_INSTALL_SCRIPT))
epc_s1_if = epc.addInterface("epc_s1if")

# epclink2.addNode(epc)
hacklan.addInterface(epc_s1_if)
hacklan.link_multiplexing = True
hacklan.vlan_tagging = True
hacklan.best_effort = True

tour = IG.Tour()
tour.Description(IG.Tour.MARKDOWN, tourDescription)
tour.Instructions(IG.Tour.MARKDOWN, tourInstructions)
request.addTour(tour)

#
# Print and go!
#
pc.printRequestRSpec(request)
