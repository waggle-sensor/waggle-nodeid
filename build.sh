#!/bin/bash -e

docker run --rm \
  -e NAME="waggle-nodeid" \
  -e DESCRIPTION="Service to create the node's ID file" \
  -e "DEPENDS=python3-click, iproute2" \
  -v "$PWD:/repo" \
  waggle/waggle-deb-builder:latest
  