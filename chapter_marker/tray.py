#!/usr/bin/env nix-shell
#!nix-shell -p python3Packages.docopt python3Packages.pyqt5 python3Packages.notify2 python3Packages.requests qt5.qtbase -i python3 # noqa
""" usage: chapter-marker [options] TITLEFILE [SHOW]

options:
    --settings-dir=DIR       The base directory of the chapter-marker [Default: ~/.local/share/chapter-marker]
    --disable-notification   If set notify2 is disables which can help with dbus issues

starts chapter-marker with the given TITLE and starts with the top entry of TITLEFILE
if the chapter marker file for this SHOW already exists it will be backed up.
"""
import logging
import pickle
import sys
from datetime import datetime, timedelta
from os.path import expanduser, join

from docopt import docopt
from pynput import keyboard
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMenu, QSystemTrayIcon

from . import resources  # noqa F401

try:
    import notify2
except ImportError:
    import fakenotify2 as notify2


now = datetime.now

log = logging.getLogger("chapter-tray")
logging.basicConfig(level=logging.INFO)


def current_show():
    import urllib.request

    url = "https://pad.binaergewitter.de/"
    ret = urllib.request.urlopen(url)
    return ret.geturl().split("/")[-1]


class KeyBoardManager(QObject):
    j_signal = pyqtSignal()
    u_signal = pyqtSignal()

    def start(self):
        self.hotkeys = keyboard.GlobalHotKeys({"<ctrl>+j": self.j_signal.emit, "<ctrl>+u": self.u_signal.emit})
        self.hotkeys.start()


class LeftClickMenu(QtWidgets.QMenu):
    def __init__(self, parent=None):
        QtWidgets.QMenu.__init__(self, "File", parent)

        self.dateAction = QtWidgets.QAction(QIcon(":/icons/start-date.png"), "Start Date", self)
        self.addAction(self.dateAction)
        self.currentChapterAction = QtWidgets.QAction(QIcon(":/icons/current-chapter.png"), "Current Chapter", self)
        self.addAction(self.currentChapterAction)
        self.nextChapterAction = QtWidgets.QAction(QIcon(":/icons/next-chapter.png"), "Next Chapter", self)
        self.addAction(self.nextChapterAction)


class ChapterEntry:
    def __init__(self, title, is_comment=False, delta=None):
        self.title = title
        self.is_comment = is_comment
        self.delta = delta  # timedelta

    def __str__(self):

        if self.is_comment:
            return "# " + self.title
        elif self.delta is None:
            return f"not-started  {self.title}"
        else:
            m, s = divmod(self.delta.seconds, 60)
            h, m = divmod(m, 60)
            millis = round(self.delta.microseconds / 1000)
            return f"{h:02}:{m:02}:{s:02}.{millis:03} {self.title}"

    def to_simple_element(self):
        raise NotImplementedError("sorry")


states = ["preshow", "show", "postshow"]


class ChapterMarkFile:
    active_chapter = 0

    def __init__(self, show: str, titles: list, location: str):
        log.info(f"Initialize ChapterMarkFile for show {show} at {location}")
        self.initial_titles = titles.copy()
        self.show = show
        self.location = location
        # if location is empty:
        self.state = "preshow"  #
        self.timers = {}  # timer for preshow, show und postshow
        self.initialize_chapters(titles)

    def reset(self):
        """clean up everything and start a new show"""
        self.active_chapter = 0
        self.__init__(self.show, self.initial_titles, self.location)

    def set_state(self, state):
        self.state = state
        self.timers[state] = now()

    def initialize_chapters(self, titles):
        # put "hallihallo" at the top
        titles.insert(0, "Hallihallo und Herzlich Willkommen")
        self.storage = [ChapterEntry(title) for title in titles]
        self.active_chapter = 0
        self.add_comment(f"Preshow für '{self.show}' gestartet um {now().replace(microsecond=0)}")
        self.set_state("preshow")

    def add_comment(self, text, before=True):
        loc = self.active_chapter if before else self.active_chapter + 1
        log.info(f"Comment {'before' if before else 'after'}: {text}")
        notify2.Notification(text).show()
        self.storage.insert(loc, ChapterEntry(text, is_comment=True))
        self.active_chapter += 1

    def begin(self):
        # initialize the time tracker
        self.started = True
        self.start_date = now()
        self.set_state("show")

        duration = self.timers["show"] - self.timers["preshow"]
        m, s = divmod(duration.seconds, 60)
        h, m = divmod(m, 60)
        self.add_comment(f"Preshow ende um {self.start_date.replace(microsecond=0) } ({h:02}:{m:02}:{s:02} Vorgeplänkel)")
        self.get_current().delta = timedelta(seconds=0)

    def end(self):
        log.info(f"Start Postshow at {now()}")
        self.set_state("postshow")

        duration = self.timers["postshow"] - self.timers["show"]
        m, s = divmod(duration.seconds, 60)
        h, m = divmod(m, 60)
        self.add_comment(f"Postshow beginnt um {now()} ({h:02}:{m:02}:{s:02} Show)", before=False)
        log.debug(self)

    def get_current(self):
        return self.storage[self.active_chapter]

    def get_next(self):
        return self.storage[self.active_chapter + 1]

    def last_chapter(self):
        return self.active_chapter == len(self.storage) - 1

    def begin_next(self) -> bool:
        """moves to the next chapter, returns false if this was not possible, else true"""
        if self.last_chapter():
            log.info("cannot go beyond last chapter")
            return False
        elif self.state != "show":
            log.info("Show has not started yet, start show first!")
            return False

        self.active_chapter += 1
        log.debug(f"Current Chapter: {self.active_chapter}, Total Chapters: {len(self.storage)}")
        active = self.get_current()
        active.delta = now() - self.timers["show"]

        if self.last_chapter():
            log.info("at last chapter")
            self.end()
        # print(self)
        return True

    def persist(self):
        dbpath = join(self.location, self.show + ".db")
        with open(dbpath, "wb+") as f:
            log.info(f"writing chaptermark state to {dbpath}")
            pickle.dump(self, f)
        chapterpath = join(self.location, self.show + "_chapters.txt")

        with open(chapterpath, "w+") as f:
            log.info(f"writing real chaptermarks to {chapterpath}")
            f.write(str(self))

        log.info("Also writing the last state to stdout:")
        print(self)

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
        QSystemTrayIcon.__init__(self, QIcon(":/icons/main.png"), parent)
        self.left_menu = LeftClickMenu()
        self.markers = ChapterMarkFile(show, titles, settingsdir)
        log.debug(self.markers)
        # left click
        self.activated.connect(self.left_click)

        # Right Click
        menu = QMenu(parent=None)
        self.setContextMenu(menu)

        setting_action = menu.addAction(QIcon(":/icons/save.png"), "save")
        setting_action.triggered.connect(self.save)

        setting_action = menu.addAction("---")

        setting_action = menu.addAction(QIcon(":/icons/main.png"), "Reset and Restart")
        setting_action.triggered.connect(self.reset)

        setting_action = menu.addAction(QIcon(":/icons/exit.png"), "exit")
        setting_action.triggered.connect(self.exit)

        manager = KeyBoardManager(self)
        manager.j_signal.connect(self.next_chapter)
        manager.start()

    def exit(self):
        log.info("Persisting Chaptermarks")
        self.markers.persist()
        sys.exit()

    def refresh_menu(self):
        self.left_menu.dateAction.setText(f"{self.markers.state} since {self.markers.timers[self.markers.state].replace(microsecond=0)}")
        self.left_menu.currentChapterAction.setText(f"Current: {self.markers.get_current()}")
        try:
            self.left_menu.nextChapterAction.setText(f"Next: {self.markers.get_next().title}")
        except:  # noqa E722
            self.left_menu.nextChapterAction.setText("No next Chapter")

    def next_chapter(self):
        log.info("Markers Status:")
        log.info(self.markers)
        if self.markers.state == "preshow":
            self.markers.begin()
            text = f"start show {self.markers.show} with follwing chapter marks planned:\n{self.markers}"
            notify2.Notification(text).show()
            log.info(text)
        elif self.markers.begin_next():
            notify2.Notification(f"Next Chapter: {self.markers.get_current().title}").show()
            log.info(f"next chapter {self.markers.get_current().title}")
        else:
            log.info("Cannot move to next chapter")
            notify2.Notification("Cannot move to next Chapter").show()

    def left_click(self, value):
        self.refresh_menu()
        if value == self.Trigger:  # left click!
            self.left_menu.exec_(QtGui.QCursor.pos())

    def reset(self):
        log.warn("performing complete rewind of chaptermarks")
        self.markers.persist()
        self.markers.reset()

    def save(self):
        self.markers.persist()


def main():
    args = docopt(__doc__)
    settingsdir = expanduser(args["--settings-dir"])
    disable_notifications = args["--disable-notification"]
    if not disable_notifications:
        notify2.init("chapter-marker")
    else:

        class FakeNotify2:
            def Notification(self, text):  # noqa N802
                return self

            def show(self):
                pass

        notify2.Notification = FakeNotify2().Notification

    show = args["SHOW"]
    if not show:
        show = current_show()

    titles = [line.strip() for line in open(args["TITLEFILE"]).readlines()]

    app = QtWidgets.QApplication([])  # can also take sys.argv
    tray = SystemTrayIcon(app, show, titles, settingsdir)
    tray.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
