#!/usr/local/EagleEP/bin/python
import os, sys

sys.path.append('/usr/local/EagleEP')
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "EagleEP.settings")
django.setup()
from inspect import stack
from cli.cliLogger import cliLogger as logger
import json
from plogical.virtualHostUtilities import virtualHostUtilities
import re
from websiteFunctions.models import Websites, ChildDomains
from plogical.dnsUtilities import DNS
import time
import plogical.backupUtilities as backupUtilities
import requests
from loginSystem.models import Administrator
from packages.models import Package
from plogical.mysqlUtilities import mysqlUtilities
from cli.cliParser import cliParser
from plogical.vhost import vhost
from plogical.mailUtilities import mailUtilities
from plogical.ftpUtilities import FTPUtilities
from plogical.sslUtilities import sslUtilities
from plogical.processUtilities import ProcessUtilities
from plogical.backupSchedule import backupSchedule

# All that we see or seem is but a dream within a dream.

def get_eaglepanel_version():
    with open('/usr/local/EagleEP/version.txt') as version:
        version_file = version.read()
        version = json.loads(str(version_file))
    return f"{version['version']}.{version['build']}"


class eaglePanel:

    def printStatus(self, operationStatus, errorMessage):
        data = json.dumps({'success': operationStatus,
                           'errorMessage': errorMessage
                           })
        print(data)

    ## Website Functions

    def createWebsite(self, package, owner, domainName, email, php, ssl, dkim, openBasedir):
        try:
            from random import randint
            externalApp = "".join(re.findall("[a-zA-Z]+", domainName))[:5] + str(randint(1000, 9999))
            phpSelection = 'PHP ' + php

            try:
                counter = 0
                _externalApp = externalApp
                while True:
                    tWeb = Websites.objects.get(externalApp=externalApp)
                    externalApp = '%s%s' % (_externalApp, str(counter))
                    counter = counter + 1
            except BaseException as msg:
                logger.writeforCLI(str(msg), "Error", stack()[0][3])
                time.sleep(2)

            result = virtualHostUtilities.createVirtualHost(domainName, email, phpSelection, externalApp, ssl, dkim,
                                                            openBasedir, owner, package, 0)

            if result[0] == 1:
                self.printStatus(1, 'None')
            else:
                self.printStatus(0, result[1])

        except BaseException as msg:
            logger.writeforCLI(str(msg), "Error", stack()[0][3])
            self.printStatus(0, str(msg))

    def createDomain(self, masterDomain, domainName, owner, php, ssl, dkim, openBasedir, path):
        try:

            complete_path = '/home/' + masterDomain + '/' + path
            phpSelection = 'PHP ' + php

            result = virtualHostUtilities.createDomain(masterDomain, domainName, phpSelection, complete_path, ssl, dkim, openBasedir, owner, 0)

            if result[0] == 1:
                self.printStatus(1, 'None')
            else:
                self.printStatus(0, result[1])

        except BaseException as msg:
            logger.writeforCLI(str(msg), "Error", stack()[0][3])
            self.printStatus(0, str(msg))

    def deleteWebsite(self, domainName):
        try:
            vhost.deleteVirtualHostConfigurations(domainName)
            self.printStatus(1, 'None')

        except BaseException as msg:
            logger.writeforCLI(str(msg), "Error", stack()[0][3])
            print(0)

    def deleteChild(self, childDomain):
        try:

            result = virtualHostUtilities.deleteDomain(childDomain)

            if result[0] == 1:
                self.printStatus(1, 'None')
            else:
                self.printStatus(0, result[1])

        except BaseException as msg:
            logger.writeforCLI(str(msg), "Error", stack()[0][3])
            print(0)

    def listWebsitesJson(self):
        try:

            websites = Websites.objects.all()
            ipFile = "/etc/eaglepanel/machineIP"
            with open(ipFile, 'r') as f:
                ipData = f.read()
            ipAddress = ipData.split('\n', 1)[0]

            json_data = []

            for items in websites:
                if items.state == 0:
                    state = "Suspended"
                else:
                    state = "Active"
                dic = {'domain': items.domain, 'adminEmail': items.adminEmail, 'ipAddress': ipAddress,
                       'admin': items.admin.userName, 'package': items.package.packageName, 'state': state}
                json_data.append(dic)

            final_json = json.dumps(json_data)
            print(final_json)

        except BaseException as msg:
            logger.writeforCLI(str(msg), "Error", stack()[0][3])
            print(0)

    def listWebsitesPretty(self):
        try:
            from prettytable import PrettyTable

            websites = Websites.objects.all()
            ipFile = "/etc/eaglepanel/machineIP"
            f = open(ipFile)
            ipData = f.read()
            ipAddress = ipData.split('\n', 1)[0]

            table = PrettyTable(['ID', 'Domain', 'IP Address', 'Package', 'Owner', 'State', 'Email'])

            for items in websites:
                if items.state == 0:
                    state = "Suspended"
                else:
                    state = "Active"
                table.add_row(
                    [items.id, items.domain, ipAddress, items.package.packageName, items.admin.userName, state,
                     items.adminEmail])
            print(table)

        except BaseException as msg:
            logger.writeforCLI(str(msg), "Error", stack()[0][3])
            print(0)

    def changePHP(self, virtualHostName, phpVersion):
        try:

            phpVersion = 'PHP ' + phpVersion

            confPath = virtualHostUtilities.Server_root + "/conf/vhosts/" + virtualHostName
            completePathToConfigFile = confPath + "/vhost.conf"

            result = vhost.changePHP(completePathToConfigFile, phpVersion)

            if result[0] == 1:
                self.printStatus(1, 'None')
            else:
                self.printStatus(0, result[1])

        except BaseException as msg:
            logger.writeforCLI(str(msg), "Error", stack()[0][3])
            self.printStatus(0, str(msg))

    def changePackage(self, virtualHostName, packageName):
        try:
            if Websites.objects.filter(domain=virtualHostName).count() == 0:
                self.printStatus(0, 'This website does not exists.')
            if Package.objects.filter(packageName=packageName).count() == 0:
                self.printStatus(0, 'This package does not exists.')

            website = Websites.objects.get(domain=virtualHostName)
            package = Package.objects.get(packageName=packageName)

            website.package = package
            website.save()

            self.printStatus(1, 'None')

        except BaseException as msg:
            logger.writeforCLI(str(msg), "Error", stack()[0][3])
            self.printStatus(0, str(msg))


    ## DNS Functions

    def listDNSJson(self, virtualHostName):
        try:

            records = DNS.getDNSRecords(virtualHostName)

            json_data = "["
            checker = 0

            for items in records:
                dic = {'id': items.id,
                       'type': items.type,
                       'name': items.name,
                       'content': items.content,
                       'priority': items.prio,
                       'ttl': items.ttl
                       }

                if checker == 0:
                    json_data = json_data + json.dumps(dic)
                    checker = 1
                else:
                    json_data = json_data + ',' + json.dumps(dic)

            json_data = json_data + ']'
            final_json = json.dumps(json_data)
            print(final_json)

        except BaseException as msg:
            logger.writeforCLI(str(msg), "Error", stack()[0][3])
            print(0)

    def listDNSPretty(self, virtualHostName):
        try:
            from prettytable import PrettyTable

            records = DNS.getDNSRecords(virtualHostName)

            table = PrettyTable(['ID', 'TYPE', 'Name', 'Value', 'Priority', 'TTL'])
            for items in records:
                if len(items.content) >= 30:
                    content = items.content[0:30] + " ..."
                else:
                    content = items.content
                table.add_row([items.id, items.type, items.name, content, items.prio, items.ttl])
            print(table)

        except BaseException as msg:
            logger.writeforCLI(str(msg), "Error", stack()[0][3])
            print(0)

    def listDNSZonesJson(self):
        try:

            records = DNS.getDNSZones()

            json_data = "["
            checker = 0

            for items in records:
                dic = {'id': items.id,
                       'name': items.name,
                       }

                if checker == 0:
                    json_data = json_data + json.dumps(dic)
                    checker = 1
                else:
                    json_data = json_data + ',' + json.dumps(dic)

            json_data = json_data + ']'
            final_json = json.dumps(json_data)
            print(final_json)

        except BaseException as msg:
            logger.writeforCLI(str(msg), "Error", stack()[0][3])
            print(0)

    def listDNSZonesPretty(self):
        try:
            from prettytable import PrettyTable

            records = records = DNS.getDNSZones()

            table = PrettyTable(['ID', 'Name'])

            for items in records:
                table.add_row([items.id, items.name])
            print(table)

        except BaseException as msg:
            logger.writeforCLI(str(msg), "Error", stack()[0][3])
            print(0)

    def createDNSZone(self, virtualHostName, owner):
        try:
            admin = Administrator.objects.get(userName=owner)
            DNS.dnsTemplate(virtualHostName, admin)
            self.printStatus(1, 'None')
        except BaseException as msg:
            logger.writeforCLI(str(msg), "Error", stack()[0][3])
            self.printStatus(0, str(msg))

    def createDNSRecord(self, virtualHostName, name, recordType, value, priority, ttl):
        try:
            zone = DNS.getZoneObject(virtualHostName)
            DNS.createDNSRecord(zone, name, recordType, value, int(priority), int(ttl))
            self.printStatus(1, 'None')
        except BaseException as msg:
            logger.writeforCLI(str(msg), "Error", stack()[0][3])
            self.printStatus(0, str(msg))

    def deleteDNSZone(self, virtualHostName):
        try:
            DNS.deleteDNSZone(virtualHostName)
            self.printStatus(1, 'None')
        except BaseException as msg:
            logger.writeforCLI(str(msg), "Error", stack()[0][3])
            self.printStatus(0, str(msg))

    def deleteDNSRecord(self, recordID):
        try:
            DNS.deleteDNSRecord(recordID)
            self.printStatus(1, 'None')
        except BaseException as msg:
            logger.writeforCLI(str(msg), "Error", stack()[0][3])
            self.printStatus(0, str(msg))

    ## Backup Functions

    def createBackup(self, virtualHostName, backupPath=None):
        try:
            # Setup default backup path to /home/<domain name>/backup if not passed in
            if backupPath is None:
                backupPath = '/home/' + virtualHostName + '/backup'

            # remove trailing slash in path
            backupPath = backupPath.rstrip("/")
            backuptime = time.strftime("%m.%d.%Y_%H-%M-%S")
            backupLogPath = "/usr/local/lscp/logs/backup_log." + backuptime

            print('Backup logs to be generated in %s' % (backupLogPath))
            tempStoragePath = backupPath + '/backup-' + virtualHostName + '-' + backuptime
            backupName = 'backup-' + virtualHostName + '-' + backuptime
            backupDomain = virtualHostName
            backupUtilities.submitBackupCreation(tempStoragePath, backupName, backupPath, backupDomain)

        except BaseException as msg:
            logger.writeforCLI(str(msg), "Error", stack()[0][3])
            print(0)

    def restoreBackup(self, fileName):
        try:
            if os.path.exists('/home/backup/' + fileName):
                dir = "EaglePanelRestore"
            else:
                dir = 'CLI'

            backupUtilities.submitRestore(fileName, dir)

            while (1):
                time.sleep(1)
                finalData = json.dumps({'backupFile': fileName, "dir": dir})
                r = requests.post("http://localhost:5003/backup/restoreStatus", data=finalData,
                                  verify=False)
                data = json.loads(r.text)

                if data['abort'] == 1 and data['running'] == "Error":
                    print('Failed to restore backup, Error message : ' + data['status'] + '\n')
                    break
                elif data['abort'] == 1 and data['running'] == "Completed":
                    print('\n\n')
                    print('Backup restore completed.\n')
                    break
                else:
                    print('Waiting for restore to complete. Current status: ' + data['status'])


        except BaseException as msg:
            logger.writeforCLI(str(msg), "Error", stack()[0][3])
            print(0)

    ## Packages

    def createPackage(self, owner, packageName, diskSpace, bandwidth, emailAccounts, dataBases, ftpAccounts,
                      allowedDomains):
        try:

            admin = Administrator.objects.get(userName=owner)

            newPack = Package(admin=admin, packageName=packageName, diskSpace=diskSpace, bandwidth=bandwidth,
                              emailAccounts=emailAccounts, dataBases=dataBases, ftpAccounts=ftpAccounts,
                              allowedDomains=allowedDomains)

            newPack.save()

            self.printStatus(1, 'None')

        except BaseException as msg:
            logger.writeforCLI(str(msg), "Error", stack()[0][3])
            self.printStatus(0, str(msg))

    def deletePackage(self, packageName):
        try:

            delPack = Package.objects.get(packageName=packageName)
            delPack.delete()
            self.printStatus(1, 'None')

        except BaseException as msg:
            logger.writeforCLI(str(msg), "Error", stack()[0][3])
            self.printStatus(0, str(msg))

    def listPackagesJson(self):
        try:

            records = Package.objects.all()

            json_data = "["
            checker = 0

            for items in records:
                dic = {'id': items.id,
                       'packageName': items.packageName,
                       'domains': items.allowedDomains,
                       'diskSpace': items.diskSpace,
                       'bandwidth': items.bandwidth,
                       'ftpAccounts ': items.ftpAccounts,
                       'dataBases': items.dataBases,
                       'emailAccounts': items.emailAccounts
                       }

                if checker == 0:
                    json_data = json_data + json.dumps(dic)
                    checker = 1
                else:
                    json_data = json_data + ',' + json.dumps(dic)

            json_data = json_data + ']'
            final_json = json.dumps(json_data)
            print(final_json)

        except BaseException as msg:
            logger.writeforCLI(str(msg), "Error", stack()[0][3])
            print(0)

    def listPackagesPretty(self):
        try:
            from prettytable import PrettyTable

            records = Package.objects.all()

            table = PrettyTable(
                ['Name', 'Domains', 'Disk Space', 'Bandwidth', 'FTP Accounts', 'Databases', 'Email Accounts'])

            for items in records:
                table.add_row(
                    [items.packageName, items.allowedDomains, items.diskSpace, items.bandwidth, items.ftpAccounts,
                     items.dataBases, items.emailAccounts])
            print(table)

        except BaseException as msg:
            logger.writeforCLI(str(msg), "Error", stack()[0][3])
            print(0)


    ## Database functions

    def createDatabase(self, dbName, dbUsername, dbPassword, databaseWebsite):
        try:

            result = mysqlUtilities.submitDBCreation(dbName, dbUsername, dbPassword, databaseWebsite)
            if result[0] == 1:
                self.printStatus(1, 'None')
            else:
                self.printStatus(1, result[1])
        except BaseException as msg:
            logger.writeforCLI(str(msg), "Error", stack()[0][3])
            self.printStatus(0, str(msg))

    def deleteDatabase(self, dbName):
        try:

            result = mysqlUtilities.submitDBDeletion(dbName)

            if result[0] == 1:
                self.printStatus(1, 'None')
            else:
                self.printStatus(1, result[1])
        except BaseException as msg:
            logger.writeforCLI(str(msg), "Error", stack()[0][3])
            self.printStatus(0, str(msg))

    def listDatabasesJson(self, virtualHostName):
        try:

            records = mysqlUtilities.getDatabases(virtualHostName)

            json_data = "["
            checker = 0

            for items in records:
                dic = {'id': items.id,
                       'dbName': items.dbName,
                       'dbUser': items.dbUser,
                       }

                if checker == 0:
                    json_data = json_data + json.dumps(dic)
                    checker = 1
                else:
                    json_data = json_data + ',' + json.dumps(dic)

            json_data = json_data + ']'
            final_json = json.dumps(json_data)
            print(final_json)

        except BaseException as msg:
            logger.writeforCLI(str(msg), "Error", stack()[0][3])
            print(0)

    def listDatabasesPretty(self, virtualHostName):
        try:
            from prettytable import PrettyTable

            records = mysqlUtilities.getDatabases(virtualHostName)

            table = PrettyTable(['ID', 'Database Name', 'Database User'])

            for items in records:
                table.add_row([items.id, items.dbName, items.dbUser])
            print(table)

        except BaseException as msg:
            logger.writeforCLI(str(msg), "Error", stack()[0][3])
            print(0)

    ## Email functions

    def createEmail(self, domain, userName, password):
        try:

            result = mailUtilities.createEmailAccount(domain, userName, password)
            if result[0] == 1:
                self.printStatus(1, 'None')
            else:
                self.printStatus(1, result[1])
        except BaseException as msg:
            logger.writeforCLI(str(msg), "Error", stack()[0][3])
            self.printStatus(0, str(msg))

    def deleteEmail(self, email):
        try:

            result = mailUtilities.deleteEmailAccount(email)
            if result[0] == 1:
                self.printStatus(1, 'None')
            else:
                self.printStatus(1, result[1])
        except BaseException as msg:
            logger.writeforCLI(str(msg), "Error", stack()[0][3])
            self.printStatus(0, str(msg))

    def changeEmailPassword(self, email, password):
        try:

            result = mailUtilities.changeEmailPassword(email, password)
            if result[0] == 1:
                self.printStatus(1, 'None')
            else:
                self.printStatus(1, result[1])
        except BaseException as msg:
            logger.writeforCLI(str(msg), "Error", stack()[0][3])
            self.printStatus(0, str(msg))

    def listEmailsJson(self, virtualHostName):
        try:

            records = mailUtilities.getEmailAccounts(virtualHostName)

            json_data = "["
            checker = 0

            for items in records:
                dic = {
                    'email': items.email,
                }

                if checker == 0:
                    json_data = json_data + json.dumps(dic)
                    checker = 1
                else:
                    json_data = json_data + ',' + json.dumps(dic)

            json_data = json_data + ']'
            final_json = json.dumps(json_data)
            print(final_json)

        except BaseException as msg:
            logger.writeforCLI(str(msg), "Error", stack()[0][3])
            print(0)

    def listEmailsPretty(self, virtualHostName):
        try:
            from prettytable import PrettyTable

            records = mailUtilities.getEmailAccounts(virtualHostName)

            table = PrettyTable(['Email'])

            for items in records:
                table.add_row([items.email])
            print(table)

        except BaseException as msg:
            logger.writeforCLI(str(msg), "Error", stack()[0][3])
            print(0)

    ## FTP Functions

    ## FTP Functions


    # FTP Functions

    def createFTPAccount(self, domain, userName, password, owner):
        try:

            result = FTPUtilities.submitFTPCreation(domain, userName, password, 'None', owner)
            if result[0] == 1:
                self.printStatus(1, 'None')
            else:
                self.printStatus(1, result[1])
        except BaseException as msg:
            logger.writeforCLI(str(msg), "Error", stack()[0][3])
            self.printStatus(0, str(msg))

    def deleteFTPAccount(self, userName):
        try:

            result = FTPUtilities.submitFTPDeletion(userName)
            if result[0] == 1:
                self.printStatus(1, 'None')
            else:
                self.printStatus(1, result[1])
        except BaseException as msg:
            logger.writeforCLI(str(msg), "Error", stack()[0][3])
            self.printStatus(0, str(msg))

    def changeFTPPassword(self, userName, password):
        try:

            result = FTPUtilities.changeFTPPassword(userName, password)
            if result[0] == 1:
                self.printStatus(1, 'None')
            else:
                self.printStatus(1, result[1])
        except BaseException as msg:
            logger.writeforCLI(str(msg), "Error", stack()[0][3])
            self.printStatus(0, str(msg))

    def listFTPJson(self, virtualHostName):
        try:

            records = FTPUtilities.getFTPRecords(virtualHostName)

            json_data = "["
            checker = 0

            for items in records:
                dic = {'id': items.id,
                       'username': items.user,
                       'path': items.dir
                       }

                if checker == 0:
                    json_data = json_data + json.dumps(dic)
                    checker = 1
                else:
                    json_data = json_data + ',' + json.dumps(dic)

            json_data = json_data + ']'
            final_json = json.dumps(json_data)
            print(final_json)

        except BaseException as msg:
            logger.writeforCLI(str(msg), "Error", stack()[0][3])
            print(0)

    def listFTPPretty(self, virtualHostName):
        try:
            from prettytable import PrettyTable

            records = FTPUtilities.getFTPRecords(virtualHostName)

            table = PrettyTable(['ID', 'User', 'Path'])

            for items in records:
                table.add_row([items.id, items.user, items.dir])
            print(table)

        except BaseException as msg:
            logger.writeforCLI(str(msg), "Error", stack()[0][3])
            print(0)

    ## FTP Functions


    ## SSL Functions

    def issueSSL(self, virtualHost):
        try:

            path = ''
            adminEmail = ''

            try:
                website = ChildDomains.objects.get(domain=virtualHost)
                adminEmail = website.master.adminEmail
                path = website.path
            except:
                website = Websites.objects.get(domain=virtualHost)
                adminEmail = website.adminEmail
                path = "/home/" + virtualHost + "/public_html"

            result = virtualHostUtilities.issueSSL(virtualHost, path, adminEmail)
            if result[0] == 1:
                self.printStatus(1, 'None')
            else:
                self.printStatus(1, result[1])
        except BaseException as msg:
            logger.writeforCLI(str(msg), "Error", stack()[0][3])
            self.printStatus(0, str(msg))

    def issueSSLForHostName(self, virtualHost):
        try:

            path = ''
            adminEmail = ''

            try:
                website = ChildDomains.objects.get(domain=virtualHost)
                adminEmail = website.master.adminEmail
                path = website.path
            except:
                website = Websites.objects.get(domain=virtualHost)
                adminEmail = website.adminEmail
                path = "/home/" + virtualHost + "/public_html"

            result = virtualHostUtilities.issueSSLForHostName(virtualHost, path)
            if result[0] == 1:
                self.printStatus(1, 'None')
            else:
                self.printStatus(1, result[1])
        except BaseException as msg:
            logger.writeforCLI(str(msg), "Error", stack()[0][3])
            self.printStatus(0, str(msg))

    def issueSSLForMailServer(self, virtualHost):
        try:

            path = ''
            adminEmail = ''

            try:
                website = ChildDomains.objects.get(domain=virtualHost)
                adminEmail = website.master.adminEmail
                path = website.path
            except:
                website = Websites.objects.get(domain=virtualHost)
                adminEmail = website.adminEmail
                path = "/home/" + virtualHost + "/public_html"

            result = virtualHostUtilities.issueSSLForMailServer(virtualHost, path)
            if result[0] == 1:
                self.printStatus(1, 'None')
            else:
                self.printStatus(1, result[1])
        except BaseException as msg:
            logger.writeforCLI(str(msg), "Error", stack()[0][3])
            self.printStatus(0, str(msg))


    def issueSelfSignedSSL(self, virtualHost):
        try:

            try:
                website = ChildDomains.objects.get(domain=virtualHost)
                adminEmail = website.master.adminEmail
            except:
                website = Websites.objects.get(domain=virtualHost)
                adminEmail = website.adminEmail

            pathToStoreSSL = "/etc/letsencrypt/live/" + virtualHost
            command = 'mkdir -p ' + pathToStoreSSL
            ProcessUtilities.executioner(command)

            pathToStoreSSLPrivKey = "/etc/letsencrypt/live/" + virtualHost + "/privkey.pem"
            pathToStoreSSLFullChain = "/etc/letsencrypt/live/" + virtualHost + "/fullchain.pem"

            command = 'openssl req -newkey rsa:2048 -new -nodes -x509 -days 3650 -subj "/C=US/ST=Denial/L=Springfield/O=Dis/CN=www.example.com" -keyout ' + pathToStoreSSLPrivKey + ' -out ' + pathToStoreSSLFullChain
            ProcessUtilities.executioner(command)

            sslUtilities.installSSLForDomain(virtualHost, adminEmail)
            ProcessUtilities.restartLitespeed()
            self.printStatus(1, 'None')

        except BaseException as msg:
            logger.writeforCLI(str(msg), "Error", stack()[0][3])
            self.printStatus(0, str(msg))

def main():

    parser = cliParser()
    args = parser.prepareArguments()
    eaglepanel = eaglePanel()

    ## Website functions

    if args.function == "createWebsite":

        completeCommandExample = 'eaglepanel createWebsite --package Detault --owner admin --domainName eaglepanel.net --email support@eaglepanel.net --php 5.6'

        if not args.package:
            print("\n\nPlease enter the package name. For example:\n\n" + completeCommandExample + "\n\n")
            return

        if not args.owner:
            print("\n\nPlease enter the owner name. For example:\n\n" + completeCommandExample + "\n\n")
            return

        if not args.domainName:
            print("\n\nPlease enter the domain name. For example:\n\n" + completeCommandExample + "\n\n")
            return

        if not args.email:
            print("\n\nPlease enter the email. For example:\n\n" + completeCommandExample + "\n\n")
            return

        if not args.php:
            print("\n\nPlease enter the PHP version such as 5.6 for PHP version 5.6. For example:\n\n" + completeCommandExample + "\n\n")
            return

        if args.ssl:
            ssl = int(args.ssl)
        else:
            ssl = 0

        if args.dkim:
            dkim = int(args.dkim)
        else:
            dkim = 0

        if args.openBasedir:
            openBasedir = int(args.openBasedir)
        else:
            openBasedir = 0

        eaglepanel.createWebsite(args.package, args.owner, args.domainName, args.email, args.php, ssl, dkim,
                                 openBasedir)
    elif args.function == "deleteWebsite":

        completeCommandExample = 'eaglepanel deleteWebsite --domainName eaglepanel.net'

        if not args.domainName:
            print("\n\nPlease enter the domain to delete. For example:\n\n" + completeCommandExample + "\n\n")
            return

        eaglepanel.deleteWebsite(args.domainName)
    elif args.function == "createChild":

        completeCommandExample = 'eaglepanel createChild --masterDomain eaglepanel.net --childDomain child.eaglepanel.net' \
                                 ' --owner admin --php 5.6'

        if not args.masterDomain:
            print("\n\nPlease enter Master domain. For example:\n\n" + completeCommandExample + "\n\n")
            return

        if not args.childDomain:
            print("\n\nPlease enter the Child Domain. For example:\n\n" + completeCommandExample + "\n\n")
            return

        if not args.owner:
            print("\n\nPlease enter owner for this domain DNS records. For example:\n\n" + completeCommandExample + "\n\n")
            return

        if not args.php:
            print("\n\nPlease enter required PHP version. For example:\n\n" + completeCommandExample + "\n\n")
            return

        if args.ssl:
            ssl = int(args.ssl)
        else:
            ssl = 0

        if args.dkim:
            dkim = int(args.dkim)
        else:
            dkim = 0

        if args.openBasedir:
            openBasedir = int(args.openBasedir)
        else:
            openBasedir = 0
            
        if args.path:
            path = args.path
        else:
            path = "public_html/" + args.childDomain

        eaglepanel.createDomain(args.masterDomain, args.childDomain, args.owner, args.php, ssl, dkim, openBasedir, path)
    elif args.function == "deleteChild":

        completeCommandExample = 'eaglepanel deleteChild --childDomain eaglepanel.net'

        if not args.childDomain:
            print("\n\nPlease enter the child domain to delete. For example:\n\n" + completeCommandExample + "\n\n")
            return

        eaglepanel.deleteChild(args.childDomain)
    elif args.function == "listWebsitesJson":
        eaglepanel.listWebsitesJson()
    elif args.function == "listWebsitesPretty":
        eaglepanel.listWebsitesPretty()

    elif args.function == "changePHP":

        completeCommandExample = 'eaglepanel changePHP --domainName eaglepanel.net --php 5.6'

        if not args.domainName:
            print("\n\nPlease enter Domain. For example:\n\n" + completeCommandExample + "\n\n")
            return

        if not args.php:
            print("\n\nPlease enter required PHP version. For example:\n\n" + completeCommandExample + "\n\n")
            return


        eaglepanel.changePHP(args.domainName, args.php)
    elif args.function == "changePackage":

        completeCommandExample = 'eaglepanel changePackage --domainName eaglepanel.net --packageName CLI'

        if not args.domainName:
            print("\n\nPlease enter the Domain. For example:\n\n" + completeCommandExample + "\n\n")
            return

        if not args.packageName:
            print("\n\nPlease enter the package name. For example:\n\n" + completeCommandExample + "\n\n")
            return

        eaglepanel.changePackage(args.domainName, args.packageName)

    ## DNS Functions

    elif args.function == "listDNSJson":

        completeCommandExample = 'eaglepanel listDNSJson --domainName eaglepanel.net'

        if not args.domainName:
            print("\n\nPlease enter the domain. For example:\n\n" + completeCommandExample + "\n\n")
            return

        eaglepanel.listDNSJson(args.domainName)
    elif args.function == "listDNSPretty":

        completeCommandExample = 'eaglepanel listDNSPretty --domainName eaglepanel.net'

        if not args.domainName:
            print("\n\nPlease enter the domain. For example:\n\n" + completeCommandExample + "\n\n")
            return

        eaglepanel.listDNSPretty(args.domainName)
    elif args.function == "listDNSZonesJson":
        eaglepanel.listDNSZonesJson()
    elif args.function == "listDNSZonesPretty":
        eaglepanel.listDNSZonesPretty()
    elif args.function == "createDNSZone":
        completeCommandExample = 'eaglepanel createDNSZone --owner admin --domainName eaglepanel.net'

        if not args.domainName:
            print("\n\nPlease enter the domain. For example:\n\n" + completeCommandExample + "\n\n")
            return

        if not args.owner:
            print("\n\nPlease enter the owner name. For example:\n\n" + completeCommandExample + "\n\n")
            return

        eaglepanel.createDNSZone(args.domainName, args.owner)
    elif args.function == "deleteDNSZone":
        completeCommandExample = 'eaglepanel deleteDNSZone --domainName eaglepanel.net'

        if not args.domainName:
            print("\n\nPlease enter the domain. For example:\n\n" + completeCommandExample + "\n\n")
            return

        eaglepanel.deleteDNSZone(args.domainName)
    elif args.function == "createDNSRecord":
        completeCommandExample = 'eaglepanel createDNSRecord --domainName eaglepanel.net --name eaglepanel.net' \
                                 ' --recordType A --value 192.168.100.1 --priority 0 --ttl 3600'

        if not args.domainName:
            print("\n\nPlease enter the domain. For example:\n\n" + completeCommandExample + "\n\n")
            return

        if not args.name:
            print("\n\nPlease enter the record name. For example:\n\n" + completeCommandExample + "\n\n")
            return

        if not args.recordType:
            print("\n\nPlease enter the record type. For example:\n\n" + completeCommandExample + "\n\n")
            return

        if not args.value:
            print("\n\nPlease enter the record value. For example:\n\n" + completeCommandExample + "\n\n")
            return

        if not args.priority:
            print("\n\nPlease enter the priority. For example:\n\n" + completeCommandExample + "\n\n")
            return

        if not args.ttl:
            print("\n\nPlease enter the ttl. For example:\n\n" + completeCommandExample + "\n\n")
            return

        eaglepanel.createDNSRecord(args.domainName, args.name, args.recordType, args.value, args.priority, args.ttl)
    elif args.function == "deleteDNSRecord":
        completeCommandExample = 'eaglepanel deleteDNSRecord --recordID 200'

        if not args.recordID:
            print("\n\nPlease enter the record ID to be deleted, you can find record ID by listing the current DNS records. For example:\n\n" + completeCommandExample + "\n\n")
            return

        eaglepanel.deleteDNSRecord(args.recordID)

    ## Backup Functions.

    elif args.function == "createBackup":

        completeCommandExample = 'eaglepanel createBackup --domainName eaglepanel.net'

        if not args.domainName:
            print("\n\nPlease enter the domain. For example:\n\n" + completeCommandExample + "\n\n")
            return

        eaglepanel.createBackup(args.domainName)
    elif args.function == "restoreBackup":

        completeCommandExample = 'eaglepanel restoreBackup --fileName /home/talkshosting.com/backup/backup-talksho-01-30-53-Fri-Jun-2018.tar.gz'

        if not args.fileName:
            print("\n\nPlease enter the file name or complete path to file. For example:\n\n" + completeCommandExample + "\n\n")
            return

        eaglepanel.restoreBackup(args.fileName)

    ## Package functions.

    elif args.function == "createPackage":

        completeCommandExample = 'eaglepanel createPackage --owner admin --packageName CLI --diskSpace 1000 --bandwidth 10000 --emailAccounts 100' \
                                 ' --dataBases 100 --ftpAccounts 100 --allowedDomains 100'

        if not args.owner:
            print("\n\nPlease enter the owner name. For example:\n\n" + completeCommandExample + "\n\n")
            return
        if not args.packageName:
            print("\n\nPlease enter the package name. For example:\n\n" + completeCommandExample + "\n\n")
            return
        if not args.diskSpace:
            print("\n\nPlease enter value for Disk Space. For example:\n\n" + completeCommandExample + "\n\n")
            return

        if not args.bandwidth:
            print("\n\nPlease enter value for Bandwidth. For example:\n\n" + completeCommandExample + "\n\n")
            return

        if not args.emailAccounts:
            print("\n\nPlease enter value for Email accounts. For example:\n\n" + completeCommandExample + "\n\n")
            return

        if not args.dataBases:
            print("\n\nPlease enter value for Databases. For example:\n\n" + completeCommandExample + "\n\n")
            return

        if not args.ftpAccounts:
            print("\n\nPlease enter value for Ftp accounts. For example:\n\n" + completeCommandExample + "\n\n")
            return

        if not args.allowedDomains:
            print("\n\nPlease enter value for Allowed Child Domains. For example:\n\n" + completeCommandExample + "\n\n")
            return

        eaglepanel.createPackage(args.owner, args.packageName, args.diskSpace, args.bandwidth, args.emailAccounts,
                                 args.dataBases, args.ftpAccounts, args.allowedDomains)
    elif args.function == "deletePackage":
        completeCommandExample = 'eaglepanel deletePackage --packageName CLI'
        if not args.packageName:
            print("\n\nPlease enter the package name. For example:\n\n" + completeCommandExample + "\n\n")
            return

        eaglepanel.deletePackage(args.packageName)
    elif args.function == "listPackagesJson":
        eaglepanel.listPackagesJson()
    elif args.function == "listPackagesPretty":
        eaglepanel.listPackagesPretty()

    ## Database functions.

    elif args.function == "createDatabase":

        completeCommandExample = 'eaglepanel createDatabase --databaseWebsite eaglepanel.net --dbName eaglepanel ' \
                                 '--dbUsername eaglepanel --dbPassword eaglepanel'

        if not args.databaseWebsite:
            print("\n\nPlease enter database website. For example:\n\n" + completeCommandExample + "\n\n")
            return
        if not args.dbName:
            print("\n\nPlease enter the database name. For example:\n\n" + completeCommandExample + "\n\n")
            return
        if not args.dbUsername:
            print("\n\nPlease enter the database username. For example:\n\n" + completeCommandExample + "\n\n")
            return

        if not args.dbPassword:
            print("\n\nPlease enter the password for database. For example:\n\n" + completeCommandExample + "\n\n")
            return

        eaglepanel.createDatabase(args.dbName, args.dbUsername, args.dbPassword, args.databaseWebsite)
    elif args.function == "deleteDatabase":
        completeCommandExample = 'eaglepanel deleteDatabase --dbName eaglepanel'
        if not args.dbName:
            print("\n\nPlease enter the database name. For example:\n\n" + completeCommandExample + "\n\n")
            return

        eaglepanel.deleteDatabase(args.dbName)
    elif args.function == "listDatabasesJson":

        completeCommandExample = 'eaglepanel listDatabasesJson --databaseWebsite eaglepanel.net'

        if not args.databaseWebsite:
            print("\n\nPlease enter database website. For example:\n\n" + completeCommandExample + "\n\n")
            return
        eaglepanel.listDatabasesJson(args.databaseWebsite)
    elif args.function == "listDatabasesPretty":
        completeCommandExample = 'eaglepanel listDatabasesPretty --databaseWebsite eaglepanel.net'

        if not args.databaseWebsite:
            print("\n\nPlease enter database website. For example:\n\n" + completeCommandExample + "\n\n")
            return

        eaglepanel.listDatabasesPretty(args.databaseWebsite)

    ## Email Functions

    elif args.function == "createEmail":

        completeCommandExample = 'eaglepanel createEmail --domainName eaglepanel.net --userName eaglepanel ' \
                                 '--password eaglepanel'

        if not args.domainName:
            print("\n\nPlease enter Domain name. For example:\n\n" + completeCommandExample + "\n\n")
            return
        if not args.userName:
            print("\n\nPlease enter the user name. For example:\n\n" + completeCommandExample + "\n\n")
            return

        if not args.password:
            print("\n\nPlease enter the password for database. For example:\n\n" + completeCommandExample + "\n\n")
            return

        eaglepanel.createEmail(args.domainName, args.userName, args.password)
    elif args.function == "deleteEmail":
        completeCommandExample = 'eaglepanel deleteEmail --email eaglepanel@eaglepanel.net'

        if not args.email:
            print("\n\nPlease enter the email. For example:\n\n" + completeCommandExample + "\n\n")
            return

        eaglepanel.deleteEmail(args.email)
    elif args.function == "changeEmailPassword":

        completeCommandExample = 'eaglepanel changeEmailPassword --email eaglepanel@eaglepanel.net --password eaglepanel'

        if not args.email:
            print("\n\nPlease enter email. For example:\n\n" + completeCommandExample + "\n\n")
            return

        if not args.password:
            print("\n\nPlease enter the password. For example:\n\n" + completeCommandExample + "\n\n")
            return

        eaglepanel.changeEmailPassword(args.email, args.password)
    elif args.function == "listEmailsJson":
        completeCommandExample = 'eaglepanel listEmailsJson --domainName eaglepanel.net'

        if not args.domainName:
            print("\n\nPlease enter domain name. For example:\n\n" + completeCommandExample + "\n\n")
            return

        eaglepanel.listEmailsJson(args.domainName)
    elif args.function == "listEmailsPretty":
        completeCommandExample = 'eaglepanel listEmailsPretty --domainName eaglepanel.net'

        if not args.domainName:
            print("\n\nPlease enter domain name. For example:\n\n" + completeCommandExample + "\n\n")
            return

        eaglepanel.listEmailsPretty(args.domainName)

    ## FTP Functions

    elif args.function == "createFTPAccount":

        completeCommandExample = 'eaglepanel createFTPAccount --domainName eaglepanel.net --userName eaglepanel ' \
                                 '--password eaglepanel --owner admin'

        if not args.domainName:
            print("\n\nPlease enter Domain name. For example:\n\n" + completeCommandExample + "\n\n")
            return
        if not args.userName:
            print("\n\nPlease enter the user name. For example:\n\n" + completeCommandExample + "\n\n")
            return

        if not args.password:
            print("\n\nPlease enter the password for database. For example:\n\n" + completeCommandExample + "\n\n")
            return

        if not args.owner:
            print("\n\nPlease enter the owner name. For example:\n\n" + completeCommandExample + "\n\n")
            return

        eaglepanel.createFTPAccount(args.domainName, args.userName, args.password, args.owner)
    elif args.function == "deleteFTPAccount":
        completeCommandExample = 'eaglepanel deleteFTPAccount --userName eaglepanel'

        if not args.userName:
            print("\n\nPlease enter the user name. For example:\n\n" + completeCommandExample + "\n\n")
            return

        eaglepanel.deleteFTPAccount(args.userName)
    elif args.function == "changeFTPPassword":

        completeCommandExample = 'eaglepanel changeFTPPassword --userName eaglepanel --password eaglepanel'

        if not args.userName:
            print("\n\nPlease enter the user name. For example:\n\n" + completeCommandExample + "\n\n")
            return

        if not args.password:
            print("\n\nPlease enter the password for database. For example:\n\n" + completeCommandExample + "\n\n")
            return

        eaglepanel.changeFTPPassword(args.userName, args.password)
    elif args.function == "listFTPJson":
        completeCommandExample = 'eaglepanel listFTPJson --domainName eaglepanel.net'

        if not args.domainName:
            print("\n\nPlease enter domain name. For example:\n\n" + completeCommandExample + "\n\n")
            return

        eaglepanel.listFTPJson(args.domainName)
    elif args.function == "listFTPPretty":
        completeCommandExample = 'eaglepanel listFTPPretty --domainName eaglepanel.net'

        if not args.domainName:
            print("\n\nPlease enter domain name. For example:\n\n" + completeCommandExample + "\n\n")
            return

        eaglepanel.listFTPPretty(args.domainName)

    ## SSL Functions
    elif args.function == "issueSSL":
        completeCommandExample = 'eaglepanel issueSSL --domainName eaglepanel.net'

        if not args.domainName:
            print("\n\nPlease enter Domain name. For example:\n\n" + completeCommandExample + "\n\n")
            return

        eaglepanel.issueSSL(args.domainName)
    elif args.function == "hostNameSSL":
        completeCommandExample = 'eaglepanel hostNameSSL --domainName eaglepanel.net'

        if not args.domainName:
            print("\n\nPlease enter Domain name. For example:\n\n" + completeCommandExample + "\n\n")
            return

        eaglepanel.issueSSLForHostName(args.domainName)
    elif args.function == "mailServerSSL":

        completeCommandExample = 'eaglepanel mailServerSSL --domainName eaglepanel.net'

        if not args.domainName:
            print("\n\nPlease enter Domain name. For example:\n\n" + completeCommandExample + "\n\n")
            return

        eaglepanel.issueSSLForMailServer(args.domainName)

    elif args.function == "issueSelfSignedSSL":
        completeCommandExample = 'eaglepanel issueSelfSignedSSL --domainName eaglepanel.net'

        if not args.domainName:
            print("\n\nPlease enter Domain name. For example:\n\n" + completeCommandExample + "\n\n")
            return

        eaglepanel.issueSelfSignedSSL(args.domainName)

    elif args.function == 'utility':
        if not os.path.exists('/usr/bin/eaglepanel_utility'):
            command = 'wget -q -O /usr/bin/eaglepanel_utility https://eaglepanel.sh/misc/eaglepanel_utility.sh'
            ProcessUtilities.executioner(command)

            command = 'chmod 700 /usr/bin/eaglepanel_utility'
            ProcessUtilities.executioner(command)

        command = '/usr/bin/eaglepanel_utility'
        ProcessUtilities.executioner(command)
    elif args.function == 'upgrade' or args.function == 'update':
        if not os.path.exists('/usr/bin/eaglepanel_utility'):
            command = 'wget -q -O /usr/bin/eaglepanel_utility https://eaglepanel.sh/misc/eaglepanel_utility.sh'
            ProcessUtilities.executioner(command)

            command = 'chmod 700 /usr/bin/eaglepanel_utility'
            ProcessUtilities.executioner(command)

        command = '/usr/bin/eaglepanel_utility --upgrade'
        ProcessUtilities.executioner(command)
    elif args.function == 'help':
        if not os.path.exists('/usr/bin/eaglepanel_utility'):
            command = 'wget -q -O /usr/bin/eaglepanel_utility https://eaglepanel.sh/misc/eaglepanel_utility.sh'
            ProcessUtilities.executioner(command)

            command = 'chmod 700 /usr/bin/eaglepanel_utility'
            ProcessUtilities.executioner(command)

        command = '/usr/bin/eaglepanel_utility --help'
        ProcessUtilities.executioner(command)
    elif args.function == 'version' or args.function == 'v' or args.function == 'V':
        ## Get CurrentVersion
        print(get_eaglepanel_version())

    ### User Functions

    elif args.function == "createUser":

        completeCommandExample = 'eaglepanel createUser --firstName Cyber --lastName Panel --email email@eaglepanel.net --userName eaglepanel --password securepassword --websitesLimit 10 --selectedACL user --securityLevel HIGH'

        if not args.firstName:
            print("\n\nPlease enter First Name. For example:\n\n" + completeCommandExample + "\n\n")
            return

        if not args.lastName:
            print("\n\nPlease enter Last Name. For example:\n\n" + completeCommandExample + "\n\n")
            return

        if not args.email:
            print("\n\nPlease enter Email. For example:\n\n" + completeCommandExample + "\n\n")
            return

        if not args.userName:
            print("\n\nPlease enter User name. For example:\n\n" + completeCommandExample + "\n\n")
            return

        if not args.password:
            print("\n\nPlease enter password. For example:\n\n" + completeCommandExample + "\n\n")
            return

        if not args.websitesLimit:
            print("\n\nPlease enter website limit. For example:\n\n" + completeCommandExample + "\n\n")
            return

        if not args.selectedACL:
            print("\n\nPlease enter select acl. For example:\n\n" + completeCommandExample + "\n\n")
            return

        if not args.securityLevel:
            print("\n\nPlease set security level. For example:\n\n" + completeCommandExample + "\n\n")
            return

        from userManagment.views import submitUserCreation

        data = {}
        data['firstName'] = args.firstName
        data['lastName'] = args.lastName
        data['email'] = args.email
        data['userName'] = args.userName
        data['password'] = args.password
        data['websitesLimit'] = args.websitesLimit
        data['selectedACL'] = args.selectedACL
        data['securityLevel'] = args.securityLevel
        data['userID'] = 1

        response = submitUserCreation(data)

        print(response.content.decode())

    elif args.function == "deleteUser":

        completeCommandExample = 'eaglepanel deleteUser --userName eaglepanel'

        if not args.userName:
            print("\n\nPlease enter User Name. For example:\n\n" + completeCommandExample + "\n\n")
            return

        from userManagment.views import submitUserDeletion

        data = {}
        data['accountUsername'] = args.userName
        data['userID'] = 1

        response = submitUserDeletion(data)

        print(response.content.decode())

    elif args.function == "listUsers":

        from userManagment.views import fetchTableUsers
        data = {}
        data['userID'] = 1
        response = fetchTableUsers(data)

        print(response.content.decode())

    elif args.function == "suspendUser":

        completeCommandExample = 'eaglepanel suspendUser --userName eaglepanel --state SUSPEND'

        if not args.userName:
            print("\n\nPlease enter User Name. For example:\n\n" + completeCommandExample + "\n\n")
            return

        if not args.state:
            print("\n\nPlease enter state value i.e SUSPEND/UnSuspend. For example:\n\n" + completeCommandExample + "\n\n")
            return

        from userManagment.views import controlUserState

        data = {}
        data['accountUsername'] = args.userName
        data['state'] = args.state
        data['userID'] = 1

        response = controlUserState(data)

        print(response.content.decode())

    elif args.function == "editUser":

        completeCommandExample = 'eaglepanel editUser --userName eaglepanel --firstName Cyber --lastName Panel --email email@eaglepanel.net --password securepassword --securityLevel HIGH'

        if not args.firstName:
            print("\n\nPlease enter First Name. For example:\n\n" + completeCommandExample + "\n\n")
            return

        if not args.lastName:
            print("\n\nPlease enter Last Name. For example:\n\n" + completeCommandExample + "\n\n")
            return

        if not args.email:
            print("\n\nPlease enter Email. For example:\n\n" + completeCommandExample + "\n\n")
            return

        if not args.userName:
            print("\n\nPlease enter User name. For example:\n\n" + completeCommandExample + "\n\n")
            return

        if not args.password:
            print("\n\nPlease enter password. For example:\n\n" + completeCommandExample + "\n\n")
            return

        if not args.securityLevel:
            print("\n\nPlease set security level. For example:\n\n" + completeCommandExample + "\n\n")
            return

        from userManagment.views import saveModifications

        data = {}
        data['accountUsername'] = args.userName
        data['firstName'] = args.firstName
        data['lastName'] = args.lastName
        data['email'] = args.email
        data['passwordByPass'] = args.password
        data['securityLevel'] = args.securityLevel
        data['userID'] = 1

        response = saveModifications(data)

        print(response.content.decode())

    ### Application installers

    elif args.function == "installWordPress":
        completeCommandExample = 'eaglepanel installWordPress --domainName eaglepanel.net --email support@eaglepanel.net --userName eaglepanel --password helloworld --siteTitle "WordPress Site" --path helloworld (this is optional)'

        if not args.domainName:
            print("\n\nPlease enter Domain name. For example:\n\n" + completeCommandExample + "\n\n")
            return

        if not args.email:
            print("\n\nPlease enter email. For example:\n\n" + completeCommandExample + "\n\n")
            return

        if not args.userName:
            print("\n\nPlease enter User name. For example:\n\n" + completeCommandExample + "\n\n")
            return

        if not args.password:
            print("\n\nPlease enter password. For example:\n\n" + completeCommandExample + "\n\n")
            return

        if not args.siteTitle:
            print("\n\nPlease enter site title. For example:\n\n" + completeCommandExample + "\n\n")
            return

        if not args.path:
            home = '1'
            path = ''
        else:
            home = '0'
            path = args.path

        from websiteFunctions.website import WebsiteManager

        data = {}
        data['adminUser'] = args.userName
        data['blogTitle'] = args.siteTitle
        data['domain'] = args.domainName
        data['adminEmail'] = args.email
        data['passwordByPass'] = args.password
        data['home'] = home
        data['path'] = path

        wm = WebsiteManager()
        wm.installWordpress(1, data)

    elif args.function == "installJoomla":

        completeCommandExample = 'eaglepanel installJoomla --domainName eaglepanel.net --password helloworld --siteTitle "WordPress Site" --path helloworld (this is optional)'

        if not args.domainName:
            print("\n\nPlease enter Domain name. For example:\n\n" + completeCommandExample + "\n\n")
            return

        if not args.password:
            print("\n\nPlease enter password. For example:\n\n" + completeCommandExample + "\n\n")
            return

        if not args.siteTitle:
            print("\n\nPlease enter site title. For example:\n\n" + completeCommandExample + "\n\n")
            return

        if not args.path:
            home = '1'
            path = ''
        else:
            home = '0'
            path = args.path

        from websiteFunctions.website import WebsiteManager

        data = {}
        data['prefix'] = 'jm_'
        data['siteName'] = args.siteTitle
        data['domain'] = args.domainName
        data['passwordByPass'] = args.password
        data['home'] = home
        data['path'] = path

        wm = WebsiteManager()
        wm.installJoomla(1, data)

    elif args.function == "switchTOLSWS":

        completeCommandExample = 'eaglepanel switchTOLSWS --licenseKey <Your lsws key here or you can enter TRIAL)'

        if not args.licenseKey:
            print("\n\nPlease enter LiteSpeed License key. For example:\n\n" + completeCommandExample + "\n\n")
            return

        from serverStatus.serverStatusUtil import ServerStatusUtil

        ServerStatusUtil.switchTOLSWSCLI(args.licenseKey)


if __name__ == "__main__":
    main()
