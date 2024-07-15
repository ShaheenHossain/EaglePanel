# -*- coding: utf-8 -*-


from django.test import TestCase
import json
import requests
import urllib3
from plogical.EagleEPLogFileWriter import EagleEPLogFileWriter as logging
from plogical.processUtilities import ProcessUtilities

urllib3.disable_warnings()


# Create your tests here.


class TestManageSSL(TestCase):
    httpClient = requests.Session()

    def MakeRequest(self, endPoint, data):
        json_data = json.dumps(data)
        path = 'https://eaglepanel.xyz:8090/%s' % (endPoint)
        result = TestManageSSL.httpClient.post(path, data=json_data, verify=False)
        return json.loads(result.text)

    def MakeRequestRaw(self, path):
        result = requests.get(path)
        return str(result.text)

    def setUp(self):
        ## Verify login

        data_ret = {'username': 'admin', 'password': '1234567'}
        response = self.MakeRequest('verifyLogin', data_ret)
        self.assertEqual(response['loginStatus'], 1)

    def test_issueSSL(self):
        ## Issue SSL

        data_ret = {'virtualHost': 'eaglepanel.xyz'}

        response = self.MakeRequest('manageSSL/issueSSL', data_ret)

        self.assertEqual(response['status'], 1)

        ## Verify SSL

        command = 'rm -rf /home/%s/public_html/' % ('eaglepanel.xyz')
        ProcessUtilities.normalExecutioner(command)

        command = 'mkdir /home/%s/public_html/' % ('eaglepanel.xyz')
        ProcessUtilities.normalExecutioner(command)

        command = 'chown cyberpa:cyberpa /home/%s/public_html/' % ('eaglepanel.xyz')
        ProcessUtilities.normalExecutioner(command)

        path = '/home/%s/public_html/index.html' % ('eaglepanel.xyz')

        writeToFile = open(path, 'w')
        writeToFile.write('EaglePanel')
        writeToFile.close()

        exists = 0
        if self.MakeRequestRaw('https://eaglepanel.xyz').find('EaglePanel') > -1:
            exists = 1

        self.assertEqual(exists, 1)

    def test_obtainHostNameSSL(self):
        ## Issue SSL

        data_ret = {'virtualHost': 'eaglepanel.xyz'}

        try:
            self.MakeRequest('manageSSL/obtainHostNameSSL', data_ret)
        except:
            pass

        import time
        time.sleep(2)

        ## Verify SSL

        path = '/usr/local/lscp/conf/key.pem'

        import os
        self.assertEqual(os.path.islink(path), True)

    def test_obtainMailServerSSL(self):
        ## Issue SSL

        data_ret = {'virtualHost': 'eaglepanel.xyz'}

        response = self.MakeRequest('manageSSL/obtainMailServerSSL', data_ret)

        self.assertEqual(response['status'], 1)

        ## Verify SSL

        path = '/etc/postfix/key.pem'

        import os
        self.assertEqual(os.path.islink(path), True)




