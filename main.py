#! python3

"""
Version: MPL 1.1

The contents of this file are subject to the Mozilla Public License Version
1.1 the "License"; you may not use this file except in compliance with
the License. You may obtain a copy of the License at
http://www.mozilla.org/MPL/

Software distributed under the License is distributed on an "AS IS" basis,
WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
for the specific language governing rights and limitations under the
License.

The Original Code is the open.mp server browser.

The Initial Developer of the Original Code is Adib "adib_yg".
Portions created by the Initial Developer are Copyright (c) 2023
the Initial Developer. All Rights Reserved.

Contributor(s):
  adib-yg

Special Thanks to:
  open.mp team
  icons8.com
"""

from PyQt5 import QtWidgets, QtGui, QtCore, QtTest, uic 
#from PyQt5.QtWidgets import QMessageBox
import sys
import requests
import resources_rc
from pathlib import Path
import json
import hashlib
import os

home = Path.home()

#favourites_list = ['91.218.67.206:7777']

errormsg = ''

try:
    with open(home / "Documents" / "GTA San Andreas User Files" / "launcher-settings.json", "x") as f:
        f.write('{"omppath":"", "gamepath":"","username":""}')
        f.flush()
except FileExistsError:
    pass

with open(home / "Documents" / "GTA San Andreas User Files" / "launcher-settings.json") as f:
    global settings 
    settings = json.load(f)


# try:
#     with open(home / "Documents" / "GTA San Andreas User Files" / "launcher-settings.json") as f:
#         data = json.load(f)
#         try:
#             if data['gamepath'] and data['omppath'] and data['username']:
#                 pass
#         except Exception as e:
#             errormsg = "Your settings are set incorrecly, you should have a json file called launcher-settings.json in your GTA User Files directory, which has gamepath, omppath, and username set.\n {e}"
 
# except Exception as e:
#     errormsg = f"You do not have a config file! {e}"
#     pass


try:
    with open(home / "Documents" / "GTA San Andreas User Files" / "launcher-favourites.txt", "x") as f:
        pass
except FileExistsError:
    pass



class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()

        self.favourites_list = open(home / "Documents" / "GTA San Andreas User Files" / "launcher-favourites.txt", "r+") 
        self.fake_favourites = self.favourites_list.read().split(',')
        self.favourites_list.seek(0)


        # Load UI file from resources
        stream = QtCore.QFile(":/uiPrefix/form.ui")
        stream.open(QtCore.QFile.ReadOnly)
        uic.loadUi(stream, self)
        stream.close()

        self.iconOpenMp = QtGui.QIcon()
        self.iconOpenMp.addPixmap(
            QtGui.QPixmap(":/imagesPrefix/icons/open-mp-icon.ico"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.On)

        self.iconSamp = QtGui.QIcon()
        self.iconSamp.addPixmap(
            QtGui.QPixmap(":/imagesPrefix/icons/samp-icon.ico"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.On)

        self.setWindowTitle("open.mp server browser")
        self.setWindowIcon(self.iconOpenMp)
        self.setMinimumSize(846, 568)

        self.tableWidget.setColumnWidth(0, 130)
        self.tableWidget.setColumnWidth(1, 250)
        self.tableWidget.setColumnWidth(3, 170)
        self.tableWidget.setColumnWidth(4, 100)

        self.tableWidget.clicked.connect(self.on_clicked_row)
        self.tableWidget.doubleClicked.connect(self.on_double_clicked_row)

        self.pushButtonRefresh.clicked.connect(self.on_clicked_button_refresh)

        self.lineEdit.textChanged.connect(self.on_line_edit_changed)

        self.checkBoxFavourites.stateChanged.connect(
            self.on_favourites_check_box_state_changed)

        self.checkBoxOpenMpServers.stateChanged.connect(
            self.on_omp_check_box_state_changed)

        self.checkBoxSampServers.stateChanged.connect(
            self.on_samp_check_box_state_changed)

        self.actionTheme.triggered.connect(self.on_triggered_action_theme)
        self.actionSettings.triggered.connect(self.on_triggered_action_settings)
        self.actionOMP_Downloader.triggered.connect(self.on_triggered_action_omp_downloader)

        self.downloaderWindow = None
        self.settingsWindow = None

        if (settings['omppath'] or settings['gamepath'] or settings['username']) == '':
            print(settings['omppath'])
            print(settings['gamepath'])
            print(settings['username'])
            if self.settingsWindow == None:
                self.settingsWindow = SettingsWindow()
            self.settingsWindow.exec_()
            
        if CHECK_FOR_OMP_PLUGIN_UPDATES == True:
            self.checkForOpenMpUpdates()

        self.current_theme = "Light"

        if detect_darkmode_in_windows():
            self.setThemeDarkMode()

#        if CHECK_FOR_UPDATES:
#            self.checkForUpdates()

        servers_count, players_count = self.loadServerList()

        try:
            self.fake_favourites.remove('')
        except Exception:
            pass
        
    
        collist = self.get_full_column(0)
        for i in self.fake_favourites:
            if i not in collist:
                self.addServer(
                f"{i}",
                "",
                0,
                0,
                "",
                "",
                "",
                False,
                False)


        self.setLabelOnlineServersText(str(servers_count))
        self.setLabelOnlinePlayersText(str(players_count))
        

    def addServer(
            self,
            ip: str,
            hostname: str,
            players_count: int,
            players_max: int,
            gamemode: str,
            version: str,
            language: str,
            password: bool,
            omp: bool) -> None:

        rowPosition = self.tableWidget.rowCount()
        self.tableWidget.insertRow(rowPosition)

        numcols = self.tableWidget.columnCount()
        numrows = self.tableWidget.rowCount()
        row = numrows - 1

        self.tableWidget.setRowCount(numrows)
        self.tableWidget.setColumnCount(numcols)

        self.tableWidget.setItem(row, 0, QtWidgets.QTableWidgetItem(ip))

        self.tableWidget.setItem(row, 1, QtWidgets.QTableWidgetItem(hostname))

        self.tableWidget.setItem(
            row,
            2,
            QtWidgets.QTableWidgetItem(
                f"{str(players_count)}/{str(players_max)}"))

        self.tableWidget.setItem(row, 3, QtWidgets.QTableWidgetItem(gamemode))

        self.tableWidget.setItem(row, 4, QtWidgets.QTableWidgetItem(language))

        self.tableWidget.setItem(row, 5, QtWidgets.QTableWidgetItem(version))

        if password:
            item = QtWidgets.QTableWidgetItem("Yes")

            item.setTextAlignment(
                QtCore.Qt.AlignLeading | QtCore.Qt.AlignVCenter)
            brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
            brush.setStyle(QtCore.Qt.NoBrush)
            item.setBackground(brush)
            brush = QtGui.QBrush(QtGui.QColor(170, 0, 0))
            brush.setStyle(QtCore.Qt.SolidPattern)
            item.setForeground(brush)

            self.tableWidget.setItem(row, 6, item)
        else:
            item = QtWidgets.QTableWidgetItem("No")
            self.tableWidget.setItem(row, 6, item)

        if omp:
            item = QtWidgets.QTableWidgetItem("Yes")

            item.setTextAlignment(
                QtCore.Qt.AlignLeading | QtCore.Qt.AlignVCenter)
            brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
            brush.setStyle(QtCore.Qt.NoBrush)
            item.setBackground(brush)
            brush = QtGui.QBrush(QtGui.QColor(170, 0, 0))
            brush.setStyle(QtCore.Qt.SolidPattern)
            item.setForeground(brush)

            self.tableWidget.setItem(row, 7, item)

            item = QtWidgets.QTableWidgetItem()
            item.setIcon(self.iconOpenMp)
            self.tableWidget.setVerticalHeaderItem(row, item)

            if self.checkBoxFavourites.isChecked():
                self.checkBoxOpenMpServers.setEnabled(False)
                self.checkBoxSampServers.setEnabled(False)
                self.lineEdit.setEnabled(False)
                for row in range(self.tableWidget.rowCount()):
                    item = self.tableWidget.item(row, 0)
                    if item.text() in self.fake_favourites:
                        self.tableWidget.setRowHidden(row, False)
                    else:
                        self.tableWidget.setRowHidden(row, True)
            
            else:
                if self.checkBoxOpenMpServers.isChecked():
                    self.tableWidget.setRowHidden(row, False)
                else:
                    self.tableWidget.setRowHidden(row, True)
        else:
            item = QtWidgets.QTableWidgetItem("No")
            self.tableWidget.setItem(row, 7, item)

            item = QtWidgets.QTableWidgetItem()
            item.setIcon(self.iconSamp)
            self.tableWidget.setVerticalHeaderItem(row, item)

            if self.checkBoxFavourites.isChecked():
                self.checkBoxOpenMpServers.setEnabled(False)
                self.checkBoxSampServers.setEnabled(False)
                self.lineEdit.setEnabled(False)
                for row in range(self.tableWidget.rowCount()):
                    item = self.tableWidget.item(row, 0)
                    if item.text() in self.fake_favourites:
                        self.tableWidget.setRowHidden(row, False)
                    else:
                        self.tableWidget.setRowHidden(row, True)
            
            else:
                if self.checkBoxSampServers.isChecked():
                    self.tableWidget.setRowHidden(row, False)
                else:
                    self.tableWidget.setRowHidden(row, True)

    def loadServerList(self) -> int:
        url = "https://api.open.mp/servers"
        try:
            response = requests.get(url, timeout=7)
        except requests.exceptions.RequestException as e:
            message = QtWidgets.QMessageBox()
            message.setIcon(QtWidgets.QMessageBox.Critical)
            message.setWindowIcon(self.iconOpenMp)
            message.setWindowTitle("Error")
            message.setText("Could not get server list.\t\t")
            message.setInformativeText(
                "Failed to resolve 'api.open.mp'\n"
                "Please check your connection.")
            message.exec_()

            raise SystemExit(e)

        if response.status_code != 200:
            message = QtWidgets.QMessageBox()
            message.setIcon(QtWidgets.QMessageBox.Critical)
            message.setWindowIcon(self.iconOpenMp)
            message.setWindowTitle("Error")
            message.setText("Could not get server list.\t\t")
            message.setInformativeText(
                "Internal server error 'api.open.mp'\n"
                "Please try again later.")
            message.exec_()

            sys.exit(0)
            return

        servers_count = int()
        players_count = int()

        json = response.json()


        for i in json:
            servers_count += 1
            players_count += i["pc"]

            self.addServer(
                i["ip"],
                i["hn"],
                i["pc"],
                i["pm"],
                i["gm"],
                i["vn"],
                i["la"],
                i["pa"],
                i["omp"])

        return servers_count, players_count

    def filterRows(self, text: str) -> None:
        if self.checkBoxFavourites.isChecked() == True:
            self.checkBoxSampServers.setEnabled(False)
            self.lineEdit.setEnabled(False)
            for row in range(self.tableWidget.rowCount()):
                item = self.tableWidget.item(row, 0)
                if item.text() in self.fake_favourites:
                    self.tableWidget.setRowHidden(row, False)
                else:
                    self.tableWidget.setRowHidden(row, True)

        elif len(text) > 2:
            for row in range(self.tableWidget.rowCount()):
                item = self.tableWidget.item(row, 7)

                if (not self.checkBoxOpenMpServers.isChecked() and
                        item.text() == "Yes"):
                    continue
                if (not self.checkBoxSampServers.isChecked() and
                        item.text() == "No"):
                    continue


                for col in [0, 1, 3, 4, 5]:
                    item = self.tableWidget.item(row, col)
                    if text.casefold() not in item.text().casefold():
                        if col == 5:
                            self.tableWidget.setRowHidden(row, True)
                    else:
                        self.tableWidget.setRowHidden(row, False)
                        break

        else:
            if self.checkBoxOpenMpServers.isChecked():
                for row in range(self.tableWidget.rowCount()):
                    item = self.tableWidget.item(row, 7)
                    if item.text() == "Yes":
                        self.tableWidget.setRowHidden(row, False)
                    else:
                        if self.checkBoxSampServers.isChecked():
                            self.tableWidget.setRowHidden(row, False)
                        else:
                            self.tableWidget.setRowHidden(row, True)
                    
    def checkForOpenMpUpdates(self):
        url = "https://api.open.mp/launcher"
        try:
            response = requests.get(url, timeout=5)
        except requests.exceptions.RequestException:
            return
        
        if response.status_code != 200:
            return

        try:
            data = json.loads(response.text)
            checksum = data["ompPluginChecksum"]
            with open(home / 'AppData' / 'Local' / 'com.open.mp' / 'omp' / 'omp-client.dll' , 'rb') as file:
                calculated_hash = hashlib.md5(file.read()).hexdigest()
            if calculated_hash == checksum:
                pass
            else:
                errorbox = QtWidgets.QErrorMessage(self)
                errorbox.setWindowTitle('An update for omp-client.dll is available!')
                errorbox.showMessage('The hash of your file is not the same as the hash on the API, which usually means that it has been updated!')
                errorbox.exec_()
        except FileNotFoundError:
            errorbox = QtWidgets.QErrorMessage(self)
            errorbox.setWindowTitle('Error!')
            errorbox.showMessage(f'The omp-client.dll file does not exist, download it through the launcher')
            errorbox.exec_()
        except Exception as e:
            errorbox = QtWidgets.QErrorMessage(self)
            errorbox.setWindowTitle('Error!')
            errorbox.showMessage(f'Something has failed \n {e}')
            errorbox.exec_()

    def checkForUpdates(self) -> None:
        """
        version.json
        {
            "version": "1.0.0",
            "new_version_link": "https://..."
        }
        """

        url = (
            "https://raw.githubusercontent.com/adib-yg/"
            "openmp-server-browser/main/version.json")

        try:
            response = requests.get(url, timeout=5)
        except requests.exceptions.RequestException:
            return

        if response.status_code != 200:
            return

        try:
            json = response.json()

            if json["version"] == __version__:
                pass
            elif json["version"] > __version__:
                message = QtWidgets.QMessageBox()
                message.setIcon(QtWidgets.QMessageBox.Information)
                message.setWindowIcon(self.iconOpenMp)
                message.addButton("Later", QtWidgets.QMessageBox.YesRole)
                downloadButton = message.addButton(
                    "Download", QtWidgets.QMessageBox.ActionRole)
                message.setWindowTitle("A newer version is available!")
                message.setText(
                    "A newer version of "
                    "omp-server-browser is available!\t\t")
                message.setInformativeText(
                    "Click the \"Download\" button to get the new version.")
                message.exec_()

                if message.clickedButton() == downloadButton:
                    url = QtCore.QUrl(json["new_version_link"])
                    QtGui.QDesktopServices.openUrl(url)

        except Exception:
            pass

    def setLabelOnlineServersText(self, text: str) -> None:
        self.labelOnlineServers.setText(f"""
            <html>
                <head/>
                <body>
                    <p>Online Servers:
                        <span style=\" font-weight:600;\">
                            {text}
                        </span>
                    </p>
                </body>
            </html>""")

    def setLabelOnlinePlayersText(self, text: str) -> None:
        self.labelOnlinePlayers.setText(f"""
            <html>
                <head/>
                <body>
                    <p>Online Players:
                        <span style=\" font-weight:600;\">
                            {text}
                        </span>
                    </p>
                </body>
            </html>""")

    def setThemeDarkMode(self) -> None:
        self.current_theme = "Dark"

        app.setStyle("fusion")

        self.actionTheme.setText("Light Mode")
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(":/imagesPrefix/images/icon-sun-48px-white.png"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.On)
        self.actionTheme.setIcon(icon)

        self.setStyleSheet(
            """
            * {
                font-family: "Verdana"
            }
            QWidget {
                background-color: rgb(76, 76, 76);
            }
            QMenu {
                color: rgb(255, 255, 255);
            }
            QMenuBar {
                background-color: rgb(100, 100, 100);
            }
            QMenuBar::item {
                color: rgb(255,255,255);
            }
            QMenuBar::item:selected {
                background-color: rgba(203, 203, 203, 100);
            }
            QFrame#frame {
                background-color: #212121;
            }
            QTableWidget QTableCornerButton::section {
               background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                           stop:0 #616161, stop: 0.5 #505050,
                                           stop: 0.6 #434343, stop:1 #656565);
            }
            QCheckBox::indicator {
                border: 2px solid;
                border-color: rgb(83, 83, 83);
            }
            QCheckBox::indicator:checked {
                background-color: rgba(255, 255, 255, 200);
            }
            QCheckBox#checkBoxOpenMpServers {
                color: rgb(255, 255, 255);
                background-color: rgba(54, 54, 54, 50);
            }
            QCheckBox::hover#checkBoxOpenMpServers {
                background-color: rgba(54, 54, 54, 150);
            }
            QCheckBox#checkBoxSampServers {
                color: rgb(255, 255, 255);
                background-color: rgba(54, 54, 54, 50);
            }
            QCheckBox::hover#checkBoxSampServers {
                background-color: rgba(54, 54, 54, 150);
            }
            QPushButton#pushButtonRefresh {
                color: rgb(255, 255, 255);
            }
            QLineEdit#lineEdit {
                color: rgb(255, 255, 255);
            }
            QTableWidget#tableWidget {
                color: rgb(255, 255, 255);
                background-color: rgb(62, 62, 62);
                selection-background-color: rgba(184, 184, 184, 70);
                gridline-color: rgba(255, 255, 255, 20);
            }
            QHeaderView::section {
                color: rgb(255, 255, 255);
                border: 1px solid rgba(255, 255, 255, 30);
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                           stop:0 #616161, stop: 0.5 #505050,
                                           stop: 0.6 #434343, stop:1 #656565);
            }
            QLabel#label {
                background-color: transparent;
                color: rgb(255, 255, 255);
            }
            QLabel#labelOnlineServers {
                background-color: transparent;
                color: rgb(255, 255, 255);
            }
            QLabel#labelOnlinePlayers {
                background-color: transparent;
                color: rgb(255, 255, 255);
            }
            """)

        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(
                ":/imagesPrefix/images/icon-refresh-24px-white.png"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.On)
        self.pushButtonRefresh.setIcon(icon)

        self.tableWidget.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarAsNeeded)

    def setThemeLightMode(self) -> None:
        self.current_theme = "Light"

        app.setStyle("windowsvista")

        self.actionTheme.setText("Dark Mode")
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(":/imagesPrefix/images/icon-dark-64px.png"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.On)
        self.actionTheme.setIcon(icon)

        self.setStyleSheet("""
            * {
                font-family: "Verdana"
            }
            """)

        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(":/imagesPrefix/images/icon-refresh-24px.png"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.On)
        self.pushButtonRefresh.setIcon(icon)

        self.tableWidget.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOn)

    def on_clicked_row(self, item):
        if item.column() == 0:  # Clicked on a row in the "IP Address" column
            cell_content = item.data()

            if len(cell_content):
                QtWidgets.QApplication.clipboard().setText(cell_content)

    def on_double_clicked_row(self, item):
        if item.column() == 0:  # Clicked on a row in the "IP Address" column
            cell_content = item.data()
            server_ip = str(cell_content).split(':')[0]
            server_port = str(cell_content).split(':')[1]
            if errormsg:
                box = QtWidgets.QMessageBox()
                box.setText(f"Error! {errormsg}")
                box.exec_()
            else:
                try:
                    if len(cell_content):
                        QtCore.QProcess.execute(f"{settings['omppath']} -h {server_ip} -p {server_port} -n {settings['username']} -g {settings['gamepath']}")
                except Exception:
                    box = QtWidgets.QMessageBox()
                    box.setText('Your settings are set up incorrectly')
                    box.exec_()
        elif item.column() == 1: # Server name column
            cell_content = item.data()
            cell_content = item.model().data(item.model().index(item.row(), 0))
            if len(cell_content):
                if cell_content not in self.fake_favourites:
                    self.fake_favourites.append(cell_content)

                elif cell_content in self.fake_favourites:
                    self.fake_favourites.remove(cell_content)

                temporary = ",".join(self.fake_favourites)

                # write to file
                self.favourites_list.seek(0)
                self.favourites_list.write(temporary)
                self.favourites_list.truncate()
                self.favourites_list.flush()
                #self.filterRows('') # update list
                text = self.lineEdit.text()
                if len(text) > 2:
                    self.filterRows(text)
                else:
                    self.filterRows('')

    def on_clicked_button_refresh(self):
        self.pushButtonRefresh.setEnabled(False)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(
            lambda: self.pushButtonRefresh.setEnabled(True))
        self.timer.start(30000)

        self.tableWidget.setRowCount(0)  # Remove all rows

        self.setLabelOnlineServersText("-")
        self.setLabelOnlinePlayersText("-")

        QtTest.QTest.qWait(500)

        servers_count, players_count = self.loadServerList()

        self.setLabelOnlineServersText(str(servers_count))
        self.setLabelOnlinePlayersText(str(players_count))

        # Check filter again
        text = self.lineEdit.text()
        if len(text) > 2:
            self.filterRows(text)

    def on_line_edit_changed(self):
        text = self.lineEdit.text()
        self.filterRows(text)

    def on_omp_check_box_state_changed(self):
        if self.checkBoxOpenMpServers.isChecked():
            if self.checkBoxFavourites.isChecked():
                pass
            else:
                for row in range(self.tableWidget.rowCount()):
                    item = self.tableWidget.item(row, 7)
                    if item.text() == "Yes":
                        self.tableWidget.setRowHidden(row, False)
                    else:
                        if self.checkBoxSampServers.isChecked():
                            self.tableWidget.setRowHidden(row, False)
                        else:
                            self.tableWidget.setRowHidden(row, True)
        else:
            if self.checkBoxFavourites.isChecked():
                pass
            else:
                for row in range(self.tableWidget.rowCount()):
                    item = self.tableWidget.item(row, 7)
                    if item.text() == "Yes":
                        self.tableWidget.setRowHidden(row, True)
                    else:
                        if self.checkBoxSampServers.isChecked():
                            self.tableWidget.setRowHidden(row, False)
                        else:
                           self.tableWidget.setRowHidden(row, True)

        # Check filter again
        text = self.lineEdit.text()
        self.filterRows(text)

    def get_full_column(self, colnum):
        myfunlist = []
        for row in range(self.tableWidget.rowCount()):
            myfunlist.append(self.tableWidget.item(row, colnum).text())
        return myfunlist

    def on_favourites_check_box_state_changed(self):
        if self.checkBoxFavourites.isChecked():
            self.filterRows('')
            self.checkBoxOpenMpServers.setEnabled(False)
            self.checkBoxSampServers.setEnabled(False)
            self.lineEdit.setEnabled(False)
            for row in range(self.tableWidget.rowCount()):
                item = self.tableWidget.item(row, 0)
                if item.text() in self.fake_favourites:
                    self.tableWidget.setRowHidden(row, False)
                else:
                    self.tableWidget.setRowHidden(row, True)
        
        else:
            self.checkBoxOpenMpServers.setEnabled(True)
            self.checkBoxSampServers.setEnabled(True)
            self.lineEdit.setEnabled(True)
            for row in range(self.tableWidget.rowCount()):
                item = self.tableWidget.item(row, 7)
                if self.checkBoxSampServers.isChecked() and self.checkBoxOpenMpServers.isChecked():
                    self.tableWidget.setRowHidden(row, False)
                elif self.checkBoxSampServers.isChecked():
                    if item.text() == "No":
                        self.tableWidget.setRowHidden(row, False)
                elif self.checkBoxOpenMpServers.isChecked():
                    if item.text() == "Yes":
                        self.tableWidget.setRowHidden(row, False)
                else:
                    self.tableWidget.setRowHidden(row, True)
                    

        # Check filter again
            text = self.lineEdit.text()
            if len(text) > 2:
                self.filterRows(text)

    def on_samp_check_box_state_changed(self):
        if self.checkBoxSampServers.isChecked():
            if self.checkBoxFavourites.isChecked():
                pass
            else:
                for row in range(self.tableWidget.rowCount()):
                    item = self.tableWidget.item(row, 7)
                    if item.text() == "No":
                        self.tableWidget.setRowHidden(row, False)
                    else:
                        if self.checkBoxOpenMpServers.isChecked():
                            self.tableWidget.setRowHidden(row, False)
                        else:
                            self.tableWidget.setRowHidden(row, True)
        else:
            if self.checkBoxFavourites.isChecked():
                pass
            else:
                for row in range(self.tableWidget.rowCount()):
                    item = self.tableWidget.item(row, 7)
                    if item.text() == "No":
                        self.tableWidget.setRowHidden(row, True)
                    else:
                        if self.checkBoxOpenMpServers.isChecked():
                            self.tableWidget.setRowHidden(row, False)
                        else:
                            self.tableWidget.setRowHidden(row, True)

        # Check filter again
        text = self.lineEdit.text()
        if len(text) > 2:
            self.filterRows(text)

    def on_triggered_action_theme(self):
        if self.current_theme == "Light":
            self.setThemeDarkMode()
        else:
            self.setThemeLightMode()

    def on_triggered_action_settings(self):
        if self.settingsWindow == None:
            self.settingsWindow = SettingsWindow()
        self.settingsWindow.exec_()

    def on_triggered_action_omp_downloader(self):
        if self.downloaderWindow == None:
            self.downloaderWindow = DownloaderWindow()
        self.downloaderWindow.exec_()

class SettingsWindow(QtWidgets.QDialog):
    def __init__(self):
        super(SettingsWindow, self).__init__()

        #load the ui
        stream = QtCore.QFile(":/uiPrefix/settings.ui")
        stream.open(QtCore.QFile.ReadOnly)
        uic.loadUi(stream, self)
        stream.close()

        self.iconOpenMp = QtGui.QIcon()
        self.iconOpenMp.addPixmap(
        QtGui.QPixmap(":/imagesPrefix/icons/open-mp-icon.ico"),
        QtGui.QIcon.Normal,
        QtGui.QIcon.On)

        self.setWindowTitle("Settings")
        self.setWindowIcon(self.iconOpenMp)
        
        self.pushButtonOMP.clicked.connect(self.on_clicked_button_OMP)
        self.labelOMP.setText(settings['omppath'])
        
        self.pushButtonGame.clicked.connect(self.on_clicked_button_game)
        self.labelGamePath.setText(settings['gamepath'])

        self.lineEditUsername.textChanged.connect(self.on_line_edit_username_changed)
        self.lineEditUsername.setText(settings['username'])


    def on_line_edit_username_changed(self):
        settings['username'] = self.lineEditUsername.text()
        with open(home / "Documents" / "GTA San Andreas User Files" / "launcher-settings.json", "w") as file:
            file.write(json.dumps(settings, indent=4))          

    def on_clicked_button_OMP(self):
        try:
            settings['omppath'] = self.file_picker("Executable files (*.exe)")[0]
            self.labelOMP.setText(settings['omppath'])
            with open(home / "Documents" / "GTA San Andreas User Files" / "launcher-settings.json", "w") as file:
                file.write(json.dumps(settings, indent=4))
        except IndexError:
            pass

    def on_clicked_button_game(self):
        try:
            path = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Your GTA Folder"))
            if path != '':
                settings['gamepath'] = path
                self.labelGamePath.setText(settings['gamepath'])
                with open(home / "Documents" / "GTA San Andreas User Files" / "launcher-settings.json", "w") as file:
                    file.write(json.dumps(settings, indent=4))
        except IndexError:
            pass
        
    def file_picker(self, filetype: str):
        dlg = QtWidgets.QFileDialog()
        dlg.setFileMode(QtWidgets.QFileDialog.AnyFile)
        dlg.setNameFilter(filetype)
        #filenames = QtCore.QstringList()

        dlg.exec_()
        filenames = dlg.selectedFiles()
        return filenames


class DownloaderWindow(QtWidgets.QDialog):
    def __init__(self):
        super(DownloaderWindow, self).__init__()

        #load the ui
        stream = QtCore.QFile(":/uiPrefix/downloader.ui")
        stream.open(QtCore.QFile.ReadOnly)
        uic.loadUi(stream, self)
        stream.close()
        
        self.iconOpenMp = QtGui.QIcon()
        self.iconOpenMp.addPixmap(
        QtGui.QPixmap(":/imagesPrefix/icons/open-mp-icon.ico"),
        QtGui.QIcon.Normal,
        QtGui.QIcon.On)

        self.setWindowTitle("OMP Downloader")
        self.setWindowIcon(self.iconOpenMp)

        self.pushButtonClient.clicked.connect(self.on_clicked_button_client)
        self.pushButtonLauncher.clicked.connect(self.on_clicked_button_launcher)

    def on_clicked_button_client(self):
        destination_path = home / "AppData" / "Local" / "com.open.mp" / "omp"
        url = 'https://assets.open.mp/omp-client.dll'
        try:
            os.makedirs(destination_path, exist_ok=True)
            response = requests.get(url)
            if response.status_code == 200:
                with open(destination_path / "omp-client.dll", "wb") as file:
                    file.write(response.content)
                messagebox = QtWidgets.QMessageBox()
                messagebox.setWindowTitle("Success!")
                messagebox.setText("File donwloaded successfully!")
                messagebox.exec_()
            else:
                messagebox = QtWidgets.QMessageBox()
                messagebox.setWindowTitle("Failed")
                messagebox.setText("The api couldn't be reached.")
                messagebox.exec_()
        except Exception as e:
            messagebox = QtWidgets.QMessageBox()
            messagebox.setWindowTitle('Something went wrong!')
            messagebox.setText(f"Something went wrong! \n {e}")
            messagebox.exec_()

    def on_clicked_button_launcher(self):
        destination_path = home / "AppData" / "Local" / "com.open.mp" / "omp"
        latest = 'https://api.github.com/repos/openmultiplayer/launcher/releases/latest'
        try:
            os.makedirs(destination_path, exist_ok=True)
            response = requests.get(latest)
            data = response.json()
            url = data['assets'][1]['browser_download_url']
            launcher = requests.get(url)
            if response.status_code == 200:
                with open(destination_path / "omp-launcher.exe", "wb") as file:
                    file.write(launcher.content)
                messagebox = QtWidgets.QMessageBox()
                messagebox.setWindowTitle("Success!")
                messagebox.setText(f"Downloaded to {destination_path / 'omp-launcher.exe'}")
                messagebox.exec_()
            else:
                messagebox = QtWidgets.QMessageBox()
                messagebox.setWindowTitle("Failed")
                messagebox.setText("The api couldn't be reached.")
                messagebox.exec_()
        except Exception as e:
            messagebox = QtWidgets.QMessageBox()
            messagebox.setWindowTitle('Something went wrong!')
            messagebox.setText(f"Something went wrong! \n {e}")
            messagebox.exec_()
            


if __name__ == '__main__':
    __version__ = "1.1.0"

    CHECK_FOR_OMP_PLUGIN_UPDATES = True
    CHECK_FOR_UPDATES = False

    def detect_darkmode_in_windows() -> bool:
        try:
            import winreg

            registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        except ImportError:
            return False
        except Exception:
            return False

        reg_keypath = (
            r'SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize')

        try:
            reg_key = winreg.OpenKey(registry, reg_keypath)
        except FileNotFoundError:
            return False

        for i in range(1024):
            try:
                value_name, value, _ = winreg.EnumValue(reg_key, i)
                if value_name == 'AppsUseLightTheme':
                    return value == 0
            except OSError:
                break
        return False

    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    window.show()
    app.exec_()
