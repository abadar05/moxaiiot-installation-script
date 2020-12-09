#!/usr/bin/env python 3

import sys
import requests
import logging
from colorlog import ColoredFormatter

__author__ = "Amjad B., Andreas R."
__license__ = "MIT"
__version__ = '1.0.0'
__status__ = "beta"

'''
Change log

Date: 09 Dec 2020 
New Feature:
    - Added coloered logs 
    - Enable verbose level 

'''

class Config_BaseClass():
    global logger
    mainFHandler = "Not initiated"
    errorFHandler = "Not initiated"
    
    def __init__(self, args, **kwargs):
        
        self._client = None
        #self._cmd_timeout = None
    
        #self._guiUser = "admin"
        #self._guiPass = "admin@123"
        self._def_Lan2ip = "192.168.4.127"
        
        self._ip_address = None
        self._username = None
        self._password = None
        self._sshPort = None
        self._local_dir = None
        self._remote_dir = None
        self._command = None
        self._command_post = None
        self._command_post1 = None
        self._tv_remote_assignment = None
        self._tv_set_properties = None
   
        self._download_files = None
        self._upload_files = None
        self._download_all = False
        self._upload_all = False

        self._enable_installation = False
        self._enable_post_installation = False
        self._enable_checker = False
        self._retry_count = 1
        self._install_time = 15
         
        self._ext_conf = kwargs.get('conf', None)
        
        self._verbose_level = "default"
        
        #override default logger level if comes via command line
        if args.verbose_level is not None:
            if args.verbose_level == '1':
                self._verbose_level = args.verbose_level
            elif args.verbose_level == '2':
                self._verbose_level = args.verbose_level
            else:
                print("[ERROR] Invalid Verbose Level: {}. Please use -h argument to see usage".format(args.verbose_level)) 
                sys.exit()
        
        # from now we can start to write logs in the file
        # needed to pre-read "ip_address here :/"
        if args.IP is not None:     #override IP from config file if comes via command line
             self._ip_address = args.IP
        elif self._ext_conf["general"]["ip_address"]: 
            self._ip_address = self._ext_conf["general"]["ip_address"]
        self.set_loggingFileHandler(str(self._ip_address)+".log", str(self._ip_address)+'.error.log') # initiate logging to File
        
        logger.debug("Read External Config: {}".format(self._ext_conf))    
         
        self.parse_configuration(args)
           
    
    # Parse config.json file        
    def parse_configuration(self, args):
        
        logger.info("*********** Parse Configuration ***********")
        
        if not self._ext_conf:
            logger.error('Empty configuration!')
            return False          
        
        # continue here 
        if self._ext_conf["general"]["ip_address"]: 
            self._ip_address = self._ext_conf["general"]["ip_address"]
            if args.IP is not None:     #override IP from config file if comes via command line
                 self._ip_address = args.IP
            logger.info("ip_address: {}".format(self._ip_address))

        if self._ext_conf["general"]["username"]: 
            self._username = self._ext_conf["general"]["username"] 
            logger.info("username: {}".format(self._username))
        
        if self._ext_conf["general"]["password"]: 
            self._password = self._ext_conf["general"]["password"] 
            logger.info("password: {}".format(self._password))
           
        if self._ext_conf["general"]["ssh_port"]: 
            self._sshPort = self._ext_conf["general"]["ssh_port"] 
            logger.info("ssh_port: {}".format(self._sshPort))
         
        if self._ext_conf["directory"]["local_dir"]: 
            self._local_dir = self._ext_conf["directory"]["local_dir"] 
            logger.info("local_dir: {}".format(self._local_dir))
        
        if self._ext_conf["directory"]["remote_dir"]: 
            self._remote_dir = self._ext_conf["directory"]["remote_dir"] 
            logger.info("remote_dir: {}".format(self._remote_dir))
        
        if self._ext_conf["directory"]["download_all"]: 
            self._download_all = self._ext_conf["directory"]["download_all"] 
            logger.info("download_all: {}".format(self._download_all))
            
        if self._ext_conf["directory"]["download_files"]:
            self._download_files = self._ext_conf["directory"]["download_files"] 
            logger.info("download_files: {}".format(self._download_files))
        
        if self._ext_conf["directory"]["upload_all"]:
            self._upload_all = self._ext_conf["directory"]["upload_all"] 
            logger.info("upload_all: {}".format(self._upload_all))
            
        if self._ext_conf["directory"]["upload_files"]:
            self._upload_files = self._ext_conf["directory"]["upload_files"] 
            logger.info("upload_files: {}".format(self._upload_files))
         
        if self._ext_conf["linux"]["command"]: 
            self._command = self._ext_conf["linux"]["command"] 
            logger.info("Command: {}".format(self._command))
            
        if self._ext_conf["linux"]["commandPost"]: 
            self._command_post = self._ext_conf["linux"]["commandPost"] 
            logger.info("CommandPost: {}".format(self._command_post))
        
        if self._ext_conf["linux"]["commandPost1"]: 
            self._command_post1 = self._ext_conf["linux"]["commandPost1"] 
            logger.info("CommandPost1: {}".format(self._command_post1))  

        if self._ext_conf["options"]["enable_installation"]: 
            self._enable_installation = self._ext_conf["options"]["enable_installation"] 
            logger.info("enable_installation: {}".format(self._enable_installation)) 
            
        if self._ext_conf["options"]["enable_post_installation"]: 
            self._enable_post_installation = self._ext_conf["options"]["enable_post_installation"] 
            logger.info("enable_post_installation: {}".format(self._enable_post_installation)) 
            
        if self._ext_conf["options"]["enable_checker"]: 
            self._enable_checker = self._ext_conf["options"]["enable_checker"]
            logger.info("enable_checker: {}".format(self._enable_checker)) 
        
        if self._ext_conf["options"]["retry_count"]: 
            self._retry_count = self._ext_conf["options"]["retry_count"]
            logger.info("retry_count: {}".format(self._retry_count)) 
  
        if self._ext_conf["options"]["install_time"]: 
            self._install_time = self._ext_conf["options"]["install_time"]
            logger.info("install_time in minutes: {}".format(self._install_time)) 
            
        if self._ext_conf["options"]["tv_remote_assignment"]: 
            self._tv_remote_assignment = self._ext_conf["options"]["tv_remote_assignment"]
            logger.info("tv_remote_assignment: {}".format(self._tv_remote_assignment)) 
            
        if self._ext_conf["options"]["tv_set_properties"]: 
            self._tv_set_properties = self._ext_conf["options"]["tv_set_properties"]
            logger.info("tv_set_properties: {}".format(self._tv_set_properties)) 
                 
        logger.info("Parse Configuration Successfull! ")
        return True 
    
    # logging configuration
    def set_loggingFileHandler(self, mainlog, errorlog):  
        """
        From now display logs on console in colored output
        """
        global logger
        log_format = '%(asctime)s: %(levelname)s - %(name)s - %(message)s'
      
        # Save full log
        logging.basicConfig(level=logging.DEBUG, datefmt="[%Y-%m-%d %H:%M:%S]", format=log_format, filename=mainlog, filemode = "w")
        
        color_format = ColoredFormatter("%(asctime)s: %(log_color)s %(levelname) - 2s%(reset)s - %(name)s - %(message)s",
            datefmt="[%Y-%m-%d %H:%M:%S]",
            reset = False,
            log_colors={
                'DEBUG':    'cyan',
                'INFO':     'green',
                'WARNING':  'yellow',
                'ERROR':    'red',
                'CRITICAL': 'red',})
        
        logger = logging.getLogger(__name__)
        
        console = logging.StreamHandler()  
        if self._verbose_level == '1':
            console.setLevel(logging.WARN)
            logger.info("Enabled Warning Mode: {}".format(self._verbose_level))
        elif self._verbose_level == '2':
            console.setLevel(logging.DEBUG)
            logger.info("Enabled Debug Mode: {}".format(self._verbose_level))  
        else:
            console.setLevel(logging.INFO)
    
        console.setFormatter(color_format) 
        logging.getLogger('').addHandler(console)
       
        # Save error log
        global errorFHandler
        errorFHandler = logging.FileHandler(errorlog)
        errorFHandler.setLevel(logging.ERROR)
        formatter = logging.Formatter(log_format)
        errorFHandler.setFormatter(formatter)
        logging.getLogger('').addHandler(errorFHandler)   
        
       
    