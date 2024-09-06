# Proxler
A discord bot for Proxmox Cluster integration

## Database
A Sqlite3 database needs to be created with a table named USERDATA, with columns (USERID VARCHAR(255), VMID VARINTEGER(255), VNCPORT VARINTEGER(255), NODE VARCHAR(255))
Call it database.db

## Environment Variables
Make a .env file with the following variables:
- CONTROLLERADDR: The ip address or fqdn of the proxmox host or cluster 'controller'
- ROOTPASS: The root password of the proxmox host or cluster 'controller'
- DISCORDSERVER: The name of the discord server to attach this instance of the bot to
- DISCORDTOKEN: The token generated in the discord developer portal
- CHANNELID: The ID of the channel you want the bot to live in

## Python
Make sure to install the modules in requirements.txt and all that good stuff
