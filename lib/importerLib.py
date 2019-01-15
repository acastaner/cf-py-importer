import os
import json
import time


def getPcapFiles(path):
    files = []
    if os.path.exists(path) != True:
        print("Provided path is missing, canceling.")
        exit
    for file in os.listdir(path):
        if file.endswith(".pcap"):
            files.append(os.path.abspath(path + os.sep + file))
    return files

def getFilesDetail(cfClient, fileIds):
    files = []
    for fileId in fileIds:
        files.append(cfClient.getFile(fileId))
    return files

def uploadFiles(cfClient, files):
    uploadedFiles = []
    fileCount = files.__len__()
    i = 1
    for file in files:
        print("Uploading file " + str(i) + "/" + str(fileCount))
        response = cfClient.uploadFileMultipart(file)
        if response.status_code == 201:
            uploadedFiles.append(response.text)
            print("\tDone.")
            i += 1
        else:
            print("\tFile failed uploading")
            i += 1
    return uploadedFiles

def waitForFilesProcessing(cfClient, files):
    completedFiles = []
    while files.__len__() > 0:
        for file in files:
            fileDetailsResponse = cfClient.getFile(json.loads(file)["id"])
            if(fileDetailsResponse.status_code == 200):
                if (json.loads(fileDetailsResponse.text)["status"] == "completed"):
                    completedFiles.append(fileDetailsResponse.text)
                    files.remove(file)
                #else:
                #    print("file not completed")
                #    print(json.loads(fileDetailsResponse.text)["status"])            
        time.sleep(1)
    return completedFiles

def createAttackScenarios(cfClient, attackScenarios):
    createdScenarios = []
    scenarioScount = attackScenarios.__len__()
    for scenario in attackScenarios:
        i = 1
        print("Creating Attack Scenario " + str(i) + "/" +
              str(scenarioScount))

        createdScenarioResponse = cfClient.createAttackScenario(
            json.loads(scenario)['id'], 'ATTACK-' + json.loads(scenario)['name'], 'Imported from CyberFlood Importer')
        # print(createdScenarioResponse)
        if createdScenarioResponse.status_code == 201:
            print("\tOk.")
            createdScenarios.append(createdScenarioResponse.text)
        else:
            print("\t Fail! API returned error " + str(createdScenarioResponse.status_code))
        i += 1    
    return createdScenarios
