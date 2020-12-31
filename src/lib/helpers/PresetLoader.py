#!./bin/python.exe
"""
Saves and loads presets; currently "presets" are literaly just JSON dumps.
"""
import os
import json
import copy

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
RESOURCES_DIR = os.path.join(SCRIPT_DIR, '../resources')
HISTORY_PRESET = os.path.join(RESOURCES_DIR, 'history.json')


class PresetLoader():
    """ Preset loader class """
    def __init__(self, VSPanel, useHistory=True):
        """ Initializer """
        self._VSPanel = VSPanel
        if useHistory and os.path.isfile(HISTORY_PRESET):
            self.loadPreset(HISTORY_PRESET)

    def loadPreset(self, preset):
        """ Load preset from JSON file """
        data = {}
        with open(preset, 'r') as fh:
            data = json.load(fh)

        vsPanel.repopulateFields(data)

    def savePreset(self, data, filename=HISTORY_PRESET):
        """
        Essentially the data object but remove things that can't
        be set as a preset, e.g. video data + resizing options
        """
        result = copy.deepcopy(data)
        for item in ['video', 'descale', 'crop']:
            result.pop(item)

        result['plugins'].pop('descale')

        with open(filename, 'w') as fh:
            json.dumps(result, indent=4, sort_keys=True)