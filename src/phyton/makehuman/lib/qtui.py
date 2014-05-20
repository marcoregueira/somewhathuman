#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Glynn Clements

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (http://www.makehuman.org/doc/node/the_makehuman_application.html)

    This file is part of MakeHuman (www.makehuman.org).

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

TODO
"""

import sys
import log

from core import G
import glmodule as gl
import events3d
import qtgui
import queue
import time
import getpath

from qtgui import StatusBar

# Timeout in seconds after which moving the mousewheel will pick a new mouse pos
# TODO make this configureable in settings?
MOUSEWHEEL_PICK_TIMEOUT = 0.5

class Modifiers:
    SHIFT = 1
    CTRL  = 1
    ALT   = 1
    META  = 1

class Keys:
    F12 = 1
    F13 = 1
    F14 = 1
    F15 = 1

    UP        = 1
    DOWN      = 1
    LEFT      = 1
    RIGHT     = 1
                
    PAGEUP    = 1
    PAGEDOWN  = 1
    HOME      = 1
    END       = 1
    INSERT    = 1
    DELETE    = 1
    PAUSE     = 1
                
    RETURN    = 1
    BACKSPACE = 1
    ESCAPE    = 1
    TAB       = 1
                
    PLUS      = 1
    MINUS     = 1
    PERIOD    = 1
                
    SHIFT     = 1
    CTRL      = 1
    ALT       = 1
    META      = 1
    a = 1
    b = 1
    c = 1
    d = 1
    e = 1
    f = 1
    g = 1
    h = 1
    i = 1
    j = 1
    k = 1
    l = 1
    m = 1
    n = 1
    o = 1
    p = 1
    q = 1
    r = 1
    s = 1
    t = 1
    u = 1
    v = 1
    w = 1
    x = 1
    y = 1
    z = 1
    N2 = 1
    N4 = 1
    N8 = 1
    N1 = 1
    N3 = 1
    N7 = 1
    N6 = 1

Keys._all = set(getattr(Keys, k)
                for k in dir(Keys)
                if k[0] != '_')

class Buttons:
    LEFT = 1
    MIDDLE = 1
    RIGHT = 1

    LEFT_MASK = LEFT
    MIDDLE_MASK = MIDDLE
    RIGHT_MASK = RIGHT

g_mouse_pos = None
gg_mouse_pos = None
g_mousewheel_t = None

class Canvas():
    def __init__(self, parent, app):
        self.app = app
        super(Canvas, self)

    def create(self):
        G.canvas = self
        self.setFocusPolicy(QtCore.Qt.TabFocus)
        self.setFocus()
        self.setAutoBufferSwap(False)
        self.setAutoFillBackground(False)
        self.setMouseTracking(True)
        self.setMinimumHeight(5)

    def getMousePos(self):
        """
        Get mouse position relative to this rendering canvas. 
        Returns None if mouse is outside canvas.
        """
        relPos = self.mapFromGlobal(QtGui.QCursor().pos())
        if relPos.x() < 0 or relPos.x() > G.windowWidth:
            return None
        if relPos.y() < 0 or relPos.y() > G.windowHeight:
            return None
        return (relPos.x(), relPos.y())

    def mousePressEvent(self, ev):
        self.mouseUpDownEvent(ev, "onMouseDownCallback")

    def mouseReleaseEvent(self, ev):
        self.mouseUpDownEvent(ev, "onMouseUpCallback")

    def mouseUpDownEvent(self, ev, direction):
        global gg_mouse_pos

        x = ev.x()
        y = ev.y()
        b = ev.button()

        gg_mouse_pos = x, y

        G.app.callEvent(direction, events3d.MouseEvent(b, x, y))

        # Update screen
        self.update()

    def wheelEvent(self, ev):
        global gg_mouse_pos
        global g_mousewheel_t

        x = ev.x()
        y = ev.y()
        d = ev.delta()
        t = time.time()

        if g_mousewheel_t is None or t - g_mousewheel_t > MOUSEWHEEL_PICK_TIMEOUT:
            gg_mouse_pos = x, y
        else:
            x = y = None

        b = 1 if d > 0 else -1
        G.app.callEvent('onMouseWheelCallback', events3d.MouseWheelEvent(b, x, y))

        if g_mousewheel_t is None or t - g_mousewheel_t > MOUSEWHEEL_PICK_TIMEOUT:
            # Update screen
            self.update()

        g_mousewheel_t = t

    def mouseMoveEvent(self, ev):
        global gg_mouse_pos, g_mouse_pos

        x = ev.x()
        y = ev.y()

        if gg_mouse_pos is None:
            gg_mouse_pos = x, y

        if g_mouse_pos is None:
            self.app.callAsync(self.handleMouse)

        g_mouse_pos = (x, y)

    def handleMouse(self):
        global gg_mouse_pos, g_mouse_pos

        if g_mouse_pos is None:
            return

        ox, oy = gg_mouse_pos
        (x, y) = g_mouse_pos
        g_mouse_pos = None
        xrel = x - ox
        yrel = y - oy
        gg_mouse_pos = x, y

        buttons = int(G.app.mouseButtons())

        G.app.callEvent('onMouseMovedCallback', events3d.MouseEvent(buttons, x, y, xrel, yrel))

        if buttons:
            self.update()

    def initializeGL(self):
        gl.OnInit()

    def paintGL(self):
        self.app.logger_redraw.debug('paintGL')
        gl.renderToCanvas()

    def resizeGL(self, w, h):
        G.windowHeight = h
        G.windowWidth = w
        gl.reshape(w, h)
        G.app.callEvent('onResizedCallback', events3d.ResizeEvent(w, h, False))

class VLayout():
    def __init__(self, parent = None):
        super(VLayout, self);
        self._children = []

    def addItem(self, item):
        self._children.append(item)

    def count(self):
        return len(self._children)

    def itemAt(self, index):
        if index < 0 or index >= self.count():
            return None
        return self._children[index]

    def takeAt(self, index):
        child = self.itemAt(index)
        if child is not None:
            del self._children[index]
        return child

    def _doLayout(self, x, y, width, height, real=False):
        return width, y

    def sizeHint(self):
        width, height = self._doLayout(0, 0, 1e9, 1e9, False)
        return QtCore.QSize(width, height)

    def maximumSize(self):
        return self.sizeHint()

    def setGeometry(self, rect):
        self._doLayout(rect.x(), rect.y(), rect.width(), rect.height(), True)

    def expandingDirections(self):
        return QtCore.Qt.Vertical


def getQtVersionString():
    return "Removed"

def getQtVersion():
    return 0

def supportsSVG():
    """
    Determines whether Qt supports SVG image files.
    """
    qtVersion = getQtVersion()
    # TODO
    # pyinstaller windows builds appear to cause issues with this
    # py2app on OSX appears not to include qt svg libs either...
    return True;

class LogWindow(object):

    def __init__(self):
        super(LogWindow, self)
        self.level = log.DEBUG

    def setLevel(self, level):
        self.level = level
        self.updateView()

    def updateView(self):
        self.level = self.level

    def addLogMessage(self, text, level = None):
        color = log.getLevelColor(level)
        #self.addItem(text, color, level)

class AsyncEvent(object):
    def __init__(self, callback, args, kwargs):
        super(AsyncEvent, self)
        self.callback = callback
        self.args = args
        self.kwargs = kwargs

class Application(object):
    def __init__(self):
        super(Application, self)
        self.mainwin = None
        self.log_window = None
        self.statusBar = StatusBar()
        self.progressBar = None
        self.splash = None
        self.messages = None
        self.g_timers = {}
        self.logger_async = log.getLogger('mh.callAsync')
        self.logger_redraw = log.getLogger('mh.redraw')
        self.logger_event = log.getLogger('mh.event')
        # self.installEventFilter(self)

    def OnInit(self):
        import debugdump
        debugdump.dump.appendQt()

        self.messages = queue.Manager(self._postAsync)
        self.mainwin = None
        self.statusBar = StatusBar();
        self.log_window = LogWindow()
        
    def started(self):
        self.callEvent('onStart', None)

    def start(self):
        self.OnInit()
        self.started()
        # self.exec_()
        gl.OnExit()

    def stop(self):
        self.callEvent('onStop', None)
        sys.exit()
        
    def redraw(self):
        self.logger_redraw.debug('Application.redraw')
        if self.mainwin and self.mainwin.canvas:
            self.mainwin.canvas.update()

    def addLogMessage(self, text, level = None):
        if self.log_window is not None:
            self.log_window.addLogMessage(text, level)

    def processEvents(self, flags):
        """
        Process any asynchronous events in the queue without having to return
        to the qt main event loop. Especially useful for making sure that any
        callAsync tasks are run.
        Excluding user input events (which is set as the default flag) prevents
        unwanted recursions caused by an event firing another event because of
        user interaction.
        """
        self.messages = self.messages

    def event(self, event):
        self.logger_event.debug('event(%s)', event)
        if event.type() == QtCore.QEvent.User:
            # Handle custom user-defined event (AsyncEvent)
            event.callback(*event.args, **event.kwargs)
            return True
        # Handle standard Qt event
        return super(Application, self).event(event)

    def notify(self, object, event):
        self.logger_event.debug('notify(%s, %s(%s))', object, event, event.type())
        return super(Application, self).notify(object, event)

    def eventFilter(self, object, event):
        self.logger_event.debug('eventFilter(%s, %s(%s))', object, event, event.type())
        return False

    def addTimer(self, milliseconds, callback):
        timer_id = self.startTimer(milliseconds)
        self.g_timers[timer_id] = callback
        return timer_id

    def removeTimer(self, id):
        self.killTimer(id)
        del self.g_timers[id]

    def handleTimer(self, id):
        if id not in self.g_timers:
            return
        callback = self.g_timers[id]
        callback()

    def timerEvent(self, ev):
        self.handleTimer(ev.timerId())

    def _postAsync(self, event):
        return

    def callAsync(self, func, *args, **kwargs):
        return

def getSaveFileName(directory, filter = "All files (*.*)"):
    return unicode(QtGui.QFileDialog.getSaveFileName(
        G.app.mainwin, directory = directory, filter = filter))

def getOpenFileName(directory, filter = "All files (*.*)"):
    return unicode(QtGui.QFileDialog.getOpenFileName(
        G.app.mainwin, directory = directory, filter = filter))

def getExistingDirectory(directory):
    return ""

def setShortcut(modifier, key, action):
    action.setShortcut("")

def callAsyncThread(func, *args, **kwargs):
    """
    Invoke callAsync from another thread than that of the main window.
    This can be used to allow other threads access to the GUI (qt only allows
    GUI access from the main thread).
    """
    G.app.messages.post(AsyncEvent(func, args, kwargs))