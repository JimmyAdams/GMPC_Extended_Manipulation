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
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QMessageBox, QPushButton, QApplication, QGridLayout, QListWidget, QMessageBox, QToolBar, QDialogButtonBox
from PyQt5.QtWidgets import QApplication,QVBoxLayout, QHBoxLayout, QGroupBox, QScrollArea, QVBoxLayout, QGroupBox, QLabel, QPushButton, QFormLayout
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QTableWidget,QTableWidgetItem
from pygame import mixer
from itertools import cycle
from collections import deque #iterate reversely
from mutagen.id3 import *
import mutagen
from mutagen.easyid3 import EasyID3
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
from tinytag import TinyTag
import zipfile
import wave

#my own modules
import data
import beatalg


# object for song, more similar to C struct
class Song():
    def __init__(self, name, path):
        self.name = name
        self.path = path

    def getName(self):
        return self.name

    def getPath(self):
        return self.path

    def setNewPath(self, path):
        self.path = path

# will be added to lists and playlists



"""
    A class used to represent one Playlist

    ...

    Attributes
    ----------
    name : str
        the name of the playlist
    songs : list
        the list of names of playlists
"""

class Playlist():
    #allPlaylists = []
    def __init__(self):
        self.name = "" #unique to each instance
        self.songs = [] #songs with path or list of songs

    def setNameToPlaylist(self, name):
        """ Sets new name of playlist object

            Parameters
            ----------
            name : str
                Name of playlist
        """
        self.name = name

    def addSongToPlaylist(self, songName):
        """
            Add name of playlist to list

            Parameters
            ----------
            songName : str
                name of song

            Returns
            ------
            list : playlist with names

        """
        self.songs.append(songName)

    def setMergedList(self, list1, list2):
        """ Sets similar items together

            Parameters
            ----------
            list1: list
                First list to merge
            list2: list
                Second list to merge
            Returns
            -------
            list : result of merge operation
        """
        self.songs = list(set(list1 + list2))

    def setIntersectedList(self, list1, list2):
        """ Sets all items together

            Parameters
            ----------
            list1: list
                First list of songs
            list2: list
                Second list to songs
            Returns
            -------
            list : result of intersection
        """
        self.songs = [value for value in list1 if value in list2]

    def setdiffList(self, list1, list2):
        """ Sets difference of items

            Parameters
            ----------
            list1: list
                First list of songs
            list2: list
                Second list of songs
            Returns
            -------
            list : result of difference
        """
        self.songs = [value for value in list1 if value not in list2]

    def removeSongFromPlaylist(self, songName):
        """ Removes song from playlist

            Parameters
            ----------
            songName : str
                Name of song to delete
        """
        self.songs.remove(songName)

    def addSongT(self, songObject):
        self.songs.append(songObject)

    def sortSongs(self):
        self.songs.sort()

    def deleteSongT(self, songName):
        for x in range(len(self.songs)):
            if(self.songs[x].getName() == songName):
                self.songs.pop(x)#delete playlist
                break#break, deletes last item and dynamically lowers index so crash appears

    def getSongObjectT(self, songName):
        for x in range(len(self.songs)):
            if(self.songs[x].getName() == songName):
                return(self.songs[x])#delete playlist

        #if not found
        print("Not found song object")
        return Song("","")


    def isExisting(self, songObject):#find if is song in playlist
        songName = songObject.getName()
        exist = False
        for x in range(len(self.songs)):
            if(self.songs[x].getName() == songName):
                exist = True
                print(x)
                break
        return exist

    def clearAllPlaylist(self):
        """ Removes all songs from playlist

        """
        self.songs.clear()

    def getAllSongs(self):
        """ Just gets all songs

            Returns
            -------
            list : list of songs
        """
        return self.songs #maybe next func to return for QComboBox

    def printAllsongs(self):#debugging
        for i in range(len(self.songs)):
            print(self.songs[i].getName())
            print(self.songs[i].getPath())

    def getNameOfPlaylist(self):
        """ Getter for playlist name

            Returns
            -------
            str : name
        """
        return self.name


"""
    A class for media player, that contains every aspect
    of functionality in project, uses

    ...

    Attributes
    ----------
    songsList : list
        list of songs in main playlist from system
    allPlaylists : list
        the list of names of playlists
    playLists : list
        list of songs in playlist for operations and export
"""

class MusicPlayer(QWidget):
    songsList = [] # class variable shared by all instances
    allPlaylists = []
    playLists = [] # users created class of playlists


    def __init__(self):
        super().__init__()
        mixer.init()
        mixer.pre_init(44100, -16, 2, 256)

        self.pickedSong = "" # currently playing song
        self.playlist2CurrentSong = "" #picked song in second playlist, used only for erase
        self.status = "Stopped" #activity in player ->played|paused|unpaused|stopped
        self.currentPlaylist = Playlist() # init current playlist
        self.mainPlaylist = Playlist()



        #initialization of permanent object from file
        try:
            with open('playlists', 'rb') as self.f:
                database = pickle.load(self.f)
                self.allPlaylists = copy.copy(database)
                self.f.close()

        except (IOError, EOFError):
            database = []
            print("Error with permanent data")

        #run saving at end
        atexit.register(self.loadPermanentData)

        try:
            self.file = open('playlists', 'wb')
        except:
            pass
        self.initUI()

    def initSongList(self):
        """ Function for initialization of songsList
            user has to pick directory from system
            path to file is parsed (realpath)
            MP3 and WAV formats get accepted

        """
        #TODO: gets gtkdialog error
        #self.filesList = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        #gtk_window_set_transient_for(QFileDialog)
        #print(self.filesList)
        self.filesList = "/home/jakub/Music/No Doubt-Tragic Kingdom"
        os.chdir(self.filesList)
        filesLists= os.listdir()
        self.realpath = filesLists

        for file in filesLists:
            if (file.lower().endswith(".mp3")):#case insensitive
                tempSong = Song(file, str(self.filesList + "/" + file))
                if(not self.mainPlaylist.isExisting(tempSong)):
                    self.mainPlaylist.addSongT(tempSong)

                #self.songsList.append(file)
            elif(file.lower().endswith(".wav")):
                tempSong = Song(file, str(self.filesList + "/" + file))
                if(not self.mainPlaylist.isExisting(tempSong)):
                    self.mainPlaylist.addSongT(tempSong)

                #self.songsList.append(file)

        #self.songsList.sort()
        iterSongList = cycle(self.songsList)
        #songs in main playlist
        self.listWidget.clear()
        #for song in self.songsList:#fill list with songs
            #self.listWidget.addItem(song)
        tempMain = self.mainPlaylist.getAllSongs()
        for song in tempMain:
            self.listWidget.addItem(song.getName())

        #print("Main playlist")
        #self.mainPlaylist.printAllsongs()

    def listview_clicked(self):#set variable with picked song
        """
            Runs when action click pressed in playlist widget (listwidget)

        """
        item = self.listWidget.currentItem()
        #self.pickedSong = item.text()
        self.pickedSongObject = Song("","")
        self.pickedSongObject = self.mainPlaylist.getSongObjectT(item.text())
        print(type(self.pickedSongObject))
        self.status = "Stopped"
        self.mainPLstatus = 1
        self.sidePLstatus = 0
        self.fillBoxSongInfo()
        self.fillBoxSongPic()
        #self.initTable()

    def playlistview_clicked(self):
        """
            Iterate in playlist when action click pressed
        """
        itemPlaylist2 = self.playlistWidget.currentItem()
        self.playlist2CurrentSong = itemPlaylist2.text()
        self.pickedSongObject = (self.currentPlaylist.getSongObjectT(itemPlaylist2.text()))#set value for song to show
        self.playlist2pickedSongObject = self.currentPlaylist.getSongObjectT(self.playlist2CurrentSong)#using for erase
        self.mainPLstatus = 0 #main PL clicked
        self.sidePLstatus = 1
        self.fillBoxSongInfo()
        self.fillBoxSongPic()

    def initUI(self):
        """ Main part, contains PyQt5 implementation

        """

        self.noImage =  QPixmap("icons/noImage.png")

        toolBar = QToolBar(self)

        toolButton = QToolButton()
        toolButton.setText("Edit metadata")
        #toolButton.setCheckable(True)
        toolButton.setAutoExclusive(True)
        toolButton.clicked.connect(self.showdialog)
        toolBar.addWidget(toolButton)

        # button for create playlist
        btnCreatePlaylist = QToolButton(self)
        btnCreatePlaylist.setText('Create Playlist')
        btnCreatePlaylist.setAutoExclusive(True)
        btnCreatePlaylist.clicked.connect(self.createPlaylistAction)
        toolBar.addWidget(btnCreatePlaylist)

        # button for delete playlist
        btnDeletePlaylist = QToolButton(self)
        btnDeletePlaylist.setText('Delete Playlist')
        #btnDeletePlaylist.move(620, 30)
        btnDeletePlaylist.setAutoExclusive(True)
        btnDeletePlaylist.clicked.connect(self.deletePlaylistAction)
        toolBar.addWidget(btnDeletePlaylist)

        #button to play music
        btnPlay = QPushButton(self)
        btnPlay.setIcon(QIcon(QPixmap("icons/iconPlay.svg")))
        btnPlay.move(20, 30)
        #btnPlay.setIconSize(QSize(20,20))
        btnPlay.resize(30,30)
        btnPlay.clicked.connect(self.play)

        #button to pause music
        btnPause = QPushButton(self)
        btnPause.setIcon(QIcon(QPixmap("icons/iconPause.svg")))
        btnPause.move(60, 30)
        btnPause.clicked.connect(self.pause)
        btnPause.resize(30,30)

        #button to stop music
        btnStop = QPushButton(self)
        btnStop.setIcon(QIcon(QPixmap("icons/iconStop.svg")))
        btnStop.move(100, 30)
        btnStop.clicked.connect(self.stop)
        btnStop.resize(30,30)

        #button for previous song
        btnPrev = QPushButton(self)
        btnPrev.setIcon(QIcon(QPixmap("icons/iconPrev.svg")))
        btnPrev.move(140, 30)
        btnPrev.clicked.connect(self.previous)
        btnPrev.resize(30,30)

        #button for next Song
        btnNext = QPushButton(self)
        btnNext.setIcon(QIcon(QPixmap("icons/iconNext.svg")))
        btnNext.move(180, 30)
        btnNext.clicked.connect(self.next)
        btnNext.resize(30,30)

        btnFolder = QPushButton(self)
        btnFolder.setIcon(QIcon(QPixmap("icons/iconFolder.png")))
        btnFolder.move(220, 30)
        btnFolder.clicked.connect(self.initSongList)
        btnFolder.resize(30,30)

        # button for Select playlist to show in playlist box
        btnSelectPlaylist = QPushButton('Select Playlist',self)
        btnSelectPlaylist.move(280, 30)
        btnSelectPlaylist.clicked.connect(self.selectPlaylistAction)

        # button for Adding song to playlist
        btnToPlaylist = QPushButton('Add to Playlist',self)
        btnToPlaylist.move(390, 30)
        btnToPlaylist.clicked.connect(self.addSongToPlaylistAction)

        # button for erase song from playlist
        btnEraseFromPlaylist = QPushButton('Erase from Playlist',self)
        btnEraseFromPlaylist.move(505, 30)
        btnEraseFromPlaylist.clicked.connect(self.eraseSongFromPlaylistAction)


        # button for merge playlist together
        btnMergePlaylist = QPushButton('Merge playlists',self)
        btnMergePlaylist.move(620, 80)
        btnMergePlaylist.clicked.connect(self.mergePlaylistsAction)

        # button for intersection for playlist
        btnInterPlaylist = QPushButton('Inter playlists',self)
        btnInterPlaylist.move(620, 110)
        btnInterPlaylist.clicked.connect(self.interPlaylistsAction)

        # button for  differece of two playlists
        btnDiffPlaylist = QPushButton('Diff playlists',self)
        btnDiffPlaylist.move(620,140)
        btnDiffPlaylist.clicked.connect(self.diffPlaylistsAction)

        # button for export playlist
        btnExportPlaylist = QPushButton('Export PL->ALBUM',self)
        btnExportPlaylist.move(620,170)
        btnExportPlaylist.clicked.connect(self.exportPlaylistAction)

        # button for BPM function
        btnBPM = QPushButton('Get BPM',self)
        btnBPM.move(620,210)
        btnBPM.clicked.connect(self.getBpmOfSong)



        #label to show bpm next to bpm button
        self.labelBPM = QLabel(self)
        self.labelBPM.move(620,240)
        self.labelBPM.resize(100,20)
        self.labelBPM.setStyleSheet("background-color: yellow; border: 1px inset grey;")
        self.labelBPM.setText("BPM: ")

        #show playlist name
        self.labelPlaylist = QLabel(self)
        self.labelPlaylist.move(300, 230)
        self.labelPlaylist.resize(200,20)
        self.labelPlaylist.setStyleSheet("background-color: white; border: 1px inset grey;")
        self.labelPlaylist.setText("")

        # call initialization at start of media player to init directory and playlists

        layout = QGridLayout()
        self.mainPLstatus = 1
        self.sidePLstatus = 0
        self.listWidget = QListWidget(self)
        self.listWidget.setStyleSheet("QListWidget" ## default style
                                     "{"
                                     "border : 3px solid grey;"
                                     "}")
        self.initSongList()

        #Resize width and height
        self.listWidget.resize(240,370)
        self.listWidget.move(20, 250)
        # main playlist
        self.listWidget.setWindowTitle('PyQT QListwidget Demo')
        self.listWidget.clicked.connect(self.listview_clicked)


        #playlist for operations
        self.playlistWidget = QListWidget(self)
        self.playlistWidget.resize(240,370)
        self.playlistWidget.move(300, 250)
        self.playlistWidget.clicked.connect(self.playlistview_clicked)
        #self.playlistWidget

        #Song Info Box
        self.groupbox = QGroupBox("Song Info",self)#QGroupBox("Song Info",self)
        self.groupbox.move(50, 60)
        self.groupbox.resize(500, 170)
        self.hbox = QHBoxLayout()
        self.v2box = QVBoxLayout()
        self.vbox = QVBoxLayout()
        self.infoLabels = []
        # labels in box of song for metadata
        for i in range(0,5):
            self.infoLabels.append(QLabel(""))
            self.vbox.addWidget(self.infoLabels[i])

        #self.groupbox.setLayout(vbox)
        #groupbox.setFont(QtGui.QFont("Sanserif", 15))
        self.imageAlbumLabel = QLabel(self)
        self.v2box.addWidget(self.imageAlbumLabel)
        self.v2box.setAlignment(Qt.AlignTop)

        # set box to 2 vertical boxes
        self.hbox.addLayout(self.v2box)
        self.hbox.addLayout(self.vbox)
        self.groupbox.setLayout(self.hbox)

        #vbox.addWidget(label)

        #init metadata databse table
        self.tableWidgetMeta = QTableWidget(self)
        self.tableWidgetMeta.move(550,270)
        self.tableWidgetMeta.resize(240,350)


        #self.setGeometry(100, 100, 750, 400)
        self.setFixedSize(800, 660)
        self.setWindowTitle('Gnome Music Player Clone')

        self.show()


    def getBpmOfSong(self):
        """ Calls bpm of WAV file from module beatalg
            sets value in label in red
        """
        name = self.pickedSongObject.getName()
        if(name.lower().endswith(".wav")):
            #song = self.filesList + "/" + self.pickedSong
            song = self.pickedSongObject.getPath()
            bpm = beatalg.getBPM(song)


            self.labelBPM.setText("BPM: " + str(bpm))

    def showdialog(self):

        self.dialog = QDialog()
        form = QFormLayout(self.dialog)
        song = self.pickedSongObject.getPath()
        try:
            #tags =  EasyID3(self.filesList + "/" + self.pickedSong)
            tags = EasyID3(song)
        except Exception:
            return #no id3format
        print(tags.pprint())
        #add album
        try:
            titleE = tags['title'][0]
        except:
            titleE = ""
        self.e1 = QLineEdit()
        self.e1.setText(titleE)
        form.addRow("Title", self.e1)

        try:
            artistE = tags['artist'][0]
        except:
            artistE = ""
        self.e2 = QLineEdit()
        self.e2.setText(artistE)
        form.addRow("Artist", self.e2)

        try:
            albumE = tags['album'][0]
        except:
            albumE = ""
        self.e3 = QLineEdit()
        self.e3.setText(albumE)
        form.addRow("Album", self.e3)

        try:
            genreE = tags['genre'][0]
        except:
            genreE = ""
        self.e4 = QLineEdit()
        self.e4.setText(genreE)
        form.addRow("Genre", self.e4)

        try:
            trackNumberE = tags['tracknumber'][0]
        except:
            trackNumberE = ""
        self.e5 = QLineEdit()
        self.e5.setText(trackNumberE)
        form.addRow("Tracknumber", self.e5)

        try:
            dateE = tags['date'][0]
        except:
            dateE = ""
        self.e6 = QLineEdit()
        self.e6.setText(dateE)
        form.addRow("Date", self.e6)

        try:
            moodE = tags['mood'][0]
        except:
            moodE = ""
        self.e7 = QLineEdit()
        self.e7.setText(moodE)
        form.addRow("Mood", self.e7)


        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, self)
        form.addRow(self.buttons)
        self.buttons.accepted.connect(self.saveButton)
        self.dialog.setWindowTitle("Dialog")
        self.dialog.setWindowModality(Qt.ApplicationModal)
        self.dialog.exec_()

    def saveButton(self):
        print("saving metadata")
        song = self.pickedSongObject.getPath()
        try:
            #tags =  EasyID3(self.filesList + "/" + self.pickedSong)
            tags = EasyID3(song)
        except Exception:
            return #no id3format

        if(self.e1.text()):#title
            tags['title'] = self.e1.text()
        if(self.e2.text()):#title
            tags['artist'] = self.e2.text()
        if(self.e3.text()):#title
            tags['album'] = self.e3.text()
        if(self.e4.text()):#title
            tags['genre'] = self.e4.text()
        if(self.e5.text()):#title
            tags['tracknumber'] = self.e5.text()
        if(self.e6.text()):#title
            tags['date'] = self.e6.text()
        if(self.e7.text()):#title
            tags['mood'] = self.e7.text()


        tags.save()
        self.dialog.close()
        return

    def addSongToPlaylistAction(self):
        """ Add picked song to playlist

        """
        if(self.mainPLstatus == 0):
            QMessageBox.about(self, "Warning", "Cannot add to side playlist from main")
            return

        if(self.pickedSongObject.getName()):
            for x in range(len(self.allPlaylists)):
                if(self.allPlaylists[x].getNameOfPlaylist() == self.currentPlaylist.getNameOfPlaylist()):#current playlist
                    self.allPlaylists[x].addSongToPlaylist(self.pickedSongObject)
                    self.refreshPlaylistWidget()
        '''
        if(self.pickedSong):
            for x in range(len(self.allPlaylists)):
                if(self.allPlaylists[x].getNameOfPlaylist() == self.currentPlaylist.getNameOfPlaylist()):#current playlist
                    self.allPlaylists[x].addSongToPlaylist(self.pickedSongObject)
                    self.refreshPlaylistWidget()
        '''

    def eraseSongFromPlaylistAction(self):
        """ Erase Picked song from playlist

        """
        if(self.playlist2CurrentSong):
            #print(self.playlist2CurrentSong)
            for x in range(len(self.allPlaylists)):
                if(self.allPlaylists[x].getNameOfPlaylist() == self.currentPlaylist.getNameOfPlaylist()):#current playlist
                    self.allPlaylists[x].removeSongFromPlaylist(self.playlist2CurrentSong)
                    self.refreshPlaylistWidget()

    def addToPlaylists(self, playlist):
        self.allPlaylists.append(playlist)

    def initDatabaseTable(self, nameArtist, nameSong):
        """ Automatic download of metadata from web database
            data shows in table panel in right side

            Parameters
            ----------
            nameArtist - str
                Artist to find in database
            nameSong - str
                Song from artist to search

        """
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
        """
            Permanent objects
        """
        try:
            pickle.dump(self.allPlaylists, self.f)
            self.f.close()
        except:
            pass
        #print("Saving data")


    def mergePlaylistsAction(self):
        """
            Gets all songs to one new playlist
            with new name, user as to set
        """
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
        """ Picks common songs from two playlists
            to new one
        """
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

        secondPlaylist, ok = QInputDialog.getItem(self, "Second Playlist", "Select second playlist to merge",tempArray2 , 0, False)
        if not ok:
            return

        playlist1 = Playlist()
        playlist1 = self.playlistFromName(firstPlaylist)
        playlist2 = Playlist()
        playlist2 = self.playlistFromName(secondPlaylist)

        intersected = Playlist()
        intersected.setNameToPlaylist(newName)
        intersected.setIntersectedList(playlist1.getAllSongs(), playlist2.getAllSongs())
        self.allPlaylists.append(intersected)

        self.refreshPlaylistWidget() #refresh values

    def diffPlaylistsAction(self):
        """
            Difference of playlists
        """
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

        diff = Playlist()
        diff.setNameToPlaylist(newName)
        dDiff.setdiffList(playlist1.getAllSongs(), playlist2.getAllSongs())
        self.allPlaylists.append(diff)

        self.refreshPlaylistWidget() #refresh values


    def playlistFromName(self, name):
        """ Search in list of playlists

            Parameters
            ----------
            name : str
                Name of searched playlist
            Returns
            -------
            list : copy of found playlist, to new instance in callable
        """
        for x in range(len(self.allPlaylists)):
            if(self.allPlaylists[x].getNameOfPlaylist() == name):
                tempPlaylist = Playlist()
                tempPlaylist = copy.copy(self.allPlaylists[x])

        return tempPlaylist

    def createPlaylistAction(self):
        """
            Creates new playlist, from input dialog
            make new instance of playlist
        """
        text, ok = QInputDialog.getText(self, 'Playlist Creator', 'Enter playlist name:')
        if not ok:
            return
        tempPlay = Playlist()
        tempPlay.setNameToPlaylist(str(text))
        #tempPlay.addSongToPlaylist("zzzz")

        self.allPlaylists.append(tempPlay)

        self.refreshPlaylistWidget() #refresh values

        #if ok:
         #print(str(text))

    def deletePlaylistAction(self):
        """
            Deletes playlist that user sets in input dialog
        """
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

    def exportPlaylistAction(self):
        if(not self.currentPlaylist):
            print("not selected playlist")
            return

        #setAlbum name for zip
        albumName = self.currentPlaylist.getNameOfPlaylist()
        zipName = (albumName + ".zip")
        myzip = zipfile.ZipFile(zipName, 'w', zipfile.ZIP_DEFLATED)

        # for every song add album metadata and do zipping
        for name in (self.currentPlaylist.getAllSongs()):#iterate songs in playlist
            if (name.lower().endswith(".mp3")):
                try:
                    tags =  EasyID3(self.filesList + "/" + name)
                except Exception:
                    tags =  EasyID3()

                # add album info
                originalAlbum = tags['album']
                tags['album'] = albumName
                tags.save()
                #zip to file
                myzip.write(name)
                #get original album back
                tags['album'] = originalAlbum
                tags.save()

            if (name.lower().endswith(".wav")):
                myzip.write(name)
        mess = ("Playlist exported to directory:\n\t" + self.filesList)
        QMessageBox.about(self, "Export PL", mess)
        return

    def fillBoxSongPic(self):
        """
            Creates pixmap in song box info
            image gets from metadata of song
        """
        name = self.pickedSongObject.getName()
        pixmap = QPixmap()
        song = self.pickedSongObject.getPath()
        if (name.lower().endswith(".mp3")):
            try:
                audioMeta =  mutagen.File(song)
            except Exception:
                return 0

            isPic = False
            for tag in audioMeta.tags.values():
                if tag.FrameID == 'APIC':
                    pixmap.loadFromData(tag.data)
                    pixmap = pixmap.scaled(125, 125, Qt.KeepAspectRatio)
                    isPic = True
                    break
            if(isPic):
                try:
                    self.imageAlbumLabel.setPixmap(pixmap)
                except:

                    pass#TODO: empty image
            else:
                self.noImage = self.noImage.scaled(125, 125, Qt.KeepAspectRatio)
                self.imageAlbumLabel.setPixmap(self.noImage)



    def fillBoxSongInfo(self):
        """
            Parsing metadat from local music files
            Two formats Wav and MP3

        """
        name = self.pickedSongObject.getName()
        #add path
        #song = ("/home/jakub/Music/The Cure - 1979 Boys Don't Cry/"+self.pickedSong)
        song = self.pickedSongObject.getPath()

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
                self.infoLabels[1].setText("Artist: ")
            try:
                self.infoLabels[2].setText("Length: " + self.secondsLength(mp3s.info.length))
            except:
                self.infoLabels[2].setText("Length: ")
            try:
                self.infoLabels[3].setText("Format: " + str(mp3s.info.channels) + " channels, " + str(mp3s.info.sample_rate/1000) + "KHz, " + str(int(mp3s.info.bitrate/1000)) + "kbps")
            except:
                self.infoLabels[3].setText("Format: ")

            #print(audio.pprint())
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

            #print(metadata)

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
                self.infoLabels[3].setText("Format: " + str(metadata.streaminfo['channels']) + " channels, " + str(metadata.streaminfo['sample_rate']/1000) + "KHz, " + str(int(metadata.streaminfo['bitrate']/1000)) + "kbps")
            except:
                self.infoLabels[3].setText("Format: ")

            #todo: everything to block try except
            self.initDatabaseTable(metadata.tags['artist'][0], metadata.tags['artist'][0],)

        return

    def refreshPlaylistWidget(self):
        """
            Get current playlist to show in list widget
        """
        #make label
        self.labelPlaylist.setText(self.currentPlaylist.getNameOfPlaylist())
        # update songs in list widget
        self.playlistWidget.clear()
        for song in self.currentPlaylist.getAllSongs():#fill list with songs
            self.playlistWidget.addItem(song.getName())


    def selectPlaylistAction(self):
        '''
            Select playlist from dialog
        '''
        tempArray1 = []#names of playlist to qdialog
        for x in range(len(self.allPlaylists)):
            tempArray1.append(self.allPlaylists[x].getNameOfPlaylist())

        if(len(self.allPlaylists) == 0):
            QMessageBox.about(self, "Nothing found", "No playlists available")
            return
        nameOfPickedPlaylist, ok = QInputDialog.getItem(self, "Second Playlist", "Select second playlist to merge",tempArray1 , 0, False)
        if not ok:
            return

        for idx in range(len(self.allPlaylists)):
            if self.allPlaylists[idx].getNameOfPlaylist() == nameOfPickedPlaylist:
                #print(self.allPlaylists[idx].getNameOfPlaylist())
                self.currentPlaylist = copy.copy(self.allPlaylists[idx])
                #self.currentPlaylist.printAllsongs()

                self.refreshPlaylistWidget()


    def play(self):
        """
            Play song, two parts for mixer modul,
            from status paused to unpause and status stopped to play
        """
        if self.status == "Paused": #continues playing
            self.status = "Played"
            mixer.music.unpause()
            return
        else: # play song from beginning
            self.status = "Played"
            #mixer.music.load(self.filesList + "/" + self.pickedSong)
            mixer.music.load(self.pickedSongObject.getPath())
            mixer.music.play()
            return

    def pause(self):
        """
            Pause Song
        """
        if self.status == "Played":
            self.status = "Paused"
            mixer.music.pause()
            return
        if self.status == "Stopped":
            mixer.music.pause()
            return

    def stop(self):
        """
            Just Stop playing song
        """
        mixer.music.stop()
        self.status = "Stopped"; #TODO: make enum for this
        return

    def next(self):
        """
            Play next song, with rotation of list
        """


        if(self.mainPLstatus == 1):
            arraySongs = self.mainPlaylist.getAllSongs()
        if(self.sidePLstatus == 1):
            arraySongs = self.playlist2CurrentSong.getAllSongs()
        a = []
        for x in arraySongs:
            a.append(x.getName())

        print(*a, sep = "\n")
        try:
            index = a.index(self.pickedSongObject.getName())#index of actual song
        except:
            return


        mixer.music.stop()
        deq = deque(a)
        deq.rotate(-1)#shift to left
        name = deq[index]
        print(name)
        self.pickedSongObject = self.mainPlaylist.getSongObjectT(name)
        self.fillBoxSongInfo()
        self.fillBoxSongPic()
        self.status = "Played"
        self.play()
        return

    def previous(self):
        """
            Play rpevious song, with rotation of list
        """
        mixer.music.stop()
        try:
            index = self.songsList.index(self.pickedSong)#index of actual song
        except Exception:
            print("Not in list")
            return
        deq = deque(self.songsList)
        deq.rotate(1)#shift to left
        self.pickedSong = deq[index]
        self.status = "Played"
        self.play()
        return

    def secondsLength(self, insec):
        """ Get format of time in song to show

            Parameters
            ----------
            insec : int
                number of seconds from metadata of file

            Returns
            -------
            str : String format to show in label
        """
        if insec == 0:
            return "X"
        min = int(insec / 60)
        sec = int(insec % 60)
        word = str(min) + "min:" + str(sec) + "sec"
        return word

    def loadPermanentData(self): # opens file in main Init beacuse atexit part cant write to file
        pickle.dump(self.allPlaylists, self.file, pickle.HIGHEST_PROTOCOL)
        self.file.close()


if __name__ == '__main__':
    musicbrainzngs.set_useragent(
    "python-musicbrainzngs-example",
    "0.1",
    "https://github.com/alastair/python-musicbrainzngs/",
)



    app = QApplication(sys.argv)
    ex = MusicPlayer()
    sys.exit(app.exec_())
