#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Author: Jakub Adamec
"""

import sys, os
from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QWidget, QMessageBox, QPushButton, QApplication, QGridLayout, QListWidget, QMessageBox
from PyQt5.QtWidgets import QApplication,QVBoxLayout, QHBoxLayout, QGroupBox, QScrollArea, QVBoxLayout, QGroupBox, QLabel, QPushButton, QFormLayout
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QTableWidget,QTableWidgetItem
from pygame import mixer
from itertools import cycle
from collections import deque #iterate reversely
from mutagen.id3 import *
import mutagen
from mutagen.id3 import ID3, ID3NoHeaderError
from mutagen.mp3 import MP3 #metadata manipulation
import numpy as np
from PIL import Image
from matplotlib import pyplot as plt
import musicbrainzngs #metadata from public database
import copy #copy instance of object
import gzip, pickle
import atexit
import threading
import time
import audio_metadata

import data
import beatalg

# all songs will be in one default playlist

class Playlist():
    #allPlaylists = []
    def __init__(self):
        self.name = "" #unique to each instance
        self.songs = [] #songs with path or list of songs
        #Playlist.allPlaylists.append(self)

    def setNameToPlaylist(self, name):
        self.name = name

    def addSongToPlaylist(self, songName):
        self.songs.append(songName)

    def setMergedList(self, list1, list2):
        self.songs = list(set(list1 + list2))

    def setIntersectedList(self, list1, list2):
        self.songs = [value for value in list1 if value in list2]

    def setSymDiffList(self, list1, list2):
        self.songs = [value for value in list1 + list2 if value not in list1 or value not in list2]

    def removeSongFromPlaylist(self, songName):
        self.songs.remove(songName)

    def clearAllPlaylist(self):
        self.songs.clear()

    def getAllSongs(self):
        return self.songs #maybe next func to return for QComboBox

    def printAllsongs(self):
        for i in range(len(self.songs)):
            print(self.songs[i])

    def getNameOfPlaylist(self):
        return self.name




class Dialog(QDialog):#nemusi byt ako samotna trieda asi
    nameOfPlaylist = ""

    def __init__(self,allplaylists):
        super(Dialog, self).__init__()
        self.createFormGroupBox(allplaylists)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)# | QDialogButtonBox.Cancel
        buttonBox.accepted.connect(self.accept)
        #buttonBox.rejected.connect(self.reject)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.formGroupBox)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)

        self.setWindowTitle("Playlist selector")
        self.boxCombo.activated[str].connect(self.pLaylistOnClick)
        #self.show()

    def createFormGroupBox(self, allplaylists):
        self.boxCombo = QComboBox()
        self.boxCombo.clear()
        #array = allplaylists.returnListPlaylist()
        #print(len(playlists))
        for item in range(len(allplaylists)):
            self.boxCombo.addItem(allplaylists[item].getNameOfPlaylist())
            #print(playlists[item].getNameOfPlaylist())
        self.formGroupBox = QGroupBox("Click playlist")
        layout = QFormLayout()
        layout.addRow(QLabel("Playlist:"), self.boxCombo)
        self.formGroupBox.setLayout(layout)

    def pLaylistOnClick(self, text):
        self.nameOfPlaylist = text # return name of picked playlist

    def returnPickedPlaylist(self):
        return self.nameOfPlaylist

class MusicPlayer(QWidget):
    #TODO: function for loading files
    songsList = [] # class variable shared by all instances
    dataSongs = [] #ID3 for songs
    allPlaylists = []
    playLists = [] # users created class of playlists


    def __init__(self):
        super().__init__()
        mixer.init()

        #initialization of permanent object from file
        try:
            with open('playlistsA', 'rb') as self.f:
                database = pickle.load(self.f)
                self.f.close()
        except (IOError, EOFError):
            #database = []
            #print("eeee")
            pass

        atexit.register(self.savePermanent)

        #print(*database, sep= "; ")

        self.initUI()

    def initSongList(self):
        #filesList = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        #print(filesList)
        #os.chdir(filesList)
        os.chdir("/home/jakub/Music/The Cure - 1979 Boys Don't Cry")
        filesLists= os.listdir()
        self.realpath = filesLists
        for file in filesLists:
            if (file.lower().endswith(".mp3")):#case insensitive
                self.songsList.append(file)
            elif(file.lower().endswith(".wav")):
                self.songsList.append(file)


        #os.chdir("/home/jakub/Music/No Doubt-Tragic Kingdom")
    def listview_clicked(self):#set variable with picked song
        item = self.listWidget.currentItem()
        #print(item.text())
        self.pickedSong = item.text()
        self.status = "Stopped"
        self.fillBoxSongInfo()
        #self.initTable()

    def playlistview_clicked(self):
        itemPlaylist2 = self.playlistWidget.currentItem()
        self.playlist2CurrentSong = itemPlaylist2.text()
        print("ll ",self.playlist2CurrentSong)

    def initUI(self):
        self.pickedSong = ""
        self.playlist2CurrentSong = ""
        self.status = "Stopped" #activity in player ->played|paused|unpaused|stopped
        self.currentPlaylist = Playlist()

        onePlaylist = Playlist()
        onePlaylist.setNameToPlaylist("Prvy playlist")
        onePlaylist.addSongToPlaylist("Pesnicka 1")
        onePlaylist.addSongToPlaylist("Necho boze da")
        onePlaylist.addSongToPlaylist("Siel siel")
        twoPlaylist = Playlist()
        twoPlaylist.setNameToPlaylist("Druhy Playlist")
        twoPlaylist.addSongToPlaylist("Pesnicka AA")
        twoPlaylist.addSongToPlaylist("Pesnicka AB")
        twoPlaylist.addSongToPlaylist("Pesnicka CC")
        threePlaylist = Playlist()
        threePlaylist.setNameToPlaylist("Treti Playlist")
        threePlaylist.addSongToPlaylist("Pesnicka 1233")
        self.addToPlaylists(onePlaylist)
        self.addToPlaylists(twoPlaylist)
        self.addToPlaylists(threePlaylist)


        btnPlay = QPushButton(self)
        btnPlay.setIcon(QIcon(QPixmap("icons/iconPlay.svg")))
        btnPlay.move(20, 20)
        btnPlay.clicked.connect(self.play)

        btnPause = QPushButton(self)
        btnPause.setIcon(QIcon(QPixmap("icons/iconPause.svg")))
        btnPause.move(60, 20)
        btnPause.clicked.connect(self.pause)

        btnStop = QPushButton(self)
        btnStop.setIcon(QIcon(QPixmap("icons/iconStop.svg")))
        btnStop.move(100, 20)
        btnStop.clicked.connect(self.stop)

        btnPrev = QPushButton(self)
        btnPrev.setIcon(QIcon(QPixmap("icons/iconPrev.svg")))
        btnPrev.move(140, 20)
        btnPrev.clicked.connect(self.previous)
        #btnPrev

        btnNext = QPushButton(self)
        btnNext.setIcon(QIcon(QPixmap("icons/iconNext.svg")))
        btnNext.move(180, 20)
        btnNext.clicked.connect(self.next)

        btnSelectPlaylist = QPushButton('Select Playlist',self)
        btnSelectPlaylist.move(280, 20)
        btnSelectPlaylist.clicked.connect(self.selectPlaylists)
        #self.infobox()



        btnToPlaylist = QPushButton('Add to Playlist',self)
        btnToPlaylist.move(390, 20)
        btnToPlaylist.clicked.connect(self.addSongToPlaylistAction)

        btnEraseFromPlaylist = QPushButton('Erase from Playlist',self)
        btnEraseFromPlaylist.move(620, 50)
        btnEraseFromPlaylist.clicked.connect(self.eraseSongFromPlaylistAction)

        btnCreatePlaylist = QPushButton('Create Playlist',self)
        btnCreatePlaylist.move(505, 20)
        btnCreatePlaylist.clicked.connect(self.createPlaylistAction)

        btnDeletePlaylist = QPushButton('Delete Playlist',self)
        btnDeletePlaylist.move(620, 20)
        btnDeletePlaylist.clicked.connect(self.deletePlaylistAction)

        btnMergePlaylist = QPushButton('Merge playlists',self)
        btnMergePlaylist.move(620, 80)
        btnMergePlaylist.clicked.connect(self.mergePlaylistsAction)

        btnInterPlaylist = QPushButton('Inter playlists',self)
        btnInterPlaylist.move(620, 110)
        btnInterPlaylist.clicked.connect(self.interPlaylistsAction)

        btnSymDiffPlaylist = QPushButton('Diff playlists',self)
        btnSymDiffPlaylist.move(620,140)
        btnSymDiffPlaylist.clicked.connect(self.symetricDiffPlaylistsAction)

        btnExportPlaylist = QPushButton('Export PL->ALBUM',self)
        btnExportPlaylist.move(620,170)

        btnBPM = QPushButton('Get BPM',self)
        btnBPM.move(620,200)

        self.labelBPM = QLabel(self)
        self.labelBPM.move(620,240)
        self.labelBPM.resize(100,20)
        self.labelBPM.setStyleSheet("background-color: red; border: 1px inset grey;")
        self.labelBPM.setText("BPM: ")

        #show playlist name
        self.labelPlaylist = QLabel(self)
        self.labelPlaylist.move(300, 230)
        self.labelPlaylist.resize(200,20)
        self.labelPlaylist.setStyleSheet("background-color: white; border: 1px inset grey;")
        self.labelPlaylist.setText("")
        #self.labelPlaylist

        self.initSongList()
        #print("-------------------------")
        self.songsList.sort()
        #iterSongList = iter(self.songsList)
        iterSongList = cycle(self.songsList)
        layout = QGridLayout()


        #songs in main playlist
        self.listWidget = QListWidget(self)
        for song in self.songsList:#fill list with songs
            self.listWidget.addItem(song)
        #Resize width and height
        self.listWidget.resize(270,370)
        self.listWidget.move(20, 250)


        self.listWidget.setWindowTitle('PyQT QListwidget Demo')
        #listWidget.itemClicked.connect(listWidget.Clicked)
        self.listWidget.clicked.connect(self.listview_clicked)

        self.playlistWidget = QListWidget(self)
        self.playlistWidget.resize(240,370)
        self.playlistWidget.move(300, 250)

        self.playlistWidget.clicked.connect(self.playlistview_clicked)
        #self.playlistWidget

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
            self.infoLabels.append(QLabel(""))
            vbox.addWidget(self.infoLabels[i])

        #self.groupbox.setLayout(vbox)
        #groupbox.setFont(QtGui.QFont("Sanserif", 15))

        #ADD image
        label = QLabel(self)
        pixmap = QPixmap('cover.jpg')
        pixmap = pixmap.scaled(110, 110, Qt.KeepAspectRatio)
        label.setPixmap(pixmap)
        #label.setFixedSize(180,130)
        #label.resize(150,110)

        v2box.addWidget(label)
        v2box.setAlignment(Qt.AlignTop)

        hbox.addLayout(v2box)
        hbox.addLayout(vbox)
        self.groupbox.setLayout(hbox)

        #vbox.addWidget(label)

        #init metadata databse table
        self.tableWidgetMeta = QTableWidget(self)
        self.tableWidgetMeta.move(550,270)
        self.tableWidgetMeta.resize(240,350)


        #self.setGeometry(100, 100, 750, 400)
        self.setFixedSize(800, 640)
        self.setWindowTitle('Gnome Music Player Clone')



        self.show()

    def addSongToPlaylistAction(self):
        if(self.pickedSong):
            for x in range(len(self.allPlaylists)):
                if(self.allPlaylists[x].getNameOfPlaylist() == self.currentPlaylist.getNameOfPlaylist()):#current playlist
                    self.allPlaylists[x].addSongToPlaylist(self.pickedSong)
                    self.refreshPlaylistWidget()

    def eraseSongFromPlaylistAction(self):
        print("oooooo")
        if(self.playlist2CurrentSong):
            print(self.playlist2CurrentSong)
            for x in range(len(self.allPlaylists)):
                if(self.allPlaylists[x].getNameOfPlaylist() == self.currentPlaylist.getNameOfPlaylist()):#current playlist
                    self.allPlaylists[x].removeSongFromPlaylist(self.playlist2CurrentSong)
                    self.refreshPlaylistWidget()

    def addToPlaylists(self, playlist):
        self.allPlaylists.append(playlist)

    def initDatabaseTable(self, nameArtist, nameSong):
        metadataList = data.getMetadata(nameArtist,nameSong)
        rowL = len(metadataList)
        if(rowL < 1):#do nothing, no data
            return
        #set length of rows in table
        self.tableWidgetMeta.setRowCount(rowL)
        self.tableWidgetMeta.setColumnCount(2)
        #catch error for empty metadaList
        i = 0
        for key, value in metadataList.items():
            self.tableWidgetMeta.setItem(i,0, QTableWidgetItem(key))
            self.tableWidgetMeta.setItem(i,1, QTableWidgetItem(value))
            i = i + 1


    def savePermanent(self):
        try:
            pickle.dump(self.allPlaylists, self.f)
            self.f.close()
        except:
            pass
        print("Saving data")


    def mergePlaylistsAction(self):
        newName, ok = QInputDialog.getText(self, 'Merge of Playlist', 'Set new Name for merged playlist:')
        if not ok:
            return
        if not newName:
            return
        tempArray1 = []#names of playlist to qdialog
        for x in range(len(self.allPlaylists)):
            tempArray1.append(self.allPlaylists[x].getNameOfPlaylist())
        firstPlaylist, ok = QInputDialog.getItem(self, "First Playlist", "Select first playlist to merge",tempArray1 , 0, False)
        if not ok:
            return
        tempArray2 = []#names of playlist to qdialog
        for x in range(len(self.allPlaylists)):
            if(self.allPlaylists[x].getNameOfPlaylist() != firstPlaylist):
                tempArray2.append(self.allPlaylists[x].getNameOfPlaylist())
        if not ok:
            return
        secondPlaylist, ok = QInputDialog.getItem(self, "Second Playlist", "Select second playlist to merge",tempArray2 , 0, False)

        playlist1 = Playlist()
        playlist1 = self.playlistFromName(firstPlaylist)
        playlist2 = Playlist()
        playlist2 = self.playlistFromName(secondPlaylist)

        merged = Playlist()
        merged.setNameToPlaylist(newName)
        merged.setMergedList(playlist1.getAllSongs(), playlist2.getAllSongs())
        self.allPlaylists.append(merged)

        self.refreshPlaylistWidget() #refresh values

    def interPlaylistsAction(self):
        newName, ok = QInputDialog.getText(self, 'Intersection of Playlists', 'Set new Name for final playlist:')
        if not ok:
            return
        if not newName:
            return
        tempArray1 = []#names of playlist to qdialog
        for x in range(len(self.allPlaylists)):
            tempArray1.append(self.allPlaylists[x].getNameOfPlaylist())
        firstPlaylist, ok = QInputDialog.getItem(self, "First Playlist", "Select first playlist to intersect",tempArray1 , 0, False)
        if not ok:
            return
        tempArray2 = []#names of playlist to qdialog without one
        for x in range(len(self.allPlaylists)):
            if(self.allPlaylists[x].getNameOfPlaylist() != firstPlaylist):
                tempArray2.append(self.allPlaylists[x].getNameOfPlaylist())
        if not ok:
            return
        secondPlaylist, ok = QInputDialog.getItem(self, "Second Playlist", "Select second playlist to merge",tempArray2 , 0, False)

        playlist1 = Playlist()
        playlist1 = self.playlistFromName(firstPlaylist)
        playlist2 = Playlist()
        playlist2 = self.playlistFromName(secondPlaylist)

        intersected = Playlist()
        intersected.setNameToPlaylist(newName)
        intersected.setIntersectedList(playlist1.getAllSongs(), playlist2.getAllSongs())
        self.allPlaylists.append(intersected)

        self.refreshPlaylistWidget() #refresh values

    def symetricDiffPlaylistsAction(self):
        newName, ok = QInputDialog.getText(self, 'Intersection of Playlists', 'Set new Name for final playlist:')
        if not ok:
            return
        if not newName:
            return
        tempArray1 = []#names of playlist to qdialog
        for x in range(len(self.allPlaylists)):
            tempArray1.append(self.allPlaylists[x].getNameOfPlaylist())
        firstPlaylist, ok = QInputDialog.getItem(self, "First Playlist", "Select first playlist to intersect",tempArray1 , 0, False)
        if not ok:
            return
        tempArray2 = []#names of playlist to qdialog without one
        for x in range(len(self.allPlaylists)):
            if(self.allPlaylists[x].getNameOfPlaylist() != firstPlaylist):
                tempArray2.append(self.allPlaylists[x].getNameOfPlaylist())
        if not ok:
            return
        secondPlaylist, ok = QInputDialog.getItem(self, "Second Playlist", "Select second playlist to merge",tempArray2 , 0, False)

        playlist1 = Playlist()
        playlist1 = self.playlistFromName(firstPlaylist)
        playlist2 = Playlist()
        playlist2 = self.playlistFromName(secondPlaylist)

        symDiff = Playlist()
        symDiff.setNameToPlaylist(newName)
        symDiff.setSymDiffList(playlist1.getAllSongs(), playlist2.getAllSongs())
        self.allPlaylists.append(symDiff)

        self.refreshPlaylistWidget() #refresh values


    def playlistFromName(self, name):
        for x in range(len(self.allPlaylists)):
            if(self.allPlaylists[x].getNameOfPlaylist() == name):
                tempPlaylist = Playlist()
                tempPlaylist = copy.copy(self.allPlaylists[x])

        return tempPlaylist

    def createPlaylistAction(self):
        text, ok = QInputDialog.getText(self, 'Playlist Creator', 'Enter playlist name:')
        tempPlay = Playlist()
        tempPlay.setNameToPlaylist(str(text))
        #tempPlay.addSongToPlaylist("zzzz")

        self.allPlaylists.append(tempPlay)

        self.refreshPlaylistWidget() #refresh values

        #if ok:
         #print(str(text))

    def deletePlaylistAction(self):

        tempArray = []#names of playlist to qdialog
        for x in range(len(self.allPlaylists)):
            tempArray.append(self.allPlaylists[x].getNameOfPlaylist())


        item, ok = QInputDialog.getItem(self, "select input dialog", "list of playlists",tempArray , 0, False)

        if not ok:
            return

        if not item:
            return
        nameOfDeletedPlaylist = str(item)

        #print(len(self.allPlaylists))
        for x in range(len(self.allPlaylists)):
            if(self.allPlaylists[x].getNameOfPlaylist() == nameOfDeletedPlaylist):
                self.allPlaylists.pop(x)#delete playlist
                break#break, deletes last item and dynamically lowers index so crash appears

        #check for current playlsit deleted
        if(self.currentPlaylist.getNameOfPlaylist() == nameOfDeletedPlaylist):
            if( len(self.allPlaylists) > 0 ):
                self.currentPlaylist = self.allPlaylists[0]
            else:#if there is no other playlist
                self.currentPlaylist.setNameToPlaylist("")
                self.currentPlaylist.clearAllPlaylist()

        self.refreshPlaylistWidget()

    def fillBoxSongInfo(self):
        name = self.pickedSong
        #add path
        song = ("/home/jakub/Music/The Cure - 1979 Boys Don't Cry/"+self.pickedSong)

        if (name.lower().endswith(".mp3")):
            try:
                audio = ID3(song)
            except (ID3NoHeaderError):
                audio = ID3()#or return
                self.infoLabels[0].setText("Name: ")
                self.infoLabels[1].setText("Artist: ")
                self.infoLabels[2].setText("Length: ")
                self.infoLabels[3].setText("Format: ")
                return

            mp3s = MP3(song)
            try:
                self.infoLabels[0].setText("Name: " + audio["TIT2"].text[0])
            except:
                self.infoLabels[0].setText("Name: ")
            try:
                self.infoLabels[1].setText("Artist: " + audio["TPE1"].text[0])
            except:
                self.infoLabels[0].setText("Artist: ")
            try:
                self.infoLabels[2].setText("Length: " + self.secondsLength(mp3s.info.length))
            except:
                self.infoLabels[0].setText("Length: ")
            try:
                self.infoLabels[3].setText("Format: " + str(mp3s.info.channels) + " channels, " + str(mp3s.info.sample_rate/1000) + "Hz, " + str(int(mp3s.info.bitrate/1000)) + "kbps")
            except:
                self.infoLabels[0].setText("Format: ")

            print(audio.pprint())
            self.initDatabaseTable(audio["TPE1"].text[0], audio["TIT2"].text[0],)


        elif(name.lower().endswith(".wav")):

            try:
                metadata = audio_metadata.load(song)

            except:
                self.infoLabels[0].setText("Name: ")
                self.infoLabels[1].setText("Artist: ")
                self.infoLabels[2].setText("Length: ")
                self.infoLabels[3].setText("Format: ")
                return

            print(metadata)

            try:
                self.infoLabels[0].setText("Name: " + metadata.tags['title'][0])
            except:
                self.infoLabels[0].setText("Name: ")
            try:
                self.infoLabels[1].setText("Artist: "+ metadata.tags['artist'][0])
            except:
                self.infoLabels[1].setText("Artist: ")
            try:
                self.infoLabels[2].setText("Length: " + self.secondsLength(metadata.streaminfo['duration']))
            except:
                self.infoLabels[2].setText("Length: ")
            try:
                self.infoLabels[3].setText("Format: " + str(metadata.streaminfo['channels']) + " channels, " + str(metadata.streaminfo['sample_rate']/1000) + "Hz, " + str(int(metadata.streaminfo['bitrate']/1000)) + "kbps")
            except:
                self.infoLabels[3].setText("Format: ")

            #todo: everything to block try except


        return

    def refreshPlaylistWidget(self):
        #make label
        self.labelPlaylist.setText(self.currentPlaylist.getNameOfPlaylist())
        # update songs in list widget
        self.playlistWidget.clear()
        for song in self.currentPlaylist.getAllSongs():#fill list with songs
            self.playlistWidget.addItem(song)

    def selectPlaylists(self):


        #self.allPlaylists.printAllPlaylists()
        self.dialog = Dialog(self.allPlaylists) # popup window to select playlist
        self.dialog.exec_()

        #print(self.dialog.returnPickedPlaylist())
        nameOfPickedPlaylist = self.dialog.returnPickedPlaylist()
        for idx in range(len(self.allPlaylists)):
            if self.allPlaylists[idx].getNameOfPlaylist() == nameOfPickedPlaylist:
                #print(self.allPlaylists[idx].getNameOfPlaylist())
                self.currentPlaylist = copy.copy(self.allPlaylists[idx])
                self.currentPlaylist.printAllsongs()

                self.refreshPlaylistWidget()

        return


    def play(self):
        #print("Status in play is " + self.status)
        if self.status == "Paused": #continues playing
            self.status = "Played"
            mixer.music.unpause()
            return
        else: # play song from beginning
            #self.stop()
            self.status = "Played"
            #print("Mixer loads "+ self.pickedSong)
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

        '''
    def closeEvent(self, event):

        quit_msg = "Are you sure you want to exit the program?"
        reply = QMessageBox.question(self, 'Message',
                         quit_msg, QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.saveToFile()

            event.accept()
        else:
            event.ignore()

    def saveToFile(self):
        with open('playlistsA', 'wb') as self.f:
            pickle.dump(self.allPlaylists, self.f)
        self.f.close()
        '''



if __name__ == '__main__':
    musicbrainzngs.set_useragent(
    "python-musicbrainzngs-example",
    "0.1",
    "https://github.com/alastair/python-musicbrainzngs/",
)

    #result = musicbrainzngs.search_releases(artist=artist, tracks=album,limit=1)
    #print(result['release-list'])


    app = QApplication(sys.argv)
    ex = MusicPlayer()
    sys.exit(app.exec_())
