import sys
import ctypes

from PyQt5.QtCore import QDir, QThread
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QFileDialog, QDialog, \
    QApplication, QMainWindow, QMessageBox, QTableWidgetItem
from dbf import ver_33 as dbf

from Table2DBF_Main import Ui_MainWindow as GUI
from Table2DBF_Table import Ui_Updates
import table2dbf
import common
import gui_settings

myappid = u'mineguild.table2dbf.gui.0.5' # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


class WorkThread(QThread):
    def __init__(self, mw):
        QThread.__init__(self)
        self.mw = mw
        self.mbox = None
        self.updates = {}

    def run(self):
        mw = self.mw
        if mw.google_radio.isChecked():
            mw.start_button.setText("Loading...")
            mw.setEnabled(False)
            try:
                streetdb = table2dbf.load_from_google(mw.username.text(), mw.password.text(), mw.document_id.text())
            except:
                self.mbox = ("Google-Fail", QMessageBox.Warning, QIcon.fromTheme("dialog-warning"),
                        "Couldn't login or load data from google!", None)
                return
        else:
            streetdb = table2dbf.load_street_db(mw.csv_file.text())
        mw.start_button.setText("Updating...")
        try:
            table = dbf.Table(mw.dbf_file.text())
            table.open()
            self.updates = table2dbf.update_table(table, streetdb)
            table.close()
        except dbf.DbfError as e:
            self.mbox = ("DB-Fail", QMessageBox.Warning, QIcon.fromTheme("dialog-warning"),
                        "Couldn't open/update table!", e.message)
            return

        from pprint import pprint
        pprint(self.updates)
        mw.start_button.setText("Start")
        mw.setEnabled(True)


class TableDialog(QDialog, Ui_Updates):
    def __init__(self, updates):
        QDialog.__init__(self)
        self.setupUi(self)
        table = self.tableWidget
        table.setRowCount(len(updates)+1)
        table.setColumnCount(len(common.ATT))
        for i in range(len(common.ATT)):
            item = QTableWidgetItem(common.ATT_HR[common.ATT[i]])
            table.setItem(0, i, item)
        for i, street in enumerate(updates):
            changes = updates[street]
            row = []
            for z, att in enumerate(common.ATT_INV):
                found = False
                for change in changes:
                    if change.split(":")[0] == att:
                        row.append(change.split(":")[1])
                        found = True
                if not found:
                    row.append("")
            for x, update in enumerate(row):
                item = QTableWidgetItem(update)
                print(i+1, x, update)
                table.setItem(i+1, x, item)


class MainWindow(QMainWindow, GUI):
    def __init__(self):
        super(QMainWindow, self).__init__()
        # Set up the user interface from Designer.
        self.setupUi(self)
        self.open_dbf.clicked.connect(self.ask_dbf)
        self.open_csv.clicked.connect(self.ask_csv)
        self.google_radio.clicked.connect(self.switch_google)
        self.csv_radio.clicked.connect(self.switch_csv)
        self.start_button.clicked.connect(self.start)

        self.load_settings()

        if self.google_radio.isChecked():
            self.switch_google()
        else:
            self.switch_csv()
        self.adjustSize()

        self.changed_styles = []
        self.working_thread = None

    def ask_dbf(self):
        dialog = QFileDialog()
        filter = "DBF files (*.dbf)"
        dialog.setAcceptMode(QFileDialog.AcceptOpen)
        dialog.setFilter(QDir.Files)
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilter(filter)
        res = dialog.exec()
        if res:
            self.dbf_file.setText(dialog.selectedFiles()[0])

    def ask_csv(self):
        dialog = QFileDialog()
        filter = "CSV files (*.csv)"
        dialog.setAcceptMode(QFileDialog.AcceptOpen)
        dialog.setFilter(QDir.Files)
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilter(filter)
        res = dialog.exec()
        if res:
            self.csv_file.setText(dialog.selectedFiles()[0])

    def switch_csv(self):
        self.username.setEnabled(False)
        self.password.setEnabled(False)
        self.document_id.setEnabled(False)
        self.csv_file.setEnabled(True)
        self.open_csv.setEnabled(True)
        self.repaint()

    def switch_google(self):
        self.csv_file.setEnabled(False)
        self.open_csv.setEnabled(False)
        self.username.setEnabled(True)
        self.password.setEnabled(True)
        self.document_id.setEnabled(True)
        self.repaint()

    def start(self):
        incomplete = []
        if self.google_radio.isChecked():
            if not self.username.text():
                incomplete.append(self.username)
            if not self.password.text():
                incomplete.append(self.password)
            if not self.document_id.text():
                incomplete.append(self.document_id)
        elif not self.csv_file.text():
            incomplete.append(self.csv_file)
        if not self.dbf_file.text():
            incomplete.append(self.dbf_file)

        if len(incomplete) > 0:
            mbox = QMessageBox(self)
            mbox.setWindowTitle("Warning incomplete fields!")
            mbox.setIcon(QMessageBox.Warning)
            mbox.setWindowIcon(QIcon.fromTheme("dialog-warning"))
            mbox.setText("%d fields are incomplete" % len(incomplete))
            mbox.exec()
            for field in self.changed_styles:
                field.setStyleSheet("")
            for field in incomplete:
                field.setStyleSheet("border: 1.5px solid red; border-radius: 5px")
            self.changed_styles = incomplete.copy()
            return
        for field in self.changed_styles:
            field.setStyleSheet("")

        self.working_thread = WorkThread(self)
        self.working_thread.finished.connect(self.finished_start)
        self.working_thread.start()

    def finished_start(self):
        self.save_settings()
        self.start_button.setText("Start")
        self.setEnabled(True)
        if self.working_thread.mbox:
            data = self.working_thread.mbox
            mbox = QMessageBox(self)
            mbox.setWindowTitle(data[0])
            mbox.setIcon(data[1])
            mbox.setWindowIcon(data[2])
            mbox.setText(data[3])
            if data[4]:
                mbox.setDetailedText(data[4])
            mbox.exec()
        if self.working_thread.updates:
            d = TableDialog(self.working_thread.updates)
            d.exec()

    def save_settings(self):
        settings = common.get_gui_settings()
        settings.beginGroup("MainWindow")
        gui_settings.guisave(self, settings)
        settings.endGroup()

    def load_settings(self):
        settings = common.get_gui_settings()
        settings.beginGroup("MainWindow")
        gui_settings.guirestore(self, settings)
        settings.endGroup()


if __name__== "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())



