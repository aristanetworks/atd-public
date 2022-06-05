CloudVision Studios  -  L3LS/EVPN
=================================
Cloudvision Studios allows us to easily and quickly deploy complicated network topologies in a matter of minutes. 
Before we get started, let's get familiarized with the basic data structure of CVP Studios. 
CVPS works much like the GIT framework. 
In GIT we have a staging area, a commit to finalize our changes to, and 
pull requests that will submit our changes to a top level authority to either approve or deny our changes. 


.. image:: images/cvp_studios_l3ls_evpn/1GIT.png
   :align: center

CVPS follows that schema very closely. 

.. image:: images/cvp_studios_l3ls_evpn/2CVPSASGIT.png
   :align: center

In CVPS, we have our Workspace (staging area) , our Studios (Local Repositories) and our Workspace Submit (commit) just like in git. 
In CVPS we modify our Studios, then check/validate the configuration for submission. 
The Workspace Submit closes out the workspace,and no further change can be made to that particular workspace. 
The changes are then merged into the base state of the modified studios to be used in a new workspace for Day2 changes. 

Our Change Control request is analogous to the Pull Request, in that we are asking permission for our changes to be the new state of the network. 
Once complete, both the state of the operating network and Studios are the same. 
No action is performed on the network until the change control process is authorized.
It’s important to note that the modified workspace can be abandoned at any time before submission, which returns the modified studios to their original pre-workspace state. 
Now that we’ve covered the structure of CVPS, let’s move onto the lab itself. 

Our topology consists of two spines and 4 leafs.  Any other switch should be ignored from a studios perspective. 
Our hosts will be pre-configured as L2 LACP trunk port-channels up to their respective leafs. 
VLAN 60 and 70 will be pre-configured with SVIs on each host for post change reachability testing. 
All underlay addressing will be performed by CVPS.

.. image:: images/cvp_studios_l3ls_evpn/3TOPO.PNG
   :align: center
