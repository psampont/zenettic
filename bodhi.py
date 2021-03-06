#!/usr/bin/python
""" Remotely manage network devices """

__docformat__ = 'epytext en'

######################################################################
## Constants
######################################################################
__version__ = "0.4"

######################################################################
## Imports
######################################################################

from optparse import OptionParser
import string
import logging
import getpass

######################################################################
## Django Initiatlization
######################################################################

from django.core.management import setup_environ
import zenettic.settings

setup_environ(zenettic.settings)

from bodhi.models import Device, History
from bodhi.choices import *
from lib.device import wake_on_lan, shutdown_win, shutdown_nix, ping
from lib.karma import Karma

######################################################################
## Program options
######################################################################
usage = "usage: %prog [options] NIC"
description = "Manage a network device"
version = "%prog " + __version__
parser = OptionParser(usage=usage, version=version, description=description)
parser.add_option("-p", "--ping",
                  action="store_true", dest="ping", default=True,
                  help="Make a ping to the device.")
parser.add_option("-w", "--wol",
                  action="store_true", dest="wol", default=False,
                  help="Wake up the device.")
parser.add_option("-r", "--reboot",
                  action="store_true", dest="reboot", default=False,
                  help="Reboot the device.")
parser.add_option("-s", "--shutdown",
                  action="store_true", dest="shutdown", default=False,
                  help="Shutdown the device.")
parser.add_option("--username",
                  action="store", dest="username",
                  help="Username for shutdown")
parser.add_option("--message",
                  action="store", dest="message",
                  help="A message")
parser.add_option("--timeout",
                  action="store", dest="timeout", type="int",
                  help="An operation timeout in minute.")
parser.add_option("-i", "--history",
                  action="store_true", dest="history", default=False,
                  help="Display history.")
parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose", default=False,
                  help="Print status messages to stdout.")

(options, args) = parser.parse_args()

if len(args) == 0 :
    parser.error("Please specify a NIC.")

# Default timeout = 5 minutes
if options.timeout :
    timeout = options.timeout
else:
    timeout = 5

# Default username is the username of current user
if options.username :
    user = options.username
else :
    user = getpass.getuser()

######################################################################
## Logging & History
######################################################################

if options.verbose :
    log_level=logging.DEBUG
else:
    log_level=logging.WARNING
logging.basicConfig(format='%(levelname)s-%(asctime)s-%(message)s',
            level=log_level,
            datefmt='%H:%M:%S')

hf = Karma(user=user)

######################################################################
## Main
######################################################################

logging.info("Searching devices %s*..." % args[0])
devices = Device.objects.filter(name__istartswith=string.upper(args[0]))

if len(devices) == 0 :
    logging.error("Device not found.")
    exit(1)

for device in devices :
    logging.info("... found devices %s." % device)
    if options.shutdown :
        if (device.shutdown == False) :
            logging.error("This device don't allow the shutdown.")
        else:
            if not options.message :
                message = 'Remote shutdown by %s.' % user
            else :
                message = options.message
            print("Shutdown device : %s" % device.name)
            try :
                if (device.platform == 'linux') :
                    shutdown_nix(device.name, user, msg=message,
                                 timeout=timeout)
                else:
                    shutdown_win(device.name, user, msg=message,
                                 timeout=timeout*60)
            except Exception as e:
                logging.error("Exception %s" % e)
                hf.save(device, 2, 1)
            else:
                hf.save(device, 2, 0, message)
    elif options.reboot :
        if (device.shutdown == False) :
            logging.error("This device don't allow the shutdown.")
        else:
            print("Reboot device : %s" % device.name)
            try :
                if (device.platform == 'linux') :
                    shutdown_nix(device.name, user, msg=options.message,
                                 timeout=timeout, reboot=True)
                else:
                    shutdown_win(device.name, user, msg=options.message,
                                 timeout=timeout*60, reboot=True)
            except Exception as e:
                logging.error("Exception %s" % e)
                hf.save(device, 3, 1)
            else:
                hf.save(device, 3, 0, options.message)
    elif options.wol :
        if (device.wakeup == False) :
            logging.error("This device don't allow the wake up.")
        else:
            print("Booting with mac address : %s" % device.MAC)
            try:
                wake_on_lan(device.MAC)
            except Exception as e:
                logging.error("Exception %s" % e)
                hf.save(device, 1, 1)
            else:
                hf.save(device, 1, 0)
    elif options.history :
        record = History.objects.filter(device=device).latest('timestamp')
        print("%s %s @ %s -> %s " %
              (ACTION_TYPES_CHOICES[record.action][1], record.device.name,
               str(record.timestamp)[:19], RESULTS_CODE[record.result][1]))
    else:
        try:
            isUp = ping(device.name)
        except Exception as e:
            logging.error("Exception %s" % e)
            hf.save(device, 0, 1)
        else:
            hf.save(device, 0, not isUp)
        if isUp :
            print("Device %s is up." % device.name)
        else :
            print("Device %s is down." % device.name)
