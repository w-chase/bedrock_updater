

#
#   Minecraft Bedrock Linux Server v. 0.1
#   A script for automatically downloading and installing the latest version of Minecraft Bedrock Edition on an ubuntu 20.04 server 
#
#   Author: Chase W
#
#   Python 3.10.2
# 
#
#   ***COMMENTS AND TO DO"S ****
#   1. Need to fine tune exception checking and review for any infite loops if an error does occur.
#   2. Add in commands to build the file structure 
#   3. Clean up and smooth out code to make it more readable and concise
#   4. Create a dependencies package

# Imports
import time
import requests
import subprocess
from requests_html import HTMLSession
from datetime import datetime
from zipfile import ZipFile


def logging(log_entry):
#   Logging function, appends to the server_update_log.txt or creates the file if not found
    timestamp = datetime.utcnow()
    log_file = open("~/minecraft-server/_logs/server_update_log.txt", "r+")
    log_file.write("\n" + str(timestamp) + "    " + str(log_entry))
    log_file.close()



def term_cmds(cmd):
#   Uses the subperocess module to input and run terminal commands from within the python script
#   ref: https://docs.python.org/3/library/subprocess.html
    try:
        subprocess.run(cmd)
    except:
        logging("Tried to perform" + cmd + " and it failed")



# This section scrapes Minecraft Website for the link to the Server.
session = HTMLSession()
request = session.get('https://www.minecraft.net/en-us/download/server/bedrock')
response = request.status_code
data = request.html.links

def linkfinder():
#   This uses the information saved in the variable "data" and iterates through looking for the string containing "bin-linux" 
#   it then returns the link for use outside the function.
    for link in data:
        if "bin-linux" in link:
            serverLink = link
    return serverLink


# Converting the link from a URL to a string and stripping all but the file name to check versions
newVersion = str(linkfinder()).replace("-","_").rstrip(".zip").rsplit("/",1)




def version_file():
#   This  creates/opens a file that will contain the new version of the server for use in checking against upcoming updates.
    logging("Updating Version File to new Version")
    vfile = open("~/minecraft-server/server_version.txt","w")
    vfile.write(newVersion[1])
    vfile.close()



def server_download():
#   This function uses requests to download the zip file from the minecraft website
#   and then save it as a file with name "bedrock_server.zip"
    logging("Beginning Download of updated server .zip file...")
    download = requests.get(linkfinder())
    serverFile = open("~/minecraft-server/_Downloads/bedrock_server.zip","wb")
    for chunk in download.iter_content(chunk_size=128):
        serverFile.write(chunk)
    serverFile.close()
    logging("... updated server .zip file has been downloaded")
    version_file()



def version_checking():
#   Compares the installed version of the server to the version available online and either exits or downloads the .zip
    try:
        vfile = open("~/minecraft-server/server_version.txt","r")
        oldVersion = vfile.readline()
        vfile.close()
        if newVersion[1] == oldVersion:
            logging("No new Version is available for download \n")
            exit()
        else:
            logging("New Version is available")
            server_download()
    except NameError:
        logging("'server_version.txt' is not found, creating one")
        version_file()
    except:
        logging("something has gone wrong with version checking")
        exit()



def server_installer():
#   Extracts the server from the downloaded .zip file and places it in the proper file location.
    logging("Beginning extraction of server files to /home/minecraft-server/_bedrock-server/")
    with ZipFile('~/minecraft-server/_Downloads/bedrock_server.zip') as serverFile:
        try:
            serverFile.extractall('~/minecraft-server/_bedrock-server')
            logging("Extraction completed, continuing to next step")
        except:
            logging("Something happened while extracting the server files from the .zip file")



def copyconfigs():
#   copies important unique files from the old server to teh new server
    try:
        term_cmds(["mv", "~/minecraft-server/_Backup/worlds/", "~/minecraft/_bedrock-server/worlds/"])
    except:
        logging("Error copying 'world/' file into new server")
    else:
        logging("Copied 'world/' file into new server")

    try:
        term_cmds(["mv", "~/minecraft-server/_Backup/permissions.json", "~/minecraft/_bedrock-server/permissions.json"])
    except:
        logging("Error copying 'permissions.json' into new server")
    else:
        logging("Copied 'permissions.json' into new server")

    try:
        term_cmds(["mv", "~/minecraft-server/_Backup/server.properties", "~/minecraft/_bedrock-server/server.properties"])
    except:
        logging("Error copying 'server.properties' into new server")
    else:
        logging("Copied 'server.properties' into new server")

    try:
        term_cmds(["mv", "~/minecraft-server/_Backup/whitelist.json", "~/minecraft/_bedrock-server/whitelist.json"])
    except:
        logging("Error copying 'whitelist.json' into new server")
    else:
        logging("Copied 'whitelist.json' into new server")

    try:
        term_cmds(["mv", "~/minecraft-server/_Backup/resource_packs/", "~/minecraft/_bedrock-server/resource_packs/"])
    except:
        logging("Error copying 'resource_packs/' into new server")
    else:
        logging("Copied 'resource_packs/' into new server")
    

def main():
    logging("\n<<<------    Beginnning Server updating script    ------>>>")

    #Subprocess module command variables

    stoppingServer = ["sudo", "systemctl", "stop", "minecraft"]
    startingServer = ["sudo", "systemctl", "start", "minecraft"]
    backupServer = ["mv", "~/minecraft-server/_bedrock-server", "~/minecraft-server/_Backup/old_version"]
    setting_exec = ["chmod", "755", "~/minecraft-server/_bedrock-server/bedrock_server"]

    if response == 200:
        linkfinder()
        logging("Website has responded. Link found is " + str(linkfinder()))
        logging("Available version of server is: " + str(newVersion[1]))
        logging("Checking version available online")
        version_checking()
        server_installer()
        logging("Stopping the Minecraft Server")
        term_cmds(stoppingServer)
        time.sleep(30)
        logging("Backing up the old server files to the '_Backup' file")
        term_cmds(backupServer)
        time.sleep(30)
        logging("copying old server configurations to new server")
        copyconfigs()
        time.sleep(60)
        logging("setting executable permissions")
        term_cmds(setting_exec)
        time.sleep(10)
        logging("Attempting to start server")
        term_cmds(startingServer)
        time.sleep(30)
        logging("Pretty sure all is working well. See installer comments for a list of todos \n")


    else:
        logging("Website Response status is: " + response)


main()