Rollback
========

Oops. We’ve made a horrible mistake and we need to roll it back before
anyone notices.

Fortunately, using Git we have a record of what changed and we can
revert everything back to the previous ``commit``. Once we revert the change,
Jenkins will see see it and run your playbook again, undoing the changes
that we just made.

Step #1: See the diff(erence)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Before we roll back, let’s check what Git has on record. To do that,
we’re going to have to get the checksum of the first commit in Lab #6
and the checksum of the commit after you added VLAN 2000 and 3000. Once
we get the checksums, we can ``diff`` them. ``Diff`` shows the difference between
two items.

To find the checksums, we need to use the ``git reflog`` command
on **devbox**. The ``git reflog`` command lists every commit, their checksum, their
distance from the current commit, and the commit message.

Run ``git reflog`` inside your lab6 directory (``~/Desktop/labfiles/lab6/lab``):

.. code-block:: bash

    aristagui@labvm:~/Desktop/labfiles/lab6/lab$ git reflog
    30fed59 HEAD@{0}: commit: Added VLAN 2000 and 3000
    524c2bb HEAD@{1}: commit: (initial): Initial commit

Note the two checksums, ``30fed59`` and ``524c2bb``. Let’s diff them with ``git diff
524c2bb 30fed59``.

.. note:: Your checksums will be different than in this lab guide. Please
          make sure to use your checksums from git reflog and not the ones in
          the guide.

.. code-block:: bash

    aristagui@labvm:~/Desktop/labfiles/lab6/lab$ git diff 524c2bb 30fed59
    diff --git a/group_vars/leafs.yml b/group_vars/leafs.yml
    index c17ea3b..6bf591e 100644
    --- a/group_vars/leafs.yml
    +++ b/group_vars/leafs.yml
    @@ -9,6 +9,10 @@ provider:
    vlans:
       - vlanid: 1001
         name: default
    -  - vlanid: 2000
    -    name: production
    -  - vlanid: 3000
    -    name: development

The ``diff`` shows - next to lines that were removed. If we roll back, we would
lose anything that’s different. We did want to roll those VLANs back,
right? We’re good to go!

Step #2: Revert the change
~~~~~~~~~~~~~~~~~~~~~~~~~~

To roll back, we need to use the ``git revert`` command, coupled
with ``HEAD``. ``HEAD`` is the Git method of saying the last commit (in the
checked out branch). If you revert the last commit it will bring you
back to the commit before the latest commit.

You can also use this command to revert to any other commit - useful if
you want to roll back to 2 weeks and 30 commits ago.

Let’s revert with ``git revert HEAD``.

.. code-block:: bash

    aristagui@labvm:~/Desktop/labfiles/lab6/lab$ git revert HEAD

A window will pop up asking you to enter a commit message. Let’s just
stick with the default. Hit **Ctrl-X** to save.

.. code-block:: bash

    aristagui@labvm:~/Desktop/labfiles/lab6/lab$ git revert HEAD
    [master b1e1694] Revert "Added VLAN 2000 and 3000"
    1 file changed, 4 deletions(-)

Note the 4 deletions - those are the 4 lines in the ``diff`` above. If you
were to open your group_vars file, you would see that those lines are
now missing.

Now if you were to look at your log using git reflog, you will see a
revert:

.. code-block:: bash

    aristagui@labvm:~/Desktop/labfiles/lab6/lab$ git reflog
    b1e1694 HEAD@{0}: revert: Revert "Added VLAN 2000 and 3000"
    30fed59 HEAD@{1}: commit: Added VLAN 2000 and 3000
    524c2bb HEAD@{2}: commit: (initial): Initial commit

Now let's push our changes to our remote repo so Jenkins can pick up on the changes

.. code-block:: bash

    aristagui@labvm:~/Desktop/labfiles/lab6/lab$ git push origin master
    Counting objects: 6, done.
    Delta compression using up to 2 threads.
    Compressing objects: 100% (5/5), done.
    Writing objects: 100% (6/6), 783 bytes | 0 bytes/s, done.
    Total 6 (delta 1), reused 0 (delta 0)
    To /home/aristagui/Desktop/labfiles/lab6/repo
        19404fc..983adb8  master -> master

Hurray!

Step #3: Watch Jenkins undo
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Go back into Jenkins and look at the job history for the latest job,
just like you did in the previous lab. Also, log into your switches and
notice that the VLANs are no longer present.