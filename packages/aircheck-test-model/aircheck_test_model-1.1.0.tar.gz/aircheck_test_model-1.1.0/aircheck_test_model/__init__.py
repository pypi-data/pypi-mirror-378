try:
    from . import _version

    __version__ = _version.__version__
except:  # noqa: E722
    __version__ = "0.0.0-dev"

from .model.main import main as train
from .model.main import screen_compound as screen

__all__ = ["train", "screen"]
