#!/bin/bash
# Resolve our magic names to docker internal ip, needs root privileges to write to the hosts file
sed 's/.*localmaeher.*//g' /etc/hosts >/etc/hosts.new && cat /etc/hosts.new >/etc/hosts
echo "$(getent ahostsv4 host.docker.internal | awk '{ print $1 }') localmaeher.dev.pvarki.fi mtls.localmaeher.dev.pvarki.fi bl.localmaeher.dev.pvarki.fi mtls.bl.localmaeher.dev.pvarki.fi" >>/etc/hosts || true
cat /etc/hosts
