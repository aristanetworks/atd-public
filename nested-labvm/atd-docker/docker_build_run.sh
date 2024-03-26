#!/bin/bash

echo "Starting one-time build containers"

docker run --name atd-ceosbuilder -d --rm -v /etc/atd:/etc/atd:ro -v /opt/atd:/opt/atd:ro -v /opt/ceos:/opt/ceos:rw -e PYTHONUNBUFFERED=1 us.gcr.io/beta-atds/atddocker_ceosbuilder:3.3.1