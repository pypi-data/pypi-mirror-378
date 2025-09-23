import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import Any, ClassVar

import numpy as np
from cryovit.run import (
    run_dino,
    run_evaluation,
    run_inference,
    run_training,
)
from cryovit.types import ModelType
from cryovit.utils import load_labels, load_model
from loguru import logger
from napari.qt.threading import thread_worker
from psygnal import Signal, evented


## Monitored Data Classes
@dataclass
class Dataset:
    dset_file: Path
    data_files: list[Path]
    data_zlims: list[tuple[int, int]]
    label_files: list[Path]
    labels: list[str]
    val_data_files: list[Path] | None = None
    val_data_zlims: list[tuple[int, int]] | None = None
    val_label_files: list[Path] | None = None

    changed: ClassVar[Signal] = Signal()

    @property
    def data_as_tuple(self) -> tuple[list[Path], list[Path]]:
        return (self.data_files, self.val_data_files or [])

    @property
    def data_as_dict(self) -> dict[str, Any]:
        return {
            "dset_file": self.dset_file,
            "data_files": self.data_files,
            "data_zlims": self.data_zlims,
            "label_files": self.label_files,
            "labels": self.labels,
            "val_data_files": self.val_data_files,
            "val_data_zlims": self.val_data_zlims,
            "val_label_files": self.val_label_files,
        }

    def update(
        self,
        data_file: Path,
        label_file: Path,
        zlims: tuple[int, int],
        as_val: bool = False,
    ) -> None:
        if as_val:
            data_files = self.val_data_files if self.val_data_files else []
            label_files = self.val_label_files if self.val_label_files else []
            data_zlims = self.val_data_zlims if self.val_data_zlims else []
        else:
            data_files = self.data_files
            label_files = self.label_files
            data_zlims = self.data_zlims
        if data_file in data_files:
            idx = data_files.index(data_file)
            data_files[idx] = data_file
            label_files[idx] = label_file
            data_zlims[idx] = zlims
        else:
            data_files.append(data_file)
            label_files.append(label_file)
            data_zlims.append(zlims)
        if as_val:
            self.val_data_files = data_files
            self.val_label_files = label_files
            self.val_data_zlims = data_zlims
        else:
            self.data_files = data_files
            self.label_files = label_files
            self.data_zlims = data_zlims
        self.changed.emit()

    def remove(self, data_file: Path, as_val: bool = False) -> None:
        if as_val:
            if (
                self.val_data_files is None
                or self.val_label_files is None
                or self.val_data_zlims is None
            ):
                return
            if data_file in self.val_data_files:
                idx = self.val_data_files.index(data_file)
                self.val_data_files.pop(idx)
                self.val_label_files.pop(idx)
                self.val_data_zlims.pop(idx)
        else:
            if data_file in self.data_files:
                idx = self.data_files.index(data_file)
                self.data_files.pop(idx)
                self.label_files.pop(idx)
                self.data_zlims.pop(idx)
        self.changed.emit()


@evented
@dataclass
class CryovitModel:
    name: str
    model_type: ModelType
    label: str
    model_path: Path


## Dataset Management Functions
def create_dset(
    dset_file: Path,
    labels: list[str],
) -> Dataset:
    dset = Dataset(
        data_files=[],
        data_zlims=[],
        label_files=[],
        val_data_files=None,
        val_label_files=None,
        val_data_zlims=None,
        labels=labels,
        dset_file=dset_file,
    )
    save_dset(dset)
    return dset


def load_dset(dset_file: Path) -> Dataset | None:
    if not dset_file.exists():
        return None
    with open(dset_file, "rb") as f:
        dset_data = pickle.load(f)
        dset = Dataset(**dset_data)
    return dset


def save_dset(dset: Dataset) -> None:
    dset.dset_file.parent.mkdir(parents=True, exist_ok=True)
    with open(dset.dset_file, "wb") as f:
        pickle.dump(dset.data_as_dict, f)


## Model Management Functions
def load_cryovit_model(model_path: Path) -> CryovitModel | None:
    try:
        _, model_type, model_name, label = load_model(
            model_path, load_model=False
        )
    except FileNotFoundError:
        return None
    return CryovitModel(
        name=model_name,
        model_type=model_type,
        label=label,
        model_path=model_path,
    )


## Training Management Functions
def feature_extract_dset(
    dset: Dataset,
    result_dir: Path,
    batch_size: int,
    window_size: int | None = None,
) -> None:
    train_data = dset.data_files
    val_data = dset.val_data_files if dset.val_data_files else []
    all_data = train_data + val_data
    run_dino(
        all_data,
        result_dir=result_dir,
        batch_size=batch_size,
        window_size=window_size,
    )
    logger.info(f"Features saved to {result_dir}")


@thread_worker(start_thread=True)
def train_dset(
    dset: Dataset,
    model_name: str,
    model_type: ModelType,
    label_key: str,
    result_dir: Path,
    epochs: int = 50,
    log_training: bool = False,
    ckpt_path: Path | None = None,
) -> CryovitModel:
    train_data = dset.data_files
    train_labels = dset.label_files
    val_data = dset.val_data_files
    val_labels = dset.val_label_files
    labels = dset.labels
    model_path = run_training(
        train_data,
        train_labels,
        labels=labels,
        model_type=model_type,
        model_name=model_name,
        label_key=label_key,
        result_dir=result_dir,
        val_data=val_data,
        val_labels=val_labels,
        num_epochs=epochs,
        log_training=log_training,
        ckpt_path=ckpt_path,
    )
    model = CryovitModel(
        name=model_name,
        model_type=model_type,
        label=label_key,
        model_path=model_path,
    )
    logger.info(f"Model saved to {model_path}")
    return model


@thread_worker(start_thread=True)
def eval_dset(
    model: CryovitModel,
    dset: Dataset,
    result_dir: Path,
    visualize: bool = True,
) -> Path:
    test_data = dset.val_data_files if dset.val_data_files else dset.data_files
    test_labels = (
        dset.val_label_files if dset.val_label_files else dset.label_files
    )
    labels = dset.labels
    model_path = model.model_path
    result_path = run_evaluation(
        test_data,
        test_labels,
        labels=labels,
        model_path=model_path,
        result_dir=result_dir,
        visualize=visualize,
    )
    logger.info(f"Evaluation results saved to {result_path}")
    return result_path


## Inference Management Functions
def infer_image(
    data: Path,
    model: CryovitModel,
    temp_dir: Path,
    threshold: float,
) -> np.ndarray | None:
    result_paths = run_inference(
        [data], model.model_path, temp_dir, threshold=threshold
    )
    if not result_paths:
        return None
    label_key = f"{model.label}_preds"
    result_data = load_labels(
        result_paths[0], label_keys=[label_key], key=label_key
    )[label_key]
    return result_data
