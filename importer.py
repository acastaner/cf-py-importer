#! python3

# Author: Arnaud Castaner | arnaud.castaner@oultook.com
# First started: 2018/12/17
# License: MIT

# dependencies: requests

# This program imports PCAP of attacks, malware and applications in the provided Spirent CyberFlood Controller
# This program is NOT officially supported by Spirent

from config import *
#from lib.models.CfClient import CfClient
from lib import importerLib
from lib.models.Scenario import Scenario, ScenarioType

import sys
import os

import cyberfloodClient

# temp
import json

# TODO: Gather each entry's ID by type
# TODO: Build app/attack/malware profiles with the newly uploaded content
# TODO: Run a CSA test with these profiles

print("Welcome to the CyberFlood Mass PCAP Importer!")
print("Checking for connectivity & credentials...", end=" ")
cfClient = cyberfloodClient.CfClient(globalSettings["userName"],
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
attacks = importerLib.getPcapFiles(os.path.join(
    '.', 'content', 'to_process', 'attacks'), ScenarioType.ATTACK)
applications = importerLib.getPcapFiles(
    os.path.join('.', 'content', 'processed', 'applications'), ScenarioType.APPLICATION)
print("\tAttacks: " + str(attacks.__len__()))
print("\tApplications: " + str(applications.__len__()))
print("\tMalware: 0")

createdAttackScenarios = importerLib.createScenarios(cfClient, attacks)
print("Created " + str(createdAttackScenarios.__len__()) + " scenarios.")
