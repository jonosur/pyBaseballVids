import math
import webbrowser
import sys
import requests
import time
import datetime
import wget
import pychromecast
import configparser

from PyQt5.QtCore import QDate, QDir, Qt, QUrl, QSize, QTimer, QEvent
from PyQt5 import QtGui, QtWidgets, uic, QtCore
from PyQt5.QtGui import QIcon, QFont, QLinearGradient
from PyQt5.QtWidgets import (QApplication, QWidget, QListWidget, QVBoxLayout, QListWidgetItem,
                             QPushButton, QInputDialog, QMessageBox, QDialog, qApp, QSystemTrayIcon,
                             QStyle, QAction, QMenu, QFileDialog, QHBoxLayout, QLabel, QSizePolicy, QSlider,
                             QStatusBar, QProgressBar, QComboBox, QFontDialog)
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtGui import QKeySequence, QPalette, QColor, QTextCharFormat
from PyQt5.QtWebEngineWidgets import QWebEngineView

teamids = {
    "None": 0,
    "OAK": 133,
    "PIT": 134,
    "SD": 135,
    "SEA": 136,
    "SF": 137,
    "STL": 138,
    "TB": 139,
    "TEX": 140,
    "TOR": 141,
    "MIN": 142,
    "PHI": 143,
    "ATL": 144,
    "CWS": 145,
    "MIA": 146,
    "NYY": 147,
    "MIL": 158,
    "LAA": 108,
    "ARI": 109,
    "BAL": 110,
    "BOS": 111,
    "CHC": 112,
    "CIN": 113,
    "CLE": 114,
    "COL": 115,
    "DET": 116,
    "HOU": 117,
    "KC": 118,
    "LAD": 119,
    "WSH": 120,
    "NYM": 121,
}

teamcolors = {
    "OAK": ["#003831","#EFB21E"],
    "PIT": ["#27251F","#FDB827"],
    "SD": ["#2F241D","#FFC425"],
    "SEA": ["#0C2C56","#005C5C"],
    "SF": ["#FD5A1E","#27251F"],
    "STL": ["#C41E3A","#0C2340"],
    "TB": ["#092C5C","#8FBCE6"],
    "TEX": ["#003278","#C0111F"],
    "TOR": ["#1D2D5C","#134A8E"],
    "MIN": ["#002B5C","#D31145"],
    "PHI": ["#E81828","#002D72"],
    "ATL": ["#CE1141","#13274F"],
    "CWS": ["#27251F","#C4CED4"],
    "MIA": ["#00A3E0","#000"],
    "NYY": ["#003087","#E4002C"],
    "MIL": ["#FFC52F","#12284B"],
    "LAA": ["#003263","#BA0021"],
    "ARI": ["#A71930","#E3D4AD"],
    "BAL": ["#DF4601","#000"],
    "BOS": ["#BD3039","#0C2340"],
    "CHC": ["#0E3386","#CC3433"],
    "CIN": ["#C6011F","#000"],
    "CLE": ["#0C2340","#E31937"],
    "COL": ["#33006F","#C4CED4"],
    "DET": ["#0C2340","#FA4616"],
    "HOU": ["#002D62","#EB6E1F"],
    "KC": ["#004687","#BD9B60"],
    "LAD": ["#005A9C","#FFF"],
    "WSH": ["#AB0003","#14225A"],
    "NYM": ["#002D72","#FF5910"],
}


about = '''pyBaseballVids v1
--------------------------------------
MIT License

Copyright (c) 2020, Jonathan "grateful" Surman

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

class BaseballVids(QtWidgets.QMainWindow):
    def __init__(self):
        super(BaseballVids, self).__init__()
        self.config = configparser.ConfigParser()
        self.config.read('settings.ini')
        self.favteam = self.config['SETTINGS']['FavTeam']
        self.teamid = self.config['SETTINGS']['FavTeamID']
        self.color2 = self.config['SETTINGS']['Color2']
        self.color1 = self.config['SETTINGS']['Color1']
        self.showToolTip = self.config['SETTINGS']['ShowToolTip']
        self.favfont = QFont(self.config['SETTINGS']['FavFont'])
        self.favfont.setBold(True)
        self.begin = None
        self.end = None
        self.dates = []
        self.castplayer = None
        # Set QMainWindow
        self.alabel = QLabel()
        self.resize(800, 700)
        self.setMinimumSize(QtCore.QSize(800, 700))
        self.setMaximumSize(QtCore.QSize(800, 700))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("img/baseball.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)
        self.setWindowTitle("pyBaseballVids")

        # Set centralWidget
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")

        # Set calendarWidget
        self.calendarWidget = QtWidgets.QCalendarWidget(self.centralwidget)
        self.calendarWidget.setGeometry(QtCore.QRect(10, 470, 781, 181))
        if self.showToolTip == "True":
            self.calendarWidget.setToolTip('Select date')
        self.calendarWidget.setFont(self.favfont)
        self.calendarWidget.setCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))
        d = datetime.datetime.now()
        self.calendarWidget.setSelectedDate(QtCore.QDate(d.year, d.month, d.day))
        self.calendarWidget.setMinimumDate(QtCore.QDate(2010, 1, 1))
        self.calendarWidget.setGridVisible(True)
        self.calendarWidget.setVerticalHeaderFormat(QtWidgets.QCalendarWidget.NoVerticalHeader)
        self.calendarWidget.setObjectName("calendarWidget")

        # Set listGames
        self.listGames = QtWidgets.QListWidget(self.centralwidget)
        self.listGames.setGeometry(QtCore.QRect(10, 10, 171, 290))
        self.listGames.setFont(self.favfont)
        self.listGames.viewport().setProperty("cursor", QtGui.QCursor(QtCore.Qt.OpenHandCursor))
        self.listGames.setObjectName("listGames")
        self.listGames.setStyleSheet('selection-background-color: {}; selection-color: {};'.format(self.color1, self.color2))
        # Set listVideos
        self.listVideos = QtWidgets.QListWidget(self.centralwidget)
        self.listVideos.setGeometry(QtCore.QRect(195, 11, 591, 351))
        if self.showToolTip == "True":
            self.listVideos.setToolTip('Click to play')
        self.listVideos.setFont(self.favfont)
        self.listVideos.viewport().setProperty("cursor", QtGui.QCursor(QtCore.Qt.OpenHandCursor))
        self.listVideos.setStyleSheet('selection-background-color: {}; selection-color: {};'.format(self.color1, self.color2))
        self.listVideos.setObjectName("listVideos")

        # Set labelStatus
        self.labelStatus = QtWidgets.QLabel(self.centralwidget)
        self.labelStatus.setGeometry(QtCore.QRect(10, 650, 781, 21))
        self.labelStatus.setText("")
        self.labelStatus.setObjectName("labelStatus")

        self.clockStatus = QtWidgets.QLabel()
        self.clockStatus.setStyleSheet("background-color: rgb(53, 53, 53);")
        self.clockStatus.setText("0:00")

        # Set the time used to update the slider and clock
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.setSlider)
        self.timer.start(1)

        # Set Chromecast Controls Box
        btnSize = QSize(26, 26)
        self.labelCast = QtWidgets.QLabel(self.centralwidget)
        self.labelCast.setGeometry(QtCore.QRect(200, 370, 401, 91))
        self.labelCast.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.labelCast.setObjectName("labelCast")

        self.playButton = QPushButton()
        self.playButton.setEnabled(False)
        self.playButton.setFixedHeight(24)
        self.playButton.setIconSize(btnSize)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)
        self.playButton.setAutoFillBackground(True)
        self.playButton.setFlat(True)
        if self.showToolTip == "True":
            self.playButton.setToolTip('Play')

        self.backButton = QPushButton()
        self.backButton.setEnabled(False)
        self.backButton.setFixedHeight(24)
        self.backButton.setIconSize(btnSize)
        self.backButton.setIcon(self.style().standardIcon(QStyle.SP_MediaSkipBackward))
        self.backButton.clicked.connect(self.back)
        self.backButton.setAutoFillBackground(True)
        self.backButton.setFlat(True)
        if self.showToolTip == "True":
            self.backButton.setToolTip('Skip Backward')

        self.nextButton = QPushButton()
        self.nextButton.setEnabled(False)
        self.nextButton.setFixedHeight(24)
        self.nextButton.setIconSize(btnSize)
        self.nextButton.setIcon(self.style().standardIcon(QStyle.SP_MediaSkipForward))
        self.nextButton.clicked.connect(self.next)
        self.nextButton.setAutoFillBackground(True)
        self.nextButton.setFlat(True)
        if self.showToolTip == "True":
            self.nextButton.setToolTip('Skip Forward')

        self.snextButton = QPushButton()
        self.snextButton.setEnabled(False)
        self.snextButton.setFixedHeight(24)
        self.snextButton.setIconSize(btnSize)
        self.snextButton.setIcon(self.style().standardIcon(QStyle.SP_MediaSeekForward))
        self.snextButton.clicked.connect(self.seekf)
        self.snextButton.setAutoFillBackground(True)
        self.snextButton.setFlat(True)
        if self.showToolTip == "True":
            self.snextButton.setToolTip('Seek Forward')

        self.sbackButton = QPushButton()
        self.sbackButton.setEnabled(False)
        self.sbackButton.setFixedHeight(24)
        self.sbackButton.setIconSize(btnSize)
        self.sbackButton.setIcon(self.style().standardIcon(QStyle.SP_MediaSeekBackward))
        self.sbackButton.clicked.connect(self.seekb)
        self.sbackButton.setAutoFillBackground(True)
        self.sbackButton.setFlat(True)
        if self.showToolTip == "True":
            self.sbackButton.setToolTip('Seek Backward')

        self.muteButton = QPushButton()
        self.muteButton.setEnabled(False)
        self.muteButton.setFixedHeight(24)
        self.muteButton.setIconSize(btnSize)
        self.muteButton.setIcon(self.style().standardIcon(QStyle.SP_MediaVolume))
        self.muteButton.clicked.connect(self.mute)
        self.muteButton.setAutoFillBackground(True)
        self.muteButton.setFlat(True)
        if self.showToolTip == "True":
            self.muteButton.setToolTip('Mute')

        self.castButton = QPushButton()
        self.castButton.setCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))
        devices = pychromecast.get_chromecasts()
        self.devices = []
        for data in devices[0]:
            if data.cast_type == "cast":
                self.devices.append(data)

        if len(self.devices) > 0:
            self.castButton.setEnabled(True)
            self.labelStatus.setText("Found {} Chromecasts, click cast button to connect".format(len(self.devices)))
        else:
            self.castButton.setEnabled(False)
            self.labelStatus.setText("No Chromecasts, make sure device is connected and restart".format(len(self.devices)))

        self.castButton.setFixedHeight(24)
        self.castButton.setIconSize(btnSize)
        self.castButton.setIcon(QIcon("img/cast.png"))
        self.castButton.clicked.connect(self.get_chromecasts)
        self.castButton.setAutoFillBackground(True)
        self.castButton.setFlat(True)
        if self.showToolTip == "True":
            self.castButton.setToolTip('Find Chromecast')

        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 100)
        self.positionSlider.setEnabled(False)
        self.positionSlider.sliderReleased.connect(self.setSliderLocal)
        self.positionSlider.sliderPressed.connect(self.stopSlider)

        self.saveButton = QPushButton("Save Video")
        self.saveButton.setCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))
        if self.showToolTip == "True":
            self.saveButton.setToolTip("Save Video File")
        self.saveButton.setStatusTip("Save Video File")
        self.saveButton.setFixedHeight(24)
        self.saveButton.setIconSize(btnSize)
        self.saveButton.setFont(self.favfont)
        self.saveButton.setIcon(QIcon.fromTheme("document-save", QIcon("D:/_Qt/img/save.png")))
        self.saveButton.clicked.connect(self.save)
        self.saveButton.setAutoFillBackground(True)
        self.saveButton.setFlat(True)
        self.saveButton.setCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))

        self.horizontalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(200, 400, 575, 51))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.castLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.castLayout.setContentsMargins(0, 0, 0, 0)
        self.castLayout.setObjectName("castLayout")
        self.castLayout.addWidget(self.castButton)
        self.castLayout.addWidget(self.playButton)
        self.castLayout.addWidget(self.muteButton)
        self.castLayout.addWidget(self.backButton)
        self.castLayout.addWidget(self.sbackButton)
        self.castLayout.addWidget(self.snextButton)
        self.castLayout.addWidget(self.nextButton)
        self.castLayout.addWidget(self.positionSlider)
        self.castLayout.addWidget(self.clockStatus)
        self.castLayout.addWidget(self.saveButton)

        self.eventButton = QtWidgets.QPushButton(self.centralwidget)
        self.eventButton.setGeometry(QtCore.QRect(10, 310, 171, 31))
        self.eventButton.setFlat(True)
        self.eventButton.setEnabled(False)
        self.eventButton.clicked.connect(self.gamebox)
        self.eventButton.setObjectName("eventButton")
        if self.showToolTip == "True":
            self.eventButton.setToolTip('Boxscore')

        self.playsButton = QtWidgets.QPushButton(self.centralwidget)
        self.playsButton.setGeometry(QtCore.QRect(10, 345, 171, 31))
        self.playsButton.setFlat(True)
        self.playsButton.setEnabled(False)
        self.playsButton.clicked.connect(self.gameplays)
        if self.showToolTip == "True":
            self.playsButton.setToolTip('Play by Play')
            
        self.Tlabel = QLabel(self.centralwidget)
        self.Tlabel.setGeometry(QtCore.QRect(50, 380, 100, 80))
        self.Tlabel.setPixmap(QtGui.QPixmap("teams/{}.svg".format(self.teamid)))
        self.Tlabel.setScaledContents(True)
        self.Tlabel.setEnabled(True)
        if self.showToolTip == "True":
            self.Tlabel.setToolTip('IMAGE') 
            

    

        # Set CentralWidget
        self.setCentralWidget(self.centralwidget)

        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 22))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.setMenuBar(self.menubar)
        self.actionAbout = QtWidgets.QAction(self)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("img/about.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionAbout.setIcon(icon1)
        self.actionAbout.setObjectName("actionAbout")
        self.actionSettings = QtWidgets.QAction(self)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("img/settings.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSettings.setIcon(icon2)
        self.actionSettings.setObjectName("actionSettings")
        self.actionExit = QtWidgets.QAction(self)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap("img/exit.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionExit.setIcon(icon3)
        self.actionExit.setObjectName("actionExit")
        self.actionMinimize = QtWidgets.QAction(self)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap("img/minimize.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionMinimize.setIcon(icon4)
        self.actionMinimize.setObjectName("actionMinimize")
        self.actionExit.triggered.connect(self.close)
        self.actionAbout.triggered.connect(self.get_about)
        self.actionSettings.triggered.connect(self.settings)
        self.actionMinimize.triggered.connect(self.hide)
        self.menuFile.addAction(self.actionMinimize)
        self.menuFile.addAction(self.actionAbout)
        self.menuFile.addAction(self.actionSettings)
        self.menuFile.addAction(self.actionExit)
        self.menubar.addAction(self.menuFile.menuAction())


        self.labelCast.setText("Chromecast Controls")
        self.labelCast.setFont(self.favfont)
        self.menuFile.setTitle("File")
        self.menuFile.setFont(self.favfont)
        self.menubar.setStyleSheet('background-color: {};'.format(self.color1))
        self.actionAbout.setText("About")
        self.actionSettings.setText("Settings")
        self.actionExit.setText("Exit")
        self.actionMinimize.setText("Minimize")

        # Init QSystemTrayIcon
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("teams/{}.svg".format(self.teamid)))
        show_action = QAction(QIcon("img/maximize.png"),"Show", self)
        quit_action = QAction(QIcon("img/exit.png"), "Exit", self)
        hide_action = QAction(QIcon("img/minimize.png"), "Hide", self)
        games_action = QAction(QIcon(None), "No Games", self)
        show_action.triggered.connect(self.show)
        hide_action.triggered.connect(self.hide)
        quit_action.triggered.connect(qApp.quit)
        tray_menu = QMenu()
        tray_menu.addAction(games_action)
        tray_menu.addAction(show_action)
        tray_menu.addAction(hide_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        if self.showToolTip == "True":
            self.tray_icon.setToolTip('pyBaseballVids v1')
        self.tray_icon.show()

        self.listGames.itemClicked.connect(self.get_videos)
        self.listVideos.itemClicked.connect(self.play_videos)
        self.calendarWidget.clicked[QDate].connect(self.get_games)
        self.calendarWidget.currentPageChanged.connect(self.get_dates) 

        nav1 = '#qt_calendar_navigationbar { background-color : ' + "{}".format(self.color1) + "; }"
        nav2 = '#qt_calendar_qtoolbutton { color : white; }'
        nav3 = 'QCalendarWidget QAbstractItemView { selection-background-color: ' + "{}".format(self.color1) + "; selection-color:" + "{}".format(self.color2) + "; }"
        self.calendarWidget.setStyleSheet(nav1 + nav2 + nav3)
        for d in (QtCore.Qt.Saturday, QtCore.Qt.Sunday, QtCore.Qt.Monday, QtCore.Qt.Tuesday, QtCore.Qt.Wednesday, QtCore.Qt.Thursday, QtCore.Qt.Friday):
            fmt = self.calendarWidget.weekdayTextFormat(d)
            fmt.setForeground(Qt.white)
            fmt.setBackground(QColor(53, 53, 53))
            self.calendarWidget.setWeekdayTextFormat(d, fmt)
        # Get Dates for favourite team and plot in CalendarWidget
        self.calendarWidget.setGridVisible(False)
        self.fav_games()

    def stopSlider(self):
        if self.timer.isActive():
            self.timer.stop()

    def setSliderLocal(self):
        num = self.positionSlider.value() * self.castplayer.media_controller.status.duration / 100
        print(num)
        #self.timer.stop()
        #self.castplayer.media_controller.pause()
        self.castplayer.media_controller.seek(num)
        #self.positionSlider.setValue(num)
        #self.castplayer.media_controller.play()
        self.timer.start(1)

    def get_dates(self, date, month):
        d = QDate(int(date), int(month), 1)
        e = QDate(int(date), int(month), int(d.daysInMonth()))
        self.begin = d.toString("yyyy-MM-dd")
        self.end = e.toString("yyyy-MM-dd")
        self.fav_games()       

    def fav_games(self):
        if self.teamid == "None":
            return
        else:
            url1 = "https://statsapi.mlb.com/api/v1/schedule?sportId=1&hydrate=team&expand=schedule.teams&startDate={}&endDate={}&teamId={}".format(self.begin, self.end, self.teamid)
            print(url1)
        content1 = requests.get(url1).json()
        #lets remove the old dates first
        for each in self.dates:
            favd = QDate(int(each[0]), int(each[1]), int(each[2]))
            favFormat = QTextCharFormat()
            favFormat.setBackground(QColor(53, 53, 53))
            favFormat.setForeground(Qt.white)
            self.calendarWidget.setDateTextFormat(favd, favFormat)
        self.dates = []
        try:
            for each in content1['dates']:
                data = each['date'].split('-')
                self.dates.append([data[0], data[1], data[2]])
        except:
            return
        for each in self.dates:
            favd = QDate(int(each[0]), int(each[1]), int(each[2]))
            favFormat = QTextCharFormat()
            favFormat.setBackground(QColor(self.color1))
            favFormat.setForeground(Qt.white)
            if self.showToolTip == "True":
                favFormat.setToolTip(self.favteam)
            self.calendarWidget.setDateTextFormat(favd, favFormat)

    def get_games(self, date):
        url = "https://statsapi.mlb.com/api/v1/schedule?sportId=1&hydrate=team&expand=schedule.teams&date={}".format(date.toString("yyyy-MM-dd"))
        print(url)
        content = requests.get(url).json()
        self.gamesList = []
        self.listGames.clear()
        self.listVideos.clear()
        try:
            gameslist = content['dates'][0]['games']
        except:
            msg = "No games found on {}".format(date.toString("yyyy-MM-dd"))
            self.labelStatus.setText(msg)
            QListWidgetItem('No games found', self.listGames)
            return
        for each in gameslist:
            away = each['teams']['away']['team']['abbreviation']
            awayS = each['teams']['away']['score']
            home = each['teams']['home']['team']['abbreviation']
            homeS = each['teams']['home']['score']
            gamePk = each['gamePk']
            status = each['status']['detailedState']
            if status == "Final":
                status = "F"
            self.gamesList.append(['{:3} {:2} @ {:3} {:2} {}'.format(away, awayS, home, homeS, status), gamePk])
        self.labelStatus.setText('Found {} games, select the game you wish to search'.format(len(self.gamesList)))
        for txt, data in self.gamesList:
            item = QListWidgetItem(txt, self.listGames)
            if self.showToolTip == "True":
                item.setToolTip('Click to load videos')


    def play_videos(self):
        try:
            self.url = self.videoList[int(self.listVideos.currentRow())][1]
            self.urldata = self.videoList[int(self.listVideos.currentRow())][2]
        except:
            return
        try:
            self.castplayer.play_media(self.url, 'video/mp4')
        except:
            if self.castplayer == None:
                self.labelStatus.setText("No Chromecast not connected, opening in default web browser")
                webbrowser.open(self.url)

        if self.castplayer != None:
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))

    def play_url(self, url, urldata):
        self.url = url
        self.urldata = urldata
        try:
            self.castplayer.play_media(self.url, 'video/mp4')
        except:
            if self.castplayer == None:
                self.labelStatus.setText("No Chromecast not connected, opening in default web browser")
                webbrowser.open(self.url)

        if self.castplayer != None:
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))

    def get_about(self):
        self.adialog = QDialog(self)
        self.adialog.setFixedSize(550,500)
        self.adialog.setWindowTitle('About')
        self.alabel = QLabel(self.adialog)
        self.alabel.move(15, 15)
        self.alabel.setText(about)
        self.alabel.setFont(self.favfont)
        self.adone = QPushButton(self.adialog)
        self.adone.setText('Close')
        self.adone.move(250, 450)
        self.adone.clicked.connect(self.adialog.close)
        self.adialog.show()

    def get_videos(self, item):
        self.eventButton.setText("BoxScore")
        self.eventButton.setFont(self.favfont)
        self.eventButton.setCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))
        self.playsButton.setText("Play by Play")
        self.playsButton.setFont(self.favfont)
        self.playsButton.setCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))
        self.eventButton.setEnabled(True)
        self.eventButton.setAutoFillBackground(True)
        self.playsButton.setAutoFillBackground(True)
        self.playsButton.setEnabled(True)
        self.videoList = []
        self.listVideos.clear()
        try:
            self.gamePk = self.gamesList[int(self.listGames.currentRow())][1]
        except:
            return
        url = "https://statsapi.mlb.com/api/v1/game/{}/content".format(self.gamePk)
        print(url)
        content = requests.get(url).json()
        vidlist = content['highlights']['highlights']['items']

        try:
            if len(vidlist) == 0:
                self.labelStatus.setText('No videos found')
        except:
            self.labelStatus.setText('No videos found')
            vidlist = []

        vidcount = 0
        for each in vidlist:
            for v in each['playbacks']:
                if "mp4Avc" in v['name']:
                    vidurl = v['url']
                    vidcount = vidcount + 1
                    data = "{}_{}".format(each['date'].split('T')[0], each['description'].replace(' ','_'))
                    self.videoList.append(['{} | {}'.format(each['duration'],
                                                        each['description']), vidurl, data])
        
        for txt, url, data in self.videoList:
            QListWidgetItem(txt, self.listVideos)


        self.labelStatus.setText('Found {} videos, click to play'.format(vidcount))

    def castpick(self):
        pick = self.castlistWidget.currentRow()
        self.castplayer = self.devices[pick]
        self.castplayer.wait()
        self.cast.close()
        self.labelCast.setText("{} Controls".format(self.castplayer.name))
        self.labelStatus.setText("Connected to {}".format(self.castplayer.name))
        self.castplayer.play_media('img/connected.png','image/png')
        self.playButton.setEnabled(True)
        self.playButton.setCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))
        self.nextButton.setEnabled(True)
        self.nextButton.setCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))
        self.backButton.setEnabled(True)
        self.backButton.setCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))
        self.muteButton.setEnabled(True)
        self.muteButton.setCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))
        self.snextButton.setEnabled(True)
        self.snextButton.setCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))
        self.sbackButton.setEnabled(True)
        self.sbackButton.setCursor
        self.positionSlider.setEnabled(True)
        self.positionSlider.setCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))


    def get_chromecasts(self):
        self.cast = QDialog(self)
        self.cast.setWindowTitle('Chromecasts')
        self.cast.resize(200, 200)

        self.castpickButton = QPushButton()
        self.castpickButton.setFixedHeight(24)
        self.castpickButton.setText('Select')
        self.castpickButton.clicked.connect(self.castpick)

        self.castlistWidget = QtWidgets.QListWidget(self.cast)
        castLayout = QVBoxLayout()
        castLayout.setContentsMargins(0, 0, 0, 0)
        castLayout.addWidget(self.castlistWidget)
        castLayout.addWidget(self.castpickButton)
        self.cast.setLayout(castLayout)
        for data in self.devices:
            try:
                if data.cast_type == "cast":
                    text = "{}".format(data.name)
                    QListWidgetItem(text, self.castlistWidget)
            except:
                pass
        self.cast.show()

    def save(self):
        try:
            name = QFileDialog.getSaveFileName(self, 'Save File', self.urldata + ".mp4")
            print(name)
            done = wget.download(self.url, out=name)
            print(done)
            if done:
                self.labelStatus.setText("Video saved as {}".format(name))
        except:
            self.labelStatus.setText("Video not loaded!")

    def mute(self):
        print(self.castplayer.status.volume_muted)
        if self.castplayer.status.volume_muted == True:
            self.castplayer.set_volume_muted(False)
            self.muteButton.setIcon(self.style().standardIcon(QStyle.SP_MediaVolumeMuted))
        else:
            self.castplayer.set_volume_muted(True)
            self.muteButton.setIcon(self.style().standardIcon(QStyle.SP_MediaVolume))

    def next(self):
        vint = int(self.listVideos.currentRow()) + 1
        self.listVideos.setCurrentRow(vint)
        max = len(self.videoList)
        if vint > max:
            return
        vid = self.videoList[vint][1]
        vidt = self.videoList[vint][0]
        vidd = self.videoList[vint][2]
        self.play_url(vid, vidd)
        self.labelStatus.setText("Playing {}".format(vidt))

    def back(self):
        vint = int(self.listVideos.currentRow()) - 1
        self.listVideos.setCurrentRow(vint)
        if 0 > vint:
            return
        vid = self.videoList[vint][1]
        vidt = self.videoList[vint][0]
        vidd = self.videoList[vint][2]
        self.play_url(vid, vidd)
        self.labelStatus.setText("Playing {}".format(vidt))


    def play(self):
        if self.castplayer.media_controller.is_playing:
            self.castplayer.media_controller.pause()
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        else:
            self.castplayer.media_controller.play()
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))

    def setSlider(self):
        try:
            if self.castplayer.media_controller.is_playing:
                self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
            else:
                self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        except:
            pass
        try:
            position = int("{:.0f}".format(self.castplayer.media_controller.status.adjusted_current_time))
            pos = str(position)
            if len(pos) == 1:
                pretty = "0:0{}".format(position)
            elif position < 60:
                pretty = "0:{}".format(position)
            else:
                pretty = str(datetime.timedelta(seconds=position)).split(':', 1)[1]
            self.clockStatus.setText(pretty)
            position = int("{:.0f}".format(position/self.castplayer.media_controller.status.duration*100))
            self.current = position
            self.positionSlider.setValue(position)
        except:
            pass

    def seekf(self):
        position = int("{:.0f}".format(self.castplayer.media_controller.status.adjusted_current_time)) + 5
        print(position)
        self.castplayer.media_controller.seek(position)

    def seekb(self):
        position = int("{:.0f}".format(self.castplayer.media_controller.status.adjusted_current_time)) - 5
        print(position)
        self.castplayer.media_controller.seek(position)


    def handleError(self):
        self.playButton.setEnabled(False)
        self.labelStatus.setText("Error: {}".format(self.vidPlayer.errorString()))

    def gamebox(self):
        self.web = QDialog(self)
        data = self.gamesList[int(self.listGames.currentRow())][0]
        self.web.setWindowTitle('Gameday Report - {}'.format(data))
        self.web.resize(820, 760)
        self.webView = QWebEngineView(self.web)
        self.webView.setGeometry(QtCore.QRect(10, 10, 800, 700))
        s = str(self.gamePk)
        url = 'https://www.mlb.com/gameday/{}#game_tab=boxscore'.format(s)
        self.webView.setUrl(QtCore.QUrl(url))
        self.webButton = QPushButton(self.web)
        self.webButton.setText("Close")
        self.webButton.move(10, 720)
        self.webButton.resize(800, 30)
        self.webButton.setAutoFillBackground(True)
        self.webButton.setFlat(True)
        self.webButton.clicked.connect(self.web.close)
        self.web.show()

    def gameplays(self):
        self.web = QDialog(self)
        data = self.gamesList[int(self.listGames.currentRow())][0]
        self.web.setWindowTitle('Gameday Report - {}'.format(data))
        self.web.resize(820, 760)
        self.webView = QWebEngineView(self.web)
        self.webView.setGeometry(QtCore.QRect(10, 10, 800, 700))
        s = str(self.gamePk)
        url = 'https://www.mlb.com/gameday/{}#game_tab=play-by-play'.format(s)
        self.webView.setUrl(QtCore.QUrl(url))
        self.webButton = QPushButton(self.web)
        self.webButton.setText("Close")
        self.webButton.move(10, 720)
        self.webButton.resize(800, 30)
        self.webButton.setAutoFillBackground(True)
        self.webButton.setFlat(True)
        self.webButton.clicked.connect(self.web.close)
        self.web.show()

    def settings(self):
        self.setdialog = QDialog(self)
        self.setdialog.setWindowTitle('Settings')
        self.setdialog.setFixedSize(400, 475)
        self.combo = QComboBox(self.setdialog)
        self.combo.resize(100, 50)
        self.combo.setFont(self.favfont)
        teams = sorted(teamids)
        teams.remove('None')
        teams.insert(0, 'None')
        if self.favteam:
            self.combo.addItem(self.favteam)
            teams.remove(self.favteam)
        for each in teams:
            self.combo.addItem(each)

        self.combo.move(15, 50)
        self.combo.activated[str].connect(self.onChanged)
        self.combo.setAutoFillBackground(True)
        self.favlabel = QLabel(self.setdialog)
        self.favlabel.setText('Select Your Favourite Team')
        self.favlabel.adjustSize()
        self.favlabel.move(15, 15)
        self.favlabel.resize(370, 25)
        self.favlabel.setFont(self.favfont)

        self.cpicker1 = QLabel(self.setdialog)
        self.cpicker1.move(150, 50)
        self.cpicker1.resize(100, 100)
        self.cpicker1.setStyleSheet('background-color: {};'.format(self.color1))
        self.cpicker2 = QLabel(self.setdialog)
        self.cpicker2.move(250, 50)
        self.cpicker2.resize(100, 100)
        self.cpicker2.setStyleSheet('background-color: {};'.format(self.color2))

        self.okayButton = QPushButton(self.setdialog)
        self.okayButton.setText('Done')
        self.okayButton.resize(370, 50)
        self.okayButton.move(15, 400)
        self.okayButton.clicked.connect(self.onClose)
        self.okayButton.setFont(self.favfont)

        self.toollabel = QLabel(self.setdialog)
        self.toollabel.setText('Options')
        self.toollabel.adjustSize()
        self.toollabel.move(15, 175)
        self.toollabel.setFont(self.favfont)

        self.tooltipButton = QPushButton(self.setdialog)
        if self.showToolTip == "True":
            self.tooltipButton.setText('Show ToolTip On')
        else:
            self.tooltipButton.setText('Show ToolTip Off')
        self.tooltipButton.setFont(self.favfont)
        self.tooltipButton.resize(370, 50)
        self.tooltipButton.move(15, 200)
        self.tooltipButton.clicked.connect(self.onToolTip)

        self.favfontButton = QPushButton(self.setdialog)
        fonttext = self.favfont.toString().split(',')[0]
        fontsize = self.favfont.toString().split(',')[1]
        self.favfontButton.setText("{} - {}pt".format(fonttext, fontsize))
        self.favfontButton.setFont(self.favfont)
        self.favfontButton.resize(370, 50)
        self.favfontButton.move(15, 250)
        self.favfontButton.clicked.connect(self.onFont)

        self.setdialog.show()

    def onFont(self):
        font, status = QFontDialog.getFont()
        if status:
            fonttext = font.toString().split(',')[0]
            fontsize = font.toString().split(',')[1]
        self.favfontButton.setText("{} - {}pt".format(fonttext, fontsize))
        self.favfont = font
        self.saveButton.setFont(font)
        self.listGames.setFont(font)
        self.calendarWidget.setFont(font)
        self.listVideos.setFont(font)
        self.eventButton.setFont(font)
        self.playsButton.setFont(font)
        self.labelCast.setFont(font)
        self.menuFile.setFont(font)
        self.tooltipButton.setFont(font)
        self.favfontButton.setFont(font)
        self.combo.setFont(font)
        self.favlabel.setFont(font)
        self.okayButton.setFont(font)
        self.toollabel.setFont(font)
        self.labelStatus.setFont(font)
        self.alabel.setFont(font)

    def onToolTip(self):
        if self.showToolTip == "False":
            self.tooltipButton.setText('Show ToolTip On')
            self.showToolTip = "True"
        else:
            self.tooltipButton.setText('Show ToolTip Off')
            self.showToolTip = "False"

    def onClose(self, text):
        self.config['SETTINGS']['FavTeam'] = self.favteam
        self.config['SETTINGS']['Color1'] = self.color1
        self.config['SETTINGS']['Color2'] = self.color2
        self.config['SETTINGS']['FavTeamID'] = str(self.teamid)
        self.config['SETTINGS']['ShowToolTip'] = self.showToolTip
        self.config['SETTINGS']['FavFont'] = self.favfont.toString()
        with open('settings.ini', 'w') as configfile:
            self.config.write(configfile)
        self.setdialog.close()


    def onChanged(self, text):
        text = str(text)
        self.favteam = text
        self.teamid = teamids[text]
        self.Tlabel.setPixmap(QtGui.QPixmap("teams/{}.svg".format(self.teamid)))
        self.tray_icon.setIcon(QIcon("teams/{}.svg".format(self.teamid)))
        self.color1 = teamcolors[text][0]
        self.cpicker1.setStyleSheet('background-color: {};'.format(self.color1))
        self.color2 = teamcolors[text][1]
        self.cpicker2.setStyleSheet('background-color: {};'.format(self.color2))
        self.listGames.setStyleSheet('selection-background-color: {}; selection-color: {};'.format(self.color1, self.color2))
        nav1 = '#qt_calendar_navigationbar { background-color : ' + "{}".format(self.color1) + "; }"
        nav2 = '#qt_calendar_qtoolbutton { color : white; }'
        nav3 = 'QCalendarWidget QAbstractItemView { selection-background-color: ' + "{}".format(self.color1) + "; selection-color:" + "{}".format(self.color2) + "; }"
        self.calendarWidget.setStyleSheet(nav1 + nav2 + nav3)
        self.fav_games()
        self.combo.setStyleSheet('background-color: {}; color : {};'.format(self.color1, self.color2))
        self.okayButton.setStyleSheet('background-color: {}; color : {};'.format(self.color1, self.color2))
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, QColor(self.color1))
        palette.setColor(QPalette.ToolTipText, QColor(self.color2))
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(self.color1))
        palette.setColor(QPalette.ButtonText, QColor(self.color2))
        palette.setColor(QPalette.BrightText, Qt.white)
        palette.setColor(QPalette.Link, QColor(self.color2))
        palette.setColor(QPalette.Highlight, QColor(self.color2))
        palette.setColor(QPalette.HighlightedText, Qt.white)
        QApplication.instance().setPalette(palette)
        self.listVideos.setStyleSheet('selection-background-color: {}; selection-color: {};'.format(self.color1, self.color2))
        self.menubar.setStyleSheet('background-color: {}; selection-background-color: {};'.format(self.color1, self.color1))

if __name__ == '__main__':
    import sys
    import configparser
    config = configparser.ConfigParser()
    config.read('settings.ini')
    color2 = config['SETTINGS']['Color2']
    color1 = config['SETTINGS']['Color1']
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, QColor(color1))
    palette.setColor(QPalette.ToolTipText, QColor(color2))
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(color1))
    palette.setColor(QPalette.ButtonText, QColor(color2))
    palette.setColor(QPalette.BrightText, Qt.white)
    palette.setColor(QPalette.Link, QColor(color2))
    palette.setColor(QPalette.Highlight, QColor(color2))
    palette.setColor(QPalette.HighlightedText, Qt.white)
    app.setPalette(palette)
    window = BaseballVids()
    window.show()
    sys.exit(app.exec_())

