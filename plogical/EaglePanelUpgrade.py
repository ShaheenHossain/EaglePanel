import json
import os.path
import sys
import argparse
import requests

sys.path.append('/usr/local/EagleEP')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "EagleEP.settings")

class UpgradeEaglePanel:

    LogURL = "https://platform.cyberpersons.com/settings/RecvData"

    def __init__(self, branch, mail, dns, ftp):
        ipFile = "/etc/eaglepanel/machineIP"
        f = open(ipFile)
        ipData = f.read()
        self.ipAddress = ipData.split('\n', 1)[0]
        self.branch = branch
        self.mail = mail
        self.ftp = ftp
        self.dns = dns

    def PostStatus(self, message):
        finalData = json.dumps({'ipAddress': self.ipAddress, "UpgradeEaglePanelStatus": message})

        try:
            resp = requests.post(UpgradeEaglePanel.LogURL, data=finalData, timeout=10)
        except:
            pass

    def RestoreOldCP(self):

        from plogical.upgrade import Upgrade

        command = 'rm -rf /usr/local/EagleEP'
        Upgrade.executioner(command, command)

        command = 'mv /usr/local/EagleEPBak /usr/local/EagleEP'
        Upgrade.executioner(command, command)
        Upgrade.fixPermissions()

    def UpgardeNow(self):

        from plogical.upgrade import Upgrade

        ## If any update command fails this check make sure upgrade process does not quit

        Upgrade.FromCloud = 1

        ## Backup current EagleEP, incase of failure restore

        self.PostStatus('Backing up current installation..,5')

        command = 'cp -R /usr/local/EagleEP /usr/local/EagleEPBak'
        Upgrade.executioner(command, command)

        if not Upgrade.executioner(command, command, 1):
            self.PostStatus('Failed to execute %s. [404]' % (command))

        self.PostStatus('Upgrading/Downgrading to branch %s..,10' % (self.branch))

        status, message = Upgrade.downloadAndUpgrade(None, self.branch)

        if status == 0:
            self.RestoreOldCP()
            self.PostStatus('Failed to upgrade, error %s.[404]' % (message))
            return 0

        self.PostStatus('EaglePanel is now on %s..,40' % (self.branch))

        ##

        self.PostStatus('Updating database..,45')

        Upgrade.mailServerMigrations()
        Upgrade.emailMarketingMigrationsa()
        Upgrade.dockerMigrations()
        Upgrade.CLMigrations()
        Upgrade.IncBackupMigrations()
        Upgrade.applyLoginSystemMigrations()
        Upgrade.s3BackupMigrations()
        Upgrade.containerMigrations()
        Upgrade.manageServiceMigrations()

        self.PostStatus('Database updated.,55')

        ## Put function here to update custom ACLs

        Upgrade.UpdateConfigOfCustomACL()
        Upgrade.enableServices()
        Upgrade.someDirectories()
        Upgrade.GeneralMigrations()

        ## Upgrade version

        self.PostStatus('Fixing permissions,70')

        Upgrade.fixPermissions()

        ##

        Upgrade.upgradeVersion()
        Upgrade.UpdateMaxSSLCons()

        command = 'systemctl restart lscpd'
        if not Upgrade.executioner(command, command, 1):
            self.PostStatus('Failed to execute %s. [404]' % (command))

        self.PostStatus('EaglePanel Upgraded/Downgraded to %s. [200]' % (self.branch))


def main():
    parser = argparse.ArgumentParser(description='EaglePanel Installer')
    parser.add_argument('--branch', help='Branch to install.')
    parser.add_argument('--mail', help='Upgrade mail services.')
    parser.add_argument('--dns', help='Upgrade dns services.')
    parser.add_argument('--ftp', help='Upgrade ftp services.')

    args = parser.parse_args()

    uc = UpgradeEaglePanel(args.branch,int(args.mail),int(args.dns),int(args.ftp))
    uc.UpgardeNow()


if __name__ == "__main__":
    main()