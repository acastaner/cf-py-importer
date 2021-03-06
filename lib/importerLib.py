import os
import json
import time
from lib.models.Scenario import Scenario, ScenarioType
import time
import sys


def getPcapFiles(path, scenarioType):
    scenarios = []
    absPath = os.path.abspath(path + os.sep)
    if os.path.exists(absPath) != True:
        print("Provided path is missing, canceling.")
        exit
    for file in os.listdir(path):
        if file.endswith(".pcap") or file.endswith(".har"):
            sourcePath = absPath + os.sep + file
            dstFileName = sanitizeFileName(file)
            dstPath = absPath + os.sep + dstFileName
            # print(dstPath)
            scenario = Scenario()
            try:
                if (os.path.exists(dstPath) != True):
                    os.rename(sourcePath, dstPath)
                scenario.setSourceFilePath(dstPath)
                scenario.setScenarioTypeFromEnum(scenarioType)
                scenarios.append(scenario)
            except:
                print("\tError handling file " + file + ", skipping.")
                print("\\Exception: " + sys.exc_info()[0])
                print("\t\tSource file: " + sourcePath)
                print("\t\tDestination file: " + dstPath)
    return scenarios


def sanitizeFileName(file):
    dstFileName = file
    # API won't accept file with names larger than 50 characters so we slice the file name to 50 (minus the extension size)
    if file.__len__() > 50:
        ext = os.path.splitext(file)[1]
        base = os.path.splitext(file)[0]
        maxlength = 50 - ext.__len__()
        dstFileName = base[:maxlength] + ext

    # API won't accept some characters, so swapping those with a dot like the CF GUI does
    dstFileName = dstFileName.replace("-", ".")
    dstFileName = dstFileName.replace("^", ".")
    dstFileName = dstFileName.replace("+", ".")
    dstFileName = dstFileName.replace("$", ".")
    # print("DEBUG: dstFileName = " + dstFileName)

    return dstFileName


def uploadFile(cfClient, scenario):
    file = scenario.sourceFilePath
    print("\tSource: " + file)
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

    if (scenario.sourceFileUploaded != True):
        return scenario

    # Wait up to 10 secs for file processing to complete
    completed = False
    count = 1
    print("\tWaiting for file processing... ", end="")
    while completed != True:
        if count >= 11:
            # We waited 10 seconds, if not completed yet, we won't attempt to create the scenario
            completed = True
            print("\tFile processing timed out, exiting.")
            return scenario
        fileDetailsResponse = cfClient.getFile(scenario.sourceFileId)
        if(fileDetailsResponse.status_code == 200):
            if (json.loads(fileDetailsResponse.text)["contentType"] == "pcap"):
                if (json.loads(fileDetailsResponse.text)["info"]["status"] == "completed"):
                    print("Done.")
                    completed = True
            elif (json.loads(fileDetailsResponse.text)["completed"] == True):
                print("Done.")
                completed = True
        time.sleep(1)
        count += 1
    if (scenario.sourceFileUploaded == False):
        moveFailedImportFile(scenario.sourceFilePath)
    # Create actual scenario
    print("\tCreating scenario... ", end="")
    if (scenario.scenarioType.name == "ATTACK"):
        scenario = createAttackScenario(cfClient, scenario)
    elif (scenario.scenarioType.name == "APPLICATION"):
        scenario = createApplicationScenario(cfClient, scenario)
    elif (scenario.scenarioType == ScenarioType.MALWARE):
        scenario = createMalwareScenario(cfClient, scenario)
    else:
        print("Scenario type not defined, cancelling")
        moveFailedImportFile(scenario.sourceFilePath)
        scenario.scenarioCreated = False
        return scenario

    if scenario.scenarioCreated:
        moveSuccessImportFile(scenario.sourceFilePath)
    else:
        moveFailedImportFile(scenario.sourceFilePath)
    return scenario


def getScenarioIds(scenarios):
    scenarioIds = []
    for scenario in scenarios:
        entry = {'id': scenario.scenarioId}
        scenarioIds.append(entry)
    return scenarioIds


def createAttackProfile(cfClient, scenarioIds):
    date = time.strftime("%c", time.localtime())
    name = "Attacks - " + date
    description = "Attacks automatically imported on " + date
    createAttackProfileResponse = cfClient.createAttackProfile(
        name, description, scenarioIds)
    if createAttackProfileResponse.status_code == 201:
        print("Created Attack Profile: " + name)
    else:
        print("Error creating Attack Profile: " + name)
        print(str(createAttackProfileResponse.content))


def createApplicationProfile(cfClient, scenarioIds):
    date = time.strftime("%c", time.localtime())
    name = "Applications - " + date
    description = "Applications automatically imported on " + date
    createApplicationProfile = cfClient.createApplicationProfile(
        name, description, scenarioIds)
    if createApplicationProfile.status_code == 201:
        print("Created Application Profile: " + name)
    else:
        print("Error creating Application Profile: " + name)
        print(str(createApplicationProfile.content))


def createMalwareProfile(cfClient, scenarioIds):
    date = time.strftime("%c", time.localtime())
    name = "Malwares - " + date
    description = "Malwares automatically imported on " + date
    createMalwareProfile = cfClient.createMalwareProfile(
        name, description, scenarioIds)
    if createMalwareProfile.status_code == 201:
        print("Created Malware Profile: " + name)
    else:
        print("Error creating Malware Profile: " + name)
        print(str(createMalwareProfile.content))


def createScenarios(cfClient, scenarios):
    scenariosCount = scenarios.__len__()
    createdScenarios = []
    i = 1
    for scenario in scenarios:
        print("Creating scenario " + str(i) + "/" + str(scenariosCount))
        createdScenario = createScenario(cfClient, scenario)
        createdScenarios.append(createdScenario)
        i += 1
    createdScenarios = cleanUpScenarios(cfClient, createdScenarios)
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
                print("\t\tUnused file deleted from Controller.")
        elif (scenario.sourceFileUploaded == False and os.path.exists(scenario.sourceFilePath)):
            moveFailedImportFile(scenario.sourceFilePath)
    cleaned = scenarios.__len__() - sanitizedList.__len__()
    print("Cleaned scenarios/files: " + str(cleaned))
    return sanitizedList


def moveFailedImportFile(path):
    if(os.path.exists(path) == True):
        try:
            os.rename(path, path.replace(
                "to_process", "failed_import"))
        except:
            print("\t\tError moving file after failed import: ")
            print("\t\t" + path)


def moveSuccessImportFile(path):
    if(os.path.exists(path) == True):
        try:
            os.rename(path, path.replace(
                "to_process", "processed"))
        except:
            print("\t\tError moving file after successful import: ")
            print("\t\t" + path)


def createAttackScenario(cfClient, scenario):
    createdScenarioResponse = cfClient.createAttackScenario(
        scenario.sourceFileId, scenario.sourceFileName, 'Imported Attack Scenario')

    return handleCreatedScenarioResponse(cfClient, createdScenarioResponse, scenario)


def createApplicationScenario(cfClient, scenario):
    createdScenarioResponse = cfClient.createApplicationScenario(
        scenario.sourceFileId, scenario.sourceFileName, 'Imported Application Scenario'
    )
    return handleCreatedScenarioResponse(cfClient, createdScenarioResponse, scenario)


def createMalwareScenario(cfClient, scenario):
    createdScenarioResponse = cfClient.createMalwareScenario(
        scenario.sourceFileId, scenario.sourceFileName, 'Imported Malware Scenario'
    )
    return handleCreatedScenarioResponse(cfClient, createdScenarioResponse, scenario)


def handleCreatedScenarioResponse(cfClient, createdScenarioResponse, scenario):
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
