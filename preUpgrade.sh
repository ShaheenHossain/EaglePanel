#!/bin/sh

BRANCH_NAME=v$(curl -s https://eaglepanel.net/version.txt | sed -e 's|{"version":"||g' -e 's|","build":|.|g'| sed 's:}*$::')

rm -f /usr/local/eaglepanel_upgrade.sh
wget -O /usr/local/eaglepanel_upgrade.sh https://raw.githubusercontent.com/usmannasir/eaglepanel/$BRANCH_NAME/eaglepanel_upgrade.sh 2>/dev/null
chmod 700 /usr/local/eaglepanel_upgrade.sh
/usr/local/eaglepanel_upgrade.sh
