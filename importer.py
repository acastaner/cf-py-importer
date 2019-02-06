#! python3

# Author: Arnaud Castaner | arnaud.castaner@oultook.com
# First started: 2018/12/17
# License: MIT

# dependencies: requests

# This program imports PCAP of attacks, malware and applications in the provided Spirent CyberFlood Controller
# This program is NOT officially supported by Spirent

from config import *
from lib.models.CfClient import CfClient
from lib import importerLib

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
attacks = importerLib.getPcapFiles(os.path.join('.', 'content', 'attacks'))
print("\tAttacks: " + str(attacks.__len__()))
print("\tApplications: 0")
print("\tMalware: 0")

uploadedAttackFiles = importerLib.uploadFiles(cfClient, attacks)
processedAttackFiles = importerLib.waitForFilesProcessing(
    cfClient, uploadedAttackFiles)
#importerLib.createAttackScenarios(cfClient, processedAttackFiles)
