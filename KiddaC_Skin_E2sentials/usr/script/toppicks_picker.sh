#!/bin/sh

# toppicks (C) kiddac. 2024

echo 1 > /proc/sys/vm/drop_caches
echo 2 > /proc/sys/vm/drop_caches
echo 3 > /proc/sys/vm/drop_caches


if test -f /etc/enigma2/e2sentials/all_channels_data.json; then
    # If file exists, run the picker script
    python /usr/lib/enigma2/python/Plugins/Extensions/KiddaC_Skin_E2sentials/picker.py
else
    # If file does not exist, run the scraper script
    python /usr/lib/enigma2/python/Plugins/Extensions/KiddaC_Skin_E2sentials/scraper.py
fi

exit 0
