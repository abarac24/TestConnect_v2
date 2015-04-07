from __future__ import division


import csv
from difflib import Differ
import socket
#from modbus import SlaveRtu_MasterTcp
#import modbus_pr

#import SlaveRtu_MasterTcp


#add logging capability

import modbus_tk
import modbus_tk.defines as cst
import modbus_tk.modbus_tcp as modbus_tcp
import modbus_tk.modbus_rtu as modbus_rtu
import serial
import struct
import time
import sys
import unittest
import TelnetController
import re

logger = modbus_tk.utils.create_logger("udp")


#initialization and open the port
#possible timeout values:
#    1. None: wait forever, block call
#    2. 0: non-blocking mode, return immediately
#    3. x, x is bigger than 0, float allowed, timeout block call
#====serial settings
class Connect:


    def __init__(self):
        self.TestId=''
        self.TestStatus=''
        self.sport=''
        self.comport=''
        self.interface=''
        self.srate=''
        self.sbytesize=''
        self.sparity=''
        self.sstopbits=''
        self.sxonxoff=''
        self.srtscts=''
        self.sdsrdtr=''
        self.host=''
        self.tcport=''
        self.packlength=''
        self.iterations=''
        self.filesend=''
        self.buffer=1024
        self.operationmode=''
        
        iplist = open('properties')
        for ip in iplist.readlines():
            self.host=ip.rstrip()
            self.telnet = TelnetController.TelnetController(host_name = self.host, user_name = 'admin', password = 'admin', prompt = '#')
            self.telnet.login()
       
    def stringTObool(self,val):
        if val=='False':
            return False
        else:
            return True
        
    def timeTOwait(self,baudrate,field):
        bits=len(field)*10
        wait=6
        if baudrate<=bits:
            wait=bits/baudrate+15
        return wait
        
    #serial interpreter
    def serial_interpreter(self,flag,ser):
        if flag==1:
            if self.sbytesize=='8':
                ser.bytesize=serial.EIGHTBITS
            elif self.sbytesize=='7':
                ser.bytesize=serial.SEVENBITS
            elif self.sbytesize=='6':
                ser.bytesize=serial.SIXBITS
            elif self.sbytesize=='5':
                ser.bytesize=serial.FIVEBITS
            if self.sparity=='none':
                ser.parity=serial.PARITY_NONE
            if self.sparity=='odd':
                ser.parity=serial.PARITY_ODD
            if self.sparity=='even':
                ser.parity=serial.PARITY_EVEN
            if self.sstopbits=='1':
                ser.stopbits=serial.STOPBITS_ONE
            if self.sstopbits=='2':
                ser.stopbits=serial.STOPBITS_TWO
        elif flag==0:
            if self.sbytesize==serial.EIGHTBITS:
                self.sbytesize='8'
            elif self.sbytesize==serial.SEVENBITS:
                self.sbytesize='7'
            elif self.sbytesize==serial.SIXBITS:
                self.sbytesize='6'
            elif self.sbytesize==serial.FIVEBITS:
                self.sbytesize='5'
            if self.sparity==serial.PARITY_NONE:
                self.sparity='none'
            if self.sparity==serial.PARITY_ODD:
                self.sparity='odd'
            if self.sparity==serial.PARITY_EVEN:
                self.sparity='even'
            if self.sstopbits==serial.STOPBITS_ONE:
                self.sstopbits='1'
            if self.sstopbits==serial.STOPBITS_TWO:
                self.sstopbits='2'


            
    def setserial(self,sport,srate,sxonxoff,srtscts,sdsrdtr):
        ser = serial.Serial()
        ser.port = sport
        ser.baudrate = srate
        
        self.serial_interpreter(1,ser)
        #ser.timeout = None          #block read
        ser.timeout = 0              #non-block read
        #ser.timeout = 2             #timeout block read
        ser.xonxoff =sxonxoff     #disable software flow control
        ser.rtscts = srtscts     #disable hardware (RTS/CTS) flow control
        ser.dsrdtr = sdsrdtr       #disable hardware (DSR/DTR) flow control
        ser.writeTimeout = 0     #timeout for write
        return ser

    def settcp(self,host,tcport,buffer):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, tcport))
        return s


    def telnetsession(self,comport,srate,sbytesize,interface,sparity,sstopbits,tcpport,operationmode):
        
        vgateway=re.findall('([0-9]+)', comport)
        self.telnet.run_command('set serial '+comport+' '+'baudrate '+srate,0)
        self.telnet.run_command('set serial '+comport+' '+'databits '+sbytesize,0)
        self.telnet.run_command('set serial '+comport+' '+'interface '+interface,0)
        self.telnet.run_command('set serial '+comport+' '+'parity '+sparity,0)
        self.telnet.run_command('set serial '+comport+' '+'stopbits '+sstopbits,0)
        self.telnet.run_command('set vgateway '+''.join(vgateway)+' mode '+operationmode,0)
        self.telnet.run_command('set vgateway '+''.join(vgateway)+' '+operationmode +' localport'+' '+tcpport,0)
        self.telnet.run_command('apply config',0)
        #telnet.run_command('exit',0)
        

    def logger(self,file,stream):
        file_w = open(file, "a")
        file_w.write(stream)
        return file_w
        
        
    def sendreceive(self):
        
        iteration=0
        if self.operationmode=="rawtcpserver":
            count_pckt=0
            count_pct_rcv=0
            count_pct_rcv1=0
            list_time=list()
            list_time1=list()
            d=Differ()
            self.logger('Logger.txt', '  *'*10+'  Test Name: '+self.TestId+'  *'*10+'\n')
            '''self.telnet = TelnetController.TelnetController(host_name = self.host.strip(), user_name = 'admin', password = 'admin', prompt = '#')
            self.telnet.login()
            self.telnet.logout()'''
            self.telnetsession(self.comport, self.srate, self.sbytesize, self.interface, self.sparity, self.sstopbits,self.tcport,self.operationmode)
            s=self.settcp(self.host,int(self.tcport),self.buffer)
            ser=self.setserial(self.sport,int(self.srate),self.stringTObool(self.sxonxoff.lower().capitalize()),self.stringTObool(self.srtscts.lower().capitalize()),self.stringTObool(self.sdsrdtr.lower().capitalize()))
            self.serial_interpreter(0,ser)
            self.logger('Logger.txt', '='*200+'\n'+'\n')
            self.logger('Logger.txt', 'Gateway Operating mode: '+self.operationmode+'\n')
            self.logger('Logger.txt', 'Client COM Port: '+self.sport+'\n')
            self.logger('Logger.txt', 'Device COM Port: '+self.comport+'\n')
            self.logger('Logger.txt', 'Interface: '+self.interface+'\n')
            self.logger('Logger.txt', 'Baudrate: '+self.srate+'\n')
            self.logger('Logger.txt', 'Device IP: '+self.host+'\n')
            self.logger('Logger.txt', 'Device TCP port: '+self.tcport+'\n')
            self.logger('Logger.txt','='*200+'\n')
            try: 
                ser.open()
            except Exception, e:
                print sys.exc_traceback.tb_lineno      
                print "error open serial port: " + str(e)
                exit()
            if ser.isOpen():
                try:
                    ser.flushInput() #flush input buffer, discarding all its contents
                    ser.flushOutput()#flush output buffer, aborting current output    #and discard all that is in buffer
                    while iteration<int(self.iterations):
                        iteration=iteration+1 ## contor send packets
                        filesend= open('filesend.txt')
                        self.logger('Logger.txt','='*200+'\n')
                        self.logger('Logger.txt','Iterations: '+str(iteration)+'\n')
                        self.logger('Logger.txt','='*200+'\n')
                        if self.interface=='loopback':
                            self.logger('Logger.txt','   Write data from serial to tcp   '+'\t'*20+'   Write data from tcp to tcp in loop:   '+'\n')
                        else: self.logger('Logger.txt','   Write data from serial to tcp   '+'\t'*20+'   Write data from tcp to serial:   '+'\n')
                        #self.logger('Logger.txt','='*200+'\n')
                        count_pckt=0
                        count_pct_rcv=0
                        count_pct_rcv1=0
                        for field in filesend.readlines():
                            count_pckt=count_pckt+1
                            send_data=''.join(field).replace('\n','')
                            ser.write(send_data)
                            time_send=time.time()
                            #print("Time send serial to tcp"+str(time_send)+" Write data: "+send_data)
                            #print '\n'
                            ser.flushInput() #flush input buffer, discarding all its contents
                            ser.flushOutput()#flush output buffer, aborting current output 
                            time.sleep(self.timeTOwait(int(self.srate),send_data))
                            data = s.recv(self.buffer)
                            s.close()
                            s=self.settcp(self.host,int(self.tcport),self.buffer)
                            data=data.replace('\n','')
                            time_received=time.time()
                            s.send(send_data.replace('\n', ''))
                            time_send1=time.time()
                            
                            
                            #print("Time send serial to tcp"+str(time_send)+" Write data: "+send_data)
                            #print '\n'
                            time.sleep(self.timeTOwait(int(self.srate),send_data))
                            if self.interface=='loopback':
                                recv_data=s.recv(self.buffer)
                            else:
                                recv_data=ser.read(self.buffer)
        
                            recv_data=recv_data.replace('\n','')
                            if recv_data=='':
                                time.sleep(0.5)
                                recv_data=ser.read(self.buffer)
                                
                            
                            time_recv1=time.time()
                            time_diff1=time_recv1-time_send1
                            #self.logger('Logger.txt',data.replace('\n','')+'\t\t'+recv_data.replace('\n','')+'\n')
                            
                            if data!='':
                                if len(send_data.replace('\n',''))==len(data.replace('\n','')) and send_data.find(data)!=-1 :
                                    count_pct_rcv=count_pct_rcv+1
                            comp_data=list(d.compare(send_data.splitlines(),data.splitlines()))
                            #for item in comp_data:
                            if ''.join(comp_data).rfind('-',0,1)!=-1 or ''.join(comp_data).rfind('+',0,1)!=-1:
                                for i in range(0,len(''.join(send_data)),100):
                                    self.logger('Logger.txt','Send: '+str(count_pckt)+' '+''.join(send_data.splitlines())[i:100+i]+'\n')
                                for i in range(0,len(''.join(data)),100):
                                    self.logger('Logger.txt','Received: '+str(count_pckt)+' '+''.join(data.splitlines())[i:100+i]+'\n')
                            
                                    
                            
                            if recv_data!='':
                                if len(send_data.replace('\n',''))==len(recv_data.replace('\n','')) and send_data.find(recv_data)!=-1:
                                    count_pct_rcv1=count_pct_rcv1+1
                            comp_data=list(d.compare(send_data.splitlines(),recv_data.splitlines()))
                            #for item in comp_data:
                            if ''.join(comp_data).rfind('-',0,1)!=-1 or ''.join(comp_data).rfind('+',0,1)!=-1:
                                for i in range(0,len(''.join(send_data)),100):
                                    self.logger('Logger.txt','\t'*29+'Send: '+str(count_pckt)+' '+''.join(send_data.splitlines())[i:100+i]+'\n')
                                for i in range(0,len(''.join(recv_data)),100):
                                    self.logger('Logger.txt','\t'*29+'Received: '+str(count_pckt)+' '+''.join(recv_data.splitlines())[i:100+i]+'\n')
        
                            time_diff=time_received-time_send
                            list_time.append(round(time_diff,2))
                            list_time1.append(round(time_diff1,2))
                            print '\n'
                            print 'Difference time pkt send/pkt received: '+str(time_diff)
                            print '\n'
                            #time.sleep(2)            
                        loss_pkt=count_pckt-count_pct_rcv
                        loss_pkt1=count_pckt-count_pct_rcv1
                        if count_pct_rcv!=0:
                            ratio_loss=float(loss_pkt)/float(count_pct_rcv)
                        else:
                            ratio_loss=100
                        if count_pct_rcv1!=0:
                            ratio_loss1=float(loss_pkt1)/float(count_pct_rcv1)
                        else:
                            ratio_loss1=100
                        print 'Send pkt: '+str(count_pckt)+' Received pkt: '+str(count_pct_rcv)+' Loss packets: '+str(loss_pkt) 
                        print 'Packet loss ratio is: '+str(round(ratio_loss,2))
                        #print 'Throughput value: '+str(Throughput.getThroughput(self.host))+' Mbps'
                        self.logger('Logger.txt','\n')
                        self.logger('Logger.txt','='*200+'\n')
                        self.logger('Logger.txt','Average time to receive '+self.iterations+' from serial to tcp '+str(round(sum(list_time) / float(len(list_time)),2))+' seconds'+'\t'*11+'Average time to receive '+self.iterations+' from serial to tcp '+str(round(sum(list_time) / float(len(list_time)),2))+' seconds'+'\n')
                        self.logger('Logger.txt','Send pkt: '+str(count_pckt)+' Received pkt: '+str(count_pct_rcv)+' Loss packets: '+str(loss_pkt)+'\t'*16+'Send pkt: '+str(count_pckt)+' Received pkt: '+str(count_pct_rcv1)+' Loss packets: '+str(loss_pkt1)+'\n')
                        self.logger('Logger.txt','Packet loss ratio is: '+str(round(ratio_loss,2))+'%'+'\t'*20+'Packet loss ratio is: '+str(round(ratio_loss1,2))+'%'+'\n')
                        '''self.logger('Logger.txt','Throughput value: '+str(Throughput.getThroughput(self.host))+' Mbps'+'\n')'''
                        #self.logger('Logger.txt','='*200+'\n')
                    ser.close()
                    s.close()

                except Exception, e1:
                    print e1.__doc__
                    print e1.message
                    print "error communicating...: " + str(e1)
                    
        elif self.operationmode=='modbustcpserver':
            while iteration<int(self.iterations):
                iteration=iteration+1 ## contor send packets
                #import SlaveRtu_MasterTcp
                #self.read_testsuite()
                '''self.telnet = TelnetController.TelnetController(host_name = self.host.strip(), user_name = 'admin', password = 'admin', prompt = '#')
                self.telnet.login()
                self.telnet.logout()'''
                self.telnetsession(self.comport, self.srate, self.sbytesize, self.interface, self.sparity, self.sstopbits,self.tcport,self.operationmode)
                host=self.host
                tcpport=self.tcport
                scom=self.sport
                srate=self.srate
                self.logger('Logger.txt', '  *'*10+'  Test Name: '+self.TestId+'  *'*10+'\n')
                self.logger('Logger.txt', '='*200+'\n'+'\n')
                self.logger('Logger.txt', 'Gateway Operating mode: '+self.operationmode+'\n')
                self.logger('Logger.txt', 'Client COM Port: '+self.sport+'\n')
                self.logger('Logger.txt', 'Device COM Port: '+self.comport+'\n')
                self.logger('Logger.txt', 'Interface: '+self.interface+'\n')
                self.logger('Logger.txt', 'Baudrate: '+self.srate+'\n')
                self.logger('Logger.txt', 'Device IP: '+self.host+'\n')
                self.logger('Logger.txt', 'Device TCP port: '+self.tcport+'\n')
                self.logger('Logger.txt','='*200+'\n')
                #logFile=self.logger("modbus_results.txt",'='*200+'\n')
                logFile = open("Logger.txt", "a")
                print "Start Modbus testing"
                print "test"




                #####################################
                class SlaveRtu_MasterTcp(unittest.TestCase):   
                    
                        
                    def setUp(self):     
                        """Start testing using RTU over Tcp"""
                        self.master = modbus_tcp.TcpMaster(host, int(tcpport), 15.0)
                        #self.master = modbus_tcp.TcpMaster("10.117.65.2", 502, 5.0)
                        self.master.set_timeout(15.0)
                        logger.info("master tcp connected")
                        self.server_slave=modbus_rtu.RtuServer(serial.Serial(port=scom, baudrate=int(srate), bytesize=8, parity='N', stopbits=1, timeout=None, xonxoff=False, rtscts=False, dsrdtr=False))
                        self.server_slave.start()
                        logger.info("rtu slave connected")
                        self.slave1 = self.server_slave.add_slave(1)
                        self.slave1.add_block("hr0-100", modbus_tk.defines.HOLDING_REGISTERS, 0, 100)
                        self.slave1.add_block("hr100-100", modbus_tk.defines.HOLDING_REGISTERS, 100, 200)
                        self.slave1.add_block("ai100-50", modbus_tk.defines.ANALOG_INPUTS, 100, 150)
                        self.slave1.add_block("c0-100", modbus_tk.defines.COILS, 0, 100)
                        self.slave1.add_block("di100-1", modbus_tk.defines.DISCRETE_INPUTS, 100, 1)
                        self.slave1.add_block("di200-10", modbus_tk.defines.DISCRETE_INPUTS, 200, 10)
                        self.slave1.add_block("hr1000-1500", modbus_tk.defines.HOLDING_REGISTERS, 1000, 500)
                        self.slave1.add_block("c1000-4000", modbus_tk.defines.COILS, 1000, 3000)
                                
                        self.slave5 = self.server_slave.add_slave(5)
                        self.slave5.add_block("hr0-100", modbus_tk.defines.HOLDING_REGISTERS, 300, 20)
                
                        
                    def testReadHoldingRegisters(self):
                        """read holding register"""
                        slave_2 = self.server_slave.add_slave(2)
                        logger.info(slave_2.add_block("myblock", cst.HOLDING_REGISTERS, 500, 100))
                        logger.info(slave_2.set_values("myblock", 500, range(100))) #write to address 500 the 100 values
                        logger.info("set values to HOLDING_REGISTERS")
                        result=self.master.execute(2, cst.READ_HOLDING_REGISTERS, 500, 100)
                        logger.info(self.master.execute(2, cst.READ_HOLDING_REGISTERS, 500, 100))#read from 
                        
                        self.assertEqual(tuple(range(100)), result,'READ_HOLDING_REGISTERS does not contain the expected values')
                    
                    def testRead100HoldingRegistersOn2Blocks(self):
                        """check that an error is raised where reading on 2 consecutive blocks"""
                        try:
                            self.master.execute(1, modbus_tk.defines.READ_HOLDING_REGISTERS, 50, 100)
                        except modbus_tk.modbus.ModbusError, ex:
                            self.assertEqual(ex.get_exception_code(), 2)
                            return
                        self.assert_(False)
                   
                    def testRead5HoldingRegisters(self):
                        """set the values of 3 registers and let's the master reading 5 values"""
                        self.slave1.set_values("hr0-100", 1, [2, 2, 2])
                        result = self.master.execute(1, modbus_tk.defines.READ_HOLDING_REGISTERS, 0, 5)
                        self.assertEqual((0, 2, 2, 2, 0), result)
                    
                    def testReadOneHoldingRegisters(self):
                        """set the values of 3 registers and let's the master reading 5 values"""
                        self.slave1.set_values("hr0-100", 6, 4)
                        
                        result = self.master.execute(1, modbus_tk.defines.READ_HOLDING_REGISTERS, 6, 1)
                        self.assertEqual((4, ), result)
                
                    def testReadHoldingRegistersOnSlave5(self):
                        """set and read the values of some registers on slave 5"""
                        self.slave5.set_values("hr0-100", 310, (1, 2, 3))
                        
                        result = self.master.execute(5, modbus_tk.defines.READ_HOLDING_REGISTERS, 308, 10)
                        self.assertEqual((0, 0, 1, 2, 3, 0, 0, 0, 0, 0), result)
                    
                    def testReadHoldingRegistersOutOfBlock(self):
                        """read out of block and make sure that the correct exception is raised"""
                        self.assertRaises(modbus_tk.modbus.ModbusError, self.master.execute, 1, modbus_tk.defines.READ_HOLDING_REGISTERS, 300, 10)
                        
                        try:
                            self.master.execute(1, modbus_tk.defines.READ_HOLDING_REGISTERS, 300, 10)
                        except modbus_tk.modbus.ModbusError, ex:
                            self.assertEqual(ex.get_exception_code(), 2)
                            return
                        self.assert_(False)
                
                    def testReadTooManyHoldingRegisters(self):
                        """check than an error is raised when reading too many holding registers"""
                        try:
                            self.master.execute(1, modbus_tk.defines.READ_HOLDING_REGISTERS, 1000, 126)
                        except modbus_tk.modbus.ModbusError, ex:
                            self.assertEqual(ex.get_exception_code(), 3)
                            return
                        self.assert_(False)
                   
                    def testReadAnalogInputs(self):
                        """Test that response for read analog inputs function is ok"""
                        self.slave1.set_values("ai100-50", 120, range(10))
                        result = self.master.execute(1, modbus_tk.defines.READ_INPUT_REGISTERS, 120, 10)
                        self.assertEqual(tuple(range(10)), result)
                        result = self.master.execute(1, modbus_tk.defines.READ_INPUT_REGISTERS, 120, 1)
                        self.assertEqual((0,), result)
                
                    def testReadCoils(self):
                        """Test that response for read coils function is ok"""
                        self.slave1.set_values("c0-100", 0, [0, 1, 1]+[0, 1]*20)
                        result = self.master.execute(1, modbus_tk.defines.READ_COILS, 0, 1)
                        self.assertEqual((0,), result)
                        result = self.master.execute(1, modbus_tk.defines.READ_COILS, 0, 3)
                        self.assertEqual((0,1,1), result)
                        result = self.master.execute(1, modbus_tk.defines.READ_COILS, 0, 8)
                        self.assertEqual(tuple([0, 1, 1]+[0,1]*2+[0]), result)
                        result = self.master.execute(1, modbus_tk.defines.READ_COILS, 0, 9)
                        self.assertEqual(tuple([0, 1, 1]+[0,1]*3), result)
                        result = self.master.execute(1, modbus_tk.defines.READ_COILS, 0, 20)
                        self.assertEqual(tuple([0, 1, 1]+[0,1]*8+[0]), result)
                        result = self.master.execute(1, modbus_tk.defines.READ_COILS, 0, 21)
                        self.assertEqual(tuple([0, 1, 1]+[0,1]*9), result)
                
                    def testReadManyCoils(self):
                        """Test that response for read many coils function is ok"""
                        self.slave1.set_values("c1000-4000", 1000, tuple([0,1]*1000))
                
                        result = self.master.execute(1, modbus_tk.defines.READ_COILS, 1000, 1)
                        self.assertEqual(1, len(result))
                        self.assertEqual((0,), result)
                
                        result = self.master.execute(1, modbus_tk.defines.READ_COILS, 1000, 8)
                        self.assertEqual(8, len(result))
                        self.assertEqual(tuple([0,1]*4), result)
                
                        result = self.master.execute(1, modbus_tk.defines.READ_COILS, 1000, 1999)
                        self.assertEqual(1999, len(result))
                        self.assertEqual(tuple([0,1]*999+[0]), result)
                        
                        result = self.master.execute(1, modbus_tk.defines.READ_COILS, 1000, 2000)
                        self.assertEqual(2000, len(result))
                        self.assertEqual(tuple([0,1]*1000), result)
                
                    def testReadCoilsOutOfBlocks(self):
                        """Test that an error is raised when reading an invalid address"""
                        try:
                            self.master.execute(1, modbus_tk.defines.READ_COILS, 500, 12)
                        except modbus_tk.modbus.ModbusError, ex:
                            self.assertEqual(ex.get_exception_code(), 2)
                            return
                        self.assert_(False)
                        
                    def testReadTooManyCoils(self):
                        """Test that an error is raised when too many coils are read"""
                        try:
                            self.master.execute(1, modbus_tk.defines.READ_COILS, 1000, 2001)
                        except modbus_tk.modbus.ModbusError, ex:
                            self.assertEqual(ex.get_exception_code(), 3)
                            return
                        self.assert_(False)
                
                    def testReadDiscreteInputs(self):
                        """Test that response for read digital inputs function is ok"""
                        result = self.master.execute(1, modbus_tk.defines.READ_DISCRETE_INPUTS, 100, 1)
                        self.assertEqual((0,), result)
                        self.slave1.set_values("di100-1", 100, 1)
                        result = self.master.execute(1, modbus_tk.defines.READ_DISCRETE_INPUTS, 100, 1)
                        self.assertEqual((1,), result)
                        self.slave1.set_values("di200-10", 200, range(8))
                        result = self.master.execute(1, modbus_tk.defines.READ_DISCRETE_INPUTS, 200, 1)
                        self.assertEqual((0,), result)
                        result = self.master.execute(1, modbus_tk.defines.READ_DISCRETE_INPUTS, 200, 3)
                        self.assertEqual((0,1,1), result)
                        result = self.master.execute(1, modbus_tk.defines.READ_DISCRETE_INPUTS, 200, 8)
                        self.assertEqual(tuple([0]+[1]*7), result)
                        result = self.master.execute(1, modbus_tk.defines.READ_DISCRETE_INPUTS, 200, 10)
                        self.assertEqual(tuple([0]+[1]*7+[0]*2), result)
                
                    def testWriteSingleRegisters(self):
                        """Write the values of a single register and check that it is correctly written"""
                        result = self.master.execute(1, modbus_tk.defines.WRITE_SINGLE_REGISTER, 0, output_value=54)
                        self.assertEqual((0, 54), result)
                        self.assertEqual((54,), self.slave1.get_values("hr0-100", 0, 1))
                        
                        result = self.master.execute(1, modbus_tk.defines.WRITE_SINGLE_REGISTER, 10, output_value=33)
                        self.assertEqual((10, 33), result)
                        self.assertEqual((33,), self.slave1.get_values("hr0-100", 10, 1))
                        
                    def testWriteSingleRegistersOutOfBlocks(self):
                        """Check taht an error is raised when writing a register out of block"""
                        try:
                            self.master.execute(1, modbus_tk.defines.WRITE_SINGLE_REGISTER, 500, output_value=11)
                        except modbus_tk.modbus.ModbusError, ex:
                            self.assertEqual(ex.get_exception_code(), 2)
                            return
                        self.assert_(False)
                
                    def testWriteSingleCoil(self):
                        """Write the values of coils and check that it is correctly written"""
                        result = self.master.execute(1, modbus_tk.defines.WRITE_SINGLE_COIL, 0, output_value=1)
                        self.assertEqual((0, int("ff00", 16)), result)
                        self.assertEqual((1,), self.slave1.get_values("c0-100", 0, 1))
                        
                        result = self.master.execute(1, modbus_tk.defines.WRITE_SINGLE_COIL, 22, output_value=1)
                        self.assertEqual((22, int("ff00", 16)), result)
                        self.assertEqual((1,), self.slave1.get_values("c0-100", 22, 1))
                        
                        result = self.master.execute(1, modbus_tk.defines.WRITE_SINGLE_COIL, 22, output_value=0)
                        self.assertEqual((22, 0), result)
                        self.assertEqual((0,), self.slave1.get_values("c0-100", 22, 1))
                            
                    def testWriteSingleCoilOutOfBlocks(self):
                        """Check taht an error is raised when writing a coil out of block"""
                        try:
                            self.master.execute(1, modbus_tk.defines.WRITE_SINGLE_COIL, 500, output_value=1)
                        except modbus_tk.modbus.ModbusError, ex:
                            self.assertEqual(ex.get_exception_code(), modbus_tk.defines.ILLEGAL_DATA_ADDRESS)
                            return
                        self.assert_(False)
                        
                    def testWriteMultipleRegisters(self):
                        """Write the values of a multiple registers and check that it is correctly written"""
                        result = self.master.execute(1, modbus_tk.defines.WRITE_MULTIPLE_REGISTERS, 0, output_value=(54, ))
                        self.assertEqual((0, 1), result)
                        self.assertEqual((54,), self.slave1.get_values("hr0-100", 0, 1))
                        
                        result = self.master.execute(1, modbus_tk.defines.WRITE_MULTIPLE_REGISTERS, 10, output_value=range(20))
                        self.assertEqual((10, 20), result)
                        self.assertEqual(tuple(range(20)), self.slave1.get_values("hr0-100", 10, 20))
                        
                        result = self.master.execute(1, modbus_tk.defines.WRITE_MULTIPLE_REGISTERS, 1000, output_value=range(123))
                        self.assertEqual((1000, 123), result)
                        self.assertEqual(tuple(range(123)), self.slave1.get_values("hr1000-1500", 1000, 123))
                        
                    def testWriteMultipleRegistersOutOfBlocks(self):
                        """Check that an error is raised when writing a register out of block"""
                        try:
                            self.master.execute(1, modbus_tk.defines.WRITE_MULTIPLE_REGISTERS, 500, output_value=(11, 12))
                        except modbus_tk.modbus.ModbusError, ex:
                            self.assertEqual(ex.get_exception_code(), modbus_tk.defines.ILLEGAL_DATA_ADDRESS)
                            return
                        self.assert_(False)
                    '''def testWriteTooManyMultipleRegisters(self):
                        """Check that an error is raised when writing too many registers"""
                        try:
                            self.master.execute(1, modbus_tk.defines.WRITE_MULTIPLE_REGISTERS, 1000, output_value=range(124))
                        except modbus_tk.modbus.ModbusError, ex:
                            self.assertEqual(ex.get_exception_code(), modbus_tk.defines.ILLEGAL_DATA_VALUE)
                            return
                        self.assert_(False)'''
                        
                    def testWriteMultipleCoils(self):
                        """Write the values of a multiple coils and check that it is correctly written"""
                        result = self.master.execute(1, modbus_tk.defines.WRITE_MULTIPLE_COILS, 0, output_value=(1, ))
                        self.assertEqual((0, 1), result)
                        self.assertEqual((1,), self.slave1.get_values("c0-100", 0, 1))
                        
                        result = self.master.execute(1, modbus_tk.defines.WRITE_MULTIPLE_COILS, 10, output_value=[1]*20)
                        self.assertEqual((10, 20), result)
                        self.assertEqual(tuple([1]*20), self.slave1.get_values("c0-100", 10, 20))
                        
                        result = self.master.execute(1, modbus_tk.defines.WRITE_MULTIPLE_COILS, 1000, output_value=[1]*1968)
                        self.assertEqual((1000, 1968), result)
                        self.assertEqual(tuple([1]*1968), self.slave1.get_values("c1000-4000", 1000, 1968))
                
                    def testWriteMultipleCoilsOutOfBlocks(self):
                        """Check that an error is raised when writing a register out of block"""
                        try:
                            self.master.execute(1, modbus_tk.defines.WRITE_MULTIPLE_COILS, 500, output_value=(11, 12))
                        except modbus_tk.modbus.ModbusError, ex:
                            self.assertEqual(ex.get_exception_code(), modbus_tk.defines.ILLEGAL_DATA_ADDRESS)
                            return
                        self.assert_(False)
                
                    '''def testWriteTooManyMultipleCoils(self):
                        """Check that an error is raised when writing too many registers"""
                        try:
                            self.master.execute(1, modbus_tk.defines.WRITE_MULTIPLE_COILS, 1000, output_value=[1]*(int("7B0", 16)+1))
                        except modbus_tk.modbus.ModbusError, ex:
                            self.assertEqual(ex.get_exception_code(), modbus_tk.defines.ILLEGAL_DATA_VALUE)
                            return
                        self.assert_(False)'''
                
                    def testBroadcast(self):
                        """Check that broadcast queries are handled correctly"""
                        self.slave1.add_block("D", modbus_tk.defines.COILS, 5000, 50)
                        self.slave1.add_block("A", modbus_tk.defines.HOLDING_REGISTERS, 5000, 50)
                        
                        self.slave5.add_block("D", modbus_tk.defines.COILS, 5000, 50)
                        self.slave5.add_block("A", modbus_tk.defines.HOLDING_REGISTERS, 5000, 50)
                        
                        self.master.execute(0, modbus_tk.defines.WRITE_MULTIPLE_REGISTERS, 5000, output_value=range(20))
                        time.sleep(1)
                        self.master.execute(0, modbus_tk.defines.WRITE_SINGLE_REGISTER, 5030, output_value=12)
                        time.sleep(0.5)
                        self.master.execute(0, modbus_tk.defines.WRITE_MULTIPLE_COILS, 5000, output_value=tuple([1]*10))
                        time.sleep(0.5)
                        self.master.execute(0, modbus_tk.defines.WRITE_SINGLE_COIL, 5030, output_value=1)
                        time.sleep(0.5)
                        
                        self.assertEqual(self.slave1.get_values("A", 5000, 20), tuple(range(20)))
                        self.assertEqual(self.slave5.get_values("A", 5000, 20), tuple(range(20)))
                        
                        self.assertEqual(self.slave1.get_values("A", 5030, 1), (12,))
                        self.assertEqual(self.slave5.get_values("A", 5030, 1), (12,))
                        
                        self.assertEqual(self.slave1.get_values("D", 5000, 10), tuple([1]*10))
                        self.assertEqual(self.slave5.get_values("D", 5000, 10), tuple([1]*10))
                        
                        self.assertEqual(self.slave1.get_values("D", 5030, 1), (1,))
                        self.assertEqual(self.slave5.get_values("D", 5030, 1), (1,))
                        
                    def testBroadcastReading(self):
                        """Check that broadcast queries are handled correctly"""
                        functions = (modbus_tk.defines.READ_HOLDING_REGISTERS, modbus_tk.defines.READ_COILS,
                                    modbus_tk.defines.READ_INPUT_REGISTERS, modbus_tk.defines.READ_DISCRETE_INPUTS)
                        for fct in functions:
                            self.assertEqual(None, self.master.execute(0, fct, 0, 5))
                            
                    def testInvalidRequest(self):
                        """Check that an error is returned when the request is invalid"""
                        query = self.server_slave._make_query()
                        requests = ((chr(1), 0x81), (chr(3), 0x83), ("", 0x81))
                        for (request_pdu, rc) in requests:
                            request = query.build_request(request_pdu, 1)
                            response = self.server_slave._databank.handle_request(query, request)
                            expected_response = struct.pack(">BB", rc, modbus_tk.defines.SLAVE_DEVICE_FAILURE) 
                            self.assertEquals(expected_response, response)
                            
                    '''def testSeveralClients(self):
                        """check that the slave can serve 15 masters in parallel"""
                
                        masters = [modbus_tcp.TcpMaster("10.117.65.2", 502, 5.0)] * 3
                
                        slave = self.server_slave.add_slave(8)
                
                        q = Queue.Queue()
                
                        slave.add_block("a", modbus_tk.defines.HOLDING_REGISTERS, 0, 100)
                        slave.set_values("a", 0, range(100))
                        
                        time.sleep(1.0)
                        
                        def read_vals(master):
                            try:
                                for i in xrange(100):
                                    result = master.execute(1, modbus_tk.defines.READ_HOLDING_REGISTERS, 0, 100)
                                    if result != tuple(range(100)):
                                        q.put(1)
                                    time.sleep(0.1)
                            except Exception, msg:
                                logger.error(msg)
                                q.put(1)
                        
                        threads = []
                        for m in masters:
                            threads.append(threading.Thread(target=read_vals, args=(m, )))
                        for t in threads: t.start()
                        logger.debug("all threads have been started")
                        for t in threads: t.join()
                        logger.debug("all threads have done")
                        self.assert_(q.empty())'''
                    def testInvalidSlaveId(self):
                        """Check that an error is raised when adding a slave with a wrong id"""
                        slaves = (-5, 0, "", 256, 5600)
                        for s in slaves:
                            self.assertRaises(Exception, self.server_slave.add_slave, s)
                    def testAddSlave(self):
                        """Check that a slave is added correctly"""
                        slaves = range(9, 256)
                        for id in slaves:
                            s = self.server_slave.add_slave(id)
                            self.assert_(str(s).find("modbus_tk.modbus.Slave")>0)
                
                    def testAddAndGetSlave(self):
                        """Check that a slave can be retrieved by id after added"""
                        slaves = range(9, 248)
                        d = {}
                        for id in slaves:
                            d[id] = self.server_slave.add_slave(id)
                        for id in slaves:
                            s = self.server_slave.get_slave(id)
                            self.assert_(s is d[id])
                    
                    def testErrorOnRemoveUnknownSlave(self):
                        """Check that an error is raised when removing a slave with a wrong id"""
                        slaves = range(9, 249)
                        for id in slaves:
                            self.assertRaises(Exception, self.server_slave.remove_slave, id)
                
                    def testAddAndRemove(self):
                        """Add a slave, remove it and make sure it is not there anymore"""
                        slaves = range(9, 248)
                        for id in slaves:
                            self.server_slave.add_slave(id)
                        for id in slaves:
                            self.server_slave.remove_slave(id)
                        for id in slaves:
                            self.assertRaises(Exception, self.server_slave.get_slave, id)
                
                    def testRemoveAllSlaves(self):
                        """Add somes slave, remove all and make sure it there is nothing anymore"""
                        slaves = range(9, 248)
                        for id in slaves:
                            self.server_slave.add_slave(id)
                        self.server_slave.remove_all_slaves()
                        for id in slaves:
                            self.assertRaises(Exception, self.server_slave.get_slave, id)
                
                
                
                
                
                    
                    def tearDown(self):
                        self.master.close()
                        self.server_slave.stop()
                    
              
                suite = unittest.TestLoader().loadTestsFromTestCase(SlaveRtu_MasterTcp)
                unittest.TextTestRunner(stream=logFile,verbosity=2).run(suite)
                logFile.close()
                
                    
                    ###################3

            
                         

    def read_testsuite(self):

    
        testlist  = open('TestSuiteConnect.csv', "rb")
        reader = csv.reader(testlist)
        rownum=0
        class fields():
            id=0
            status=1
            sport=2
            comport=3
            operationmode=4
            interface=5
            srate=6
            sbytesize=7
            sparity=8
            sstopbits=9
            sxonxoff=10
            srtscts=11
            sdsrdtr=12
            #host=13
            tcport=14
            packlength=15
            iterations=16
            filesend=17

        
        for row in reader:
            if rownum==0:
                rownum+=1
                continue        
            else:
                self.TestId=row[fields.id]
                self.TestStatus=row[fields.status]
                if self.TestId.startswith('#')==True:
                    continue
                if 'TRUE' in self.TestStatus: 
                    self.sport=row[fields.sport]
                    self.comport=row[fields.comport]
                    self.operationmode=row[fields.operationmode]
                    self.interface=row[fields.interface]
                    self.srate=row[fields.srate]
                    self.sbytesize=row[fields.sbytesize]
                    self.sparity=row[fields.sparity]
                    self.sstopbits=row[fields.sstopbits]
                    self.sxonxoff=row[fields.sxonxoff]
                    self.srtscts=row[fields.srtscts]
                    self.sdsrdtr=row[fields.sdsrdtr]
                    #self.host=row[fields.host]
                    self.tcport=row[fields.tcport]
                    self.packlength=row[fields.packlength]
                    self.iterations=row[fields.iterations]
                    self.filesend=row[fields.filesend]
                else:
                    continue
                
                self.sendreceive()


                # tcp settings

        
def main():
    file = open('Logger.txt', "w")
    file.close()
    inst=Connect()
    #inst.read_testsuite()
    inst.read_testsuite()
    del inst
    
if __name__ == "__main__": main()
