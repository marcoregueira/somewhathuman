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

Main application GUI component.
"""

import sys
import os
import glob
import imp
import contextlib

from core import G
import mh
import events3d
import files3d
import gui3d
import geometry3d
import animation3d
import human
import guifiles
import managed_file
import algos3d
import gui
import language
import log

@contextlib.contextmanager
def outFile(path):
    from codecs import open
    path = mh.getPath(path)
    tmppath = path + '.tmp'
    try:
        with open(tmppath, 'w', encoding="utf-8") as f:
            yield f
        if os.path.exists(path):
            os.remove(path)
        os.rename(tmppath, path)
    except:
        if os.path.exists(tmppath):
            os.remove(tmppath)
        log.error('unable to save file %s', path, exc_info=True)

@contextlib.contextmanager
def inFile(path):
    from codecs import open
    try:
        path = mh.getPath(path)
        if not os.path.isfile(path):
            yield []
            return
        with open(path, 'rU', encoding="utf-8") as f:
            yield f
    except:
        log.error('Failed to load file %s', path, exc_info=True)
        
class MHApplication(gui3d.Application, mh.Application):
    def __init__(self):
        if G.app is not None:
            raise RuntimeError('MHApplication is a singleton')
        G.app = self
        gui3d.Application.__init__(self)
        mh.Application.__init__(self)

        self.shortcuts = {
            # Actions
            'undo':         (mh.Modifiers.CTRL, mh.Keys.z),
            'redo':         (mh.Modifiers.CTRL, mh.Keys.y),
            'modelling':    (mh.Modifiers.CTRL, mh.Keys.m),
            'save':         (mh.Modifiers.CTRL, mh.Keys.s),
            'load':         (mh.Modifiers.CTRL, mh.Keys.l),
            'export':       (mh.Modifiers.CTRL, mh.Keys.e),
            'rendering':    (mh.Modifiers.CTRL, mh.Keys.r),
            'help':         (mh.Modifiers.CTRL, mh.Keys.h),
            'exit':         (mh.Modifiers.CTRL, mh.Keys.q),
            'stereo':       (mh.Modifiers.CTRL, mh.Keys.w),
            'wireframe':    (mh.Modifiers.CTRL, mh.Keys.f),
            'savetgt':      (mh.Modifiers.ALT, mh.Keys.t),
            'qexport':      (mh.Modifiers.ALT, mh.Keys.e),
            'smooth':       (mh.Modifiers.ALT, mh.Keys.s),
            'grab':         (mh.Modifiers.ALT, mh.Keys.g),
            'profiling':    (mh.Modifiers.ALT, mh.Keys.p),
            # Camera navigation
            'rotateD':      (0, mh.Keys.N2),
            'rotateL':      (0, mh.Keys.N4),
            'rotateR':      (0, mh.Keys.N6),
            'rotateU':      (0, mh.Keys.N8),
            'panU':         (0, mh.Keys.UP),
            'panD':         (0, mh.Keys.DOWN),
            'panR':         (0, mh.Keys.RIGHT),
            'panL':         (0, mh.Keys.LEFT),
            'zoomIn':       (0, mh.Keys.PLUS),
            'zoomOut':      (0, mh.Keys.MINUS),
            'front':        (0, mh.Keys.N1),
            'right':        (0, mh.Keys.N3),
            'top':          (0, mh.Keys.N7),
            'back':         (mh.Modifiers.CTRL, mh.Keys.N1),
            'left':         (mh.Modifiers.CTRL, mh.Keys.N3),
            'bottom':       (mh.Modifiers.CTRL, mh.Keys.N7),
            'resetCam':     (0, mh.Keys.PERIOD),
            # Version check
            '_versionSentinel': (0, 0x87654321)
        }

        self.mouseActions = {
            (0, mh.Buttons.LEFT_MASK): self.mouseRotate,
            (0, mh.Buttons.RIGHT_MASK): self.mouseZoom,
            (0, mh.Buttons.MIDDLE_MASK): self.mouseTranslate,
            (mh.Modifiers.CTRL, mh.Buttons.RIGHT_MASK): self.mouseFocus
        }

        if mh.isRelease():
            self.settings = {
                'realtimeUpdates': True,
                'realtimeFitting': True,
                'sliderImages': True,
                'excludePlugins': [
                    "7_data",
                    "7_example",
                    "7_material_editor",
                    "7_profile",
                    "7_scene_editor",
                    "7_scripting",
                    "7_shell",
                    "7_targets",
                ],
                'rtl': False,
                'invertMouseWheel': False,
                'lowspeed': 1,
                'preloadTargets': True,
                'cameraAutoZoom': False,
                'language': 'english',
                'highspeed': 5,
                'realtimeNormalUpdates': True,
                'units': 'metric',
                'guiTheme': 'makehuman',
                'restoreWindowSize': True
            }
        else:
            self.settings = {
                'realtimeUpdates': True,
                'realtimeFitting': True,
                'realtimeNormalUpdates': True,
                'cameraAutoZoom': False,
                'lowspeed': 1,
                'highspeed': 5,
                'units':'metric',
                'invertMouseWheel':False,
                'language':'english',
                'excludePlugins':[],
                'rtl': False,
                'sliderImages': True,
                'guiTheme': 'makehuman',
                'preloadTargets': False,
                'restoreWindowSize': False
            }

        self.loadHandlers = {}
        self.saveHandlers = []

        self.dialog = None
        self.helpIds = set()

        self.tool = None
        self.selectedGroup = None

        self.undoStack = []
        self.redoStack = []

        self.actions = Expando()

        self.clearColor = [0.5, 0.5, 0.5]
        self.gridColor = [1.0, 1.0, 1.0]
        self.gridSubColor = [0.7, 0.7, 0.7]

        self.modules = {}

        self.selectedHuman = None
        self.currentFile = managed_file.File()
        self._scene = None
        self.backplaneGrid = None
        self.groundplaneGrid = None

        self.theme = None

        @self.currentFile.mhEvent
        # def onModified(event):
        #    self.updateFilenameCaption()

        #self.modelCamera = mh.Camera()
        #self.modelCamera.switchToOrtho()
        #self.modelCamera = mh.OrbitalCamera()
        #self.modelCamera.debug = True

        #@self.modelCamera.mhEvent
        def onChanged(event):
            for category in self.categories.itervalues():
                for task in category.tasks:
                    task.callEvent('onCameraChanged', event)

        #mh.cameras.append(self.modelCamera)

        #self.guiCamera = mh.Camera()
        #self.guiCamera._fovAngle = 45
        #self.guiCamera._eyeZ = 10
        #self.guiCamera._projection = 0
        #self.guiCamera = mh.OrbitalCamera()

        #mh.cameras.append(self.guiCamera)

    def _versionSentinel(self):
        # dummy method used for checking the shortcuts.ini version
        pass

    @property
    def args(self):
        return G.args

    def loadHumanMHM(self, filename):
        self.selectedHuman.load(filename, True, self.progress)
        self.clearUndoRedo()
        # Reset mesh is never forced to wireframe
        self.actions.wireframe.setChecked(False)

    # TO THINK: Maybe move guiload's saveMHM here as saveHumanMHM?

    def loadHuman(self):
        self.progress(0.1)

        # Set a lower than default MAX_FACES value because we know the human has a good topology (will make it a little faster)
        # (we do not lower the global limit because that would limit the selection of meshes that MH would accept too much)
        mesh = files3d.loadMesh(mh.getSysDataPath("3dobjs/base.obj"), maxFaces = 5)
        humanModel = human.Human(mesh)
        self.selectedHuman = self.addObject(humanModel)

    def loadScene(self):

        self.progress(0.18)

        userSceneDir = mh.getDataPath("scenes")
        if not os.path.exists(userSceneDir):
            os.makedirs(userSceneDir)

        from scene import Scene
        from getpath import findFile
        self.setScene( Scene(findFile("scenes/default.mhscene")) )

    def loadMainGui(self):

        self.progress(0.2)

        @self.selectedHuman.mhEvent
        def onMouseDown(event):
          if self.tool:
            self.selectedGroup = self.getSelectedFaceGroup()
            self.tool.callEvent("onMouseDown", event)
          else:
            self.currentTask.callEvent("onMouseDown", event)

        @self.selectedHuman.mhEvent
        def onMouseMoved(event):
          if self.tool:
            self.tool.callEvent("onMouseMoved", event)
          else:
            self.currentTask.callEvent("onMouseMoved", event)

        @self.selectedHuman.mhEvent
        def onMouseDragged(event):
          if self.tool:
            self.tool.callEvent("onMouseDragged", event)
          else:
            self.currentTask.callEvent("onMouseDragged", event)

        @self.selectedHuman.mhEvent
        def onMouseUp(event):
          if self.tool:
            self.tool.callEvent("onMouseUp", event)
          else:
            self.currentTask.callEvent("onMouseUp", event)

        @self.selectedHuman.mhEvent
        def onMouseEntered(event):
          if self.tool:
            self.tool.callEvent("onMouseEntered", event)
          else:
            self.currentTask.callEvent("onMouseEntered", event)

        @self.selectedHuman.mhEvent
        def onMouseExited(event):
          if self.tool:
            self.tool.callEvent("onMouseExited", event)
          else:
            self.currentTask.callEvent("onMouseExited", event)

        @self.selectedHuman.mhEvent
        def onMouseWheel(event):
          if self.tool:
            self.tool.callEvent("onMouseWheel", event)
          else:
            self.currentTask.callEvent("onMouseWheel", event)

        @self.selectedHuman.mhEvent
        def onChanging(event):
            for category in self.categories.itervalues():
                for task in category.tasks:
                    task.callEvent('onHumanChanging', event)

        @self.selectedHuman.mhEvent
        def onChanged(event):
            if event.change == 'smooth':
                # Update smooth action state (without triggering it)
                self.actions.smooth.setChecked(self.selectedHuman.isSubdivided())
            elif event.change == 'load':
                self.currentFile.loaded(event.path)
            elif event.change == 'save':
                self.currentFile.saved(event.path)
            elif event.change == 'reset':
                self.currentFile.closed()
            for category in self.categories.itervalues():
                for task in category.tasks:
                    task.callEvent('onHumanChanged', event)

        @self.selectedHuman.mhEvent
        def onTranslated(event):
            for category in self.categories.itervalues():
                for task in category.tasks:
                    task.callEvent('onHumanTranslated', event)

        @self.selectedHuman.mhEvent
        def onRotated(event):
            for category in self.categories.itervalues():
                for task in category.tasks:
                    task.callEvent('onHumanRotated', event)

        @self.selectedHuman.mhEvent
        def onShown(event):
            for category in self.categories.itervalues():
                for task in category.tasks:
                    task.callEvent('onHumanShown', event)

        @self.selectedHuman.mhEvent
        def onHidden(event):
            for category in self.categories.itervalues():
                for task in category.tasks:
                    task.callEvent('onHumanHidden', event)

        @self.modelCamera.mhEvent
        def onRotated(event):
            for category in self.categories.itervalues():
                for task in category.tasks:
                    task.callEvent('onCameraRotated', event)

        # Set up categories and tasks
        # MARCO NO NEED
        return
        self.files = guifiles.FilesCategory()
        self.addCategory(self.files)
        self.getCategory("Modelling")
        self.getCategory("Geometries")
        self.getCategory("Materials")
        self.getCategory("Pose/Animate")
        self.getCategory("Rendering")

    def loadPlugins(self):

        self.progress(0.4)

        # Load plugins not starting with _
        self.pluginsToLoad = glob.glob(mh.getSysPath(os.path.join("plugins/",'[!_]*.py')))

        # Load plugin packages (folders with a file called __init__.py)
        for fname in os.listdir(mh.getSysPath("plugins/")):
            if fname[0] != "_":
                folder = os.path.join("plugins", fname)
                if os.path.isdir(folder) and ("__init__.py" in os.listdir(folder)):
                    self.pluginsToLoad.append(folder)

        self.pluginsToLoad.sort()
        self.pluginsToLoad.reverse()

        while self.pluginsToLoad:
            self.loadNextPlugin()

    def loadNextPlugin(self):

        alreadyLoaded = len(self.modules)
        stillToLoad = len(self.pluginsToLoad)
        self.progress(0.4 + (float(alreadyLoaded) / float(alreadyLoaded + stillToLoad)) * 0.4)

        if not stillToLoad:
            return

        path = self.pluginsToLoad.pop()
        try:
            name, ext = os.path.splitext(os.path.basename(path))

            if name == 'export_obj':
                return
            if name == 'scripting':
                return
                
            if name not in self.settings['excludePlugins']:
                log.message('Importing plugin %s', name)
                #module = imp.load_source(name, path)

                module = None
                fp, pathname, description = imp.find_module(name, ["plugins/"])
                try:
                    module = imp.load_module(name, fp, pathname, description)
                finally:
                    if fp:
                        fp.close()
                if module is None:
                    log.message("Could not import plugin %s", name)
                    return

                self.modules[name] = module
                log.message('Imported plugin %s', name)
                log.message('Loading plugin %s', name)
                module.load(self)
                log.message('Loaded plugin %s', name)

                # Process all non-user-input events in the queue to make sure
                # any callAsync events are run.
                # self.processEvents()
            else:
                self.modules[name] = None
        except Exception, _:
            log.warning('Could not load %s', name, exc_info=True)

    def unloadPlugins(self):

        for name, module in self.modules.iteritems():
            if module is None:
                continue
            try:
                log.message('Unloading plugin %s', name)
                module.unload(self)
                log.message('Unloaded plugin %s', name)
            except Exception, _:
                log.warning('Could not unload %s', name, exc_info=True)

    def getLoadedPlugins(self):
        """
        Get the names of loaded plugins.
        """
        return self.modules.keys()

    def getPlugin(self, name):
        """
        Get the (python) module of the plugin with specified name.
        """
        return self.modules[name]

    def loadGui(self):

        self.progress(0.9)

        #category = self.getCategory('Settings')
        #category.addTask(PluginsTaskView(category))

        mh.refreshLayout()

        self.switchCategory("Modelling")

        # Create viewport grid
        self.loadGrid()

        self.progress(1.0)
        # self.progressBar.hide()

    def loadGrid(self):
        pass

    def loadMacroTargets(self):
        """
        Preload all target files belonging to group macrodetails and its child
        groups.
        """
        import targets
        #import getpath
        for target in targets.getTargets().findTargets('macrodetails'):
            #log.debug('Preloading target %s', getpath.getRelativePath(target.path))
            algos3d.getTarget(self.selectedHuman.meshData, target.path)

    def loadFinish(self):
        #self.selectedHuman.callEvent('onChanged', events3d.HumanEvent(self.selectedHuman, 'reset'))
        self.selectedHuman.applyAllTargets(gui3d.app.progress)

        #self.prompt('Warning', 'MakeHuman is a character creation suite. It is designed for making anatomically correct humans.\nParts of this program may contain nudity.\nDo you want to proceed?', 'Yes', 'No', None, self.stop, 'nudityWarning')
        ## self.splash.hide()

        #if not self.args.get('noshaders', False) and \
        #  ( not mh.Shader.supported() or mh.Shader.glslVersion() < (1,20) ):
        #    self.prompt('Warning', 'Your system does not support OpenGL shaders (GLSL v1.20 required).\nOnly simple shading will be available.', 'Ok', None, None, None, 'glslWarning')

        self.currentFile.modified = False

        #printtree(self)

        #mh.changeCategory("Modelling")

        #self.redraw()

    def startupSequence(self):
        self._processCommandlineArgs(beforeLoaded = True)

        # mainwinGeometry = None # self.mainwin.storeGeometry()
        # mainwinBorder = None # (self.mainwin.frameGeometry().width() - self.mainwin.width(), self.mainwin.frameGeometry().height() - self.mainwin.height())

        # Move main window completely behind splash screen
        # self.mainwin.resize(self.splash.width() - mainwinBorder[0], self.splash.height() - mainwinBorder[1])
        # self.mainwin.move(self.splash.pos())

        #self.splash.setFormat('<br><br><b><font size="10" color="#ffffff">%s</font></b>')

        log.message('Loading human')
        self.loadHuman()

        log.message('Loading scene')
        # self.loadScene()

        log.message('Loading main GUI')
        # self.loadMainGui()

        log.message('Loading plugins')
        self.loadPlugins()

        #log.message('Loading GUI')
        #self.loadGui()

        #log.message('Loading theme')
        #try:
        #    self.setTheme(self.settings.get('guiTheme', 'makehuman'))
        #except:
        #    self.setTheme("default")

        log.message('Applying targets')
        self.loadFinish()

        #if self.settings.get('preloadTargets', False):
        #Always load targets
        log.message('Loading macro targets')
        self.loadMacroTargets()

        log.message('Loading done')

        log.message('')

        #if sys.platform.startswith("darwin"):
        #    self.splash.resize(0,0) # work-around for mac splash-screen closing bug

        #self.splash.hide()
        # self.splash.finish(self.mainwin)
        #self.splash.close()
        #self.splash = None

        # Restore main window size and position
        #if self.settings.get('restoreWindowSize', False):
        #    self.mainwin.restoreGeometry(self.settings.get(
        #        'windowGeometry', mainwinGeometry))
        #else:
        #    self.mainwin.restoreGeometry(mainwinGeometry)

        self._processCommandlineArgs(beforeLoaded = False)

    def _processCommandlineArgs(self, beforeLoaded):
        if beforeLoaded:
            if self.args.get('noshaders', False):
                log.message("Force shaders disabled")

        else: # After application is loaded
            if self.args.get('mhmFile', None):
                mhmFile = self.args.get('mhmFile')
                log.message("Loading MHM file %s (as specified by commandline argument)", mhmFile)
                if os.path.isfile(mhmFile):
                    self.loadHumanMHM(mhmFile)
                else:
                    log.error("Failed to load MHM file. The MHM file specified as argument (%s) does not exist!", mhmFile)
            if self.args.get('runtests', False):
                log.message("Running test suite")
                import testsuite
                testsuite.runAll()

    # Events
    def onStart(self, event):
        self.startupSequence()

    def onStop(self, event):
        if self.settings.get('restoreWindowSize', False):
            self.settings['windowGeometry'] = self.mainwin.storeGeometry()

        self.saveSettings(True)
        self.unloadPlugins()
        self.dumpMissingStrings()

    def onQuit(self, event):

        self.promptAndExit()

    def onMouseDown(self, event):
        if self.selectedHuman.isVisible():
            # Normalize modifiers
            modifiers = mh.getKeyModifiers() & (mh.Modifiers.CTRL | mh.Modifiers.ALT | mh.Modifiers.SHIFT)

            if (modifiers, event.button) in self.mouseActions:
                action = self.mouseActions[(modifiers, event.button)]
                if action == self.mouseFocus:
                    self.modelCamera.mousePickHumanFocus(event.x, event.y)
                elif action == self.mouseZoom:
                    self.modelCamera.mousePickHumanCenter(event.x, event.y)

    def onMouseDragged(self, event):

        if self.selectedHuman.isVisible():
            # Normalize modifiers
            modifiers = mh.getKeyModifiers() & (mh.Modifiers.CTRL | mh.Modifiers.ALT | mh.Modifiers.SHIFT)

            if (modifiers, event.button) in self.mouseActions:
                self.mouseActions[(modifiers, event.button)](event)

    def onMouseWheel(self, event):
        if self.selectedHuman.isVisible():
            zoomOut = event.wheelDelta > 0
            if gui3d.app.settings.get('invertMouseWheel', False):
                zoomOut = not zoomOut

            if event.x is not None:
                self.modelCamera.mousePickHumanCenter(event.x, event.y)

            if zoomOut:
                self.zoomOut()
            else:
                self.zoomIn()

    # Undo-redo
    def do(self, action):
        if action.do():
            self.undoStack.append(action)
            del self.redoStack[:]
            self.currentFile.changed()
            log.message('do %s', action.name)
            self.syncUndoRedo()

    def did(self, action):
        self.undoStack.append(action)
        self.currentFile.changed()
        del self.redoStack[:]
        log.message('did %s', action.name)
        self.syncUndoRedo()

    def undo(self):
        if self.undoStack:
            action = self.undoStack.pop()
            log.message('undo %s', action.name)
            action.undo()
            self.redoStack.append(action)
            self.currentFile.changed()
            self.syncUndoRedo()

    def redo(self):
        if self.redoStack:
            action = self.redoStack.pop()
            log.message('redo %s', action.name)
            action.do()
            self.undoStack.append(action)
            self.currentFile.changed()
            self.syncUndoRedo()

    def syncUndoRedo(self):
        self.actions.undo.setEnabled(bool(self.undoStack))
        self.actions.redo.setEnabled(bool(self.redoStack))
        self.redraw()

    def clearUndoRedo(self):
        self.undoStack = []
        self.redoStack = []
        self.syncUndoRedo()

    # Settings

    def loadSettings(self):
        with inFile("settings.ini") as f:
            if f:
                settings = mh.parseINI(f.read())
                self.settings.update(settings)

        if 'language' in self.settings:
            self.setLanguage(self.settings['language'])

    def saveSettings(self, promptOnFail=False):
        try:
            if not os.path.exists(mh.getPath()):
                os.makedirs(mh.getPath())

            with outFile("settings.ini") as f:
                f.write(mh.formatINI(self.settings))

            with outFile("shortcuts.ini") as f:
                for action, shortcut in self.shortcuts.iteritems():
                    f.write('%d %d %s\n' % (shortcut[0], shortcut[1], action))

            with outFile("mouse.ini") as f:
                for mouseAction, method in self.mouseActions.iteritems():
                    f.write('%d %d %s\n' % (mouseAction[0], mouseAction[1], method.__name__))

            if self.dialog is not None:
                self.helpIds.update(self.dialog.helpIds)

            with outFile("help.ini") as f:
                for helpId in self.helpIds:
                    f.write('%s\n' % helpId)
        except:
            log.error('Failed to save settings file', exc_info=True)
            if promptOnFail:
                self.prompt('Error', 'Could not save settings file.', 'OK')

    # Themes
    def setTheme(self, theme):

        # Disabling this check allows faster testing of a skin by reloading it.
        if self.theme == theme:
            return

        # Set defaults
        self.clearColor = [0.5, 0.5, 0.5]
        self.gridColor = [1.0, 1.0, 1.0]
        self.gridSubColor = [0.7, 0.7, 0.7]
        log._logLevelColors[log.DEBUG] = 'grey'
        log._logLevelColors[log.NOTICE] = 'blue'
        log._logLevelColors[log.WARNING] = 'darkorange'
        log._logLevelColors[log.ERROR] = 'red'
        log._logLevelColors[log.CRITICAL] = 'red'

        f = open(os.path.join(mh.getSysDataPath("themes/"), theme + ".mht"), 'rU')

        update_log = False
        for data in f.readlines():
            lineData = data.split()

            if len(lineData) > 0:
                if lineData[0] == "version":
                    log.message('Theme %s version %s', theme, lineData[1])
                elif lineData[0] == "color":
                    if lineData[1] == "clear":
                        self.clearColor[:] = [float(val) for val in lineData[2:5]]
                    elif lineData[1] == "grid":
                        self.gridColor[:] = [float(val) for val in lineData[2:5]]
                    elif lineData[1] == "subgrid":
                        self.gridSubColor[:] = [float(val) for val in lineData[2:5]]
                elif lineData[0] == "logwindow_color":
                    logLevel = lineData[1]
                    if hasattr(log, logLevel) and isinstance(getattr(log, logLevel), int):
                        update_log = True
                        logLevel = int(getattr(log, logLevel))
                        log._logLevelColors[logLevel] = lineData[2]

        if self.groundplaneGrid:
            self.groundplaneGrid.mesh.setMainColor(self.gridColor)
            self.groundplaneGrid.mesh.setSubColor(self.gridSubColor)
        if self.backplaneGrid:
            self.backplaneGrid.mesh.setMainColor(self.gridColor)
            self.backplaneGrid.mesh.setSubColor(self.gridSubColor)
        mh.setClearColor(self.clearColor[0], self.clearColor[1], self.clearColor[2], 1.0)

        if update_log:
            self.log_window.updateView()
        log.debug("Loaded theme %s", mh.getSysDataPath('themes/'+theme+'.mht'))

        self.theme = theme
        self.reloadIcons()
        self.redraw()

    def reloadIcons(self):
        return

    def getLookAndFeelStyles(self):
        return [ str(style) for style in gui.QtGui.QStyleFactory.keys() ]

    def setLookAndFeel(self, platform):
        style = gui.QtGui.QStyleFactory.create(platform)
        self.setStyle(style)

    def getLookAndFeel(self):
        return ""

    def getThemeResource(self, folder, id):
        if '/' in id:
            return id
        path = os.path.join(mh.getSysDataPath("themes/"), self.theme, folder, id)
        if os.path.exists(path):
            return path
        else:
            return os.path.join(mh.getSysDataPath("themes/default/"), folder, id)

    def setLanguage(self, lang):
        log.debug("Setting language to %s", lang)
        language.language.setLanguage(lang)
        self.settings['rtl'] = language.language.rtl

    def getLanguages(self):
        """
        The languages available on this MH installation, by listing all .json
        files in the languages folder in user and system data path.
        """
        return language.getLanguages()

    def getLanguageString(self, string):
        return language.language.getLanguageString(string)

    def dumpMissingStrings(self):
        language.language.dumpMissingStrings()

    # Caption
    def setCaption(self, caption):
        """Set the main window caption."""
        mh.setCaption(caption)

    def updateFilenameCaption(self):
        """Calculate and set the window title according to the
        name of the current open file and the version of MH."""
        filename = self.currentFile.name
        if filename is None:
            filename = "Untitled"
        if mh.isRelease():
            from getpath import pathToUnicode
            self.setCaption(
                "MakeHuman %s - [%s][*]" %
                (mh.getVersionStr(), pathToUnicode(filename)))
        else:
            from getpath import pathToUnicode
            self.setCaption(
                "MakeHuman r%s (%s) - [%s][*]" %
                (os.environ['HGREVISION'], os.environ['HGNODEID'], 
                pathToUnicode(filename)))
        self.mainwin.setWindowModified(self.currentFile.modified)

    # Global status bar
    def status(self, text, *args):
        if self.statusBar is None:
            return
        self.statusBar.showMessage(text, *args)

    def statusPersist(self, text, *args):
        if self.statusBar is None:
            return
        self.statusBar.setMessage(text, *args)

    # Global progress bar
    def progress(self, value, text=None, *args):
        if text is not None:
            self.status(text, *args)

        if self.splash:
            self.splash.setProgress(value)

        if self.progressBar is None:
            return

        if value >= 1.0:
            self.progressBar.reset()
        else:
            self.progressBar.setProgress(value)

        # Process all non-user-input events in the queue to run callAsync tasks.
        # This is invoked here so events are processed in every step during the
        # onStart() init sequence.
        # self.processEvents()

    # Global dialog
    def prompt(self, title, text, button1Label, button2Label=None, button1Action=None, button2Action=None, helpId=None, fmtArgs = None):
        if fmtArgs is None:
            fmtArgs = []
        elif isinstance(fmtArgs, basestring):
            fmtArgs = [fmtArgs]
        if self.dialog is None:
            self.dialog = gui.Dialog(self.mainwin)
            self.dialog.helpIds.update(self.helpIds)
        return self.dialog.prompt(title, text, button1Label, button2Label, button1Action, button2Action, helpId, fmtArgs)

    def setGlobalCamera(self):
        human = self.selectedHuman

        tl = animation3d.Timeline(0.20)
        tl.append(animation3d.PathAction(self.modelCamera, [self.modelCamera.getPosition(), [0.0, 0.0, 0.0]]))
        tl.append(animation3d.RotateAction(self.modelCamera, self.modelCamera.getRotation(), [0.0, 0.0, 0.0]))
        tl.append(animation3d.ZoomAction(self.modelCamera, self.modelCamera.zoomFactor, 1.0))
        tl.append(animation3d.UpdateAction(self))
        tl.start()

    def setTargetCamera(self, vIdx, zoomFactor = 1.0, animate = True):
        if isinstance(vIdx, (tuple, list)):
            return
        human = self.selectedHuman
        coord = human.meshData.coord[vIdx]
        direction = human.meshData.vnorm[vIdx].copy()
        self.modelCamera.focusOn(coord, direction, zoomFactor, animate)
        if not animate:
            self.redraw()

    def setFaceCamera(self):
        self.setTargetCamera(132, 8.7)

    def setLeftHandFrontCamera(self):
        self.setTargetCamera(9828, 10)

    def setLeftHandTopCamera(self):
        self.setTargetCamera(9833, 10)

    def setRightHandFrontCamera(self):
        self.setTargetCamera(3160, 10)

    def setRightHandTopCamera(self):
        self.setTargetCamera(3165, 10)

    def setLeftFootFrontCamera(self):
        self.setTargetCamera(12832, 7.7)

    def setLeftFootLeftCamera(self):
        self.setTargetCamera(12823, 7)

    def setRightFootFrontCamera(self):
        self.setTargetCamera(6235, 7.7)

    def setRightFootRightCamera(self):
        self.setTargetCamera(6208, 7)

    def setLeftArmFrontCamera(self):
        self.setTargetCamera(9981, 4.2)

    def setLeftArmTopCamera(self):
        self.setTargetCamera(9996, 2.9)

    def setRightArmFrontCamera(self):
        self.setTargetCamera(3330, 4.2)

    def setRightArmTopCamera(self):
        self.setTargetCamera(3413, 2.9)

    def setLeftLegFrontCamera(self):
        self.setTargetCamera(11325, 2.7)

    def setLeftLegLeftCamera(self):
        self.setTargetCamera(11381, 2.3)

    def setRightLegFrontCamera(self):
        self.setTargetCamera(4707, 2.7)

    def setRightLegRightCamera(self):
        self.setTargetCamera(4744, 2.3)

    def getScene(self):
        """
        The scene used for rendering the viewport.
        """
        return self._scene

    def setScene(self, scene):
        """
        Set the scene used for rendering the viewport,
        and connect its events with appropriate handler methods.
        """
        setSceneEvent = managed_file.FileModifiedEvent.fromObjectAssignment(
            scene.file if scene else None,
            self._scene.file if self._scene else None)

        self._scene = scene

        if self._scene is None:
            return

        @self._scene.file.mhEvent
        def onModified(event):
            self._sceneChanged(event)

        self._sceneChanged(setSceneEvent)

    scene = property(getScene, setScene)

    def _sceneChanged(self, event):
        """
        Method to be called internally when the scene is modified,
        that updates the view according to the modified scene,
        and emits the onSceneChanged event application - wide.
        """
        if event.file != self.scene.file:
            return

        if event.objectWasChanged:
            from glmodule import setSceneLighting
            setSceneLighting(self.scene)

        for category in self.categories.itervalues():
            for task in category.tasks:
                task.callEvent('onSceneChanged', event)

    # Shortcuts
    def setShortcut(self, modifier, key, action):

        shortcut = (modifier, key)

        if shortcut in self.shortcuts.values():
            self.prompt('Warning', 'This combination is already in use.', 'OK', helpId='shortcutWarning')
            return False

        self.shortcuts[action.name] = shortcut
        mh.setShortcut(modifier, key, action)

        return True

    def getShortcut(self, action):
        return self.shortcuts.get(action.name)

    # Mouse actions
    def setMouseAction(self, modifier, key, method):

        mouseAction = (modifier, key)

        if mouseAction in self.mouseActions:
            self.prompt('Warning', 'This combination is already in use.', 'OK', helpId='mouseActionWarning')
            return False

        # Remove old entry
        for s, m in self.mouseActions.iteritems():
            if m == method:
                del self.mouseActions[s]
                break

        self.mouseActions[mouseAction] = method

        #for mouseAction, m in self.mouseActions.iteritems():
        #    print mouseAction, m

        return True

    def getMouseAction(self, method):

        for mouseAction, m in self.mouseActions.iteritems():
            if m == method:
                return mouseAction

    # Load handlers

    def addLoadHandler(self, keyword, handler):
        self.loadHandlers[keyword] = handler

    # Save handlers

    def addSaveHandler(self, handler, priority = None):
        """
        If priority is specified, should be an integer number > 0.
        0 is highest priority.
        """
        if priority is None:
            self.saveHandlers.append(handler)
        else:
            # TODO more robust solution for specifying priority weights
            self.saveHandlers.insert(priority, handler)

    # Shortcut methods

    def goToModelling(self):
        mh.changeCategory("Modelling")
        self.redraw()

    def doSave(self):
        if self.currentFile.path:
            from guisave import saveMHM
            self.currentTask.hide()
            saveMHM(self.currentFile.path)
            self.currentTask.show()
            self.redraw()
        else:
            self.goToSave()

    def goToSave(self):
        mh.changeTask("Files", "Save")
        self.redraw()

    def goToLoad(self):
        mh.changeTask("Files", "Load")
        self.redraw()

    def goToExport(self):
        mh.changeTask("Files", "Export")
        self.redraw()

    def goToRendering(self):
        mh.changeCategory("Rendering")
        self.redraw()

    def goToHelp(self):
        mh.changeCategory("Help")

    def toggleSolid(self):
        self.selectedHuman.setSolid(not self.actions.wireframe.isChecked())
        self.redraw()

    def toggleSubdivision(self):
        self.selectedHuman.setSubdivided(self.actions.smooth.isChecked(), True, self.progress)
        self.redraw()

    def symmetryRight(self):
        human = self.selectedHuman
        self.do( SymmetryAction(human, 'r') )

    def symmetryLeft(self):
        human = self.selectedHuman
        self.do( SymmetryAction(human, 'l') )

    def symmetry(self):
        human = self.selectedHuman
        human.symmetryModeEnabled = self.actions.symmetry.isChecked()

    def saveTarget(self, path=None):
        """
        Export the current modifications to the human as one single target,
        relative to the basemesh.
        """
        if path is None:
            path = mh.getPath("full_target.target")
        if os.path.splitext(path)[1] != '.target':
            raise RuntimeError("Cannot save target to file %s, expected a path to a .target file." % path)
        human = self.selectedHuman
        algos3d.saveTranslationTarget(human.meshData, path)
        log.message("Full target exported to %s", path)

    def grabScreen(self):
        import datetime
        grabPath = mh.getPath('grab')
        if not os.path.exists(grabPath):
            os.makedirs(grabPath)
        grabName = datetime.datetime.now().strftime('grab_%Y-%m-%d_%H.%M.%S.png')
        filename = os.path.join(grabPath, grabName)
        mh.grabScreen(0, 0, G.windowWidth, G.windowHeight, filename)
        self.status("Screengrab saved to %s", filename)

    def resetHuman(self):
        self._resetHuman()

    def _resetHuman(self):
        self.selectedHuman.resetMeshValues()
        self.selectedHuman.applyAllTargets(self.progress)
        self.clearUndoRedo()
        # Reset mesh is never forced to wireframe
        self.actions.wireframe.setChecked(False)

    # Camera navigation
    def rotateCamera(self, axis, amount):
        self.modelCamera.addRotation(axis, amount)
        if axis == 1 and self.modelCamera.getRotation()[1] in [0, 90, 180, 270]:
            # Make sure that while rotating the grid never appears
            self.modelCamera.addRotation(1, 0.001)
        self.redraw()

    def panCamera(self, axis, amount):
        self.modelCamera.addTranslation(axis, amount)
        self.redraw()

    def cameraSpeed(self):
        if mh.getKeyModifiers() & mh.Modifiers.SHIFT:
            return gui3d.app.settings.get('highspeed', 5)
        else:
            return gui3d.app.settings.get('lowspeed', 1)

    def zoomCamera(self, amount):
        self.modelCamera.addZoom(amount * self.cameraSpeed())
        self.redraw()

    def rotateAction(self, axis):
        return animation3d.RotateAction(self.modelCamera, self.modelCamera.getRotation(), axis)

    def axisView(self, axis):
        tmp = self.modelCamera.limitInclination
        self.modelCamera.limitInclination = False
        animation3d.animate(self, 0.20, [self.rotateAction(axis)])
        self.modelCamera.limitInclination = tmp

    def rotateDown(self):
        self.rotateCamera(0, 5.0)

    def rotateUp(self):
        self.rotateCamera(0, -5.0)

    def rotateLeft(self):
        self.rotateCamera(1, -5.0)

    def rotateRight(self):
        self.rotateCamera(1, 5.0)

    def panUp(self):
        self.panCamera(1, 0.05)

    def panDown(self):
        self.panCamera(1, -0.05)

    def panRight(self):
        self.panCamera(0, 0.05)

    def panLeft(self):
        self.panCamera(0, -0.05)

    def zoomOut(self):
        self.zoomCamera(0.65)

    def zoomIn(self):
        self.zoomCamera(-0.65)

    def frontView(self):
        self.axisView([0.0, 0.0, 0.0])

    def rightView(self):
        self.axisView([0.0, 90.0, 0.0])

    def topView(self):
        self.axisView([90.0, 0.0, 0.0])

    def backView(self):
        self.axisView([0.0, 180.0, 0.0])

    def leftView(self):
        self.axisView([0.0, -90.0, 0.0])

    def bottomView(self):
        self.axisView([-90.0, 0.0, 0.0])

    def resetView(self):
        cam = self.modelCamera
        animation3d.animate(self, 0.20, [
            self.rotateAction([0.0, 0.0, 0.0]),
            animation3d.PathAction(self.modelCamera, [self.modelCamera.getPosition(), [0.0, 0.0, 0.0]]),
            animation3d.ZoomAction(self.modelCamera, self.modelCamera.zoomFactor, 1.0) ])

    # Mouse actions
    def mouseTranslate(self, event):

        speed = self.cameraSpeed()
        self.modelCamera.addXYTranslation(event.dx * speed, event.dy * speed)

    def mouseRotate(self, event):

        speed = self.cameraSpeed()

        rotX = 0.5 * event.dy * speed
        rotY = 0.5 * event.dx * speed
        self.modelCamera.addRotation(0, rotX)
        self.modelCamera.addRotation(1, rotY)

    def mouseZoom(self, event):

        speed = self.cameraSpeed()

        if gui3d.app.settings.get('invertMouseWheel', False):
            speed *= -1

        self.modelCamera.addZoom( -0.05 * event.dy * speed )

    def mouseFocus(self, ev):
        pass

    def promptAndExit(self):
        if self.currentFile.modified:
            self.prompt('Exit', 'You have unsaved changes. Are you sure you want to exit the application?', 'Yes', 'No', self.stop)
        else:
            self.stop()

    def toggleProfiling(self):
        import profiler
        if self.actions.profiling.isChecked():
            profiler.start()
            log.notice('profiling started')
        else:
            profiler.stop()
            log.notice('profiling stopped')
            mh.changeTask('Utilities', 'Profile')

    def createActions(self):
        """
        Creates the actions toolbar with icon buttons.
        """

        def action(*args, **kwargs):
            return ExpandoAction()

        # Global actions (eg. keyboard shortcuts)
        toolbar = None

        # 1 - File toolbar
        # toolbar = self.file_toolbar = mh.addToolBar("File")

        self.actions.load      = action('load',      'Load',          self.goToLoad)
        self.actions.save      = action('save',      'Save',          self.doSave)
        self.actions.export    = action('export',    'Export',        self.goToExport)


        # 2 - Edit toolbar
        # toolbar = self.edit_toolbar = mh.addToolBar("Edit")

        self.actions.undo      = action('undo',      'Undo',          self.undo)
        self.actions.redo      = action('redo',      'Redo',          self.redo)
        self.actions.reset     = action('reset',     'Reset',         self.resetHuman)


        # 3 - View toolbar
        # toolbar = self.view_toolbar = mh.addToolBar("View")

        self.actions.smooth    = action('smooth',    'Smooth',        self.toggleSubdivision, toggle=True)
        self.actions.wireframe = action('wireframe', 'Wireframe',     self.toggleSolid, toggle=True)


        # 4 - Symmetry toolbar
        # toolbar = self.sym_toolbar = mh.addToolBar("Symmetry")

        self.actions.symmetryR = action('symm1', 'Symmmetry R>L',     self.symmetryLeft)
        self.actions.symmetryL = action('symm2', 'Symmmetry L>R',     self.symmetryRight)
        self.actions.symmetry  = action('symm',  'Symmmetry',         self.symmetry, toggle=True)


        # 5 - Camera toolbar
        # toolbar = self.camera_toolbar = mh.addToolBar("Camera")

        self.actions.front     = action('front',     'Front view',    self.frontView)
        self.actions.back      = action('back',      'Back view',     self.backView)
        self.actions.right     = action('right',     'Right view',    self.rightView)
        self.actions.left      = action('left',      'Left view',     self.leftView)
        self.actions.top       = action('top',       'Top view',      self.topView)
        self.actions.bottom    = action('bottom',    'Bottom view',   self.bottomView)
        self.actions.resetCam  = action('resetCam',  'Reset camera',  self.resetView)


        # 6 - Other toolbar
        # toolbar = self.other_toolbar = mh.addToolBar("Other")

        self.actions.grab      = action('grab',      'Grab screen',   self.grabScreen)
        self.actions.help      = action('help',      'Help',          self.goToHelp)


    def createShortcuts(self):
        for action, (modifier, key) in self.shortcuts.iteritems():
            action = getattr(self.actions, action, None)
            if action is not None:
                mh.setShortcut(modifier, key, action)

    def OnInit(self):
        mh.Application.OnInit(self)

        #[BAL 07/14/2013] work around focus bug in PyQt on OS X
        if sys.platform == 'darwin':
            G.app.mainwin.raise_()

        self.setLanguage("english")

        self.loadSettings()

        # Necessary because otherwise setting back to default theme causes crash
        self.setTheme("default")
        log.debug("Using Qt system style %s", self.getLookAndFeel())

        self.createActions()
        self.syncUndoRedo()
        self.createShortcuts()

    def run(self):
        self.start()

    def addExporter(self, exporter):
        self.getCategory('Files').getTaskByName('Export').addExporter(exporter)


class Expando(object):
    pass


class ExpandoAction(object):
    def setEnabled(enabled, second):
        return
    def setShortcut(shortcut, second):
        return        