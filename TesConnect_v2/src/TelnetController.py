#!/usr/bin/env python

#  Copyright (c) 2005, Corey Goldberg
#
#  TelnetController.py is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
 
"""

@author: Corey Goldberg
@copyright: (C) 2005 Corey Goldberg
@license: GNU General Public License (GPL)
"""


import telnetlib
import time
import random
import re


class TelnetController:
        
    """Connect to remote host with TELNET and issue commands.
        
    @ivar host_name: Host name or IP address
    @ivar user_name: User name 
    @ivar password: Password
    @ivar prompt: Command prompt (or partial string matching the end of the prompt)
    @ivar tn: Instance of a telnetlib.Telnet object
    """
        
    def __init__(self, host_name, user_name, password, prompt):
        """
            
        @param host_name: Host name or IP address
        @param user_name: User name 
        @param password: Password
        @param prompt: Command prompt (or partial string matching the end of the prompt)
        """
            
        self.host_name = host_name
        self.user_name = user_name
        self.password = password
        self.prompt = prompt
        self.tn = None
        
        
    def login(self):
        """Connect to a remote host and login.
            
        """
        login_status=False
        try:
            self.tn = telnetlib.Telnet(self.host_name)      
            #self.tn.read_until('Login: ')
            self.tn.read_until("Login:")
            self.tn.write(self.user_name + '\r\n')
            if self.password:
                time.sleep(2)
                self.tn.read_until('Password:',timeout=10)
                self.tn.write(self.password + '\r\n')
            time.sleep(2)
            check_prompt=self.tn.read_very_eager().split()
            if ''.join(check_prompt).find('Login:')!=-1:
                return login_status
            self.tn.write('\r\n')
            self.tn.read_until(self.prompt)
            login_status=True    

        except Exception, e1:
            print e1.__doc__
            print e1.message
            print "error communicating...: " + str(e1)
            login_status=False
            
        return login_status        
        
    def run_command(self, command, flag):
        """Run a command on the remote host.
            
        @param command: Unix command
        @return: Command output
        @rtype: String
        """ 
        self.tn.write(command + '\r\n')
        time.sleep(1)
        response = self.tn.read_until(self.prompt)
        if flag==0:
            return self.__strip_output(command, response)
        else:
            return self.__strip_output_more(command, response)
        '''time.sleep(1)
        response_temp=self.tn.read_very_eager()
        count_ch_double=response_temp.find('##',0,len(response_temp))
        count_ch=response_temp.find(' # ',0,len(response_temp))
        if count_ch_double!=-1:
            response=response_temp.replace(' ##', '')
        if count_ch!=-1:
            response=response_temp.replace(' # ', '')
        else:
            self.tn.write(command + '\r\n')
            time.sleep(2)
            if 'chgver' in command:
                return
            response = self.tn.read_until(self.prompt)
        if flag==0:
            return self.__strip_output(command, response)
        else:
            return self.__strip_output_more(command, response)'''
    
    def logout(self):
        """Close the connection to the remote host.
            
        """
        self.tn.close()
        
        
    def run_atomic_command(self, command):
        """Connect to a remote host, login, run a command, and close the connection.
            
        @param command: Unix command
        @return: Command output
        @rtype: String
        """
        self.login()
        command_output = self.run_command(command)
        self.logout()
        return command_output

        
    def __strip_output(self, command, response):
        """Strip everything from the response except the actual command output.
            
        @param command: Unix command        
        @param response: Command output
        @return: Stripped output
        @rtype: String
        """
        lines = response.splitlines()
        # if our command was echoed back, remove it from the output
        if command in lines[0]:
            lines.pop(0)
        # remove the last element, which is the prompt being displayed again
        lines.pop()
        # append a newline to each line of output
        #print(lines)
        #lines = [item + '\n' for item in lines]
        # join the list back into a string and return it
        return ''.join(lines)
        print(lines)

    def __strip_output_more(self, command, response):
        """Strip everything from the response except the actual command output.
            
        @param command: Unix command        
        @param response: Command output
        @return: Stripped output
        @rtype: String
        """
        lines = response.splitlines()
        # if our command was echoed back, remove it from the output
        if command in lines[0]:
            lines.pop(0)
        # remove the last element, which is the prompt being displayed again
        lines.pop()
        # append a newline to each line of output
        #print(lines)
        lines = [item + '\n' for item in lines]
        # join the list back into a string and return it
        return ''.join(lines)
        print(lines)
