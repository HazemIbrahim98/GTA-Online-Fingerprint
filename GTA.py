import io
import sys
from threading import Timer

import cv2
import numpy as np

import pyHook

import pyautogui

import pythoncom
import requests

from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QApplication


########################################################################################################################
# GUI boxes that display over the game

class boxWindow(QMainWindow):
    def __init__(self, x, y):
        QMainWindow.__init__(self)
        self.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.X11BypassWindowManagerHint
        )
        self.setGeometry(x + 60, y + 60, 50, 50)


app = QApplication(sys.argv)

windows = [None] * 4

for i in range(4):
    windows[i] = boxWindow(0, 0)


def clearWindows():
    for i in range(4):
        windows[i].close()


########################################################################################################################
# Loading images needed for the program

def loadImage(url, Finger):
    response = requests.get(url)
    image = np.asarray(bytearray(response.content), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_GRAYSCALE)

    if Finger:
        image = cv2.resize(image,(320, 550))
    else:
        image = cv2.resize(image,(127,127))

    return image

class Finerprint:
    def __init__(self):
        self.fingerImg = []
        self.fingerSol = [None] * 4


fingerprints = [None] * 4


def initFingerprints():
    # Initialize the four fingerprints
    for i in range(4):
        fingerprints[i] = Finerprint()
        fingerprints[i].fingersol = []

    for i in range(4):
        print(f"Loading F{i}")
        fingerprints[i].fingerImg = loadImage(f"https://raw.githubusercontent.com/HazemMohamed98/GTA-Online-Fingerprint/Images/F{i + 1}.jpg", True)
        for j in range(4):
            print(f"Loading F{i}S{j}")
            fingerprints[i].fingerSol[j] = loadImage(f"https://raw.githubusercontent.com/HazemMohamed98/GTA-Online-Fingerprint/Images/F{i + 1}S{j + 1}.jpg", False)

########################################################################################################################
# The core

def takeScreenshot():
    screenshot = cv2.resize(cv2.cvtColor(np.array(pyautogui.screenshot()), cv2.COLOR_BGR2GRAY), (1920, 1080))
    FPtoSolve = screenshot[150:680, 980:1300]
    return FPtoSolve, screenshot


def solveScreenshot(FPtoSolve, screenshot, fingerprints):
    bestMatch = [None] * 4

    for i in range(4):
        surf = cv2.xfeatures2d.SURF_create()
        kp1, des1 = surf.detectAndCompute(FPtoSolve, None)
        kp2, des2 = surf.detectAndCompute(fingerprints[i].fingerImg, None)

        bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=True)
        matches = bf.match(des1, des2)
        matches = sorted(matches, key=lambda x: x.distance)

        bestMatch[i] = len(matches)

    if max(bestMatch) < 400:
        return

    correctFingerIndex = bestMatch.index(max(bestMatch))

    for i in range(4):
        method = cv2.TM_SQDIFF_NORMED
        result = cv2.matchTemplate(fingerprints[correctFingerIndex].fingerSol[i], screenshot, method)

        mn, _, mnLoc, _ = cv2.minMaxLoc(result)
        MPx, MPy = mnLoc

        windows[i] = boxWindow(MPx, MPy)
        windows[i].show()

    t = Timer(2, clearWindows)
    t.start()


########################################################################################################################
# Hookng keyboard to get input

# Running this prevents further stuff from executing
def hookKeyboard():
    hm = pyHook.HookManager()
    hm.KeyDown = OnKeyboardEvent
    hm.HookKeyboard()
    pythoncom.PumpMessages()


def OnKeyboardEvent(event):
    # The / Key
    if event.KeyID == 191:
        clearWindows()
        solveScreenshot(takeScreenshot()[0], takeScreenshot()[1], fingerprints)

    return True


########################################################################################################################
# Main Stuff

initFingerprints()
print("Ready")
hookKeyboard()

########################################################################################################################

# Experemental

# def mainWindow():
#    app = QApplication(sys.argv)
#    win = QMainWindow()
#    win.setGeometry(960,540,300,300)
#    win.setWindowTitle("GTA Fingerprint Solver")
#
#    label = QtWidgets.QLabel(win)
#    label.setText("Load Images")
#    label.move(50,50)
#
#    button = QPushButton(win)
#    button.setText('Load images')
#    button.move(50, 70)
#    button.clicked.connect(initFingerprints)
#
#    win.show()
#    sys.exit(app.exec_())

#    def start():
#        updateLabel()
#        initFingerprints()
#        hookKeyboard()


#    def updateLabel():
#        label.setText("Loading Images")
#        button.setEnabled(False)

# mainWindow()
