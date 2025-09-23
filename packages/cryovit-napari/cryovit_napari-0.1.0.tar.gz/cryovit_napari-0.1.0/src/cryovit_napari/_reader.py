"""
This module is an example of a barebones numpy reader plugin for napari.

It implements the Reader specification, but your plugin may choose to
implement multiple readers or even other plugin contributions. see:
https://napari.org/stable/plugins/building_a_plugin/guides.html#readers
"""

from collections.abc import Callable
from pathlib import Path

import numpy as np
from cryovit.utils import RECOGNIZED_FILE_EXTS, load_data


def napari_get_reader(
    path: str | list[str],
) -> Callable[[str | list[str]], list[tuple[np.ndarray, dict, str]]] | None:
    """A basic implementation of a Reader contribution.

    Parameters
    ----------
    path : str or list of str
        Path to file, or list of paths.

    Returns
    -------
    function or None
        If the path is a recognized format, return a function that accepts the
        same path or list of paths, and returns a list of layer data tuples.
    """
    if isinstance(path, list):
        # reader plugins may be handed single path, or a list of paths.
        # only support tiff image stacks, and use first file to determine
        first_path = path[0]
        if first_path.endswith((".tif", ".tiff")):
            # if we have a list of tif files, we will treat them as a stack
            pass
        else:
            # otherwise, only consider the first file
            path = [path[0]]
    else:
        path = [path]

    # if we know we cannot read the file, we immediately return None.
    if any(Path(p).suffix.lower() not in RECOGNIZED_FILE_EXTS for p in path):
        return None

    # otherwise we return the *function* that can read ``path``.
    return cryovit_reader_function


def cryovit_reader_function(
    path: str | list[str],
) -> list[tuple[np.ndarray, dict, str]]:
    """Take a path or list of paths and return a list of LayerData tuples.

    Readers are expected to return data as a list of tuples, where each tuple
    is (data, [add_kwargs, [layer_type]]), "add_kwargs" and "layer_type" are
    both optional.

    Parameters
    ----------
    path : str or list of str
        Path to file, or list of paths.

    Returns
    -------
    layer_data : list of tuples
        A list of LayerData tuples where each tuple in the list contains
        (data, metadata, layer_type), where data is a numpy array, metadata is
        a dict of keyword arguments for the corresponding viewer.add_* method
        in napari, and layer_type is a lower-case string naming the type of
        layer. Both "meta", and "layer_type" are optional. napari will
        default to layer_type=="image" if not provided
    """
    # handle both a string and a list of strings
    paths = [path] if isinstance(path, str) else path
    # load all files into array
    arrays = [load_data(p)[0] for p in paths]
    # stack arrays into single array
    data = np.squeeze(np.stack(arrays))

    # optional kwargs for the corresponding viewer.add_* method
    add_kwargs = {
        "name": Path(paths[0]).stem,
        "metadata": {"source": paths[0] if len(paths) == 1 else paths},
    }

    # detect layer type based on the number of unique values in the array
    layer_type = "labels" if len(np.unique(data)) <= 20 else "image"
    if layer_type == "labels":
        data = data.astype(np.uint8)
    return [(data, add_kwargs, layer_type)]
