"""Training and evaluation GUI components for CryoVIT in Napari."""

from pathlib import Path

from loguru import logger
from magicgui.widgets import (
    CheckBox,
    ComboBox,
    Container,
    FunctionGui,
    PushButton,
    create_widget,
)

from ._cryovit import (
    CryovitModel,
    Dataset,
    ModelType,
    eval_dset,
    feature_extract_dset,
    load_cryovit_model,
    save_dset,
    train_dset,
)
from ._dataset import load_existing_dset


def feature_extraction(
    dset_file: Path,
    result_dir: Path,
    batch_size: int = 64,
    window_size: int | None = None,
) -> Dataset:
    """Extract features from the dataset using DINO, and save features in a new dataset."""
    dset = load_existing_dset(dset_file)
    if dset is None:
        raise FileNotFoundError(f"Dataset file {dset_file} not found.")
    feature_extract_dset(
        dset, result_dir, batch_size, window_size if window_size else None
    )
    data_files = dset.data_files
    val_data_files = dset.val_data_files or []
    new_data_files = [result_dir / f"{f.stem}.hdf" for f in data_files]
    new_val_files = [result_dir / f"{f.stem}.hdf" for f in val_data_files]
    new_dset_file = (
        dset.dset_file.parent / f"{dset.dset_file.stem}_features.dset"
    )
    new_dset = Dataset(
        data_files=new_data_files,
        data_zlims=dset.data_zlims,
        label_files=dset.label_files,
        val_data_files=new_val_files if new_val_files else None,
        val_label_files=dset.val_label_files,
        val_data_zlims=dset.val_data_zlims,
        labels=dset.labels,
        dset_file=new_dset_file,
    )
    save_dset(new_dset)
    return new_dset


class TrainingManager(Container):
    curr_dataset: Dataset | None = None
    curr_model: CryovitModel | None = None

    def __init__(self):
        super().__init__()
        self._feature_extractor = FunctionGui(
            feature_extraction,
            call_button="Calculate Image Features",
            name="Feature Extraction",
            layout="vertical",
            param_options={
                "dset_file": {
                    "label": "Dataset file",
                    "tooltip": "Path to an existing CryoVIT dataset file",
                    "filter": "DSET files (*.dset)",
                },
                "result_dir": {
                    "label": "Feature Directory",
                    "mode": "d",
                    "tooltip": "Directory to save the extracted features",
                },
                "window_size": {
                    "tooltip": "Size of the window to use for feature extraction. If 0, uses the default window size (630)."
                },
            },
        )
        self._dset_loader = FunctionGui(
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
        # Training parameters
        self._model_name_input = create_widget(
            label="Model Name", annotation=str, value="my_model"
        )
        self._model_type_combo = ComboBox(
            label="Model Type",
            choices=[mt.name for mt in ModelType],
            value=ModelType.CRYOVIT.name,
        )
        self._label_key_combo = ComboBox(label="Label Key", choices=[])
        self._train_result_dir_selector = create_widget(
            label="Result Model Directory",
            annotation=Path,
            value=None,
            options={"mode": "d"},
        )
        self._epoch_spinner = create_widget(
            label="Epochs", annotation=int, value=50
        )
        self._ckpt_path_selector = create_widget(
            label="Checkpoint Path",
            annotation=Path,
            value=None,
            options={
                "mode": "r",
                "filter": "Model files (*.model)",
            },
        )
        self._log_training_checkbox = CheckBox(
            value=False,
            text="Log Training",
            tooltip="Log training details to TensorBoard",
        )
        self._train_button = PushButton(text="Start Training")

        # Eval parameters
        self._model_result = create_widget(
            label="Trained Model",
            annotation=Path,
            value=None,
            options={"mode": "r", "filter": "Model files (*.model)"},
        )
        self._eval_result_dir_selector = create_widget(
            label="Evaluation Result Directory",
            annotation=Path,
            value=None,
            options={"mode": "d"},
        )
        self._eval_visualize = CheckBox(
            value=True,
            text="Visualize Results",
            tooltip="Write evaluation segmentations to .hdf files in the result directory.",
        )
        self._eval_button = PushButton(text="Start Evaluation")

        # Connect events
        self._feature_extractor.called.connect(self._set_dset)
        self._dset_loader.called.connect(self._set_dset)
        self._train_button.clicked.connect(self._start_training)
        self._eval_button.clicked.connect(self._start_eval)

        # Append widgets to the container
        self._train_container = Container(
            label="Training Parameters",
            widgets=[
                self._model_name_input,
                self._model_type_combo,
                self._label_key_combo,
                self._train_result_dir_selector,
                self._epoch_spinner,
                self._ckpt_path_selector,
                self._log_training_checkbox,
                self._train_button,
            ],
            layout="vertical",
            labels=True,
        )
        self._eval_container = Container(
            label="Evaluation Parameters",
            widgets=[
                self._model_result,
                self._eval_result_dir_selector,
                self._eval_visualize,
                self._eval_button,
            ],
            layout="vertical",
            labels=True,
        )
        self.extend(
            [
                self._feature_extractor,
                self._dset_loader,
                self._train_container,
                self._eval_container,
            ]
        )

    def _set_dset(self, dset: Dataset):
        self.curr_dataset = dset
        self._dset_loader.dset_file.value = dset.dset_file
        self._label_key_combo.choices = dset.labels
        if dset.labels:
            self._label_key_combo.value = dset.labels[0]

    def _start_training(self):
        dset = self.curr_dataset
        if dset is None:
            logger.warning("No dataset loaded.")
            return
        model_name = self._model_name_input.value  # type: ignore
        model_type_str = self._model_type_combo.value
        model_type = ModelType[model_type_str]
        label_key = self._label_key_combo.value
        result_dir = self._train_result_dir_selector.value  # type: ignore
        epochs = self._epoch_spinner.value  # type: ignore
        log_training = self._log_training_checkbox.value
        ckpt_path = self._ckpt_path_selector.value  # type: ignore
        if (
            model_name is None
            or model_type is None
            or label_key is None
            or result_dir is None
        ):
            logger.warning("Please fill in all training parameters.")
            return
        train_worker = train_dset(
            dset,
            model_name=model_name,
            model_type=model_type,
            label_key=label_key,
            result_dir=result_dir,
            epochs=epochs,
            log_training=log_training,
            ckpt_path=ckpt_path,
        )
        train_worker.returned.connect(self._train_complete)

    def _train_complete(self, model: CryovitModel):
        self.curr_model = model
        self._model_result.value = model.model_path  # type: ignore
        logger.info(f"Training complete. Model saved at {model.model_path}")

    def _start_eval(self):
        dset = self.curr_dataset
        if dset is None:
            logger.warning("No dataset loaded.")
            return
        model_path = self._model_result.value  # type: ignore
        model = load_cryovit_model(model_path)
        if model is None:
            logger.warning("No model found.")
            return
        result_dir = self._eval_result_dir_selector.value  # type: ignore
        visualize = self._eval_visualize.value
        eval_worker = eval_dset(
            model=model, dset=dset, result_dir=result_dir, visualize=visualize
        )
        eval_worker.returned.connect(self._eval_complete)

    def _eval_complete(self, result_path: Path):
        logger.info(f"Evaluation complete. Results saved at {result_path}")
