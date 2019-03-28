#! python3

# Author: Arnaud Castaner | arnaud.castaner@oultook.com
# First started: 2018/12/17
# License: MIT

# dependencies: requests

# This program imports PCAP of attacks, malware and applications in the provided Spirent CyberFlood Controller
# This program is NOT officially supported by Spirent

from config import *
from lib.models.CfClient import CfClient
#from CfClient import *
from lib import importerLib
from lib.models.Scenario import Scenario, ScenarioType

import sys
import os

# temp
import json

# TODO: Gather each entry's ID by type
# TODO: Build app/attack/malware profiles with the newly uploaded content
# TODO: Run a CSA test with these profiles

print("Welcome to the CyberFlood Mass PCAP Importer!")
print("Checking for connectivity & credentials...", end=" ")
cfClient = CfClient(globalSettings["userName"],
                    globalSettings["userPassword"],
                    globalSettings["cfControllerAddress"]
                    )
cfClient.generateToken()
if cfClient.isLogged():
    print("success! [" + cfClient.userName + "]")
else:
    print("error! Please check your configuration.")
    sys.exit()
print("Looking for PCAPs to import...")
attacks = importerLib.getPcapFiles(os.path.join('.', 'content', 'to_process', 'attacks'), ScenarioType.ATTACK)
applications = importerLib.getPcapFiles(
    os.path.join('.', 'content', 'to_process', 'applications'), ScenarioType.APPLICATION)
malwares = importerLib.getPcapFiles(
    os.path.join('.', 'content', 'to_process', 'malwares'), ScenarioType.MALWARE)
print("\tAttacks: " + str(attacks.__len__()))
print("\tApplications: " + str(applications.__len__()))
print("\tMalware: " + str(malwares.__len__()))

createdAttackScenarios = importerLib.createScenarios(cfClient, attacks)
createdApplicationScenarios = importerLib.createScenarios(cfClient, applications)
createdMalwareScenarios = importerLib.createScenarios(cfClient, malwares)
totalScenarios = createdAttackScenarios.__len__() +  createdApplicationScenarios.__len__() + createdMalwareScenarios.__len__()
print("Created " + str(totalScenarios) + " scenarios.")
print("(Attacks: " + str(createdAttackScenarios.__len__()) +
      ", Applications: " + str(createdApplicationScenarios.__len__()) + ", Malwares: " + str(createdMalwareScenarios.__len__()) + ")")
