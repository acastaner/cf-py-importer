# CyberFlood Python Importer
Python script used to import a (more or less) large amount of application, attacks or malware into a Spirent CyberFlood controller.

# Installation
* Install Python 3.x
* Install the `cyberfloodClient` package from pip

  `pip install cyberfloodClient`
  
 Put the PCAPs to be imported into \content\to_process\<subdirectory>. The scenarios will be created based on the subdirectory name : attacks, application or malware.
 
 If a file is successfully imported and the associated scenario created, it will be moved to the `processed` directory. If either operation (file upload or scenario creation) fails, the file will be moved to the `failed_import` directory.

Then you need to specify the information regarding your controller in the `config.py` file.

* `cfControllerAddress`: the IP address (or FQDN) of your CyberFlood Controller
* `userName`: a valid account on the Controller to be used as credential for the script
* `userPassword`: the password matching the username