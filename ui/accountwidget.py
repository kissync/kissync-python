import hashlib
import os
import sys
import urllib
import webbrowser

from PySide import QtGui, QtCore


class LogoutLabel(QtGui.QLabel):
    def __init__(self, parent):
        QtGui.QLabel.__init__(self)
        self.parent = parent
        self.setText("Logout")
        self.setStyleSheet("color: #1BA1E2; font-size: 14pt;")

    def mousePressEvent(self, event):
        ###print "Logout button pressed"
        reply = QtGui.QMessageBox.question(self, 'SmartFile', "Are you sure you want to logout? SmartFile will close afterwards.", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            self.parent.parent.tray.notification("SmartFile", "Logging out...")
            try:
                os.remove(self.parent.parent.settingsFile)
                os._exit(-1)
            except:
                raise
        else:
            event.ignore()

    def mouseDoubleClickEvent(self, event):
        pass

    def enterEvent(self, event):
        self.setStyleSheet("color: #8CBF26; font-size: 14pt;")
        self.repaint()

    def leaveEvent(self, event):
        self.setStyleSheet("color: #1BA1E2; font-size: 14pt;")
        self.repaint()


class UsernameLabel(QtGui.QLabel):
    def __init__(self, parent=None, fullname=""):
        QtGui.QLabel.__init__(self)
        self.parent = parent
        self.setText(fullname)
        self.setStyleSheet("color: #000000; font-size: 14pt;")
        self.repaint()

    """
    def mousePressEvent(self, event):
        webbrowser.open('https://app.smartfile.com/ftp/private/account/')
    """

    def mouseDoubleClickEvent(self, event):
        pass


class EmailLabel(QtGui.QLabel):
    def __init__(self, parent=None, email=""):
        QtGui.QLabel.__init__(self)
        self.parent = parent
        self.setText(email)
        self.setStyleSheet("color: #888888; font-size: 12pt;")
        self.repaint()


class AvatarWidget(QtGui.QWidget):
    def __init__(self, parent=None, email=None):
        QtGui.QWidget.__init__(self)
        self.parent = parent
        self.email = email

        self.setStyleSheet("QWidget { border: 0px; }")

        self.setMinimumSize(64, 64)
        self.setMaximumSize(64, 64)

        self.gridlayout = QtGui.QGridLayout()

        #TODO: initializing this takes too long
        #self.addIcon(self.email)

    def addIcon(self, email):
        self.icon = QtGui.QImage()
        size = 64
        gravatar_url = "http://www.gravatar.com/avatar/" + hashlib.md5(email.lower()).hexdigest() + "?s=" + str(size)
        img_file = urllib.urlopen(gravatar_url).read()
        self.icon.loadFromData(img_file, "JPG")
        self.icontarget = QtCore.QRectF(0, 0, 64, 64)

    """
    def paintEvent(self, e):
        painter = QtGui.QPainter()
        painter.begin(self)
        # Draw Item Thumbnail.
        painter.drawImage(self.icontarget, self.icon)
        painter.end()
    """

    def mousePressEvent(self, event):
        webbrowser.open('http://www.gravatar.com/')

    def mouseDoubleClickEvent(self, event):
        pass


class AccountWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self)
        self.parent = parent

        self.setMinimumSize(300, 125)
        self.setMaximumSize(300, 125)

        #self.setStyleSheet('QWidget { font-size: 14pt; }')

        ##get rid of the widget border
        #self.setStyleSheet("QWidget { border: 0px; }")

        #Call API to get full name and email address.
        try:
            tree = self.parent.parent.smartfile.get('/whoami', '/')
            if 'user' in tree:
                self.fullname = tree['user']['name']
                self.email = tree['user']['email']
            else:
                raise
        except:
            self.fullname = "SmartFile User"
            self.email = "user@smartfile.com"

        textTitle = QtGui.QLabel()
        textEmail = EmailLabel(self, self.email)
        self.textFullName = UsernameLabel(self, self.fullname)
        self.textLogout = LogoutLabel(self)

        textTitle.setText("Currently logged in as:")

        self.gridlayout = QtGui.QGridLayout()

        #self.gridlayout.addWidget(self.textFullName, 0, 0, 1, 1, QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.gridlayout.addWidget(self.textFullName, 0, 0, 1, 1, QtCore.Qt.AlignCenter)
        self.gridlayout.addWidget(textEmail, 1, 0, 1, 1, QtCore.Qt.AlignCenter)
        #self.gridlayout.addWidget(self.textLogout, 3, 0, 1, 1)

        self.setLayout(self.gridlayout)


class Main(QtGui.QWidget):
    def __init__(self, parent=None):
        super(Main, self).__init__(parent)
        self.setWindowTitle('Account Widget Test')
        self.setGeometry(400, 200, 300, 325)
        #Add Account Widget with dummy info.
        self.accountInfo = AccountWidget(self)
        self.grid = QtGui.QGridLayout()
        self.grid.addWidget(self.accountInfo)
        self.setLayout(self.grid)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    mainwindow = Main()
    mainwindow.show()
    sys.exit(app.exec_())
