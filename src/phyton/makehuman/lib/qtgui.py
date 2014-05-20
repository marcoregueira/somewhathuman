#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Glynn Clements, Jonas Hauquier

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
import os

from core import G
import events3d
import language
#import log
from getpath import getSysDataPath, getPath, isSubPath, pathToUnicode


def getLanguageString(text):
    """Function to get the translation of a text according to the selected
    language.

    The function will look up the given text in the current language's
    dictionary and it will return the translated string.
    """
    if not text:
        return text
    return language.language.getLanguageString(text)


class Widget(events3d.EventHandler):
    def __init__(self):
        events3d.EventHandler.__init__(self)

    def callEvent(self, eventType, event):
        super(Widget, self).callEvent(eventType, event)

    def focusInEvent(self, event):
        self.callEvent('onFocus', self)
        super(type(self), self).focusInEvent(event)

    def focusOutEvent(self, event):
        self.callEvent('onBlur', self)
        super(type(self), self).focusOutEvent(event)

    def showEvent(self, event):
        self.callEvent('onShow', self)
        super(type(self), self).showEvent(event)

    def hideEvent(self, event):
        self.callEvent('onHide', self)
        super(type(self), self).hideEvent(event)

    def onFocus(self, event):
        pass

    def onBlur(self, event):
        pass

    def onShow(self, event):
        pass

    def onHide(self, event):
        pass


def intValidator(text):
    return not text or text.isdigit() or (text[0] == '-' and (len(text) == 1 or text[1:].isdigit()))

def floatValidator(text):
    return not text or (text.replace('.', '').isdigit() and text.count('.') <= 1) or (text[0] == '-' and (len(text) == 1 or text[1:].replace('.', '').isdigit()) and text.count('.') <= 1) # Negative sign and optionally digits with optionally 1 decimal point

def filenameValidator(text):
    return not text or len(set(text) & set('\\/:*?"<>|')) == 0

class StatusBar():
    def showMessage(self, text, *args):
        text = getLanguageString(text) % args
        # super(StatusBar, self).showMessage(text, self.duration)

    def setMessage(self, text, *args):
        text = getLanguageString(text) % args
        # self._perm.setText(text)
