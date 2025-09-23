try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"


from ._dataset import DatasetManager
from ._inference import InferenceManager
from ._reader import napari_get_reader
from ._training import TrainingManager

__all__ = (
    "napari_get_reader",
    "DatasetManager",
    "TrainingManager",
    "InferenceManager",
)
