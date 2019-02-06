from requests.packages.urllib3.exceptions import InsecureRequestWarning
import requests
import json
import pickle
import logging
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class CfClient:

    def __init__(self, userName, userPassword, controllerAddress):
        self.userName = userName
        self.userPassword = userPassword
        self.controllerAddress = "https://" + controllerAddress + "/api/v2"
        self.__bearerToken = ""
        self.__isLogged = False

        #logging.basicConfig()
        #logging.getLogger().setLevel(logging.DEBUG)
        #requests_log = logging.getLogger("requests.packages.urllib3")
        #requests_log.setLevel(logging.DEBUG)
        #requests_log.propagate = True

    def generateToken(self):
        response = requests.post(
            self.controllerAddress + '/token',
            data={'email': self.userName,
                  'password': self.userPassword},
            verify=False,
        )
        if response.status_code == 201:
            self.__bearerToken = json.loads(response.text)['token']
            return self.__bearerToken

    def invalidateToken(self):
        return requests.delete(
            self.controllerAddress + '/token',
            headers={'Authorization': 'Bearer {0}'.format(self.__bearerToken)
                     },
        )

    def login(self):
        response = requests.post(
            self.controllerAddress + '/token',
            data={'email': self.userName,
                  'password': self.userPassword},
            verify=False,
        )
        if response.status_code == 201:
            self.__bearerToken = json.loads(response.text)['token']
            self.__isLogged = True

    def isLogged(self):
        return self.__isLogged

    def getFile(self, fileId):
        return requests.get(
            self.controllerAddress + '/files/' + fileId,
            headers={'Authorization': 'Bearer {0}'.format(self.__bearerToken)
                     },
            verify=False,
        )
    
    def downloadFile(self, fileId):
        return requests.get(
            self.controllerAddress + '/files/' + fileId + '/download',
            headers={'Authorization': 'Bearer {0}'.format(self.__bearerToken)
                     },
            verify=False,
        )

    def getFiles(self):
        return requests.get(
            self.controllerAddress + '/files',
            headers={'Authorization': 'Bearer {0}'.format(self.__bearerToken)
                     },
            verify=False,
        )

    def uploadFileMultipart(self, filePath):
        files = {'file': open(filePath, "rb")}
        response = requests.post(
            self.controllerAddress + '/files?type=multipart',
            headers={'Authorization': 'Bearer {0}'.format(self.__bearerToken)
                     },
            files=files,
            verify=False,
        )
        return response

    def deleteFile(self, fileId):
        return requests.delete(
            self.controllerAddress + '/files' + fileId,
            headers={'Authorization': 'Bearer {0}'.format(self.__bearerToken)
                     },
        )

    def createAttackScenario(self, fileId, name, description):
        assert len(name) <= 50 >= 1
        assert len(description) <= 280
        response = requests.post(
            self.controllerAddress + '/scenarios/attacks',
            headers={'Authorization': 'Bearer {0}'.format(self.__bearerToken)
                     },
            data={'fileId': fileId, 'name': name,
                  'description': description},
            verify=False,
        )
        return response
