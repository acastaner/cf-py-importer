#! python3

# Configuration file for cf-py-importer

globalSettings = {
    # FQDN or IP address of the CyberFlood Controller. Do NOT prefix with https://
    "cfControllerAddress": "10.75.231.9",
    "userName": "arnaud.castaner@spirent.com",
    "userPassword": "spirent12!",
    # Should the script delete the PCAPs once completed? If not, they'll be moved to the ./data_processed directories
    "deleteProcessedPcaps": False,
    # How many PCAPs to process within EACH directories (e.g.: a setting of 100 means 100 attacks, 100 malware and 100 apps max)
    "maximumPcapCount": 100,
    "maxThreads": 2,  # How many threads to upload PCAPs in parallel
}
