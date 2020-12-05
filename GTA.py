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

from multiprocessing.dummy import Pool as ThreadPool
########################################################################################################################
# GUI boxes that display over the game

print('Starting :)')

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

def loadImage(response, Finger):
    image = np.asarray(bytearray(response.content), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_GRAYSCALE)

    if Finger:
        image = cv2.resize(image,(320, 550))
    else:
        image = cv2.resize(image,(127,127))

    return image

def build_URL(f=0, s=None):
    url = "https://raw.githubusercontent.com/HazemMohamed98/GTA-Online-Fingerprint/Images/"
    insert = f'F{f}' + (f'S{s}' if s is not None else '')
    return f'{url}{insert}.jpg'

def fetch_all():
    urls = [build_URL(i+1) for i in range(4)] + [build_URL(i+1,j+1) for i in range(4) for j in range(4)]
    with ThreadPool(20) as pool:
        responses = list(pool.map(requests.get, urls))
    return responses

class Fingerprint:
    def __init__(self):
        self.fingerImg = []
        self.fingerSol = [None] * 4


fingerprints = [None] * 4


def initFingerprints():
    # Acquire all URLs in parallel
    print('Downloading Images')
    responses = fetch_all()
    # Initialize the four fingerprints
    ndx = 4
    for i in range(4):
        fingerprints[i] = Fingerprint()
        fingerprints[i].fingersol = []
    for i in range(4):
        fingerprints[i].fingerImg = loadImage(responses[i], True)
        for j in range(4):
            fingerprints[i].fingerSol[j] = loadImage(responses[ndx], False)
            ndx += 1

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
# Hooking keyboard to get input

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
        print('Solving Screenshot')

    return True

########################################################################################################################
# Main Stuff

initFingerprints()
print('Download complete!\nPress / to solve')
hookKeyboard()

########################################################################################################################
