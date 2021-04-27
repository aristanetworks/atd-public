#!/bin/bash

eval $( fixuid )

sudo /usr/sbin/sshd -D
