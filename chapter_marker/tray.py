#!/usr/bin/env nix-shell
#!nix-shell -p python3Packages.docopt python3Packages.pyqt5 python3Packages.notify2 python3Packages.requests qt5.qtbase -i python3
""" usage: chapter-marker [options] TITLEFILE [SHOW]

options:
    --settings-dir=DIR       The base directory of the chapter-marker [Default: ~/.local/share/chapter-marker]

starts chapter-marker with the given TITLE and starts with the top entry of TITLEFILE
if the chapter marker file for this SHOW already exists it will be backed up.
"""
import sys, re
from docopt import docopt
from datetime import datetime
import notify2
import requests
from os.path import exists, join, expanduser
import pickle
from PyQt5.Qt import QApplication, QClipboard
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QPlainTextEdit,
    QPushButton,
    QSystemTrayIcon,
    QMenu,
    QDialog,
    QShortcut,
)
from PyQt5.QtCore import QSize, pyqtSlot, Qt, QObject, pyqtSignal

from pynput import keyboard

now = datetime.now


def current_show():
    import urllib.request

    url = "https://pad.binaergewitter.de/"
    ret = urllib.request.urlopen(url)
    return ret.geturl().split("/")[-1]


class KeyBoardManager(QObject):
    jSignal = pyqtSignal()
    uSignal = pyqtSignal()

    def start(self):
        self.hotkeys = keyboard.GlobalHotKeys(
            {"<ctrl>+j": self.jSignal.emit, "<ctrl>+u": self.uSignal.emit}
        )
        self.hotkeys.start()


class LeftClickMenu(QtWidgets.QMenu):
    def __init__(self, parent=None):
        QtWidgets.QMenu.__init__(self, "File", parent)

        icon = QIcon("res/")

        self.dateAction = self.addAction(QtWidgets.QAction(icon, "Start Date", self))
        self.currentChapterAction = self.addAction(
            QtWidgets.QAction(icon, "Current Chapter", self)
        )
        self.nextChapterAction = self.addAction(
            QtWidgets.QAction(icon, "Current Chapter", self)
        )
        # newAction.triggered.connect(sys.exit)


class ChapterEntry:
    def __init__(self, title, is_comment=False, begin=None):
        self.title = title
        self.is_comment = is_comment
        self.begin = begin  # at which second the chapter begins

    def __str__(self):

        if self.is_comment:
            return "# " + self.title
        elif self.begin is None:
            return f"not-started  {self.title}"
        else:
            m, s = divmod(self.begin or 0, 60)
            h, m = divmod(m, 60)
            return f"{h:02}:{m:02}:{s:02}.000 {self.title}"

    def toSimpleElement(self):
        raise NotImplemented("sorry")


states = ["preshow", "show", "postshow"]


class ChapterMarkFile:
    active_chapter = 0

    def __init__(self, show: str, titles: list, location: str):
        self.show = show
        self.location = location
        # if location is empty:
        self.initialize_chapters(titles)
        self.state = "preshow"  #
        self.timers = {}  # timer for preshow, show und postshow

    def set_state(self, state):
        self.state = state
        self.timers[state] = now()

    def initialize_chapters(self, titles):
        self.storage = [ChapterEntry(title) for title in titles]
        self.active_chapter = 0
        self.add_comment(f"Preshow für '{self.show}' gestartet um '{now()}'")

    def add_comment(self, text):
        self.storage.insert(self.active_chapter, ChapterEntry(text, is_comment=True))
        self.active_chapter += 1

    def begin(self):
        # initialize the time tracker
        self.started = True
        self.start_date = now()
        self.add_comment(f"Preshow ende um {self.start_date}")
        self.storage.insert(
            self.active_chapter,
            ChapterEntry("Hallihallo und Herzlich Willkommen", begin=0),
        )
        self.set_state("show")

    def end(self, delta):
        self.active_chapter += 1
        self.add_comment(f"Postshow beginnt um '{now()}")
        self.set_state("postshow")

    def get_current(self):
        return self.storage[self.active_chapter]

    def get_next(self):
        return self.storage[self.active_chapter + 1]

    def begin_next(self, delta: int):
        self.active_chapter += 1
        active = self.storage[self.active_chapter]
        active.delta = delta

    def persist(self):
        with open(join(self.location, self.show + ".db"), "w+") as f:
            pickle.dump(self, f)

    def load(self, path=None):
        # Load existing chapter-files
        if not path:
            path = join(self.location, self.show + ".db")
        with open(path) as f:
            return pickle.load(f)

    def __str__(self):
        return "\n".join([str(s) for s in self.storage])


class SystemTrayIcon(QSystemTrayIcon):
    def __init__(self, parent, show, titles, settingsdir):
        QSystemTrayIcon.__init__(self, QIcon("res/book-clock.png"), parent)
        self.left_menu = LeftClickMenu()
        self.markers = ChapterMarkFile(show, titles, settingsdir)

        # left click
        self.activated.connect(self.left_click)

        # Right Click
        menu = QMenu(parent=None)
        self.setContextMenu(menu)
        settingAction = menu.addAction(QIcon("res/book-clock.png"), "settings")
        settingAction.triggered.connect(self.right_click)

        settingAction = menu.addAction("clear")
        settingAction.triggered.connect(self.clear)

        settingAction = menu.addAction("exit")
        settingAction.triggered.connect(sys.exit)

        manager = KeyBoardManager(self)
        manager.uSignal.connect(self.start_chaptermarks)
        manager.jSignal.connect(self.write_current_chapter)
        manager.start()

        # clipboard handling
        # QApplication.clipboard().dataChanged.connect(self.clipboardChanged)

        # shortcuts

    def refresh_menu(self):
        self.left_menu.dateAction.setText(
            f"{self.markers.state} since {self.markers.states[self.marker.state]}"
        )
        self.left_menu.currentChapterAction.setText(
            f"Current: {self.markers.get_current()}"
        )
        self.left_menu.nextChapterAction.setText(f"Next: {self.markers.get_next()}")

    def start_chaptermarks(self):
        print("start chaptermarks")
        notify2.Notification("Start Chaptermarks").show()
        self.markers.begin()
        print(self.markers)

    def write_current_chapter(self):
        print("write current chaptermark")

    def left_click(self, value):
        if value == self.Trigger:  # left click!
            self.left_menu.exec_(QtGui.QCursor.pos())

    def right_click(self):
        print("settings")

    def clear(self):
        print("cleared")
        self.urls = set()

    # Get the system clipboard contents
    def clipboardChanged(self):
        text = QApplication.clipboard().text()
        if type(text) != str:
            return
        print(text)


def main():
    notify2.init("chapter-marker")
    args = docopt(__doc__)
    settingsdir = expanduser(args["--settings-dir"])

    if not args["SHOW"]:
        show = current_show()

    titles = [l.strip() for l in open(args["TITLEFILE"]).readlines()]

    app = QtWidgets.QApplication([])  # can also take sys.argv
    tray = SystemTrayIcon(app, show, titles, settingsdir)
    tray.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
