#!/bin/bash
# Enforce reinstall, works around issue on Mark-1
sudo /opt/venvs/mycroft-core/bin/python -m pip install --upgrade --force-reinstall netifaces==0.10.7 > /dev/null 2>&1
exit 0
