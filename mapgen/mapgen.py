# beatmap generation
# file I/O
import json
import os
from tkinter import Tk, filedialog

# audio stuff
import numpy as np
from pydub import AudioSegment

from Impulse.mapgen import perlin
from Impulse.mapgen.onset_detect import superflux

#FIXME: crashes when filename ends with a '.'


def generate(persistence=0.5, octaves=6, f0=128):
    BEATMAPS = './Impulse/data/beatmaps/'
    FILE_EXT = '.mp3'
    JSON = '/beatmap.json'
    # get the file path from the user
    file_path, file_type = file_dialog()
    if not file_path or not file_type:
        return None
    # get the signal from the file
    fs, input_sig, audio_seg = file_to_ndarray(file_path, file_type)

    # If the user selected a stereo file (most likely), then store a mono version.
    mono_sig = stereo_to_mono(input_sig) if input_sig.ndim > 1 else input_sig

    # generate the onsets
    onsets = superflux(fs, to_float32(mono_sig))

    # generate the x and y locations of the beats
    n = len(onsets)
    xs = perlin.generate(n, fs, persistence, octaves, f0=f0)
    ys = perlin.generate(n, fs, persistence, octaves, f0=f0)

    basename = os.path.basename(file_path)
    folder_path, _ = os.path.splitext(basename)

    # create a new folder for this song, if it doesn't already exist.
    beatmap_path = BEATMAPS + folder_path
    try:
        os.mkdir(beatmap_path)
    except Exception as e:
        print(e)

    # write the file into the new folder, if it doesn't already exist.
    audio_path = f'{beatmap_path}/{basename}'
    if not os.path.isfile(audio_path):
        new_path, _ = os.path.splitext(audio_path)
        audio_seg._spawn(data=input_sig).export(new_path + FILE_EXT, FILE_EXT[1:])

    # write the beatmap data to a json file, overwriting if it already exists.
    json_path = beatmap_path + JSON
    beatmap = {'name': folder_path, 'onsets': onsets.tolist(), 'xs': xs.tolist(), 'ys': ys.tolist()}
    with open(json_path, 'w+') as outfile:
        json.dump(beatmap, outfile)

    return beatmap


def file_dialog():
    """Open a file dialog to prompt the user to select an audio file."""
    FILE_TYPES = [('Audio Files', '.mp3 .wav .ogg .flac .m4a .wma .ape')]
    Tk().withdraw()
    try:
        file_path = filedialog.askopenfilename(filetypes=FILE_TYPES)
    except FileNotFoundError:
        return None, None
    _, file_ext = os.path.splitext(file_path)
    return file_path, file_ext[1:]


def file_to_ndarray(file_path, file_type):
    """Given a path to a file, and its type (extension without '.'),
       Return a tuple conataining
       the sample rate, an nd numpy array containing PCM audio data,
       and an AudioSegment in audio_seg.
    """
    audio_seg = AudioSegment.from_file(file_path, file_type)
    output_sig = segment_to_ndarray(audio_seg)
    return audio_seg.frame_rate, output_sig, audio_seg


def segment_to_ndarray(audio_seg):
    """Given an AudioSegment, return a nd numpy array containing PCM audio data."""
    samples = np.array(audio_seg.get_array_of_samples())
    if audio_seg.channels == 1:
        return samples
    L_channel, R_channel = samples[::2], samples[1::2]
    return np.column_stack((L_channel, R_channel))


def stereo_to_mono(input_sig):
    """Given a stereo input signal, return the average of the L and R channels."""
    output_sig = input_sig[:, 0] + input_sig[:, 1]
    return perlin.peak_normalize(output_sig)


def to_float32(input_sig):
    return input_sig.astype(np.float32)