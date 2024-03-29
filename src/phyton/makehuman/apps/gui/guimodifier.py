#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
Modifier taskview

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

Common taskview for managing modifier sliders
"""

import gui
import gui3d
import humanmodifier
#import modifierslider
import getpath
from core import G
import log
from collections import OrderedDict
import language

class ModifierTaskView(gui3d.TaskView):
    def __init__(self, category, name, label=None, saveName=None, cameraView=None):
        if label is None:
            label = name.capitalize()
        if saveName is None:
            saveName = name
        super(ModifierTaskView, self).__init__(category, name, label=label)

        self.saveName = saveName
        self.cameraFunc = _getCamFunc(cameraView)

        self.groupBoxes = OrderedDict()
        self.radioButtons = []
        self.sliders = []
        self.modifiers = {}

        self.categoryBox = self.addRightWidget(gui.GroupBox('Category'))
        self.groupBox = self.addLeftWidget(gui.StackedBox())

        self.showMacroStats = False

    def addSlider(self, sliderCategory, slider):
        # Get category groupbox
        categoryName = sliderCategory.capitalize()
        if categoryName not in self.groupBoxes:
            # Create box
            box = self.groupBox.addWidget(gui.GroupBox(categoryName))
            self.groupBoxes[categoryName] = box

            # Create radiobutton
            isFirstBox = len(self.radioButtons) == 0
            self.categoryBox.addWidget(GroupBoxRadioButton(self, self.radioButtons, categoryName, box, selected=isFirstBox))
            if isFirstBox:
                self.groupBox.showWidget(self.groupBoxes.values()[0])
        else:
            box = self.groupBoxes[categoryName]

        # Add slider to groupbox
        self.modifiers[slider.modifier.name.replace('|','-')] = slider.modifier # TODO this strange naming scheme is legacy for MHM compatibility
        box.addWidget(slider)
        self.sliders.append(slider)

        self.updateMacro()

    def getModifiers(self):
        return self.modifiers

    # TODO is this still needed?
    def updateMacro(self):
        for modifier in self.modifiers.itervalues():
            if isinstance(modifier, humanmodifier.MacroModifier):
                modifier.setValue(modifier.getValue())

    def onShow(self, event):
        gui3d.TaskView.onShow(self, event)

        # Only show macro statistics in status bar for Macro modeling task
        # (depends on the correct task name being defined)
        if self.showMacroStats:
            self.showMacroStatus()

        if G.app.settings.get('cameraAutoZoom', True):
            self.setCamera()

        self.syncSliders()

    def syncSliders(self):
        for slider in self.sliders:
            slider.update()

    def onHide(self, event):
        super(ModifierTaskView, self).onHide(event)

        if self.name == "Macro modelling":
            self.setStatus('')

    def onHumanChanged(self, event):
        # Update sliders to modifier values
        self.syncSliders()

        if event.change in ('reset', 'load', 'random'):
            self.updateMacro()

        if self.showMacroStats and self.isVisible():
            self.showMacroStatus()

    def loadHandler(self, human, values):
        if values[0] == 'status':
            return

        if values[0] == self.saveName:
            modifier = self.modifiers.get(values[1], None)
            if modifier:
                modifier.setValue(float(values[2]))

    def saveHandler(self, human, file):
        for name, modifier in self.modifiers.iteritems():
            if name is None:
                continue
            value = modifier.getValue()
            if value or isinstance(modifier, humanmodifier.MacroModifier):
                file.write('%s %s %f\n' % (self.saveName, name, value))

    def setCamera(self):
        if self.cameraFunc:
            f = getattr(G.app, self.cameraFunc)
            f()

    def showMacroStatus(self):
        human = G.app.selectedHuman

        if human.getGender() == 0.0:
            gender = G.app.getLanguageString('female')
        elif human.getGender() == 1.0:
            gender = G.app.getLanguageString('male')
        elif abs(human.getGender() - 0.5) < 0.01:
            gender = G.app.getLanguageString('neutral')
        else:
            gender = G.app.getLanguageString('%.2f%% female, %.2f%% male') % ((1.0 - human.getGender()) * 100, human.getGender() * 100)

        age = human.getAgeYears()
        muscle = (human.getMuscle() * 100.0)
        weight = (50 + (150 - 50) * human.getWeight())
        height = human.getHeightCm()
        if G.app.settings['units'] == 'metric':
            units = 'cm'
        else:
            units = 'in'
            height *= 0.393700787

        self.setStatus('Gender: %s, Age: %d, Muscle: %.2f%%, Weight: %.2f%%, Height: %.2f %s', gender, age, muscle, weight, height, units)

    def setStatus(self, format, *args):
        G.app.statusPersist(format, *args)


#class GroupBoxRadioButton(gui.RadioButton):
#    def __init__(self, task, group, label, groupBox, selected=False):
#        super(GroupBoxRadioButton, self).__init__(group, label, selected)
#        self.groupBox = groupBox
#        self.task = task

#    def onClicked(self, event):
#        self.task.groupBox.showWidget(self.groupBox)
#        #self.task.onSliderFocus(self.groupBox.children[0]) # TODO needed for measurement


def _getCamFunc(cameraName):
    if cameraName:
        if hasattr(gui3d.app, cameraName) and callable(getattr(gui3d.app, cameraName)):
            return cameraName

        return "set" + cameraName.upper()[0] + cameraName[1:]
    else:
        return None



def loadModifierTaskViews(filename, human, category, taskviewClass=None):
    """
    Create modifier task views from modifiersliders defined in slider definition
    file.
    """
    #import json

    #if not taskviewClass:
    #    taskviewClass = ModifierTaskView

    #data = json.load(open(filename, 'rb'), object_pairs_hook=OrderedDict)
    taskViews = []
    ## Create task views
    #for taskName, taskViewProps in data.items():
    #    sName = taskViewProps.get('saveName', None)
    #    label = taskViewProps.get('label', None)
    #    taskView = taskviewClass(category, taskName, label, sName)
    #    taskView.sortOrder = taskViewProps.get('sortOrder', None)
    #    taskView.showMacroStats = taskViewProps.get('showMacroStats', None)
    #    category.addTask(taskView)

    #    # Create sliders
    #    for sliderCategory, sliderDefs in taskViewProps['modifiers'].items():
    #        for sDef in sliderDefs:
    #            modifierName = sDef['mod']
    #            modifier = human.getModifier(modifierName)
    #            label = sDef.get('label', None)
    #            camFunc = _getCamFunc( sDef.get('cam', None) )
    #            slider = modifierslider.ModifierSlider(modifier, label=label, cameraView=camFunc)
    #            taskView.addSlider(sliderCategory, slider)

    #    if taskView.saveName is not None:
    #        gui3d.app.addLoadHandler(taskView.saveName, taskView.loadHandler)
    #        gui3d.app.addSaveHandler(taskView.saveHandler)

    #    taskViews.append(taskView)

    return taskViews
