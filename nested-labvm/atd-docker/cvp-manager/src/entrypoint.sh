#!/bin/bash

eval $(fixuid -q)

exec python cvp_manager.py
