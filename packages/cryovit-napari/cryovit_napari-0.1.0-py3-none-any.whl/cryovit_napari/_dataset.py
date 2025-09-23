"""Dataset management widgets for napari plugin."""

from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import tifffile as tiff
from loguru import logger
from magicgui.widgets import (
    CheckBox,
    Container,
    FunctionGui,
    PushButton,
    create_widget,
)
from qtpy.QtCore import Qt, Signal  # type: ignore
from qtpy.QtGui import QMouseEvent
from qtpy.QtWidgets import QTableWidget, QTableWidgetItem

from ._cryovit import (
    Dataset,
    create_dset,
    load_dset,
    save_dset,
)

if TYPE_CHECKING:
    import napari


def create_new_dset(dset_name: str, label_keys: list[str]) -> Dataset:
    """Create a new dataset file."""
    dset_file = Path.cwd() / f"{dset_name}.dset"
    return create_dset(dset_file, label_keys)


class DatasetCreator(FunctionGui):
    def __init__(self):
        super().__init__(
            create_new_dset,
            call_button="Create New Dataset",
            name="Create New Dataset",
            layout="vertical",
            param_options={
                "dset_name": {
                    "label": "Dataset Name",
                    "tooltip": "Name for the new dataset",
                },
                "label_keys": {
                    "label": "Labels",
                    "tooltip": "List of label names for segmentation classes",
                },
            },
        )


def load_existing_dset(dset_file: Path) -> Dataset | None:
    """Load an existing cryoVIT dataset file."""
    return load_dset(dset_file)


class DatasetLoader(FunctionGui):
    def __init__(self):
        super().__init__(
            load_existing_dset,
            call_button="Load Existing Dataset",
            name="Load Existing Dataset",
            layout="vertical",
            param_options={
                "dset_file": {
                    "label": "Dataset file",
                    "tooltip": "Path to an existing CryoVIT dataset file",
                    "filter": "DSET files (*.dset)",
                },
            },
        )


class DatasetTable(QTableWidget):  # type: ignore
    """Table to display dataset files."""

    rowOpened: Signal = Signal(int, bool)
    rowRemoved: Signal = Signal(int, bool)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setColumnCount(2)
        self.setRowCount(0)
        self.setHorizontalHeaderLabels(["Training Data", "Validation Data"])
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setSelectionBehavior(QTableWidget.SelectItems)
        self.setSelectionMode(QTableWidget.SingleSelection)
        self.setShowGrid(True)
        self.setCornerButtonEnabled(False)
        self.horizontalHeader().setSectionResizeMode(
            self.horizontalHeader().ResizeMode.Stretch
        )
        self.verticalHeader().setVisible(False)
        self.setTextElideMode(Qt.ElideLeft)

        # Additional parameters for magicgui compatibility
        self.name = "dataset_table"
        self.tooltip = "Right-click to remove entry, double-click to open."
        self.native = self

    def set_data(self, train_dset: list[Path], val_dset: list[Path]):
        """Set the table data from a dictionary of lists."""
        train_files = [str(p) for p in train_dset]
        val_files = [str(p) for p in val_dset]
        # Extend to same length
        if len(train_files) < len(val_files):
            train_files.extend([""] * (len(val_files) - len(train_files)))
        elif len(val_files) < len(train_files):
            val_files.extend([""] * (len(train_files) - len(val_files)))
        self.setRowCount(len(train_files))
        # fill table
        for row, path in enumerate(train_files):
            self.setItem(
                row,
                0,
                QTableWidgetItem(path, QTableWidgetItem.Type),
            )
        for row, path in enumerate(val_files):
            self.setItem(
                row,
                1,
                QTableWidgetItem(path, QTableWidgetItem.Type),
            )

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle right click events for removing rows."""
        if event.button() == Qt.RightButton:
            item = self.itemAt(event.pos())
            if item is not None and item.text() != "":
                row, col = item.row(), item.column()
                self.rowRemoved.emit(row, col == 1)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        """Handle double click events for opening data files."""
        item = self.itemAt(event.pos())
        if item is not None and item.text() != "":
            row, col = item.row(), item.column()
            self.rowOpened.emit(row, col == 1)


class DatasetInfo(Container):
    """Display information about the current dataset."""

    curr_dset: Dataset | None = None

    def __init__(self):
        super().__init__(label="Dataset Info", layout="vertical", labels=True)
        self._dset_name = create_widget(
            label="Dataset Name",
            annotation=str,
            value="",
            widget_type="Label",
            is_result=True,
        )
        self._labels = create_widget(
            label="Labels",
            annotation=str,
            value="",
            widget_type="Label",
            is_result=True,
        )
        self._num_train_data = create_widget(
            label="# of Training",
            annotation=int,
            value=0,
            widget_type="Label",
            is_result=True,
        )
        self._num_val_data = create_widget(
            label="# of Validation",
            annotation=int,
            value=0,
            widget_type="Label",
            is_result=True,
        )
        self._dset_sizes = Container(
            label="",
            widgets=[self._num_train_data, self._num_val_data],
            layout="horizontal",
            labels=True,
        )
        self._file_table = DatasetTable()
        self._export_button = PushButton(text="Export Dataset to .txt")

        self._table_container = Container(
            widgets=[],
            layout="vertical",
            scrollable=True,
            labels=False,
        )
        self._table_container.append(self._file_table)
        self.extend(
            [
                self._dset_name,
                self._labels,
                self._dset_sizes,
                self._table_container,
                self._export_button,
            ]
        )

        ## Connect events
        self._export_button.clicked.connect(self._export_dataset)

    def set_dataset(self, dset: Dataset | None):
        self.curr_dset = dset
        if self.curr_dset is not None:
            self.curr_dset.changed.connect(self._update_info)
            self._file_table.rowRemoved.connect(self._remove_data)
            self._file_table.rowOpened.connect(self._open_data)
        self._update_info()

    def _remove_data(self, index: int, as_val: bool):
        if self.curr_dset is None:
            return
        if as_val:
            if self.curr_dset.val_data_files is None:
                return
            data_file = self.curr_dset.val_data_files[index]
        else:
            data_file = self.curr_dset.data_files[index]
        self.curr_dset.remove(data_file, as_val)

    def _open_data(self, index: int, as_val: bool):
        if self.curr_dset is None:
            return
        if as_val:
            if (
                self.curr_dset.val_data_files is None
                or self.curr_dset.val_label_files is None
            ):
                return
            data_file = self.curr_dset.val_data_files[index]
            label_file = self.curr_dset.val_label_files[index]
        else:
            data_file = self.curr_dset.data_files[index]
            label_file = self.curr_dset.label_files[index]

        import napari

        viewer = napari.current_viewer()
        if viewer is None:
            logger.warning("No active napari viewer found.")
            return
        viewer.open(data_file, plugin="cryovit-napari")
        label_data = tiff.imread(label_file)
        label_data = np.where(
            label_data < 0, 0, label_data
        )  # remove masked region
        viewer.add_labels(label_data, name=Path(label_file).stem)

    def _export_dataset(self):
        if self.curr_dset is None:
            return
        export_path = self.curr_dset.dset_file.parent
        train_path = export_path / f"{self.curr_dset.dset_file.stem}_train.txt"
        label_path = (
            export_path / f"{self.curr_dset.dset_file.stem}_labels.txt"
        )
        val_path = export_path / f"{self.curr_dset.dset_file.stem}_val.txt"
        val_label_path = (
            export_path / f"{self.curr_dset.dset_file.stem}_val_labels.txt"
        )
        with open(train_path, "w") as f:
            for df in self.curr_dset.data_files:
                f.write(f"{df}\n")
        with open(label_path, "w") as f:
            for lf in self.curr_dset.label_files:
                f.write(f"{lf}\n")
        if self.curr_dset.val_data_files:
            with open(val_path, "w") as f:
                for df in self.curr_dset.val_data_files:
                    f.write(f"{df}\n")
        if self.curr_dset.val_label_files:
            with open(val_label_path, "w") as f:
                for lf in self.curr_dset.val_label_files:
                    f.write(f"{lf}\n")
        logger.info(f"Exported dataset information to {export_path}")

    def _update_info(self):
        if self.curr_dset is None:
            self._dset_name.value = ""  # type: ignore
            self._labels = ""  # type: ignore
            self._num_train_data.value = 0  # type: ignore
            self._num_val_data.value = 0  # type: ignore
            self._file_table.set_data([], [])
            return
        self._dset_name.value = self.curr_dset.dset_file.stem  # type: ignore
        self._labels.value = ", ".join(self.curr_dset.labels)  # type: ignore
        self._num_train_data.value = len(self.curr_dset.data_files)  # type: ignore
        self._num_val_data.value = len(self.curr_dset.val_data_files) if self.curr_dset.val_data_files else 0  # type: ignore
        self._file_table.set_data(*self.curr_dset.data_as_tuple)


class DatasetManager(Container):
    def __init__(self):
        super().__init__()
        # Add widgets and functionality for managing datasets
        self._dset_creator = DatasetCreator()
        self._dset_loader = DatasetLoader()
        self._dset_info = DatasetInfo()

        self._data_combo = create_widget(
            label="Data",
            value=None,
            annotation="napari.layers.Image",
        )
        self._label_combo = create_widget(
            label="Label",
            value=None,
            annotation="napari.layers.Labels",
        )
        self._zlim_tuple = create_widget(
            label="Z-slice Range",
            value=(None, None),
            annotation=tuple[int, int],
            options={
                "nullable": True,
                "tooltip": "Range of z-slices to load (start, end). If None, load all slices.",
            },
        )
        self._val_data_checkbox: CheckBox = CheckBox(
            value=False,
            text="Is Validation Data?",
            tooltip="Check if adding data for validation (not training)",
        )
        self._add_button: PushButton = PushButton(text="Add to Dataset")

        # Connect events
        self._data_combo.changed.connect(self._update_zlims)  # type: ignore
        self._dset_creator.called.connect(self._set_dset)
        self._dset_loader.called.connect(self._set_dset)
        self._add_button.clicked.connect(self._add_to_dset)

        # Append widgets to the container
        self._dset_load_container = Container(
            label="Add Data/Label Pair",
            widgets=[
                self._data_combo,
                self._label_combo,
                self._zlim_tuple,
                self._val_data_checkbox,
                self._add_button,
            ],
            layout="vertical",
            labels=True,
        )
        self.extend(
            [
                self._dset_creator,
                self._dset_loader,
                self._dset_info,
                self._dset_load_container,
            ]
        )

    @property
    def curr_dset(self) -> Dataset | None:
        return self._dset_info.curr_dset

    def _update_zlims(self, data_layer: "napari.layers.Image"):  # type: ignore
        if data_layer is None:
            return
        data_path = Path(data_layer.source.path)
        if self.curr_dset is None:
            self._zlim_tuple.value = (0, data_layer.data.shape[0])  # type: ignore
            return
        else:
            if data_path in self.curr_dset.data_files:
                self._zlim_tuple.value = self.curr_dset.data_zlims[self.curr_dset.data_files.index(data_path)]  # type: ignore
            elif (
                self.curr_dset.val_data_files
                and data_path in self.curr_dset.val_data_files
            ):
                self._zlim_tuple.value = self.curr_dset.val_data_zlims[self.curr_dset.val_data_files.index(data_path)]  # type: ignore
            else:
                self._zlim_tuple.value = (0, data_layer.data.shape[0])  # type: ignore

    def _set_dset(self, dset: Dataset | None):
        self._dset_info.set_dataset(dset)
        if dset is None:
            logger.warning("Failed to load dataset.")
            return

    def _save_label_data(self, label_layer: "napari.layers.Labels", file_path: Path, num_slices: int) -> Path:  # type: ignore
        """Save label layer data to a specified path as a tiff."""
        save_path = file_path.parent / (file_path.stem + "_labels.tiff")
        layer_data = label_layer.data
        label_data = np.zeros_like(layer_data, dtype=np.int8)
        if label_data.shape[0] != num_slices:
            logger.warning(
                f"Label layer has {label_data.shape[0]} slices, but data has {num_slices} slices. Adjusting to match data."
            )
            layer_data = layer_data[:num_slices]
            label_data = label_data[:num_slices]
        zmin = self._zlim_tuple.get_value()[0] if self._zlim_tuple.value is not None else 0  # type: ignore
        zmax = self._zlim_tuple.get_value()[1] if self._zlim_tuple.value is not None else label_data.shape[0]  # type: ignore
        if zmin > zmax:
            raise ValueError("Invalid z-slice range: start must be <= end.")
        label_data[zmin:zmax] = -1  # masked region
        nonzero_idxs = np.unique(np.argwhere(label_layer.data > 0)[:, 0])
        label_data[nonzero_idxs] = label_layer.data[
            nonzero_idxs
        ]  # add annotated labels
        tiff.imwrite(str(save_path), label_data.astype(np.int8))
        return save_path

    def _add_to_dset(self):
        if self.curr_dset is None:
            logger.warning("No dataset loaded.")
            return
        data = self._data_combo.value  # type: ignore
        label = self._label_combo.value  # type: ignore
        if data is None or label is None:
            logger.warning("No data or label layer selected.")
            return
        data_file = Path(data.source.path)
        label_file = self._save_label_data(label, data_file, len(data.data))
        zlims = self._zlim_tuple.get_value()  # type: ignore
        zlims = (zlims[0] or 0, zlims[1] or data.data.shape[0])
        as_val = self._val_data_checkbox.value
        self.curr_dset.update(data_file, label_file, zlims, as_val)
        save_dset(self.curr_dset)
        logger.info("Added data to dataset.")
