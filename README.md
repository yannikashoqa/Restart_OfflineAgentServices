# Restart_OfflineAgentServices
Restart the Deep Security Agent services if they show as Offline in the Deep security Console

FEATURES
The ability to identify if the Deep security Agent is :
- Installed
- Running
- Failing to extract local configuration
- Listening on port 4118
- Activated
- Status as shown on the Deep Security Manager

Restart the Agent if:
- Stopped
- Not listening to port 4118
- reported as offline by the Deep Security Manager

Activate the Agent if it is not activated or failing to extract the local configuration

Tested Platforms:
- Redhat 6, 7
- Centos 6, 7
- Ubuntu
- Amazon Linux 1, 2

REQUIREMENTS:
- Root privileges
- Script requires python 2.6, 2.7
- Create a DS-Config.json in the same folder with the following content:
{
    "MANAGER": "app.deepsecurity.trendmicro.com",
    "PORT": "443",
    "APIKEY" : ""
    "ACTIVATION_URL" : "dsm://agents.deepsecurity.trendmicro.com:443/",
    "TENANT_ID" : "",
    "TOKEN" : ""
}
