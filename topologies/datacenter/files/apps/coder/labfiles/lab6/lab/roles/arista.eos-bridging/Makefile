#!/usr/bin/make
# WARN: gmake syntax
########################################################
# Makefile for ansible-eos-bridging role
#
# useful targets:
#	make flake8 -- flake8 checkes
#	make tests -- run all of the tests
#	make clean -- clean distutils
#
########################################################
# variable section

NAME = "ansible-eos-bridging"

VERSION := $(shell cat VERSION)

########################################################

all: clean flake8 build tests

flake8:
	flake8 --ignore=E265,E266,E302,E303,F401,F403 filter_plugins/

clean:
	@echo "Cleaning up byte compiled python stuff"
	find . -type f -regex ".*\.py[co]$$" -delete
	@echo "Cleaning up Ansible stuff"
	find . -type f -regex ".*\.retry$$" -delete

tests: clean
	nosetests -v
