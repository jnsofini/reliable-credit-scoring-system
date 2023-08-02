"""Module for loading and saving data to various formats."""

import json
from pathlib import Path
from omegaconf import DictConfig


def set_destination_directory(
    cfg: DictConfig, pred_stage: str, stage: str, logger
) -> list[Path]:
    """Prepares the directories.

    Args:
        cfg (DictConfig): Configuration data

    Returns:
        list[Path]: List of directories
    """
    root_dir = Path(cfg.data.source).joinpath(cfg.data.test_dir)
    predecessor_dir = root_dir.joinpath(pred_stage)
    destination_dir = root_dir.joinpath(stage)
    destination_dir.mkdir(parents=True, exist_ok=True)
    logger(f"Working dir is:  {destination_dir}")

    return predecessor_dir, destination_dir, root_dir


def save_dict_to_json(data, filename, **kwargs):
    """Save data to json file."""
    with open(file=filename, mode="w", encoding="utf-8") as fhandle:
        json.dump(data, fhandle, indent=6, **kwargs)


def read_json(path):
    """Reads json data to a python dict."""
    with open(file=path, mode="r", encoding="utf-8") as fhandle:
        data = json.load(fhandle)
    return data
