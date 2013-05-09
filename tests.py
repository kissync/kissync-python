from smartfile import OAuthClient
from PyQt4 import QtCore, QtGui
from main import Main

import unittest
import sys
import time


class LoginTestCase(unittest.TestCase):
    def test_login(self):
        api = OAuthClient("zGSJpILRq2889Ne2bPBdEmEZLsRHpe", "KOb97irJG84PJ8dtEkoYt2Kqwz3VJa")
        try:
            api.get_request_token()
            client_token = api.get_authorization_url()
        except:
            oauthtest = False
        else:
            oauthtest = True

        self.assertTrue(oauthtest)


class MainWindowCase(unittest.TestCase):
    def test_main(self):
        app = QtGui.QApplication(sys.argv)
        mainwindow = Main()
        mainwindow.exit()
        
if __name__ == '__main__':
    unittest.main()
