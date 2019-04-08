#! python3

# Author: Arnaud Castaner | arnaud.castaner@oultook.com
# First started: 2018/12/17
# License: MIT

# dependencies: requests

# This program imports PCAP of attacks, malware and applications in the provided Spirent CyberFlood Controller
# This program is NOT officially supported by Spirent

from config import *
from lib import importerLib
from lib.models.Scenario import ScenarioType

import sys
import os

from cyberfloodClient import CfClient

# TODO: Run a CSA test with these profiles

print("Welcome to the CyberFlood Mass PCAP Importer!")
print("Checking for connectivity & credentials...", end=" ")
cfClient = CfClient(globalSettings["userName"],
                                     globalSettings["userPassword"],
                                     globalSettings["cfControllerAddress"]
                                     )

# Authentication
cfClient.generateToken()
if cfClient.isLogged():
    print("success! [" + cfClient.userName + "]")
else:
    print("error! Please check your configuration.")
    sys.exit()
print("Looking for PCAPs to import...")

# Gathering files
attacks = importerLib.getPcapFiles(os.path.join(
    '.', 'content', 'to_process', 'attacks'), ScenarioType.ATTACK)
applications = importerLib.getPcapFiles(
    os.path.join('.', 'content', 'to_process', 'applications'), ScenarioType.APPLICATION)

malwares = importerLib.getPcapFiles(
    os.path.join('.', 'content', 'to_process', 'malwares'), ScenarioType.MALWARE)
print("\tAttacks: " + str(attacks.__len__()))
print("\tApplications: " + str(applications.__len__()))
print("\tMalware: " + str(malwares.__len__()))

## Scenarios & Profiles creation
# Attacks #
createdAttackScenarios = importerLib.createScenarios(cfClient, attacks)
if createdAttackScenarios.__len__() > 0:
    attackScenarioIds = importerLib.getScenarioIds(createdAttackScenarios)
    importerLib.createAttackProfile(cfClient, attackScenarioIds)
print("Created " + str(createdAttackScenarios.__len__()) + " attack scenarios.")

# Applications #
createdApplicationScenarios = importerLib.createScenarios(
    cfClient, applications)
if createdApplicationScenarios.__len__() > 0:
    applicationScenarioIds = importerLib.getScenarioIds(createdApplicationScenarios)
    importerLib.createApplicationProfile(cfClient, applicationScenarioIds)

# Malwares #
createdMalwareScenarios = importerLib.createScenarios(
    cfClient, malwares)

print("Created " + str(createdMalwareScenarios.__len__()) + " malware scenarios.")
