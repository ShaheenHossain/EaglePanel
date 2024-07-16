Server_IP=$(curl --silent --max-time 30 -4 https://raw.githubusercontent.com/ShaheenHossain/eaglepanel/master/eaglepanel.sh/?ip)
echo "$Server_IP" > "/etc/eaglepanel/machineIP"

