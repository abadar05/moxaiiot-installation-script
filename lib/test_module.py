#!/usr/bin/env python 3

import logging
import os
from lib.ssh_module import SSH_Client

__author__ = "Amjad B."
__license__ = "MIT"
__version__ = '1.0.0'
__status__ = "beta"

class Quality_Check(SSH_Client):
    """
    Note:- This class is appliation specific. However you
           can modify it for your test requirements and needs   
    """
    
    def __init__(self, Config_BaseClass):
        global logger
        logger = logging.getLogger(__name__)
        
        self._ip_address = Config_BaseClass._ip_address
        self._username = Config_BaseClass._username
        self._password = Config_BaseClass._password
        self._sshPort = Config_BaseClass._sshPort
        self._local_dir = Config_BaseClass._local_dir
        self._remote_dir = Config_BaseClass._remote_dir
        self._command = Config_BaseClass._command
        self._command_post = Config_BaseClass._command_post
        self._command_post1 = Config_BaseClass._command_post1
 
        self._download_files = Config_BaseClass._download_files
        self._upload_files = Config_BaseClass._upload_files
        self._download_all = Config_BaseClass._download_all
        self._upload_all = Config_BaseClass._upload_all 

        self._def_Lan2ip = Config_BaseClass._def_Lan2ip 
            
        self._TeamViewerInfoDict = {}   
           
    # return Dict of key value pairs        
    def _read_all_lines(self, readlines):
        """
        This function reads line by line from readlines object in for loop, 
        parse the key value pair and store variables into python dict. 
             
        Input: readlines, object which return from read_log_file() function. 
        
        Return:
        The function returns python dict with key value pair if found, 
        otheriwse return None. 
        """

        if readlines is not None:
            for line in readlines:
                if "Deamon:" in line:         
                    key = line.split(":")[0]
                    value= line.split(":")[1]
                    value = value.rstrip("\n")
                    value = value.replace(' ','')
                
                    logger.debug("****************************************************")
                    logger.debug("TeamViewer IoT Agent Deamon: {}".format([value]))
                    logger.debug("****************************************************")
                    self._TeamViewerInfoDict[key] = value 
                
                if "Status:" in line:         
                    key = line.split(":")[0]
                    value= line.split(":")[1]
                    value = value.rstrip("\n")
                    value = value.replace(' ','')
                
                    logger.debug("****************************************************")
                    logger.debug("TeamViewer IoT Agent Status: {}".format([value]))
                    logger.debug("****************************************************")
                    self._TeamViewerInfoDict[key] = value 

                if "Cloud Connectivity:" in line:         
                    key = line.split(":")[0]
                    value= line.split(":")[1]
                    value = value.rstrip("\n")
                    value = value.replace(' ','')
                
                    logger.debug("****************************************************")
                    logger.debug("TeamViewer IoT Agent Cloud Connectivity: {}".format([value]))
                    logger.debug("****************************************************")
                    self._TeamViewerInfoDict[key] = value     
                
                if "File Transfer:" in line:         
                    key = line.split(":")[0]
                    value= line.split(":")[1]
                    value = value.rstrip("\n")
                    value = value.replace(' ','')
                
                    logger.debug("****************************************************")
                    logger.debug("TeamViewer IoT Agent File Transfer {}".format([value]))
                    logger.debug("****************************************************")
                    self._TeamViewerInfoDict[key] = value 
                
                if "SN:" in line:         
                    key = line.split(":")[0]
                    value= line.split(":")[1]
                    value = value.rstrip("\n")
                    value = value.replace(' ','')
                
                    logger.debug("****************************************************")
                    logger.debug("Device Serial Number {}".format([value]))
                    logger.debug("****************************************************")
                    self._TeamViewerInfoDict[key] = value 
                             
            return self._TeamViewerInfoDict
        else:    
            return None
    
    # return readlines into an array
    def read_log_file(self, file):
        """
        This function read log file and return into an array
        Input: file, absolute path of the file to be read including suffix. Ex: "C:/files/xyz.log"
        """
        try:
            with open(file) as log_file:
                readlines = (log_file.readlines())
                logger.info("Read log info: {}".format(readlines)) 
                return readlines
        except IOError as e:
            logger.error(e)
            return None
    
    # return True if file is present in the remote dir of the gateway 
    def is_file(self, filename, directory):
        """
        This fucntion checks if file is present in the remote server at the given location. 
        When file is found it will be automatically copied on your local machine 
        at the given location defined in config file.
        
        Input: filename, file to be checked including suffix Ex: xyz.log
        Input: directory, dir where file will be check absolute path Ex: /home/moxa/   
        return: True, when file is found
        return: False, when file is not found         
        """
       
        self.init_ssh_client()
        #self.connect_sshserver()
        output = self.connect_sshserver()
        if output != False:
            sftp = self._client.open_sftp()
            getFileDict = {filename: "None"} 
          
            directory = sftp.listdir(directory) 
            logger.debug("Return home dir: {}".format(directory))
        
            for key, value in getFileDict.items():
                if key not in directory:
                    logger.error(" {} Not Found in Remote Directory {}".format(key, self._remote_dir)) 
                    sftp.close()  
                    self.disconnect_sshserver()
                    return False
                else:
                    sftp.get(os.path.join(self._remote_dir, filename), os.path.join(self._local_dir + "\\" + filename))
                    logger.info("******************************************************")
                    logger.info("Download successfully to device! [{}]".format(filename))   
                    logger.info("******************************************************")
                    
                    sftp.close()  
                    self.disconnect_sshserver()
                    return True
        
    # return Ture when all test conditions are verified   
    def test_tv_log(self, file):
        """
        This function compares the actual key values with expected value 
        from the given log file

        Input: file, absolute path of the file to be read including suffix. Ex: "C:/files/xyz.log"
        Return: True, when all if conditions are matched. 
        """        
      
        readlines = self.read_log_file(file)
        TvInfoDict = self._read_all_lines(readlines)
        
        Deamon = None
        Status = None
        CloudConnectivity = None
        FileTransfer = None
        
        for key, value in TvInfoDict.items():
            if  TvInfoDict["Deamon"] == 'Started':
                Deamon = True
            else:
                logger.error("TeamViewer IoT Agent Deamon: {}".format([TvInfoDict["Deamon"]]))
                return False, "Deamon",TvInfoDict["Deamon"]
                
            if TvInfoDict["Status"] == 'Online':
                Status = True
            else:
                logger.error("TeamViewer IoT Agent Status: {}".format([TvInfoDict["Status"]]))
                return False, "Status", TvInfoDict["Status"]
                
            if TvInfoDict["Cloud Connectivity"] == 'Enabled':
                CloudConnectivity = True
            else:
                logger.error("TeamViewer IoT Agent Cloud Connectivity: {}".format([TvInfoDict["Cloud Connectivity"]]))
                return False, "Cloud Connectivity", TvInfoDict["Cloud Connectivity"]
                
            if  TvInfoDict["File Transfer"] == '1':
                FileTransfer = True
            else:
                logger.error("TeamViewer IoT Agent File Transfer: {}".format([TvInfoDict["File Transfer"]]))
                return False, "File Transfer", TvInfoDict["File Transfer"]
                   
        if Deamon and Status and CloudConnectivity and FileTransfer == True:
           return True, None, None
        
