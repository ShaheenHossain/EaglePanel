import sys
import subprocess
import shutil
import installLog as logging
import argparse
import os
import shlex
import socket


class unInstallEaglePanel:

    def unInstallEaglePanelRepo(self):

        try:
            copyPath = "/etc/yum.repos.d/eaglepanel.repo"
            os.remove(copyPath)

        except OSError as msg:
            logging.InstallLog.writeToFile(f"{str(msg)} [unInstallEaglePanelRepo]")

    def removeGunicorn(self):
        try:

            os.chdir(self.cwd)

            service = "/etc/systemd/system/gunicorn.service"
            socket = "/etc/systemd/system/gunicorn.socket"
            conf = "/etc/tmpfiles.d/gunicorn.conf"

            os.remove(service)
            os.remove(socket)
            os.remove(conf)

        except BaseException as msg:
            logging.InstallLog.writeToFile(str(msg) + " [removeGunicorn]")

    def removePostfixDovecot(self):
        try:

            command = 'yum -y remove postfix'

            cmd = shlex.split(command)

            res = subprocess.call(cmd)

            shutil.rmtree("/etc/postfix")
            shutil.rmtree("etc/dovecot")


        except OSError as msg:
            logging.InstallLog.writeToFile(str(msg) + " [removePostfixDovecot]")
            return 0
        except ValueError as msg:
            logging.InstallLog.writeToFile(str(msg) + " [removePostfixDovecot]")
            return 0

        return 1

    def removeMysql(self):
        try:

            command = 'yum -y remove mariadb mariadb-server'

            cmd = shlex.split(command)

            res = subprocess.call(cmd)

            shutil.rmtree("/var/lib/mysql")
            os.remove("/etc/my.cnf")

        except OSError as msg:
            logging.InstallLog.writeToFile(str(msg) + " [removeMysql]")
            return 0
        except ValueError as msg:
            logging.InstallLog.writeToFile(str(msg) + " [removeMysql]")
            return 0

        return 1

    def removeLiteSpeed(self):
        try:

            command = 'yum -y remove openlitespeed'

            cmd = shlex.split(command)

            res = subprocess.call(cmd)

            shutil.rmtree("/usr/local/lsws")

        except OSError as msg:
            logging.InstallLog.writeToFile(str(msg) + " [removeLiteSpeed]")
            return 0
        except ValueError as msg:
            logging.InstallLog.writeToFile(str(msg) + " [removeLiteSpeed]")
            return 0
        return 1

    def removeEaglePanel(self):
        try:

           shutil.rmtree("/usr/local/EagleEP")
           os.remove("/usr/local/EagleEP2.tar.gz")
           shutil.rmtree("/etc/eaglepanel")

        except OSError as msg:
            logging.InstallLog.writeToFile(str(msg) + " [removeEaglePanel]")
            return 0
        except ValueError as msg:
            logging.InstallLog.writeToFile(str(msg) + " [removeEaglePanel]")
            return 0
        return 1

    def removePureFTPD(self):
        try:

           command = 'yum -y remove pure-ftpd'

           cmd = shlex.split(command)

           res = subprocess.call(cmd)

           shutil.rmtree("/etc/pure-ftpd")

        except OSError as msg:
            logging.InstallLog.writeToFile(str(msg) + " [removePureFTPD]")
            return 0
        except ValueError as msg:
            logging.InstallLog.writeToFile(str(msg) + " [removePureFTPD]")
            return 0
        return 1

    def removePowerDNS(self):
        try:

           command = 'yum -y remove pdns'

           cmd = shlex.split(command)

           res = subprocess.call(cmd)

           shutil.rmtree("/etc/pdns")

        except OSError as msg:
            logging.InstallLog.writeToFile(str(msg) + " [removePowerDNS]")
            return 0
        except ValueError as msg:
            logging.InstallLog.writeToFile(str(msg) + " [removePowerDNS]")
            return 0
        return 1

    def removePHP(self):
        try:

           command = 'yum -y remove lsphp*'

           cmd = shlex.split(command)

           res = subprocess.call(cmd)

           shutil.rmtree("/etc/pdns")

        except OSError as msg:
            logging.InstallLog.writeToFile(str(msg) + " [removePHP]")
            return 0
        except ValueError as msg:
            logging.InstallLog.writeToFile(str(msg) + " [removePHP]")
            return 0
        return 1



def Main():

    remove = unInstallEaglePanel()

    remove.removeLiteSpeed()
    remove.removeMysql()
    remove.removePostfixDovecot()
    remove.removePureFTPD()
    remove.removeEaglePanel()
    remove.removeGunicorn()
    remove.unInstallEaglePanelRepo()
    remove.removePowerDNS()
    remove.removePHP()

    print("##########################################")
    print("         Successfully Uninstalled         ")
    print("##########################################")



Main()