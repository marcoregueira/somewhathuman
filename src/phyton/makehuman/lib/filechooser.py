#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
Qt filechooser widget.

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

A Qt based filechooser widget.
"""

import os

import qtgui as gui
import mh
import getpath

class ThumbnailCache(object):
    aspect_mode = 1
    scale_mode = 1

    def __init__(self, size):
        self.cache = {}
        self.size = size

    def __getitem__(self, name):
        nstat = os.stat(name)
        if name in self.cache:
            stat, pixmap = self.cache[name]
            if stat.st_size == nstat.st_size and stat.st_mtime == nstat.st_mtime:
                return pixmap
            else:
                del self.cache[name]
        pixmap = self.loadImage(name)
        self.cache[name] = (nstat, pixmap)
        return pixmap

    def loadImage(self, path):
        #pixmap = QtGui.QPixmap(path)
        #width, height = self.size
        #pixmap = pixmap.scaled(width, height, self.aspect_mode, self.scale_mode)
        #pwidth = pixmap.width()
        #pheight = pixmap.height()
        #if pwidth > width or pheight > height:
        #    x0 = max(0, (pwidth - width) / 2)
        #    y0 = max(0, (pheight - height) / 2)
        #    pixmap = pixmap.copy(x0, y0, width, height)
        return None

class FileChooserRectangle():
    _size = (128, 128)
    _imageCache = ThumbnailCache(_size)

    def __init__(self, owner, file, label, imagePath):
        super(FileChooserRectangle, self)
        self.owner = owner
        self.file = file



    def onClicked(self, event):
        self.owner.selection = self.file
        self.owner.callEvent('onFileSelected', self.file)

class FileSort(object):
    """
    The default file sorting class. Can sort files on name, creation and modification date and size.
    """
    def __init__(self):
        pass

    def fields(self):
        """
        Returns the names of the fields on which this FileSort can sort. For each field it is assumed that the method called sortField exists.

        :return: The names of the fields on which this FileSort can sort.
        :rtype: list or tuple
        """
        return ("name", "created", "modified", "size")

    def sort(self, by, filenames):
        method = getattr(self, "sort%s" % by.capitalize())
        return method(filenames)

    def sortName(self, filenames):
        decorated = [(os.path.basename(filename), i, filename) for i, filename in enumerate(filenames)]
        return self._decoratedSort(decorated)

    def sortModified(self, filenames):
        decorated = [(os.path.getmtime(filename), i, filename) for i, filename in enumerate(filenames)]
        return self._decoratedSort(decorated)

    def sortCreated(self, filenames):
        decorated = [(os.path.getctime(filename), i, filename) for i, filename in enumerate(filenames)]
        return self._decoratedSort(decorated)

    def sortSize(self, filenames):
        decorated = [(os.path.getsize(filename), i, filename) for i, filename in enumerate(filenames)]
        return self._decoratedSort(decorated)

    def _decoratedSort(self, toSort):
        toSort.sort()
        return [filename for sortKey, i, filename in toSort]

def abspath(path):
    """
    Helper function to determine canonical path if a valid (not None) pathname
    is specified.
    Canonical pathnames are used for reliable comparison of two paths.
    """
    if path:
        return getpath.canonicalPath(path)
    else:
        return None
