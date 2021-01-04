#!./bin/python.exe
"""
Evaluate vs options from data
"""

def evaluateVapourSynthOptions(data):
    """ Evaluate VapourSynth options """
    script = evaluateTrimOptions(data.get('trim', None))
    script += evaluatePreprocessorOptions(data.get('preprocessor', None))
    script += "\nvideo = core.fmtc.resample(video, css=\"444\")\n"
    script += evaluateDescale(data.get('descale', None))
    script += evaluateDenoiseOptions(data.get('denoise', None))
    script += evaluateSharpenOptions(data.get('sharpen', None))
    script += evaluateCrop(data.get('crop', None))

    return script


def evaluateTrimOptions(trim):
    """ Evaluate trim options """
    if not trim:
        return ''

    args = trim['args']
    return f"""
video = core.std.Trim(video, first={args['start frame']}, last={args['end frame']})
"""


def evaluatePreprocessorOptions(preprocessor):
    """ Evaluate preprocessing """
    if not preprocessor:
        return ''

    return f"""
# using {preprocessor['type']}
video = haf.QTGMC(video, TFF=True, {preprocessor['args']})
"""


def evaluateDenoiseOptions(denoise):
    """ Evaluate denoise """
    if not denoise:
        return ''

    dType = denoise['type']
    args = denoise['args']
    result = f"\n# denoise option is {dType}"

    if dType == 'KNLM':
        result += f"""
video = core.knlm.KNLMeansCL(video, d={args['d']}, a={args['a']}, s={args['s']}, h={args['h']}, channels="{args['channels']}")
"""
    elif dType == 'BM3D':
        result += f"""
video = mvs.BM3D(video, sigma={args['sigma']}, radius1={args['radius1']}, profile1="{args['profile1']}", matrix="{args['matrix']}")
"""
    else:
        raise ValueError(f'Unrecognized denoise filter {dType}')

    return result


def evaluateSharpenOptions(sharpen):
    """ Evaluate sharpen """
    if not sharpen:
        return ''

    sType = sharpen['type']
    args = sharpen['args']
    result = f'\n# sharpen option is {sType}'

    if sType == 'FineSharp':
        result += f"""
video = fun.FineSharp(video, sstr={args['sstr']})
"""
    else:
        raise ValueError(f'Unrecognized sharpen filter {sType}')

    return result


def evaluateDescale(descale):
    """ Descale loaded as is """
    if not descale:
        return ''

    return '\n' + descale + '\n'


def evaluateCrop(crop):
    """ Crop loaded as is """
    if not crop:
        return ''

    return '\n' + crop + '\n'
