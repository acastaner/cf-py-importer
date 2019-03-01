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
        self.__session = requests.session()
        self.__session.verify = False

        # logging.basicConfig()
        # logging.getLogger().setLevel(logging.DEBUG)
        ## requests_log = logging.getLogger("requests.packages.urllib3")
        # requests_log.setLevel(logging.DEBUG)
        ## requests_log.propagate = True

    def generateToken(self):
        response = self.__session.post(self.controllerAddress + '/token',
                                       data={'email': self.userName,
                                             'password': self.userPassword})
        if response.status_code == 201:
            self.__bearerToken = json.loads(response.text)['token']
            self.__session.headers.update(
                {'Authorization': 'Bearer {0}'.format(self.__bearerToken)})
            self.__isLogged = True
            return self.__bearerToken

    def invalidateToken(self):
        return self.__session.delete(
            self.controllerAddress + '/token'
        )

    def isLogged(self):
        return self.__isLogged

    def getFile(self, fileId):
        return self.__session.get(
            self.controllerAddress + '/files/' + fileId
        )

    def downloadFile(self, fileId):
        return self.__session.get(
            self.controllerAddress + '/files/' + fileId + '/download'
        )

    def getFiles(self):
        return self.__session.get(
            self.controllerAddress + '/files'
        )

    def uploadFileMultipart(self, filePath):
        files = {'file': open(filePath, "rb")}
        response = self.__session.post(
            self.controllerAddress + '/files?type=multipart',
            files=files
        )
        return response

    def deleteFile(self, fileId):
        return self.__session.delete(
            self.controllerAddress + '/files' + fileId
        )

    def createAttackScenario(self, fileId, name, description):
        assert len(name) <= 50 >= 1
        assert len(description) <= 280
        response = self.__session.post(
            self.controllerAddress + '/scenarios/attacks',
            data={'fileId': fileId, 'name': name,
                  'description': description}
        )
        return response

    def createApplicationScenario(self, fileId, name, description):
        assert len(name) <= 50 >= 1
        assert len(description) <= 280
        response = self.__session.post(
            self.controllerAddress + '/scenarios/apps',
            data={'fileId': fileId,
                  'name': name,
                  'description': description,
                  'category': 'Miscellaneous'
                  }
        )
        return response
