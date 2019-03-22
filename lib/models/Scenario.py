from enum import Enum

class ScenarioType(Enum):
    APPLICATION = 1
    ATTACK = 2
    MALWARE = 3
    UNDEFINED = 100

class Scenario:

    def __init__(self):
        self.sourceFilePath = ""
        self.sourceFileName = ""
        self.sourceFileUploaded = False
        self.sourceFileId = ""
        self.scenarioType = ScenarioType.UNDEFINED
        self.scenarioId = ""
        self.scenarioCreated = False

    def setSourceFileName(self, name):
        self.sourceFileName = name

    def setSourceFilePath(self, path):
        assert len(path) >= 1
        self.sourceFilePath = path

    def setSourceFileUploaded(self, uploaded):
        self.sourceFileUploaded = uploaded

    def setSourceFileId(self, id):
        assert len(id) >= 1
        self.sourceFileId = id

    def setScenarioTypeFromEnum(self, scenarioType):
        self.scenarioType = scenarioType

    def setScenarioTypeFromString(self, scenarioType):
        # console.log = "This method isn't recommended. Please use setScenarioTypeFromEnum()"
        if scenarioType == "Application" | "application":
            self.scenarioType = ScenarioType.APPLICATION
        elif (scenarioType == "Attack" | "attack"):
            self.scenarioType = ScenarioType.ATTACK
        elif (scenarioType == "Malware" | "malware"):
            self.scenarioType = ScenarioType.MALWARE
        else:
            self.scenarioType = ScenarioType.UNDEFINED
    
    def setScenarioId(self, id):
        assert len(id) >= 1
        self.scenarioId = id    
