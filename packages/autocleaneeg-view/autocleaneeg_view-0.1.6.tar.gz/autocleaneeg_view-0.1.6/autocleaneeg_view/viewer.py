"""Module for loading and visualizing EEG files using MNE-QT Browser."""

import os
import sys
from pathlib import Path

import mne

from autocleaneeg_view import loaders

SUPPORTED_EXTENSIONS = loaders.SUPPORTED_EXTENSIONS


def _detect_extension(file_path: Path) -> str:
    """Detect registered extension, supporting multi-part suffixes.

    Chooses the longest matching registered extension for the filename.
    """
    name = file_path.name.lower()
    # Prefer longer patterns first (e.g., .xdat.json before .json)
    for key in sorted(loaders.READERS.keys(), key=len, reverse=True):
        if name.endswith(key):
            return key
    # Fallback to simple suffix
    return file_path.suffix.lower()


def validate_loader_output(eeg, file_path, ext):
    """Validate and post-process MNE loader outputs.

    Accepts Raw and Epochs-like objects. Applies global channel picking.
    """
    if eeg is None:
        raise RuntimeError(f"Loader for {ext} returned None for {file_path}")

    # Accept continuous (BaseRaw) or epoched (BaseEpochs); import guarded
    try:  # pragma: no cover - defensive import
        from mne.epochs import BaseEpochs  # type: ignore
    except Exception:  # pragma: no cover - defensive import
        BaseEpochs = tuple()  # type: ignore

    if isinstance(eeg, (mne.io.BaseRaw, BaseEpochs)):
        try:
            # Keep global picking consistent across loaders
            if hasattr(eeg, "pick_types"):
                eeg.pick_types(eeg=True, eog=True, ecg=True, misc=True)
        except Exception as pick_err:
            raise RuntimeError(
                f"Error picking channels in {file_path}: {pick_err}"
            ) from pick_err
        return eeg

    # Fallback: duck-typing for any future MNE objects
    if hasattr(eeg, "pick_types"):
        try:
            eeg.pick_types(eeg=True, eog=True, ecg=True, misc=True)
        except Exception as pick_err:
            raise RuntimeError(
                f"Error picking channels in {file_path}: {pick_err}"
            ) from pick_err
        return eeg

    raise TypeError(
        f"Loader for {ext} returned unsupported type {type(eeg)} for file {file_path}"
    )


def load_eeg_file(file_path, **kwargs):
    """Load an EEG file and return an MNE Raw or Epochs object.

    Parameters
    ----------
    file_path : str or Path
        Path to the EEG file to load. Supported extensions include ``.set``,
        ``.edf``, ``.bdf``, ``.vhdr`` (BrainVision), ``.fif`` (MNE), ``.raw``
        (EGI) and ``.gdf``. ``.mff`` files are also supported when the
        ``mne.io.read_raw_mff`` function is available.
    **kwargs : dict
        Additional keyword arguments passed to the loader (e.g., remap_channels for NeuroNexus).

    Returns
    -------
    raw : mne.io.Raw | mne.Epochs
        The loaded object.
    """
    file_path = Path(file_path)
    ext = _detect_extension(file_path)

    # Validate extension first so users get informative errors even if the
    # file does not exist.
    if ext not in loaders.READERS:
        exts = ", ".join(SUPPORTED_EXTENSIONS)
        raise ValueError(f"File must have one of {exts} extensions, got: {file_path}")

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Check if this is a NeuroNexus file to conditionally pass kwargs
    loader_func = loaders.READERS[ext]
    if ext in [".nnx", ".nex", ".xdat", ".xdat.json"]:
        # NeuroNexus loader accepts extra kwargs
        eeg = loader_func(file_path, **kwargs)
    else:
        # Other loaders don't accept extra kwargs
        eeg = loader_func(file_path)
    eeg = validate_loader_output(eeg, file_path, ext)
    return eeg


# Backwards compatibility
def load_set_file(file_path):
    """Alias for :func:`load_eeg_file` for legacy imports."""

    return load_eeg_file(file_path)


def view_eeg(eeg):
    """Display EEG data using MNE-QT Browser.

    Parameters
    ----------
    eeg : mne.io.Raw
        The Raw object to visualize.
    """

    if sys.platform == "darwin":  # pragma: no cover - platform specific
        os.environ.setdefault("QT_QPA_PLATFORM", "cocoa")

    # Launch the QT Browser with auto scaling
    fig = eeg.plot(block=True, scalings="auto")

    return fig
