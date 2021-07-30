#!/usr/bin/env python 3

import sys 
import json
import time
import argparse, logging
from lib.config_module import Config_BaseClass
from lib.ssh_module import SSH_Client
from lib.test_module import Quality_Check

'''
Change log

Date: 2020-11-12 
Modified main() to disable options when ssh connection failed

Date: 2020-11-10 
Modified Logger to show the logging module

Date: 2020-11-07 
Added retry count for ssh connection
Added options in config file with new features to extend tool functionality 
'''

__author__ = "Amjad B., Andreas R."
__license__ = "MIT"
__version__ = '1.0.0'
__status__ = "beta"


logger = logging.getLogger(__name__)

def test_post_installation(file, bc_obj):
    # Post Installation test using only Quality_Check Class
        
    q_check = Quality_Check(bc_obj) 
    logger.info('Register test functions')
    
    # This checks if log file created successfully on Moxa gateway
    result = q_check.is_file(file, bc_obj._remote_dir)
    if result:
        # get serial number
        output = q_check.read_log_file(bc_obj._local_dir + file)
        TvInfoDict = q_check._read_all_lines(output)
        if TvInfoDict is not None:
            for key, value in TvInfoDict.items():
                if  TvInfoDict["SN"]:
                    sn = TvInfoDict["SN"]
    
            status, KEY, VALUE = q_check.test_tv_log(bc_obj._local_dir + file)
            if status == True:
                logger.info("*********************************************************************")
                logger.info("TeamViewer IoT Agent Installed Successfully!")
                logger.info("Result: PASSED! DeviceIP: {} and SN: {}".format(bc_obj._ip_address, sn))
                logger.info("*********************************************************************")
            else:
                logger.error("*********************************************************************")
                logger.error("Result: FAILED! DeviceIP: {} and SN: {} => TeamViewer IoT Agent {}: {}"
                            .format(bc_obj._ip_address, sn, KEY, VALUE))
                logger.error("*********************************************************************")
         
   
def close_terminal(): 
   input('\n Press Enter to close the terminal window:\n\n')
   sys.exit()


def read_ext_config(args):
        """
        Configuration
        """
        config_file = args.config_file
        if args.config_file is None:
             config_file = 'config.json'
        try:
            with open(config_file) as json_data_file:
                cfg_obj = json.load(json_data_file)
                logger.debug("Read External Config: {}".format(cfg_obj)) 
                return cfg_obj
        except IOError as e:
            logger.error(e)


def retry_ssh(client, bc_obj):
    count = 0
    while True:
        output = client.connect_sshserver()
        if output == True:
            return True
            break
        else:
            count += 1
            print("retry_count: ", count)
            if count == bc_obj._retry_count:
                return False
                break
            else:
                continue
            
'''
__author__ = "Christian G., Andreas R."
Process command line parameter
'''
def main_argparse(assigned_args = None):  
    # type: (List)  
    """
    Parse and execute the call from command-line.
    Args:
        assigned_args: List of strings to parse. The default is taken from sys.argv.
    Returns: 
        Namespace list of args
    """
    parser = argparse.ArgumentParser(prog="appcmd", description=globals()['__doc__'], epilog="!!Note: .....")
    parser.add_argument("-c", dest="config_file", metavar="Config File", help="Configuration file to use!")
    parser.add_argument("-ip", dest="IP", metavar="Device IP", type=str, help="Overwrite Device IP!")
    #parser.add_argument("-l", dest="file_level", metavar="File logging", type=int, action="store", default=None, help="Turn on file logging with level.")
    parser.add_argument("-v", "--verbose", dest="verbose_level", default=None, help="Turn on console DEBUG mode [-v 2]")
    parser.add_argument("-V", "--version", action="version", version=__version__) 

    return parser.parse_args(assigned_args)
       
   
def main(assigned_args = None):

    cargs = main_argparse(assigned_args) # parse command line parameter

    obj_ext_configuration = read_ext_config(cargs) # create configuration object which contains all File Information from configuraiton file
    bc_obj = Config_BaseClass(cargs, conf = obj_ext_configuration) # parse configuration file to create related program variables in the configuration_object

    global logger
    logger = logging.getLogger(__name__)
 
    client = SSH_Client(bc_obj)
 
    if bc_obj._enable_installation: 
        logger.info("Uploading required files to the server and Executing commands")
        logger.info("***********************************************************")
        logger.info("************* Executing Installation **********************")
        logger.info("***********************************************************")
        time.sleep(5)
        
        # Upload required files to server and Execute commands
        client.init_ssh_client()
        output = client.connect_sshserver()
        if output == False:
            output_retry_ssh = retry_ssh(client, bc_obj)
            logger.debug("Check Return Status of Retry_SSH Funtion: {}".format(output_retry_ssh))
            
            if output_retry_ssh == False:
                bc_obj._enable_post_installation = False
                bc_obj._enable_checker = False
            else:        
                client.upload_to_server()
                client.execute_cmd(client._command)
                #print("Waiting for teamviewer-iot-agent to come online ...")
                
                for i in range(bc_obj._install_time, 0, -1): 
                    print("Waiting "+str(i)+" minutes. Please wait.")
                    time.sleep(60) # Wait for install time (minutes), defined in config file 
                    
                client.execute_cmd(bc_obj._tv_remote_assignment)     
                client.execute_cmd(bc_obj._tv_set_properties)
                client.disconnect_sshserver()
  
        else:   
            client.upload_to_server()
            client.execute_cmd(client._command)
            #print("Waiting for teamviewer-iot-agent to come online ...")
              
            for i in range(bc_obj._install_time, 0, -1): 
                print("Waiting "+str(i)+" minutes. Please wait.")
                time.sleep(60) # Wait for install time (minutes), defined in config file
            
            client.execute_cmd(bc_obj._tv_remote_assignment)    
            client.execute_cmd(bc_obj._tv_set_properties)
            client.disconnect_sshserver()
            
    if bc_obj._enable_post_installation:
        logger.info("Executing post commands, downloading logs and removed all unwanted files from server")
        logger.info("###########################################################")
        logger.info("########## Executing POST Installation ####################")
        logger.info("###########################################################")
        time.sleep(5)
            
        # Execute post commands, download logs and removed all unwanted files
        client.init_ssh_client()
        output = client.connect_sshserver()
        if output == False:
            output_retry_ssh = retry_ssh(client, bc_obj)
            logger.info("Check Return Status of Retry_SSH Funtion: {}".format(output_retry_ssh))
            
            if output_retry_ssh == False:         
                bc_obj._enable_checker = False
            else:
                client.execute_cmd(client._command_post)
                client.download_from_server()
                client.disconnect_sshserver()
                time.sleep(5) # Wait for 60 sec
        else:
            client.execute_cmd(client._command_post)
            client.download_from_server()
            client.disconnect_sshserver()
            time.sleep(5) # Wait for 60 sec
    
    if bc_obj._enable_checker:
        logger.info("Perform quality checks to verify if teamviewer app is installed properly")
        logger.info("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
        logger.info("$$$$$$$$$$$$$$$$$$ Executing CHECKER $$$$$$$$$$$$$$$$$$$$")
        logger.info("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
        time.sleep(5)
        
        client.init_ssh_client()
        output = client.connect_sshserver()
        if output == False:
            output_retry_ssh = retry_ssh(client, bc_obj)
            logger.debug("Check Return Status of Retry_SSH Funtion: {}".format(output_retry_ssh))   
             
            if output_retry_ssh == True:
                client.execute_cmd(client._command)
                print("")
        else:
            client.execute_cmd(client._command) 
            print("")
        
        #Perform quality checks to verify if teamviewer app is installed properly on Moxa gateway
        for log_file in bc_obj._download_files:
            result_post_install = test_post_installation(log_file, bc_obj)

        if result_post_install != False:

            #Execute the very last commands to delete all remaining items
            client.init_ssh_client()
            output = client.connect_sshserver()
            if output == False:
                output_retry_ssh = retry_ssh(client, bc_obj)
                logger.debug("Check Return Status of Retry_SSH Funtion: {}".format(output_retry_ssh))   
                
                if output_retry_ssh == True:
                    client.execute_cmd(client._command_post1) 
                    print("")
            else:
                client.execute_cmd(client._command_post1) 
                print("")
                
    close_terminal()
    
if __name__ == '__main__':
    main()
