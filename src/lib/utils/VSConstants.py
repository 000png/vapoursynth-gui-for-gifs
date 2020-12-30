#!./bin/python.exe
"""
Constants file for VapourSynth
"""

# available output render formats
OUTPUT_FORMATS = {
    '.mov': 'MOV File',
    '.mp4': 'MP4 File (Lossless)',
    '.png': 'PNG Sequence'
}

PREPROCESSOR_PLUGINS = {
    'haf': 'import havsfunc as haf'
}
PREPROCESSOR_CONFIG = {
    'None': None,
    'QTGMC 30 fast': 'Preset="Fast", FPSDivisor=2',
    'QTGMC 30 slow': 'Preset="Slower", FPSDivisor=2',
    'QTGMC 60 fast': 'Preset="Fast"',
    'QTGMC 60 slow': 'Preset="Slower"'
}

# descriptions from
# https://hackmd.io/@nibreon/vapoursynth-book/%2F%40nibreon%2Fdenoising
DENOISE_PLUGINS = {
    'mvs': 'import mvsfunc as mvs'
}
DENOISE_CONFIG = {
    'None': None,
    'KNLM': {
        'd': 0,             # number of past and future frames the filter uses for denoising the current frame; d=0 uses 1 frame, wile d=1 uses 3 frames, and so on
        'a': 6,             # radius of the search window; a=0 uses 1 pixel, a=1 uses 9, and so on
        's': 4,             # radius of the similarity neighbourhood window; impact on performance is low, therefore it depends on the nature of noise
        'h': 1.2,           # controls the strenght of the filtering; larger values removes more noise
        'channels': "YUV"   # the channel to use; this should be set to the video source format
    },
    'BM3D': {
        'sigma': 6.58,       # the strength of the filtering
        'radius1': 1,        # temporal radius (0 - spatial denoising / 1~16 - spatial-temporal denoising)
        'profile1': "fast",  # preset profile (fast, lc, np, high, very high)
        "matrix": "709"      # matrix (color matrix of input clips)
    }
}

SHARPEN_PLUGINS = {
    'fun': 'import G41Fun as fun'
}

SHARPEN_CONFIG = {
    'None': None,
    'FineSharp': {
        'sstr': 0.55
    }
}

DESCALE_PLUGINS = {
    'descale': 'import descale as descale'    
}
