Advanced Troubleshooting
============================

.. image:: images/tshoot_sp_1.png
   :align: center

.. note:: A set of possible answers are available here_. This hyperlink is only available to Arista employees.
          Please work with your Arista SE for access.

.. _here: 

1. Log into the **LabAccess** jumpserver:

   1. Type ``labs`` or option ``97`` at the Main Menu prompt. This will bring up additional lab menu selections.
   2. Type ``troubleshooting`` or option ``3`` at this prompt to open the troubleshooting lab section (If you were previously in the Troubleshooting Labs Menu, you can type ``back`` or option ``97`` to go back).
   3. Type ``tshoot-sp`` or option ``2`` at the prompt. The script will configure the lab into a errored set of states. It is up to you to determine
      a solution for each of the questions below. There can be many solutions, please work with your SE.

2. Lab Requirements

   1. Host 1 needs to reach Host 2

   2. All OSPF connections are up

   3. Preferred path is PE-1 -> Core-1 -> Core-2 -> PE2. Other available paths are backups

**Topology Notes**

   1. PE-1 = Leaf1

   2. PE-2 = Leaf4

   3. Core-1 = Spine1

   4. Core-2 = Spine2

