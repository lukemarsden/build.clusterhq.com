#!/bin/sh
for X in $(VBoxManage list vms|grep -v inaccessible |sed s/\"//g |awk '{print $1;}'); do VBoxManage controlvm $X poweroff || VBoxManage unregistervm --delete $X; done
