import sys
from WatchForWindow_UI import WFWMainDialog
from PyQt4 import QtGui
from PyQt4.QtCore import SIGNAL

class ModMainWindow(QtGui.QDialog):
    def __init__(self, parent=None):
        super(ModMainWindow, self).__init__(parent)
        self._user_accept_close = False
        self.setAcceptDrops(True)
        self.ui = None

    def closeEvent(self, event):
        self.emit(SIGNAL("appClosing"))

def main():
    app = QtGui.QApplication(sys.argv)
    MainDialog = ModMainWindow()
    ui = WFWMainDialog()
    MainDialog.ui = ui
    ui.setupUi(MainDialog)
    MainDialog.show()
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    main()