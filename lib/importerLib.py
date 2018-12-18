import os
import json


def getPcapFiles(path):
    files = []
    if os.path.exists(path) != True:
        print("Provided path is missing, canceling.")
        exit
    for file in os.listdir(path):
        if file.endswith(".pcap"):
            files.append(os.path.abspath(path + os.sep + file))
    return files


def uploadFiles(cfClient, files):
    uploadedFiles = []
    fileCount = files.__len__()
    for file in files:
        i = 1
        print("Uploading file " + str(i) + "/" + str(fileCount))
        # TODO Check that response is 201
        uploadedFiles.append(cfClient.uploadFileMultipart(file))
    return uploadedFiles


def createAttackScenarios(cfClient, attackScenarios):
    createdScenarios = []
    scenarioScount = attackScenarios.__len__()
    for scenario in attackScenarios:
        i = 1
        print("Creating Attack Scenario " + str(i) + "/" +
              str(scenarioScount))
        # print(scenario)
        atkId = json.loads(scenario)['id']
        atkName = 'ATTACK-' + json.loads(scenario)['name']
        # print(atkId)
        # print(atkName)

        # Returns an error 422 at the moment, don't know why
        createdScenarioResponse = cfClient.createAttackScenario(
            atkId, atkName, 'Imported from MassImporter')
        # print(createdScenarioResponse)
        if createdScenarioResponse.status_code == 201:
            print("Ok.")
            createdScenarios.append(createdScenarioResponse.text)
        else:
            print("Fail!")
        return createdScenarios
