#!/usr/bin/env python
__author__ = 'Abi'
import sys
from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import subprocess as sp
import time
import smtplib

global b,c,stop_var,diskThreshold
b = []
c = []
pvar = {}
#Replace below 4 fields with your own credentials
sender = str("sender@domain.com")
passwd = str("sendermailpassword")
receiver = 'receiver@domain.com'
#Disk Threshold % value
diskThreshold = int(80)
disk = ''

qtCreatorFile = "mon.ui" # Enter file here.

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class MyApp(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.setWindowTitle('Disk Monitor')
        self.stop_pushButton.hide()
        self.start_pushButton.clicked.connect(self.mon)
        self.wt = workerThread()
        self.connect(self.wt,SIGNAL("mon_success"),self.threadDone)
        self.connect(self.wt,SIGNAL("set_label"),self.set_label)
        self.stop_pushButton.clicked.connect(self.stop_mon)
        #self.setting_pushButton.clicked.connect(self.settings)
        self.exit_pushButton.clicked.connect(self.exit_gui)

    def set_label(self):
        global mail_stat
        self.mail_stat_label.setText(mail_stat)

    def exit_gui(self):
        exit()

    def mon(self):
        global stop_var
        stop_var = 0
        self.wt.start()

    def stop_mon(self):
        global stop_var
        stop_var = 1

    def threadDone(self):
        global b
        #print b
        self.mon_tableWidget.clearContents()
        for i in range(len(b)-1):
            for j in range(6):
                if j != 1 :
                    no = QtGui.QTableWidgetItem("%d" %(i+1) )
                    no.setTextAlignment(Qt.AlignCenter)
                    self.mon_tableWidget.setItem(i, j , no)
                    itm = b[i][j]
                    item = QtGui.QTableWidgetItem("%s" %itm )
                    item.setTextAlignment(Qt.AlignCenter)
                    if j == 0:
                        j =1
                    self.mon_tableWidget.setItem(i,j, item)
        del b[:]

class workerThread(QThread):
    def __int__(self, parent=None):
        super(workerThread,self).__init__(parent)

    def run(self):
        global b,c
        def sndmail(sender,passwd,receiver,dsk):
            global mail_stat
            message = 'From:'+sender+'\n'+\
                'To:'+receiver+'\n'+\
                'Subject: Excess Disk Usage Alert'+'\n\n'+\
                'Excess Disk Usage on :' + dsk +'\n\n'
            try:
                smtpObj = smtplib.SMTP('smtp.gmail.com',587)
                smtpObj.ehlo()
                smtpObj.starttls()
                smtpObj.login(sender,passwd)
                print "success"
                smtpObj.sendmail(sender, receiver, message)
                print "Successfully sent email"
                mail_stat = "Successfully sent email"
            except:
                print "Error: unable to send email"
                mail_stat = "Error: unable to send email"

            finally:
                self.emit(SIGNAL("set_label"))
                if stop_var != 1:
                    time.sleep(600)#keep running thread once in 10 Minutes
                    print stop_var
                    Mon()

        def checkdsk(pvar,c):
            global disk,diskThreshold
            for key in pvar:
                if (pvar[key] >= diskThreshold):
                    disk = disk +str('\nDisk:\t' +c[key][0]+ '\nMounted on:\t' +c[key][5]+ '\n')
            if (disk != ''):
                print disk
                sndmail(sender,passwd,receiver,disk)
                #print c[key][0], c[key][5]

        def Mon():
            a = sp.check_output(['df','-m']).split('\n')
            n = len(a) + 1
            for i in range(2,n):
                a1 = a[i-1].split()
                b.append(a1)
            c = b
            self.emit(SIGNAL("mon_success"))
            for i in range(len(c)-1):
                pvar[i] = int(c[i][4].replace('%',''))
            checkdsk(pvar,c)
        Mon()

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())