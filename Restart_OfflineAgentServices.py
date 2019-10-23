import urllib2 as urllib2
import sys
import time
import os
import json
import subprocess
import socket
from xml.etree import ElementTree as ElementTree

if os.geteuid() != 0:
    print ("This script require root access.  Exiting!")
    sys.exit()

with open("DS-Config.json", "r") as f:
    Config = json.load(f)

Manager = Config["MANAGER"]
Port = Config["PORT"]
api_secret_key = Config["APIKEY"]
Activation_URL = Config["ACTIVATION_URL"]
Tenant_ID = Config["TENANT_ID"]
Token = Config["TOKEN"]

RetryCount = 0

class XmlDictConfig(dict):
    # Refference : https://stackoverflow.com/questions/2148119/how-to-convert-an-xml-string-to-a-dictionary
    def __init__(self, parent_element):
        if parent_element.items():
            self.update(dict(parent_element.items()))
        for element in parent_element:
            if len(element) > 0:
                if len(element) == 1 or element[0].tag != element[1].tag:
                    aDict = XmlDictConfig(element)
                else:
                    aDict = {element[0].tag: XmlListConfig(element)}
                if element.items():
                    aDict.update(dict(element.items()))
                self.update({element.tag: aDict})
            elif element.items():
                self.update({element.tag: dict(element.items())})
            else:
                self.update({element.tag: element.text})

class XmlListConfig(list):
    # Refference : https://stackoverflow.com/questions/2148119/how-to-convert-an-xml-string-to-a-dictionary
    def __init__(self, aList):
        for element in aList:
            if len(element) > 0:
                # treat like dict
                if len(element) == 1 or element[0].tag != element[1].tag:
                    self.append(XmlDictConfig(element))
                # treat like list
                elif element[0].tag == element[1].tag:
                    self.append(XmlListConfig(element))
            elif element.text:
                text = element.text.strip()
                if text:
                    self.append(text)

def Agent_Installed():
    if (os.path.exists('/etc/init.d/ds_agent')):
        print("Agent is installed")
        return True
    else:
        print("Agent is not installed")
        return False 

def Agent_Process_Running():
    output = os.system("ps -A | grep 'ds_agent'")
    if output == 0:
        print("Agent is running")
        return True
    else:
        print("Agent is stopped.")
        return False

def Start_Agent():
    os.system("sudo /etc/init.d/ds_agent start")

def Restart_Agent():
    os.system("sudo /etc/init.d/ds_agent restart")

def Agent_Port_Open():
    result = 1
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex(('127.0.0.1',4118))
    if result == 0:
        print("Agent Port is open")
        sock.close()
        return True
    else:
        print("Agent Port is closed")
        sock.close()
        return False
    
def Agent_GetConfiguration():
    output = os.popen("/opt/ds_agent/sendCommand --get GetConfiguration").read()
    if "Socket reset" in output:
        print ("Agent GetConfiguration Failed")
        return False
    else:
        print ("Agent GetConfiguration OK")
        return True

def exctract_hostID():
    #Add try catch statement
    print ("Extracting Agent Host ID")
    DSA_Configuration_raw = os.popen("/opt/ds_agent/sendCommand --get GetConfiguration").read() # Only works if Agent is running
    DSA_Configuration = DSA_Configuration_raw.split("\n",2)[2]
    DSA_Configuration_XML_root = ElementTree.XML(DSA_Configuration)
    DSA_Configuration_XML_Dict = XmlDictConfig(DSA_Configuration_XML_root)
    AgentConfiguration = DSA_Configuration_XML_Dict.get('AgentConfiguration')  # Generated output is a dictionary
    x = json.dumps(AgentConfiguration) # Need to dump the configuration as a text format
    y = json.loads(x)  # Convert the text to json data format
    HostID = (y['hostID'])
    print (HostID)
    return HostID

def Agent_Activated():
    DSA_AgentStatus = os.popen("/opt/ds_agent/sendCommand --cmd GetAgentStatus").read()
    if ('dsmCertHash' in DSA_AgentStatus):
        print ("Agent is Activated")
        return True
    else:
        print ("Agent is Not Activated")
        return False


def Activate_Agent():    
    Activation_Command = '/opt/ds_agent/dsa_control -a {} "tenantID:{}" "token:{}"'.format(Activation_URL, Tenant_ID, Token)  
    Reset_Status = os.popen("/opt/ds_agent/dsa_control -r").read()
    if ("OK" in Reset_Status):
        print ("Reset Successful")
        print ("Activating Agent...")
        Activation_Status = os.popen(Activation_Command).read()
        print (Activation_Status)
        if ("Command session completed" in Activation_Status):
            print ("Activation Completed")
            return True
        else:
            print ("Activation Failed")
            return False 
    else:
        print("Agent Reset Failed")
        return False


def DSM_Agent_Status():
    API_Path = '/api/computers/'
    DSM_URI = ''.join(['https://',Manager, ':', Port])
    Base_URI = ''.join([DSM_URI,API_Path])
    Computer_URI = ''.join([Base_URI, HostID])

    header = {'api-secret-key' : api_secret_key,
              'api-version' : 'v1',
              'Content-Type' : 'application/json' }

    request = urllib2.Request(Computer_URI, headers=header)
    response =  urllib2.urlopen(request).read().decode()
    data = json.loads(response)
    agentStatusMessages = data['computerStatus']['agentStatusMessages']
    return (agentStatusMessages)

def Main():
    global RetryCount
    if RetryCount > 2:
        sys.exit()
    RetryCount += 1
    if (Agent_Installed()):
        if (Agent_Process_Running()):
            if (Agent_Port_Open()):
                if (Agent_Activated()):
                    if(Agent_GetConfiguration()):
                        global HostID
                        HostID = exctract_hostID()
                        agentStatusMessages = DSM_Agent_Status()
                        if "Offline" in  agentStatusMessages:
                            print ("DSM Agent status is ", agentStatusMessages)
                            Restart_Agent()
                            time.sleep(60)
                            Main()
                        else:
                            print ("DSM Agent status is ", agentStatusMessages)
                    else:
                        print ("Faileed to extract the Agent Configuration")
                        sys.exit()
                else:
                    if (Activate_Agent()):
                        time.sleep(60)
                        Main()
                    else:
                        sys.exit()
            else:
                Restart_Agent()
                time.sleep(60)
                Main()        
        else:
            Start_Agent()
            time.sleep(60)
            Main()
    else:
        sys.exit()

Main()