import sys
import ctypes

from PyQt5.Qt import *
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
        self.streetdb = None

    def run(self):
        mw = self.mw
        if mw.google_radio.isChecked():
            mw.setStatusTip("Loading...")
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
        mw.setStatusTip("Updating...")
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
        self.streetdb = streetdb


class TableDialog(QDialog, Ui_Updates):
    def __init__(self, updates, streetdb):
        QDialog.__init__(self)
        self.setupUi(self)
        table = self.tableWidget
        table.setRowCount(len(updates)+1)
        table.setColumnCount(len(common.ATT))
        self.setWindowTitle("Overview")

        for i in range(len(common.ATT)):
            item = QTableWidgetItem(common.ATT_HR[common.ATT[i]])
            table.setItem(0, i, item)
        for i, street in enumerate(updates):
            changes = updates[street]
            row = []
            for z in range(len(common.ATT)):
                found = False
                att = common.ATT[z]
                print(att)
                for change in changes:
                    split = change.split(":")
                    if split[0] == att:
                        row.append(split[1])
                        found = True
                if not found:
                    row.append(streetdb[street][att])
            for x, update in enumerate(row):
                item = QTableWidgetItem(update)
                if "->" in update:
                    item.setForeground(Qt.red)
                print(i+1, x, update)
                table.setItem(i+1, x, item)
        self.load_settings()

    def closeEvent(self, evt):
        self.save_settings()
        super(TableDialog).closeEvent(evt)

    def load_settings(self):
        settings = common.get_gui_settings()
        settings.beginGroup("table")
        if settings.value("geometry"):
            self.restoreGeometry(settings.value("geometry"))
        settings.endGroup()

    def save_settings(self):
        settings = common.get_gui_settings()
        settings.beginGroup("table")
        settings.setValue("geometry", self.saveGeometry())
        settings.endGroup()

class MainWindow(QMainWindow, GUI):
    def __init__(self):
        super(QMainWindow, self).__init__()
        # Set up the user interface from Designer.
        self.setupUi(self)
        self.setStatusTip("Ready")
        self.open_dbf.clicked.connect(self.ask_dbf)
        self.open_csv.clicked.connect(self.ask_csv)
        self.google_radio.clicked.connect(self.switch_google)
        self.csv_radio.clicked.connect(self.switch_csv)
        self.start_button.clicked.connect(self.start)
        self.actionAbout.triggered.connect(self.show_about)
        self.adjustSize()
        self.load_settings()

        if self.google_radio.isChecked():
            self.switch_google()
        else:
            self.switch_csv()

        self.changed_styles = []
        self.working_thread = None

    def show_about(self):
        about = "<html>Table2DBF by Korbinian Stein (2015)<br>P-Seminar (FLG Planegg) Digitaler Stadtplan: " \
                "'Subjektive Lebenssituation'<br><a href='https://github.com/nylser/P-Seminar-Util'>GitHub</a></html>"
        QMessageBox.about(self, "About this program", about)

    def ask_dbf(self):
        res = open_file(self, "DBF files (*.dbf)")
        if res:
            self.dbf_file.setText(res)

    def ask_csv(self):
        res = open_file(self, "CSV files (*.csv)")
        if res:
            self.csv_file.setText(res)

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

    def closeEvent(self, evnt):
        self.save_settings()
        super(MainWindow, self).closeEvent(evnt)


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
            mbox.setWindowTitle("Warning, incomplete fields!")
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
        self.setStatusTip("Working...")
        self.working_thread = WorkThread(self)
        self.working_thread.finished.connect(self.finished_start)
        self.working_thread.start()

    def finished_start(self):
        self.save_settings()
        self.start_button.setText("Start")
        self.setEnabled(True)
        self.setStatusTip("Ready")
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
            d = TableDialog(self.working_thread.updates, self.working_thread.streetdb)
            d.exec()
        else:
            mbox = QMessageBox(self)
            mbox.setWindowTitle("Done!")
            mbox.setText("Program is done! Everything was up to date!")
            mbox.setIcon(QMessageBox.Information)
            mbox.exec()

    def save_settings(self):
        settings = common.get_gui_settings()
        settings.beginGroup("MainWindow")
        gui_settings.guisave(self, settings)
        settings.setValue("state", self.saveGeometry())
        settings.endGroup()

    def load_settings(self):
        settings = common.get_gui_settings()
        settings.beginGroup("MainWindow")
        gui_settings.guirestore(self, settings)
        if settings.value("state"):
            self.restoreGeometry(settings.value("state"))
        settings.endGroup()


def open_file(parent, filter):
    dialog = QFileDialog()
    dialog.setAcceptMode(QFileDialog.AcceptOpen)
    dialog.setFilter(QDir.Files)
    dialog.setFileMode(QFileDialog.ExistingFile)
    dialog.setNameFilter(filter)
    res = dialog.exec()
    if res:
        return dialog.selectedFiles()[0]


if __name__== "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
