Rollback
========

Oops. We’ve made a horrible mistake, and we need to roll it back before
anyone notices.

Fortunately, using Git, we have a record of what changed, and we can
revert everything to the previous ``commit``. Once we revert the change,
Jenkins will see it and rerun your playbook, undoing the changes
we just made.

Step #1: See the diff(erence)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Before we roll back, let’s check what Git has on record. To do that,
we will have to get the checksum of the first commit in Lab #6
and the checksum of the commit after you added VLAN 2000 and 3000. Once
we get the checksums, we can ``diff`` them. ``Diff`` shows the difference between
two items.

We need to use the ``git reflog`` command in the **IDE** terminal to find the checksums.
The ``git reflog`` command lists every commit, its checksum, distance from the current
commit, and the commit message.

Run ``git reflog`` inside your lab6 directory (``~/project/labfiles/lab6/lab``):

.. code-block:: bash

    lab git:(master) git reflog
    116aaae (HEAD -> master, origin/master) HEAD@{0}: commit: Added VLAN 2000 and 3000
    2ad37af HEAD@{1}: commit (initial): Initial commit

Note the two checksums, ``116aaae`` and ``2ad37af`` (In this example). Let’s diff them with ``git diff
2ad37af 116aaae``.

.. note:: Your checksums will be different than in this lab guide. Please
          use your checksums from git reflog, not the ones in the guide.

.. code-block:: bash

    lab git:(master) git diff 2ad37af 116aaae
    diff --git a/group_vars/leafs.yml b/group_vars/leafs.yml
    index 9481c0c..e6040b8 100644
    --- a/group_vars/leafs.yml
    +++ b/group_vars/leafs.yml
    @@ -8,4 +8,9 @@ provider:
    eos_purge_vlans: true
    vlans:
      - vlanid: 1001
      -   name: default
    +   name: default
    + - vlanid: 2000
    +   name: production
    + - vlanid: 3000
    +   name: development

The ``diff`` shows - next to lines that were removed. If we roll back, we would
lose anything that’s different. We did want to roll those VLANs back,
right? We’re good to go!

Step #2: Revert the change
~~~~~~~~~~~~~~~~~~~~~~~~~~

To roll back, we need to use the ``git revert`` command coupled
with ``HEAD``. ``HEAD`` is the Git method of saying the last commit (in the
checked-out branch). If you revert the previous commit, it will return you
to the commit before the latest one.

You can also use this command to revert to any other commit - useful if
you want to roll back to 2 weeks and 30 commits ago.

Let’s revert with ``git revert HEAD``.

.. code-block:: bash

    lab git:(master) git revert HEAD

A window will pop up asking you to enter a commit message. Let’s
stick with the default. Hit **Ctrl-X** to save.

.. code-block:: bash

    lab git:(master) git revert HEAD
    [master 9534ae0] Revert "Added VLAN 2000 and 3000"
    1 file changed, 0 insertion(+), 4 deletions(-)

Note the four deletions - those are the four lines in the ``diff`` above. If you
were to open your group_vars file, you would see that those lines are
now missing.

Now, if you were to look at your log using git reflog, you would see a
revert:

.. code-block:: bash

    lab git:(master) git reflog
    9534ae0 (HEAD -> master) HEAD@{0}: revert: Revert "Added VLAN 2000 and 3000"
    116aaae (origin/master) HEAD@{1}: commit: Added VLAN 2000 and 3000
    2ad37af HEAD@{2}: commit (initial): Initial commit

Now let's push our changes to our remote repo so Jenkins can pick up on the changes.

.. code-block:: bash

    lab git:(master) git push origin master
    Enumerating objects: 7, done.
    Counting objects: 100% (7/7), done.
    Delta compression using up to 24 threads
    Compressing objects: 100% (3/3), done.
    Writing objects: 100% (4/4), 440 bytes | 440.00 KiB/s, done.
    Total 4 (delta 1), reused 0 (delta 0)
    To /home/coder/project/labfiles/lab6/repo
        116aaae..9534ae0  master -> master

Hurray!

Step #3: Watch Jenkins undo
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Go back into Jenkins and look at the job history for the latest job,
just like you did in the previous lab. Also, log into your switches and
notice that the VLANs are no longer present.
