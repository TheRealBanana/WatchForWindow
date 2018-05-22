import smtplib
import threading
import win32gui
from PyQt4.QtCore import SIGNAL

class guiFunctions(object):
    def __init__(self, ctx):
        super(guiFunctions, self).__init__()
        self.quitting = False
        self.ctx = ctx
        self.found_window_titles = []
        #Not a good thing to do normally but we arent going to update this app probably
        self.text_fields_to_check = []
        self.text_fields_to_check.append(self.ctx.windowName)
        self.text_fields_to_check.append(self.ctx.hostnameIPTextbox)
        self.text_fields_to_check.append(self.ctx.portTextbox)
        self.text_fields_to_check.append(self.ctx.usernameTextbox)
        self.text_fields_to_check.append(self.ctx.passwordTextbox)
        self.text_fields_to_check.append(self.ctx.emailFromTextbox)
        self.text_fields_to_check.append(self.ctx.emailToTextbox)
        self.text_fields_to_check.append(self.ctx.emailSubjectTextbox)
        self.text_fields_to_check.append(self.ctx.emailMessageTextbox)
    
    def appQuitting(self):
        self.quitting = True
    
    def watchForWindowCallback(self, window_handle, search_text):
        if search_text.lower() in str(win32gui.GetWindowText(window_handle)).lower():
            #Found our window!
            window_title = str(win32gui.GetWindowText(window_handle))
            if window_title not in self.found_window_titles:
                email_message = "New window titled %s has been detected" % window_title
                self.ctx.MW.emit(SIGNAL("sendEmail"), email_message, False)
                print "Found window! %s" % window_title
                self.found_window_titles.append(window_title)
                return False
    
    def watchForWindows(self):
        print "Checking windows again...."
        try:
            win32gui.EnumWindows(self.watchForWindowCallback, str(self.ctx.windowName.text()))
        except:
            pass
    
    def updateTLSState(self, checkstate):
        self.tls = bool(checkstate)
    
    def firstRunOK(self):
        message = "<html><head/><body><p><span style=\" font-weight:600; color:#00CC00;\">Watching for new windows...</span></p></body></html>"
        self.ctx.MW.emit(SIGNAL("updateStatusBar"), message, False)
        #self.ctx.curentStatusLabel.setText(message)
        #self.ctx.curentStatusLabel.repaint()
        
        self.ctx.timer.start(1000)
    
    def startButton(self):
        #Check our fields to be sure they have something
        for text_field in self.text_fields_to_check:
            if len(text_field.text()) == 0:
                return False
        
        message = "<html><head/><body><p><span style=\" font-weight:600; color:#ff8700;\">Testing email settings...</span></p></body></html>"
        self.ctx.MW.emit(SIGNAL("updateStatusBar"), message, False)
        self.ctx.MW.emit(SIGNAL("sendEmail"), ["Watching for windows...", "FIRSTRUN"], False)
        
    def stopButton(self):
        message = "<html><head/><body><p><span style=\" font-weight:600; color:#ff0000;\">Not watching for new windows...</span></p></body></html>"
        self.ctx.MW.emit(SIGNAL("updateStatusBar"), message, False)
        self.ctx.timer.stop()
    
    
    def sendEmailFailed(self, reason):
        message = "<html><head/><body><p><span style=\" font-weight:600; color:#ff0000;\">%s</span></p></body></html>" % reason
        self.ctx.MW.emit(SIGNAL("updateStatusBar"), message, False)
        
    def updateStatusBar(self, message):
        self.ctx.curentStatusLabel.setText(message)
        self.ctx.curentStatusLabel.repaint()
    
    def sendEmail(self, message):
        fr = False
        if isinstance(message, list):
            fr = True
            message = message[0]
        message_data = {}
        message_data["message"] = str(message)
        message_data["subject"] = str(self.ctx.emailSubjectTextbox.text())
        message_data["from_addr"] = str(self.ctx.emailFromTextbox.text())
        message_data["to_addr"] = str(self.ctx.emailToTextbox.text())
        
        server_data = {}
        server_data["server"] = str(self.ctx.hostnameIPTextbox.text())
        server_data["port"] = str(self.ctx.portTextbox.text())
        server_data["username"] = str(self.ctx.usernameTextbox.text())
        server_data["password"] = str(self.ctx.passwordTextbox.text())
        server_data["tls"] = bool(self.ctx.emailUseTLSCheck.checkState())
        
        emailer = Emailer(self.ctx, message_data, server_data)
        emailer.run()
        if fr is True:
            self.ctx.MW.emit(SIGNAL("firstRunOK"))
        

class Emailer(threading.Thread):
    def __init__(self, ctx, message_data={}, server_data={}):
        
        self.message = '''From: %s
To: %s
Subject: %s
Content-Type: text/html; charset=ISO-8859-1

<!DOCTYPE html PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">
<html>
<head></head>
<body>
%s
</body>
</html> ''' % (message_data["from_addr"], message_data["to_addr"], message_data["subject"], message_data["message"])
        self.from_addr = message_data["from_addr"]
        self.to_addr = message_data["to_addr"]
        self.server = server_data["server"]
        self.port = server_data["port"]
        self.username = server_data["username"]
        self.password = server_data["password"]
        self.tls = server_data["tls"]
        self.ctx = ctx
        super(Emailer, self).__init__()
        
    def run(self):
        
        
        
        try:
            smtpconn = smtplib.SMTP(self.server, int(self.port))
            smtpconn.ehlo()
        except:
            self.ctx.MW.emit(SIGNAL("sendEmailFailed"), "Error connecting to server", False)
            return False
        
        if self.tls:
            smtpconn.starttls()
            smtpconn.ehlo()
        try:
            smtpconn.login(self.username, self.password)
        except:
            self.ctx.MW.emit(SIGNAL("sendEmailFailed"), "Failed to authenticate with server", False)
            return False
        
        smtpconn.sendmail(self.from_addr, self.to_addr, self.message)
        smtpconn.close()
