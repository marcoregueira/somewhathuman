import os

import mh
import gui
import gui3d

from getpath import pathToUnicode
import wavefront
import exportutils
from progress import Progress
import proxy

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

    def exportObj(self, filepath):
        from export_obj import ExporterOBJ, ObjConfig, mh2obj
        from core import G

        cfg = ObjConfig()
        cfg.setHuman(G.app.selectedHuman)
        cfg.useTPose          = False 
        cfg.feetOnGround      = True
        cfg.scale,cfg.unit    = (10.0, "centimeter")
        
        mh2obj.exportObj(filepath, cfg)


support = webfunctions()
