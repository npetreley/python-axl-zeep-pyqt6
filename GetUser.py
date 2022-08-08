from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from lxml import etree
from requests import Session
from requests.auth import HTTPBasicAuth
from zeep import Client, Settings, Plugin
from zeep.transports import Transport
from zeep.cache import SqliteCache

import argparse

import sys

# Parse command line arguments. Default are sample values for DevNet sandbox
# Overwrite them with values for your own CUCM using command line args
def parse_args():

    parser = argparse.ArgumentParser()
    parser.add_argument('-u', dest='username', help="AXL username", required=False, default='administrator')
    parser.add_argument('-p', dest='password', help="AXL user password", required=False, default='ciscopsdt')
    parser.add_argument('-s', dest='server', help="CUCM hostname or IP address", required=False,default='10.194.104.83')
    args = parser.parse_args()
    return vars(args)

class MainWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.initUI()

        # The WSDL is a local file
        WSDL_URL = 'AXLAPI.wsdl'

        # Parse command line arguments
        cmdargs = parse_args()
        USERNAME, PASSWORD, SERVER = (
            cmdargs['username'], cmdargs['password'], cmdargs['server'] )
        CUCM_URL = 'https://' + SERVER + ':8443/axl/'

        # This is where the meat of the application starts
        # The first step is to create a SOAP client session
        session = Session()

        # We avoid certificate verification by default, but you can set your certificate path
        # here instead of the False setting
        session.verify = False
        session.auth = HTTPBasicAuth(USERNAME, PASSWORD)

        transport = Transport(session=session, timeout=10, cache=SqliteCache())

        # strict=False is not always necessary, but it allows zeep to parse imperfect XML
        settings = Settings(strict=False, xml_huge_tree=True)

        client = Client(WSDL_URL, settings=settings, transport=transport)

        self.service = client.create_service("{http://www.cisco.com/AXLAPIService/}AXLAPIBinding", CUCM_URL)

    def initUI(self):

        button = QPushButton("Search Username")
        self.input = QLineEdit()

        hbox = QHBoxLayout()
        hbox.addWidget(button)
        hbox.addWidget(self.input)
        self.input.setText('nicholas')

        button.clicked.connect(self.search_user)

        self.vbox = QVBoxLayout()
        self.vbox.addLayout(hbox)
        self.vbox.addStretch(1)

        self.setLayout(self.vbox)
        self.setWindowTitle("getUser")
        self.show()

    def search_user(self):
        userid = self.input.text()
        criteria = {
            'userid' : userid
        }
        response = self.service.getUser(**criteria)

        self.resBox = QGroupBox("Results")
        self.vresBox = QVBoxLayout()
        self.resBox.setLayout(self.vresBox)

        d = response['return']['user']
        self.fl = QLabel('First Name')
        self.fe = QLineEdit(d['firstName'])
        self.ll = QLabel('Last Name')
        self.le = QLineEdit(d['lastName'])
        self.dl = QLabel('Display Name')
        self.de = QLineEdit(d['displayName'])

        self.groupBox = QGroupBox("User")
        self.gridBox = QGridLayout()
        self.groupBox.setLayout(self.gridBox)
        self.gridBox.addWidget(self.fl,0,0)
        self.gridBox.addWidget(self.fe,0,1)
        self.gridBox.addWidget(self.ll,1,0)
        self.gridBox.addWidget(self.le,1,1)
        self.gridBox.addWidget(self.dl,2,0)
        self.gridBox.addWidget(self.de,2,1)

        self.adGroup = QGroupBox("Associated Devices")
        self.advbox = QVBoxLayout()
        self.adGroup.setLayout(self.advbox)

        ad = response['return']['user']['associatedDevices']['device']
        values = dict()
        for value in ad:
            values[ad.index(value)] = QLineEdit(value)
            self.advbox.addWidget(values[ad.index(value)])

        self.resetButton = QPushButton("Reset")
        self.resetButton.clicked.connect(self.resetBox)

        self.vresBox.addWidget(self.groupBox)
        self.vresBox.addWidget(self.adGroup)
        self.vresBox.addWidget(self.resetButton)
        self.vbox.addWidget(self.resBox)
        self.show()

    def resetBox(self):
        self.resBox.close()

def main():

    app = QApplication(sys.argv)
    su = MainWindow()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()

app.exec()
