Openconfig gNMI Lab
===================
.. thumbnail:: images/gnmi/gnmi-cvp-streaming.png

.. thumbnail:: images/gnmi/gnmi-eos-streaming.png

Summary
-------
This lab will walk a user through connecting to both a Arista EOS device and a Arista CloudVision instance to test streaming telemetry of common metrics all through a standard Openconfig streaming interface known as gNMI. These simply scratch the surface of what is available.  More complex and better examples are maintained by Arista on the open management page.  Examples will be using the gNMIC binary.

Lab changes for gNMIC that need to be made prior to this lab.
-------------------------------------------------------------

**Per switch the following needs to be added.**

.. Note:: You can save some time by adding these lines to the existing intrastructure configlet, since the Terminattr change below is within this configlet. Feel free to create a new gNMI configlet if you prefer.

.. code-block:: bash

    management api gnmi 
    transport grpc default
    provider eos-native
    !
    management api models
    provider aft
    ipv4-unicast
    Ipv6-unicast

**management api gnmi** - This command turns on the gNMI service which is needed for gNMI

**management api models** - This command turns on airstream /streaming route tables through gNMI

|

**Terminattr changes.**

.. code-block:: bash
   
    daemon TerminAttr
    exec /usr/bin/TerminAttr -disableaaa -cvaddr=192.168.0.5:9910 -taillogs -cvauth=key,atd-lab -smashexcludes=ale,flexCounter,hardware,kni,pulse,strata -ingestexclude=/Sysdb/cell/1/agent,/Sysdb/cell/2/agent -cvgnmi
    no shutdown

.. note::
    Notice the -cnmi flag at the end.  This is the flag that tells Terminattr to tunnel its openconfig traffic to CVP. For example, it will stream all of its Openconfig traffic gNMI through Terminattr so it is accessible via CVP as well. 
|
Installation of gNMIC
	To install gNMIC we will first need to go to the Programmability IDE and open a new terminal.  We do this once we are within the IDE by clicking the 3 line menu in the upper left > Terminal > New Terminal. 

.. thumbnail:: images/gnmi/gnmi-terminal.png
    :width: 75%
|
Once in the terminal we simply need to install the binary by the following one liner command. 

.. code-block:: bash
   
    bash -c "$(curl -sL https://get-gnmic.kmrd.dev)"
    

To verify installation issue a which gnmic.

.. code-block:: bash
   
    ➜  project which gnmic
    /usr/local/bin/gnmic

Connecting to an EOS device.
----------------------------

Capabilities
	To test what the device is capable of ie which YANG models are currently supported and which encapsulations are available we will need to show the capabilities.   In this task we will check to see the capabilities of leaf1.

.. code-block:: bash
   
    gnmic -a 192.168.0.12:6030 -u arista -p password --insecure capabilities
    

Truncated response 

.. code-block:: bash
   
    gNMI version: 0.7.0
    supported models:
  - openconfig-platform-port, OpenConfig working group, 0.4.2
  - openconfig-platform-transceiver, OpenConfig working group, 0.8.0
  - arista-bfd-augments, Arista Networks <http://arista.com/>, 1.0.4
  - ietf-yang-metadata, IETF NETMOD (NETCONF Data Modeling Language) Working Group, 
  - openconfig-segment-routing-types, OpenConfig working group, 0.2.0

Get
---	
A get request within gNMI is a good way to get a one way communication of a specific gNMI path.  For example, if we want to get Ethernet's current status we would issue the following.

.. code-block:: bash
    
    gnmic -a 192.168.0.12:6030 -u arista -p password --insecure get --path \
   "/interfaces/interface[name=Ethernet1]/state/oper-status"



**Response**

.. code-block:: bash
   
    [
  {
    "source": "192.168.0.12:6030",
    "timestamp": 1653401690344274357,
    "time": "2022-05-24T14:14:50.344274357Z",
    "updates": [
      {
        "Path": "interfaces/interface[name=Ethernet1]/state/oper-status",
        "values": {
          "interfaces/interface/state/oper-status": "UP"
        }
      }
    ]
  }
    ]

To get all possible paths within gNMI we would issue the following command.

.. code-block:: bash
   
    gnmic -a 192.168.0.12:6030 -u arista -p password --insecure get  --path /

Subscribe
---------

The most powerful portion of gNMI and Openconfig is the ability to subscribe to a specific path.  The most common path to subscribe to would be all interface counters.

.. code-block:: bash
   
    gnmic -a 192.168.0.12:6030 -u arista -p password --insecure subscribe --path \
  "/interfaces/interface/state/counters"

**Truncated output of stream.**

.. code-block:: bash
   
    {
    "source": "192.168.0.12:6030",
  "subscription-name": "default-1653401885",
  "timestamp": 1653401886216521708,
  "time": "2022-05-24T14:18:06.216521708Z",
  "updates": [
    {
      "Path": "interfaces/interface[name=Ethernet2]/state/counters/in-octets",
      "values": {
        "interfaces/interface/state/counters/in-octets": 424932
      }
    }
  ]
    }
    {
  "source": "192.168.0.12:6030",
  "subscription-name": "default-1653401885",
  "timestamp": 1653401886216521708,
  "time": "2022-05-24T14:18:06.216521708Z",
  "updates": [
    {
      "Path": "interfaces/interface[name=Ethernet2]/state/counters/in-multicast-pkts",
      "values": {
        "interfaces/interface/state/counters/in-multicast-pkts": 3310
      }
    }
  ]
    }

The stream will run endlessly until the user cancels it by pressing ctrl+c.  You can subscribe to any path within EOS.

Subscribe to the routing tables.

.. code-block:: bash

    gnmic -a 192.168.0.12:6030 -u arista -p password --insecure subscribe --path \
    "/interfaces/interface/state/counters"

**Truncated output of stream.**

.. code-block:: bash
   
    {
  "source": "192.168.0.12:6030",
  "subscription-name": "default-1653402161",
  "timestamp": 1653402062845675336,
  "time": "2022-05-24T14:21:02.845675336Z",
  "prefix": "network-instances/network-instance[name=default]/afts/ipv4-unicast/ipv4-entry[prefix=192.168.0.0/24]/state",
  "updates": [
    {
      "Path": "next-hop-group",
      "values": {
        "next-hop-group": 4294967297
      }
    },
    {
      "Path": "origin-protocol",
      "values": {
        "origin-protocol": "openconfig-policy-types:DIRECTLY_CONNECTED"
      }
    },
    {
      "Path": "prefix",
      "values": {
        "prefix": "192.168.0.0/24"
      }
    }
  ]
    }


Press crtl+c to stop the stream. 

If you'd like to see the administrative status of an interface change in real time, you can use the GET command we used above, but replace "get" with "subscribe". The command should look like this:

.. code-block:: bash
    
    gnmic -a 192.168.0.12:6030 -u arista -p password --insecure subscribe --path \
   "/interfaces/interface[name=Ethernet1]/state/oper-status"


Once you've run this command, open an SSH session to leaf1 and shutdown Ethernet1. The change is reflected instantly in gNMI.


Connecting to CVP For device telemetry.
---------------------------------------
	
**Intro for CVP**

The same gNMI service that we use for EOS we are able to move to CVP.  In the use case of CVP we use the Path Target field to distinguish between different EOS devices.  For example, every outgoing request of gNMI stream we have to embed the serial or deviceID of the EOS device to stream data from it.  This offers the tremendous advantage of talking simply only to CVP for all of the devices we want to stream device telemetry for versus going to every device individually.

Get a token
	Since CVP does not use a username/password for the gNMI service a service account and token are required.  On the **Settings gear** in the upper right hand corner click on that.  Then on the left click under **Service Accounts.**	

.. thumbnail:: images/gnmi/gnmi-serviceaccount1.png

|

Click **+ Add Service Account.** Service Account name **test** Description **test**. Roles **network-admin**. Status **Enabled**.


.. thumbnail:: images/gnmi/gnmi-serviceaccount2.png

|

Click **Add**. Now create a token for test. Click **test**.

.. thumbnail:: images/gnmi/gnmi-serviceaccount3.png
|
Under the **Generate Service Account Token** section, give your token a description, Select a date in the future for valid Until.
Click **Generate**.  

Copy the token to somewhere like your text editor. For example, my token is as follows.
eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJkaWQiOjcwNjA4OTkyMTQ5ODQ3NDEwMDQsImRzbiI6InRlc3QiLCJkc3QiOiJhY2NvdW50IiwiZXhwIjoxNjU1OTk1NDA1LCJpYXQiOjE2NTM0MDM1MTIsInNpZCI6IjQxMDQ3MzYyMDAzZmFkY2RkZWEyOTlhMGQ5NTMxOGUwYTQ5NjRiNzg4YzFmYzI2YTJlYmM2ZGJmZWMwNjM4ODQtMkZmOG40eEtubE5JZ19tS2J3Y0VHQzhLOWxFZ3lYYUY0SFVtOUpMWiJ9.SxrLU2rMNUQteqTtrfZaRye35z2OvxbK-S-wTtmDmLt8uZzEdK9i7uxOBFTYKT97w7DQY1SnRr2M1nZT0e5yxhKm-joDfzCpfZZE2WLsPszqozYrOZYgOms3vO3_oJH-_VaEj_J_dpAKTCfM7m2aBv62SfiOzXBBOx_CjqOQvJHKZPDQLUlJMtO7MiCdStRs2WxVleJrhiLjTvYy8qlRP4Od2OhSgnaRvW6S8optXO9DWMhadhmzDQvzXcYMl3JCFtDo4v_ae3SaiUvhh_j8itBjikaYyoZyNxhCxDEsh47fCYMyJGF7bhZN53UCq9mzXou-fMVD_lELKw-l2MIUQVyzFdTvuhc8cOUsrud1aYfL8vubB_s6F_rIE5p5Atj43Uy3hXz-gpZcUfbZRVUWEold44CrVJyjscVkcjdBlPCKsBvQ6EBCx-BcHjNci4r3ADPcyQuyLcch1BSphhIUjkv451FPOY82TsraGxmbomjZ1OWAI9T_9B5OR1ERKSLKlmJQXL2izk7lnfCz2C9YOW5NMFC_FFT4EPV58K9Mk1Phhfv1Gtclu4iFZHdNUwS63FJbbww5xvs5ZioHAfUqqqgjyCpcwpK73ZNhHLsS858Tcpa3msDdpY9fLAj2P8Fz0rZuZkHzw1-OPoDJtWaiBWbX3vfZ1gDelSyok_5Kk4Y

Click **okay**.

|

**Subscribe to leaf1’s interface counters.**

First we need to create an environmental variable for the token. Let's go back to Programmability IDE and run the following, pasting your own token value on the **export TOKEN** line

.. code-block:: bash
   
    export TOKEN=<paste CVP token value here>
    gnmic -a 192.168.0.5:443 subscribe --path "openconfig:/interfaces/interface/state/counters" --token=$TOKEN --target=leaf1 --skip-verify

In this example, we are asking CVP to subscribe to the path of interface state counters using our Token for the target of leaf1.  If this is tested against a device that is not standard cEOS it is typically going to be the devices serial number.

Truncated output

.. code-block:: bash
   
    {
  "source": "192.168.0.5:443",
  "subscription-name": "default-1653404149",
  "timestamp": 1653402066603530716,
  "time": "2022-05-24T14:21:06.603530716Z",
  "target": "leaf1",
  "updates": [
    {
      "Path": "interfaces/interface[name=Ethernet4]/state/counters/in-fcs-errors",
      "values": {
        "interfaces/interface/state/counters/in-fcs-errors": 0
      }
    },
    {
      "Path": "interfaces/interface[name=Ethernet4]/state/counters/in-unicast-pkts",
      "values": {
        "interfaces/interface/state/counters/in-unicast-pkts": 0
      }
    }

Press ctrl+c to stop the stream of data. 


 

