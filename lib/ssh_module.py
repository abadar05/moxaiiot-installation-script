#!/usr/bin/env python 3

import os
import time
import logging
import warnings
from socket import error as socket_error
from lib.config_module import Config_BaseClass

"""
Change log

Date: 2020-12-04 
Modified upload_to_server and download_from_server to handle error when empty file list provided. 

Added default delay (2 sec) in execute_cmd function.  
"""

__author__ = "Amjad B., Andreas R."
__license__ = "MIT"
__version__ = '1.0.0'
__status__ = "beta"


try:
    from paramiko import client
    import paramiko
except ImportError:
    print("paramiko library is not installed")


warnings.filterwarnings(action='ignore',module='.*paramiko.*')


class SSH_Client(Config_BaseClass):

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
 
 
    def init_ssh_client(self):
        """
        This function creates the client oject from the paramiko SSHClient class
        """    
        logger.info("Create SSH Client")        
        self._client = paramiko.SSHClient()  
        self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        return True
        
    
    def connect_sshserver(self):
        """
        This function establish ssh connection to the server 
        
        Return: True, when established successfully, otherwise False
        """
        try:
            logger.info("Connecting to device: " + self._username + "@" + self._ip_address) 
            self._client.connect(hostname=self._ip_address, port= self._sshPort, username=self._username, password=self._password)
            logger.info("Connected successfully to device: " + self._username + "@" + self._ip_address) 
            return True
            
        except paramiko.AuthenticationException:
            logger.error(" Authentication failed. Please verify device credentials")
           
        except socket_error as socket_err:
            logger.error("{}, Device IP: {}, Port: {}".format(socket_err,  self._ip_address, self._sshPort))
            return False
    
    def disconnect_sshserver(self):
        """
        Calling this function will disconnect client from server 
        """
        logger.info("Disconnecting from device: " + self._username + "@" + self._ip_address)  
        self._client.close()
        logger.info("Closed client Connection from device!")
        return True
    
    
    def upload_to_server(self):
        """
        This function copy files from local machine to the remote server 
        
        Flag: when upload_all is True in config file, the function upload all files 
              from local machine directory. In this case, the function ignores the 
              upload_list (upload only specific files) parameter from the config file. 
               
              When upload_all is False in config file, the function first search the file in given location 
              if found, it will be copied to remote directory defined in the config file. 
              If files that being requested for upload not found in the local directory the function raise an error              
        """
        sftp = self._client.open_sftp()
        logger.info("************************")
        logger.info("Start File Uploading...")
        logger.info("************************")    
            
        logger.info("FROM Local Host  : {}".format(self._local_dir))
        logger.info("TO Remote Machine: {}".format(self._remote_dir))
            
        directory = os.listdir(self._local_dir)
        logger.info("Return Local Files: {}".format(directory))
            
        if self._upload_all:
            for filename in directory:
                if not filename.startswith('.'): 
                    sftp.put(os.path.join(self._local_dir + "\\" + filename), os.path.join(self._remote_dir, filename))
                    logger.info("****************************************************")
                    logger.info("Upload successfully to Server! [{}]".format(filename))
                    logger.info("****************************************************")    
        else:
            getFileList = self._upload_files
            if getFileList is not None:
                getFileDict = {key: None for key in getFileList}
                for filename in directory:  
                    if filename in getFileDict:
                        sftp.put(os.path.join(self._local_dir + "\\" + filename), os.path.join(self._remote_dir, filename))
                        logger.info("****************************************************")
                        logger.info("Upload successfully to Server! [{}]".format(filename))
                        logger.info("****************************************************")    
            
                for key, value in getFileDict.items():
                    if key not in directory:
                        logger.error(" {} Not Found in Local Directory {}".format(key, self._local_dir)) 
                            
            sftp.close()
            
    def download_from_server(self):
        """
        This function copy files from remote server to the local machine
        
        Flag: when download_all is True in config file, the function download all files 
              from remote server directory. In this case the function ignores the 
              download_list (download only specific files) parameter from the config file. 
               
              When download_all is False in config file, the function first search the file in given location 
              if found, it will be copied to local directory defined in the config file. 
              If files that being requested for download not found in the remote directory the function raise an error              
        """
        sftp = self._client.open_sftp()
        logger.info("*************************")
        logger.info("Start File Downloading...") 
        logger.info("*************************")
             
        logger.info("FROM Remote Machine: {}".format(self._remote_dir))
        logger.info("TO Local Host      : {}".format(self._local_dir))
             
        directory = sftp.listdir(self._remote_dir)            
        logger.info("Return Server Files: {}".format(directory))
           
        if self._download_all:
            for filename in directory: 
                if not filename.startswith('.'):
                    sftp.get(os.path.join(self._remote_dir, filename), os.path.join(self._local_dir + "\\" + filename))
                    logger.info("******************************************************")
                    logger.info("Download successfully to device! [{}]".format(filename))
                    logger.info("******************************************************")    
        else: 
            getFileList = self._download_files
            if getFileList is not None:
                getFileDict = {key: None for key in getFileList} 
                for filename in directory:  
                    if filename in getFileDict:
                        sftp.get(os.path.join(self._remote_dir, filename), os.path.join(self._local_dir + "\\" + filename))
                        logger.info("******************************************************")
                        logger.info("Download successfully to device! [{}]".format(filename))   
                        logger.info("******************************************************")
            
                for key, value in getFileDict.items():
                    if key not in directory:
                        logger.error(" {} Not Found in Remote Directory {}".format(key, self._remote_dir)) 
                        
            sftp.close()
        
 
    def execute_cmd(self, cmdlist):
        """
        This function execute shell commands one by one in for loop given by cmdlist object. 
        The function runs command with and without sudo. When using sudo system prompt for 
        username and password. This function provides console input automatically without user intervention. 
        The function read the device credentials info from the config file. 
        
        Return: True, when command executed successfully
        """
        transport = self._client.get_transport() 
             
        if cmdlist is not None: 
            for cmd in cmdlist:         
                session = transport.open_session()
                logger.debug("Open Session {}:".format(session))                 
                session.set_combine_stderr(True)
                session.get_pty()
        
                session.exec_command(cmd)
                logger.info("*********************************")
                logger.info("Executing command: {}".format(cmd))
                logger.info("*********************************")
                
                stdin = session.makefile('wb', -1)
                stdout = session.makefile('rb', -1)
       
                stdin.write(self._password + '\n')
                stdin.flush()
                try:
                    standard_output = stdout.read().decode('UTF-8', 'ignore')
                    logger.info(standard_output)
                except UnicodeDecodeError as e:
                    logger.error(e)
                time.sleep(2)
                
            session.close()
            logger.debug("Closed Session {}:".format(session))
            return True
            
        return False

                

       
       




