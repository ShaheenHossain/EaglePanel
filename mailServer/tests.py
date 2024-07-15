# -*- coding: utf-8 -*-


from django.test import TestCase
import json
from plogical.EagleEPLogFileWriter import EagleEPLogFileWriter as logging
import requests
import time
from plogical.processUtilities import ProcessUtilities
import urllib3
urllib3.disable_warnings()
# Create your tests here.


class TestMailServer(TestCase):
    httpClient = requests.Session()

    def MakeRequest(self, endPoint, data):
        json_data = json.dumps(data)
        path = 'https://eaglepanel.xyz:8090/%s' % (endPoint)
        result = TestMailServer.httpClient.post(path, data=json_data, verify=False)
        return json.loads(result.text)

    def MakeRequestRaw(self, path):
        result = requests.get(path)
        return str(result.text)

    def setUp(self):
        ## Verify login

        data_ret = {'username': 'admin', 'password': '1234567'}
        response = self.MakeRequest('verifyLogin', data_ret)
        self.assertEqual(response['loginStatus'], 1)

        ## Issue SSL

        data_ret = {'virtualHost': 'eaglepanel.xyz'}

        response = self.MakeRequest('manageSSL/obtainMailServerSSL', data_ret)
        self.assertEqual(response['status'], 1)
        ## Verify SSL

        path = '/etc/postfix/key.pem'

        import os
        self.assertEqual(os.path.islink(path), True)

    def test_submitEmailCreation(self):

        ## Create Email

        data_ret = {'domain': 'eaglepanel.xyz', 'username':'helloworld', 'passwordByPass':'helloworld'}

        response = self.MakeRequest('email/submitEmailCreation', data_ret)

        self.assertEqual(response['status'], 1)

        ## Test Email
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText


        try:
            ok = 1
            smtpServer = smtplib.SMTP('eaglepanel.xyz', 25)
            smtpServer.login('helloworld@eaglepanel.xyz', 'helloworld')

            message = MIMEMultipart('alternative')
            message['Subject'] = 'Test Email'
            message['From'] = 'Unit Test' + ' ' + 'helloworld@eaglepanel.xyz'
            message['reply-to'] = 'helloworld@eaglepanel.xyz'
            html = MIMEText('Hello World', 'html')
            message.attach(html)
            smtpServer.sendmail(message['From'], 'usman@cyberpersons.com', message.as_string())
        except BaseException:
            ok = 0

        self.assertEqual(ok, 1)

        ## Check deletion

        data_ret = {'email': 'helloworld@eaglepanel.xyz'}

        response = self.MakeRequest('email/submitEmailDeletion', data_ret)

        self.assertEqual(response['status'], 1)

        try:
            ok = 1
            smtpServer = smtplib.SMTP('eaglepanel.xyz', 25)
            smtpServer.login('helloworld@eaglepanel.xyz', 'helloworld')

            message = MIMEMultipart('alternative')
            message['Subject'] = 'Test Email'
            message['From'] = 'Unit Test' + ' ' + 'helloworld@eaglepanel.xyz'
            message['reply-to'] = 'helloworld@eaglepanel.xyz'
            html = MIMEText('Hello World', 'html')
            message.attach(html)
            smtpServer.sendmail(message['From'], 'usman@cyberpersons.com', message.as_string())
        except BaseException:
            ok = 0

        self.assertEqual(ok, 0)