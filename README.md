# Restart_OfflineAgentServices
Restart the Deep Security Agent services if they show as Offline in the Deep security Console

FEATURES
The ability to identify if the Deep security Agent is :
- Installed
- Running
- Listening on port 4118
- Activated
- Able to run the sendCommand
Restart the Agent if:
- Stopped
- Not listening to port 4118
- reported as offline by the Deep Security Manager

REQUIREMENTS:
- Root privileges
- Script requires python 2.6, 2.7
- Create a DS-Config.json in the same folder with the following content:
{
    "MANAGER": "app.deepsecurity.trendmicro.com",
    "PORT": "443",
    "APIKEY" : ""
}
