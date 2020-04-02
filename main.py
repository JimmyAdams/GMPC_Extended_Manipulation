#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Author: Jakub Adamec
"""

import sys, os
from PyQt5 import QtGui
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QGridLayout, QListWidget, QMessageBox
from PyQt5.QtWidgets import QApplication,QVBoxLayout, QHBoxLayout, QGroupBox, QScrollArea, QVBoxLayout, QGroupBox, QLabel, QPushButton, QFormLayout
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QTableWidget,QTableWidgetItem
from pygame import mixer
from itertools import cycle
from collections import deque
from mutagen.id3 import *
import mutagen
from mutagen.mp3 import MP3
import numpy as np
from PIL import Image
from matplotlib import pyplot as plt

class MyButtons():
    def __init__(self):
        QObject.__init__(self)


class MusicPlayer(QWidget):
    #TODO: function for loading files
    songsList = [] # class variable shared by all instances
    dataSongs = [] #ID3 for songs

    def __init__(self):
        super().__init__()
        mixer.init()
        self.initUI()

    def initSongList(self):
        os.chdir("/home/jakub/Music/The Cure - 1979 Boys Don't Cry")
        filesList= os.listdir()
        for file in filesList:

            if file.lower().endswith(".mp3"):#case insensitive
                self.songsList.append(file)
                realdir = os.path.realpath(file)
                tempAudio = ID3(realdir)
                #print(tempAudio['TIT2'].text[0])
                #audio = ID3(realdir)
                self.dataSongs.append(tempAudio['TIT2'].text[0])
                #print(audio['TIT2'].text[0])


        #os.chdir("/home/jakub/Music/No Doubt-Tragic Kingdom")
    def listview_clicked(self):#set variable with picked song
        item = self.listWidget.currentItem()
        print(item.text())
        #self.play(item.text())
        #self.status == "Stopped"
        self.pickedSong = item.text()
        self.status = "Stopped"
        self.fillBoxSongInfo()

    def initUI(self):
        self.pickedSong = ""
        self.status = "Stopped" #activity in player ->played|paused|unpaused|stopped
        #qbtn = QPushButton('Quit', self)
        #qbtn.clicked.connect(QApplication.instance().quit)
        #btn.resize(qbtn.sizeHint())
        #qbtn.move(50, 50)

        btnPlay = QPushButton(self)
        btnPlay.setIcon(QIcon(QPixmap("play.png")))
        btnPlay.move(20, 20)
        btnPlay.clicked.connect(self.play)

        btnPause = QPushButton(self)
        btnPause.setIcon(QIcon(QPixmap("pause.png")))
        btnPause.move(60, 20)
        btnPause.clicked.connect(self.pause)

        btnStop = QPushButton(self)
        btnStop.setIcon(QIcon(QPixmap("stop.png")))
        btnStop.move(100, 20)
        btnStop.clicked.connect(self.stop)

        btnPrev = QPushButton(self)
        btnPrev.setIcon(QIcon(QPixmap("previous.png")))
        btnPrev.move(140, 20)
        btnPrev.clicked.connect(self.previous)
        #btnPrev

        btnNext = QPushButton(self)
        btnNext.setIcon(QIcon(QPixmap("next.png")))
        btnNext.move(180, 20)
        btnNext.clicked.connect(self.next)

        #self.infobox()

        self.initSongList()
        print("-------------------------")
        self.songsList.sort()
        #iterSongList = iter(self.songsList)
        iterSongList = cycle(self.songsList)
        layout = QGridLayout()

        self.tableWidget = QTableWidget(self)
        self.tableWidget.move(400,230)
        self.tableWidget.resize(300,370)
        self.initTable()


        self.listWidget = QListWidget(self)
        for song in self.songsList:#fill list with songs
            self.listWidget.addItem(song)
        #Resize width and height
        self.listWidget.resize(300,370)
        self.listWidget.move(50, 230)


        self.listWidget.setWindowTitle('PyQT QListwidget Demo')
        #listWidget.itemClicked.connect(listWidget.Clicked)
        self.listWidget.clicked.connect(self.listview_clicked)

        #Song Info Box
        self.groupbox = QGroupBox("Song Info",self)
        self.groupbox.move(50, 60)
        self.groupbox.resize(500, 150)
        hbox = QHBoxLayout()
        v2box = QVBoxLayout()
        vbox = QVBoxLayout()
        self.infoLabels = []
        #infoLabels[1] = QLabel()
        for i in range(0,4):
            self.infoLabels.append(QLabel("wee"))
            vbox.addWidget(self.infoLabels[i])

        #self.groupbox.setLayout(vbox)
        #groupbox.setFont(QtGui.QFont("Sanserif", 15))

        label = QLabel(self)
        pixmap = QPixmap('cover.jpg')

        label.setPixmap(pixmap)
        label.setFixedSize(150,110)

        v2box.addWidget(label)
        v2box.setAlignment(Qt.AlignTop)

        hbox.addLayout(v2box)
        hbox.addLayout(vbox)
        self.groupbox.setLayout(hbox)

        #vbox.addWidget(label)

        #self.setGeometry(100, 100, 750, 400)
        self.setFixedSize(800, 640)
        self.setWindowTitle('Gnome Music Player Clone')

        self.show()

    def fillBoxSongInfo(self):
        name = self.pickedSong
        print(("/home/jakub/Music/No Doubt-Tragic Kingdom/"+self.pickedSong))
        song = ("/home/jakub/Music/The Cure - 1979 Boys Don't Cry/"+self.pickedSong)
        audio = ID3(song)
        mp3s = MP3(song)
        #print(audio.pprint())
        #TODO: coditions for existence
        self.infoLabels[0].setText("Name: " + audio["TIT2"].text[0])
        self.infoLabels[1].setText("Artist: " + audio["TPE1"].text[0])
        self.infoLabels[2].setText("Length: " + self.secondsLength(mp3s.info.length))
        self.infoLabels[3].setText("Format: " + str(mp3s.info.channels) + " channels, " + str(mp3s.info.sample_rate/1000) + "Hz, " + str(int(mp3s.info.bitrate/1000)) + "kbps")

        # check if has picture
        has_pic = False

        for k, v in audio.items():
            if "APIC" in k:
                has_pic = True
                break

        if(has_pic):
            pict = audio.get("APIC:").data
            #print(pict)


        return

    def play(self):
        print("Status in play is " + self.status)
        if self.status == "Paused": #continues playing
            self.status = "Played"
            mixer.music.unpause()
            return
        else: # play song from beginning
            #self.stop()
            self.status = "Played"
            print("Mixer loads "+ self.pickedSong)
            mixer.music.load("/home/jakub/Music/The Cure - 1979 Boys Don't Cry/"+self.pickedSong)#"10 - No Doubt - DON'T SPEAK.MP3"
            mixer.music.play()
            return

    def pause(self):
        if self.status == "Played":
            self.status = "Paused"
            mixer.music.pause()
            return
        if self.status == "Stopped":
            mixer.music.pause()
            return

    def stop(self):
        mixer.music.stop()
        self.status = "Stopped"; #TODO: make enum for this
        return

    def next(self):
        mixer.music.stop()

        index = self.songsList.index(self.pickedSong)#index of actual song
        #print("Index is "+ str(index))
        deq = deque(self.songsList)
        deq.rotate(-1)#shift to left
        self.pickedSong = deq[index]
        #print("Wanna "+ deq[index])
        self.status = "Played"
        self.play()
        return

    def previous(self):
        mixer.music.stop()
        index = self.songsList.index(self.pickedSong)#index of actual song
        deq = deque(self.songsList)
        deq.rotate(1)#shift to left
        self.pickedSong = deq[index]
        self.status = "Played"
        self.play()
        return

    def secondsLength(self, insec):
        if insec == 0:
            return "X"
        min = int(insec / 60)
        sec = int(insec % 60)
        word = str(min) + "min:" + str(sec) + "sec"
        return word


    def initTable(self):
        # set row count
        self.tableWidget.setRowCount(12)
        # set column count
        self.tableWidget.setColumnCount(2)
        for idx,name in enumerate(self.dataSongs):
            self.tableWidget.setItem(idx,0, QTableWidgetItem(name))

if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = MusicPlayer()
    sys.exit(app.exec_())
