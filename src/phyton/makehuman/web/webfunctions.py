import os

import mh
import gui
import gui3d

from getpath import pathToUnicode
import wavefront
import exportutils
from progress import Progress
import proxy
import posemode

from core import G


class webfunctions(object):
    """description of class"""

    def __init__(self):
        pass

    def saveMHM(self, path):
        """Save the .mhm and the thumbnail to the selected save path."""
        path = pathToUnicode(os.path.normpath(path))

        savedir = os.path.dirname(path)
        if not os.path.exists(savedir):
            os.makedirs(savedir)

        name = os.path.splitext(os.path.basename(path))[0]

        # Save the model
        from core import G
        G.app.selectedHuman.save(path, name)
        #G.app.clearUndoRedo()

        G.app.status('Your model has been saved to %s.', path)

    def exportObj(self, filepath, age, weight, muscle, chest, waist, hip):
        from export_obj import ExporterOBJ, ObjConfig, mh2obj
        from core import G

        cfg = ObjConfig()
        cfg.setHuman(G.app.selectedHuman)
        import humanmodifier
        G.app.selectedHuman.setGender(0)

        G.app.selectedHuman.setAgeYears(age)

        if (age <= 12):
            chest= 0

        self.updateModelingParameter("breast/BreastSize", chest)
        
        self.updateModelingParameter("macrodetails-universal/Muscle", muscle)
        self.updateModelingParameter("macrodetails-universal/Weight", weight)

        self.updateModelingParameter("hip/hip-scale-vert-decr|incr", hip)
        self.updateModelingParameter("hip/hip-scale-horiz-decr|incr", hip)
        #self.updateModelingParameter("measure/measure-waist-decrease|increase'", waist)


        G.app.selectedHuman.applyAllTargets()

        # posemode.enterPoseMode()
        # posemode.loadMhpFile('data/poses/classic1/classic1.mhp')


        cfg.useTPose          = False 
        cfg.feetOnGround      = True
        cfg.useNormals       = True
        cfg.scale,cfg.unit    = (10.0, "centimeter")
        
        mh2obj.exportObj(filepath, cfg)
    
    def updateModelingParameter(self, parameterName, value):
        from core import G
        modifier = G.app.selectedHuman.getModifier(parameterName)
        modifier.setValue(value)
 

support = webfunctions()
