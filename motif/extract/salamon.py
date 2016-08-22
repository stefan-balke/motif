# -*- coding: utf-8 -*-
"""Salamon's method for extracting contours
"""
import csv
import numpy as np
import os

SALAMON_CONTOUR_STRING = "vamp_melodia-contours_melodia-contours_contoursall"


def salamon(audio_fpath, recompute=True, clean=True):
    """Compute contours as in Justin Salamon's melodia.
    This calls a vamp plugin in the background, which creates a csv file.
    The csv file is loaded into memory and the file is deleted, unless
    clean=False. When recompute=False, this will first look for an existing
    precomputed contour file and if successful will load it directly.

    Parameters
    ----------
    audio_fpath : str
        Path to audio file.
    recompute : bool, default=True
        If true, recompute contours from audio every time.
        If false, look for a pre-computed contour file.
    clean : bool, default=True
        If True, removes the contour file upon success.

    Returns
    -------
    c_numbers : np.array
        Array of contour numbers
    c_times : np.array
        Array of contour times
    c_freqs : np.array
        Array of contour frequencies
    c_sal : np.array
        Array of contour saliences
    """
    input_file_name = os.path.basename(audio_fpath)
    output_file_name = "{}_{}.csv".format(
        input_file_name.split('.')[0], SALAMON_CONTOUR_STRING
    )
    output_dir = os.path.dirname(audio_fpath)
    output_path = os.path.join(output_dir, output_file_name)
    if recompute or not os.path.exists(output_path):
        args = [
            "sonic-annotator", "-d", 
            "vamp:melodia-contours:melodia-contours:contoursall",
            "{}".format(audio_fpath), "-w", "csv", "--csv-force"
        ]
        os.system(' '.join(args))

    if not os.path.exists(output_path):
        raise IOError("Unable to find vamp output file {}".format(output_path))

    c_numbers, c_times, c_freqs, c_sal = load_contours(output_path)

    if clean:
        os.remove(output_path)

    return c_numbers, c_times, c_freqs, c_sal


def load_contours(fpath):
    """ Load contour data from vamp output csv file.

    Parameters
    ----------
    fpath : str
        Path to vamp output csv file.

    Returns
    -------
    index : np.array
        Array of contour numbers
    times : np.array
        Array of contour times
    freqs : np.array
        Array of contour frequencies
    contour_sal : np.array
        Array of contour saliences

    """
    index = []
    times = []
    freqs = []
    contour_sal = []
    with open(fpath, 'r') as fhandle:
        reader = csv.reader(fhandle, delimiter=',')
        contour_num = 0
        for row in reader:
            index.extend([contour_num]*len(row[14::3]))
            times.extend(row[14::3])
            freqs.extend(row[15::3])
            contour_sal.extend(row[16::3])
            contour_num += 1

    n_rows = np.min([
        len(index), len(times),
        len(freqs), len(contour_sal)
    ])

    index = np.array(index[:n_rows], dtype=int)
    times = np.array(times[:n_rows], dtype=float)
    freqs = np.array(freqs[:n_rows], dtype=float)
    contour_sal = np.array(contour_sal[:n_rows], dtype=float)

    non_nan_rows = ~(np.logical_or(
        np.logical_or(np.isnan(times), np.isnan(freqs)),
        np.isnan(contour_sal)))
    index = index[non_nan_rows]
    times = times[non_nan_rows]
    freqs = freqs[non_nan_rows]
    contour_sal = contour_sal[non_nan_rows]

    return index, times, freqs, contour_sal
