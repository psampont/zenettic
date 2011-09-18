#!/usr/bin/env python

"""
Functions to manage network devices.
"""
__docformat__ = 'epytext en'


######################################################################
## Imports
######################################################################

import socket
import struct
import os
import re
import subprocess

######################################################################
## Logging
######################################################################

import logging

class NullHandler(logging.Handler):
    def emit(self, record):
        pass

h = NullHandler()
logging.getLogger("lib-device").addHandler(h)


######################################################################
## Wake on lan
######################################################################

## {{{ http://code.activestate.com/recipes/358449/ (r3)

def wake_on_lan(MACaddress):
    """
    Wake up a remote device with MACaddress.

    @param MACaddress: The MAC address of the device
    """

    # Check MACaddress format and try to compensate.
    if len(MACaddress) == 12:
        pass
    elif len(MACaddress) == 12 + 5:
        sep = MACaddress[2]
        MACaddress = MACaddress.replace(sep, '')
    else:
        raise ValueError('Incorrect MAC address format')

    # Pad the synchronization stream.
    data = ''.join(['FFFFFFFFFFFF', MACaddress * 20])
    send_data = ''

    # Split up the hex values and pack.
    for i in range(0, len(data), 2):
        send_data = ''.join([send_data,
                             struct.pack('B', int(data[i: i + 2], 16))])

    # Broadcast it to the LAN.
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(send_data, ('<broadcast>', 7))

## end of http://code.activestate.com/recipes/358449/ }}}

######################################################################
## Shutdown of Windows devices
######################################################################

if os.name == 'nt' :

    ## {{{ http://code.activestate.com/recipes/360649/ (r1)
    # win32shutdown.py

    def shutdown_win(host=None, user=None, passwrd=None, msg=None, timeout=0, force=1, reboot=False):
        """ Shuts down a remote computer, requires NT-BASED OS. """

        import win32api
        import win32con
        import win32netcon
        import win32security
        import win32wnet

        # Create an initial connection if a username & password is given.
        connected = 0
        if user and passwrd:
            try:
                win32wnet.WNetAddConnection2(win32netcon.RESOURCETYPE_ANY, None,
                                             ''.join([r'\\', host]), None, user,
                                             passwrd)
            # Don't fail on error, it might just work without the connection.
            except:
                pass
            else:
                connected = 1
        # We need the remote shutdown or shutdown privileges.
        p1 = win32security.LookupPrivilegeValue(host, win32con.SE_SHUTDOWN_NAME)
        p2 = win32security.LookupPrivilegeValue(host,
                                                win32con.SE_REMOTE_SHUTDOWN_NAME)
        newstate = [(p1, win32con.SE_PRIVILEGE_ENABLED),
                    (p2, win32con.SE_PRIVILEGE_ENABLED)]
        # Grab the token and adjust its privileges.
        htoken = win32security.OpenProcessToken(win32api.GetCurrentProcess(),
                                               win32con.TOKEN_ALL_ACCESS)
        win32security.AdjustTokenPrivileges(htoken, False, newstate)
        win32api.InitiateSystemShutdown(host, msg, timeout, force, reboot)
        # Release the previous connection.
        if connected:
            win32wnet.WNetCancelConnection2(''.join([r'\\', host]), 0, 0)

    ## end of http://code.activestate.com/recipes/360649/ }}}
else:
    def shutdown_win(hostname, user=None, passwd=None, msg=None, timeout=0, force=False, reboot=False):
         """
         Shutdown the device 'hostname'

         @param hostname: The hostname of the device to shutdown
         @param user: An administrator of the machine
         @param passwd: The administrator password
         @param msg: The message to display on the remote computer
         @param timeout: The delay in second before making the shutdown
         @param force: If True, the user can't cancel the shutdown
         @param reboot: If True, the device is restarted after the shutdown
         @result: Command line result
         """

         command = "net rpc shutdown -I %s -U %s" % (hostname, user)
         if passwd :
             command = command + '%' + passwd
         if force :
             command = command + ' -f'
         if reboot :
             command = command + ' -r'
         if msg :
             command = command + ' -C ' + msg
         if timeout > 0 :
             command = command + ' -t ' + str(timeout)
         logging.debug(command)

         subprocess.Popen([command], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()

######################################################################
## Shutdown of Linux devices
######################################################################

def shutdown_nix(hostname, user=None, passwd=None, msg=None, timeout=0, reboot=False):
    """
    Shutdown the device 'hostname'

    @param hostname: The hostname of the device to shutdown
    @param user: An administrator of the machine
    @param passwd: The administrator password
    @param msg: The message to display on the remote computer
    @param timeout: The delay in minute before making the shutdown
    @param force: If True, the user can't cancel the shutdown
    @param reboot: If True, the device is restarted after the shutdown
    @result: Command line result
    """

    command = "ssh %s@%s shutdown" % (user, hostname)
    if reboot :
        command = command + ' -r'
    else:
        command = command + ' -h'
    command = command + " %s" % timeout
    if msg:
        command = command + " " + msg

    logging.debug(command)
    subprocess.Popen([command], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()

######################################################################
## Ping
######################################################################

def ping(hostname):
    """
    Ping the device 'hostname'

    @param hostname: The hostname of the device to ping
    @result: True if host is online
    """

    command = "ping -c 3 -i 0.3 %s" % (hostname)
    logging.debug(command)
    std = subprocess.Popen([command], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()
    logging.debug("stdout= " + std[0])
    logging.debug("stderr= " + std[1])
    result = std[0]

    return re.search('3 received', result)
