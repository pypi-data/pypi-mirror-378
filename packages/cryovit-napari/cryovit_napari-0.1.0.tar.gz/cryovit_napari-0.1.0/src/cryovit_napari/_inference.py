"""Inference GUI components for CryoVIT in Napari."""

from pathlib import Path
from typing import TYPE_CHECKING
from uuid import uuid4

from loguru import logger
from magicgui.widgets import (
    ComboBox,
    Container,
    FloatSlider,
    PushButton,
    create_widget,
)

from ._cryovit import (
    CryovitModel,
    Dataset,
    ModelType,
    feature_extract_dset,
    infer_image,
    load_cryovit_model,
)

if TYPE_CHECKING:
    import napari  # noqa: F401


class InferenceManager(Container):
    curr_model: CryovitModel | None = None

    def __init__(self):
        super().__init__()
        self._temp_dir_selector = create_widget(
            label="Temporary Directory",
            annotation=Path,
            value=Path.cwd(),
            options={
                "mode": "d",
                "tooltip": "Directory to save temporary intermediate files.",
            },
        )
        self._data_combo = create_widget(
            label="Data",
            value=None,
            annotation="napari.layers.Image",
        )
        self._model_dir_selector = create_widget(
            label="Model Directory",
            annotation=Path,
            value=None,
            options={
                "mode": "d",
                "tooltip": "Directory containing model files.",
            },
        )
        self._model_combo = ComboBox(
            label="Model",
            choices=[],
            tooltip="Select a model from the specified model directory.",
        )
        self._model_name = create_widget(
            label="Model Name",
            annotation=str,
            value="",
            is_result=True,
        )
        self._model_type = create_widget(
            label="Model Type",
            annotation=str,
            value="",
            is_result=True,
        )
        self._label_key = create_widget(
            label="Label Key",
            annotation=str,
            value="",
            is_result=True,
        )
        self._threshold_spinner = FloatSlider(
            label="Threshold",
            annotation=float,
            value=0.5,
            step=0.05,
            min=0.0,
            max=1.0,
            tooltip="Threshold for converting model probabilities to binary labels.",
        )
        self._infer_button = PushButton(text="Run Inference")

        # Connect events
        self._model_dir_selector.changed.connect(self._update_model_list)  # type: ignore
        self._model_combo.changed.connect(self._update_model_info)
        self._infer_button.clicked.connect(self._start_inference)

        # Append widgets to the container
        self._model_info_container = Container(
            label="Model Info",
            widgets=[
                self._model_name,
                self._model_type,
                self._label_key,
            ],
            layout="vertical",
            labels=True,
        )
        self._model_selector_container = Container(
            label="Select Model",
            widgets=[
                self._model_dir_selector,
                self._model_combo,
                self._model_info_container,
            ],
            layout="vertical",
            labels=True,
        )
        self.extend(
            [
                self._temp_dir_selector,
                self._data_combo,
                self._model_selector_container,
                self._threshold_spinner,
                self._infer_button,
            ]
        )

    def _update_model_list(self):
        model_dir = self._model_dir_selector.value  # type: ignore
        if model_dir is None or not model_dir.exists():
            self._model_combo.choices = []
            return
        model_files = list(model_dir.glob("*.model"))
        model_names = [f.stem for f in model_files]
        self._model_combo.choices = model_names
        if model_names:
            self._model_combo.value = model_names[0]

    def _update_model_info(self):
        if not self._model_combo.choices:
            self.curr_model = None
        else:
            model_name = self._model_combo.value
            model_dir = self._model_dir_selector.value  # type: ignore
            if model_dir and model_name:
                self.curr_model = load_cryovit_model(
                    model_dir / f"{model_name}.model"
                )
            else:
                self.curr_model = None
        model = self.curr_model
        if model is None:
            self._model_name.value = ""  # type: ignore
            self._model_type.value = ""  # type: ignore
            self._label_key.value = ""  # type: ignore
            return
        self._model_name.value = model.name  # type: ignore
        self._model_type.value = model.model_type.name  # type: ignore
        self._label_key.value = model.label  # type: ignore

    def _start_inference(self):
        # Setup temporary directory for storing DINO features
        temp_dir = self._temp_dir_selector.value  # type: ignore
        if temp_dir is None:
            temp_dir = Path.cwd()
        temp_dir = temp_dir / uuid4().hex
        temp_dir.mkdir()
        # Setup data and model
        data = self._data_combo.value  # type: ignore
        if data is None:
            logger.warning("No data layer selected.")
            return
        model = self.curr_model
        if model is None:
            logger.warning("No model selected.")
            return
        data_path = Path(data.source.path)
        temp_dset = Dataset(
            dset_file=temp_dir / "temp.dset",
            data_files=[data_path],
            data_zlims=[(0, data.data.shape[0])],
            label_files=[],
            labels=[],
        )
        threshold = self._threshold_spinner.value
        # Calculate DINO features
        if model.model_type == ModelType.CRYOVIT:
            feature_extract_dset(
                temp_dset,
                temp_dir,
                batch_size=64,
                window_size=None,
            )
            feature_file = temp_dir / f"{data_path.stem}.hdf"
            if not feature_file.exists():
                logger.error("Feature extraction failed.")
                return
            # Run inference
            results = infer_image(feature_file, model, temp_dir, threshold)
        else:
            results = infer_image(data_path, model, temp_dir, threshold)
        # Load result and add to viewer
        if results is None:
            logger.error("Inference failed.")
            return

        import napari

        viewer = napari.current_viewer()
        if viewer is None:
            logger.warning("No active napari viewer found.")
            return
        viewer.add_labels(results, name=f"{data.name}_pred")
        logger.info(
            f"Inference complete. Result added as layer {data.name}_pred."
        )
        # Clean up temporary directory
        for f in temp_dir.glob("*"):
            f.unlink()
        temp_dir.rmdir()
