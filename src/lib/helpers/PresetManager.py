#!./bin/python.exe
"""
Saves and loads presets; currently "presets" are literaly just JSON dumps.
"""
import os
import json
import copy

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
WORK_DIR = os.path.join(SCRIPT_DIR, '../../../work')
HISTORY_PRESET = os.path.join(WORK_DIR, 'history.json')


class PresetManager():
    """ Preset loader class """
    def __init__(self, vsPanel, useHistory=True):
        """ Initializer """
        self._vsPanel = vsPanel
        if useHistory and os.path.isfile(HISTORY_PRESET):
            self.loadPreset(HISTORY_PRESET)

    def loadPreset(self, preset):
        """ Load preset from JSON file """
        if not os.path.isfile(preset):
            return

        data = {}
        with open(preset, 'r') as fh:
            data = json.load(fh)

        self._vsPanel.repopulateFields(data)

    def savePreset(self, data, filename=None, isHistory=False):
        """ Essentially the data object """
        if isHistory and not filename:
            filename = HISTORY_PRESET

        result = copy.deepcopy(data)
        if not isHistory:
            result.pop('video', None)

        with open(filename, 'w') as fh:
            json.dump(result, fh, indent=4, sort_keys=True)
