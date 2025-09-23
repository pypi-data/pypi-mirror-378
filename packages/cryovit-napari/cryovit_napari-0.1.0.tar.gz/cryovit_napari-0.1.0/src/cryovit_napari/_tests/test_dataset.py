from unittest.mock import patch

from cryovit_napari._dataset import create_new_dset, load_existing_dset

## create_new_dset tests


@patch("cryovit_napari._cryovit.create_dset")
def test_create_new_dset_runs_create_dset(mock_create_dset):
    # setup fake data
    dset_name = "mydset"
    dset_labels = ["A", "B", "C"]

    # create fake dataset
    create_new_dset(dset_name, dset_labels)

    # assert create_dset was called with correct args
    mock_create_dset.assert_called_once_with(dset_name, dset_labels)


## load_existing_dset tests


@patch("cryovit_napari._cryovit.load_dset")
def test_load_existing_dset_runs_loads_dset(tmp_path, mock_load_dset):
    # setup fake dset
    dset_file = tmp_path / "mydset.dset"

    # load fake dset
    load_existing_dset(dset_file)

    # assert load_dset was called
    mock_load_dset.assert_called_once_with(dset_file)


## DatasetManager tests


@patch("cryovit_napari._cryovit.create_dset")
def test_dset_manager_creates_dset(tmp_path, mock_create_dset):
    # setup fake data
    dset_name = "mydset"
    dset_labels = ["A", "B", "C"]

    # create fake dataset
    create_new_dset(dset_name, dset_labels)

    # assert create_dset was called with correct args
    mock_create_dset.assert_called_once_with(dset_name, dset_labels)


def test_dset_manager_loads_dset(tmp_path, mock_load_dset):
    # setup fake dset
    dset_file = tmp_path / "mydset.dset"

    # load fake dset
    load_existing_dset(dset_file)

    # assert load_dset was called
    mock_load_dset.assert_called_once_with(dset_file)


# def test_dset_manager_add_to_dset_adds_data_label_pair(tmp_path):
#     pass


# def test_dset_manager_add_to_dset_creates_label_file_when_no_source_path(
#     tmp_path,
# ):
#     pass


# def test_dset_manager_add_to_dset_adds_val_data_label_pair(tmp_path):
#     pass


# def test_dset_manager_add_to_dset_fails_on_data_label_mismatch(tmp_path):
#     pass


# def test_dset_manager_add_to_dset_fails_on_val_data_label_mismatch(tmp_path):
#     pass
