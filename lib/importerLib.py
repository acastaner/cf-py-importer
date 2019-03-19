import os
import json
import time


def getPcapFiles(path):
    files = []
    absPath = os.path.abspath(path + os.sep)
    if os.path.exists(absPath) != True:
        print("Provided path is missing, canceling.")
        exit
    for file in os.listdir(path):
        if file.endswith(".pcap"):
            dstFileName = file.replace("-", ".") # API won't accept dashes, so swapping those with a dot like the CF GUI does
            os.rename(absPath + file, absPath + dstFileName)
            files.append(absPath + dstFileName)
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
        print(file)
        response = cfClient.uploadFileMultipart(file)
        if response.status_code == 201:
            uploadedFiles.append(response.text)
            print("\tDone.")
            os.rename(file, file.replace("to_process", "processed"))
            i += 1
        else:
            print("\tFile failed uploading")
            os.rename(file, file.replace("to_process", "failed_import"))
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
        time.sleep(1)
    print("All files finished processing.")
    return completedFiles


def createAttackScenarios(cfClient, attackScenarios):
    createdScenarios = []
    scenarioScount = attackScenarios.__len__()
    for scenario in attackScenarios:
        i = 1
        print("Creating Attack Scenario " + str(i) + "/" +
              str(scenarioScount))
        createdScenarioResponse = cfClient.createAttackScenario(
            json.loads(scenario)['id'], 'ATTACK-' + json.loads(scenario)['name'], 'Imported Attack Scenario')
        if createdScenarioResponse.status_code == 201:
            print("\tOk.")
            createdScenarios.append(createdScenarioResponse.text)
        else:
            print("\tFail! API returned error " +
                  str(createdScenarioResponse.status_code)
                  + ": "
                  + str(createdScenarioResponse.content)
                  )
        i += 1
    return createdScenarios


def createApplicationScenarios(cfClient, applicationScenarios):
    createdScenarios = []
    scenarioCount = applicationScenarios.__len__()
    for application in applicationScenarios:
        i = 1
        print("Creating Application Scenario " +
              str(i) + "/" + str(scenarioCount))

        createdScenarioResponse = cfClient.createApplicationScenario(
            json.loads(application)['id'],
            'APP-' + json.loads(application)['name'],
            'Imported Application Scenario')
        if createdScenarioResponse.status_code == 201:
            print("\tOk.")
            createdScenarios.append(createdScenarioResponse.text)
        else:
            print("\tFail! API returned error "
                  + str(createdScenarioResponse.status_code)
                  + ": "
                  + str(createdScenarioResponse.content)
                  )
        i += 1
    return createdScenarios
