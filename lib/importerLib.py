import os
import json
import time
from lib.models.Scenario import Scenario, ScenarioType


def getPcapFiles(path, scenarioType):
    scenarios = []
    absPath = os.path.abspath(path + os.sep)
    if os.path.exists(absPath) != True:
        print("Provided path is missing, canceling.")
        exit
    for file in os.listdir(path):
        
        if file.endswith(".pcap"):
            scenario = Scenario()
            dstFileName = file.replace("-", ".") # API won't accept dashes, so swapping those with a dot like the CF GUI does
            os.rename(absPath + file, absPath + dstFileName)
            scenario.setSourceFilePath(absPath + dstFileName)
            scenario.setScenarioTypeFromEnum(scenarioType)
            scenarios.append(scenario)
    return scenarios

def uploadFile(cfClient, scenario):
    file = scenario.sourceFilePath
    print("\tUploading... ", end="")
    response = cfClient.uploadFileMultipart(file)
    if response.status_code == 201:
        scenario.setSourceFileId(json.loads(response.text)["id"])
        scenario.setSourceFileName(json.loads(response.text)["name"])
        scenario.setSourceFileUploaded(True)
        print("Done.")
    else:
        print("Error!")
        scenario.setSourceFileUploaded(False)
    return scenario

def createScenario(cfClient, scenario):
    scenario = uploadFile(cfClient, scenario)

    # Wait up to 10 secs for file processing to complete
    completed = False
    count = 1
    print("\tWaiting for file processing... ", end="")
    print(str(count) + "... ", end="")
    time.sleep(1)
    while completed != True:    
        if count >= 11: 
            completed = True  # We waited 10 seconds, if not completed yet, we won't attempt to create the scenario
            print("\tFile processing timed out, exiting.")
            return scenario
        fileDetailsResponse = cfClient.getFile(scenario.sourceFileId)
        if(fileDetailsResponse.status_code == 200):
                if (json.loads(fileDetailsResponse.text)["status"] == "completed"):
                    print("Done.")
                    completed = True        
        count += 1
    # Create actual scenario
    print("\tCreating scenario... ", end="")
    if (scenario.scenarioType.name == "ATTACK"):
        scenario = createAttackScenario(cfClient, scenario)
    #elif (scenario.scenarioType == ScenarioType.APPLICATION):
        # TODO
    #elif (scenario.scenarioType == ScenarioType.MALWARE):
        # TODO
    else:
        print("Scenario type not defined, cancelling")
        return scenario
    return scenario

def createScenarios(cfClient, scenarios):
    scenarioScount = scenarios.__len__()
    createdScenarios = []
    for scenario in scenarios:
        i = 1
        print("Creating scenario " + str(i) + "/" + str(scenarioScount))
        createdScenario = createScenario(cfClient, scenario)
        createdScenarios.append(createdScenario)
        i += 1
    createdScenarios = cleanUpScenarios(cfClient, createdScenarios)
    # TODO: If file uploaded but scenario not created, delete file
    # TODO: Maybe log failures
    return createdScenarios

def cleanUpScenarios(cfClient, scenarios):
    print("Cleaning up scenarios.")
    sanitizedList = []
    for scenario in scenarios:
        if scenario.sourceFileUploaded == True and scenario.scenarioCreated == True:
            sanitizedList.append(scenario)
            moveSuccessImportFile(scenario.sourceFilePath)
        elif (scenario.sourceFileUploaded == True and scenario.scenarioCreated == False):
            response = cfClient.deleteFile(scenario.sourceFileId)
            moveFailedImportFile(scenario.sourceFilePath)
            if (response.status_code == 201):
                print("\tUnused file deleted from Controller.")
        elif (scenario.sourceFileUploaded == False and os.path.exists(scenario.sourceFilePath)):
            moveFailedImportFile(scenario.sourceFilePath)
    cleaned = scenarios.__len__() - sanitizedList.__len__()
    print("\tCleaned scenarios/files: " + str(cleaned))
    return sanitizedList

def moveFailedImportFile(path):
    os.rename(path, path.replace(
        "to_process", "failed_import"))

def moveSuccessImportFile(path):
    os.rename(path, path.replace(
        "to_process", "processed"))

def createAttackScenario(cfClient, scenario):
    createdScenarioResponse = cfClient.createAttackScenario(
        scenario.sourceFileId, 'ATTACK-' + scenario.sourceFileName, 'Imported Attack Scenario')
    if createdScenarioResponse.status_code == 201:
        print("Done.")
        scenario.setScenarioId(json.loads(createdScenarioResponse.text)['id'])
        scenario.scenarioCreated = True
    else:
        print("\tFail! API returned error " +
                  str(createdScenarioResponse.status_code)
                  + ": "
                  + str(createdScenarioResponse.content)
                  )
        scenario.scenarioCreated = False
    print(vars(scenario))
    return scenario

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
