#!/bin/sh

# toppicks (C) kiddac. 2024

echo 1 > /proc/sys/vm/drop_caches
echo 2 > /proc/sys/vm/drop_caches
echo 3 > /proc/sys/vm/drop_caches

python /usr/lib/enigma2/python/Plugins/Extensions/KiddaC_Skin_E2sentials/scraper.py
	
exit 0
