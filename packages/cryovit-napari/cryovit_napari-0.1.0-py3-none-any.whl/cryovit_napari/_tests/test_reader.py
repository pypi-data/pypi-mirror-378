import h5py
import mrcfile
import numpy as np
import tifffile

from cryovit_napari import napari_get_reader


def test_reader(tmp_path):
    """An example of how you might test your plugin."""

    # write some fake data using your supported file format
    my_test_file = str(tmp_path / "myfile.npy")
    original_data = np.random.rand(20, 20)
    np.save(my_test_file, original_data)

    # try to read it back in
    reader = napari_get_reader(my_test_file)
    assert callable(reader)

    # make sure we're delivering the right format
    layer_data_list = reader(my_test_file)
    assert isinstance(layer_data_list, list) and len(layer_data_list) > 0
    layer_data_tuple = layer_data_list[0]
    assert isinstance(layer_data_tuple, tuple) and len(layer_data_tuple) > 0

    # make sure it's the same as it started
    np.testing.assert_allclose(original_data, layer_data_tuple[0])


def test_reader_accepts_hdf(tmp_path):
    # create a fake hdf5 file
    my_test_file = str(tmp_path / "myfile.hdf")
    original_data = np.random.rand(20, 20)
    with h5py.File(my_test_file, "w") as f:
        f.create_dataset("data", data=original_data)

    # try to read it back in
    reader = napari_get_reader(my_test_file)
    assert callable(reader)

    # make sure we're delivering the right format
    layer_data_list = reader(my_test_file)
    assert isinstance(layer_data_list, list) and len(layer_data_list) > 0
    layer_data_tuple = layer_data_list[0]
    assert isinstance(layer_data_tuple, tuple) and len(layer_data_tuple) > 0

    # make sure it's the same as it started
    np.testing.assert_allclose(original_data, layer_data_tuple[0])


def test_reader_accepts_mrc(tmp_path):
    # create a fake mrc file
    my_test_file = str(tmp_path / "myfile.mrc")
    original_data = np.random.rand(20, 20)
    with mrcfile.new(my_test_file, overwrite=True) as f:
        f.set_data(original_data)

    # try to read it back in
    reader = napari_get_reader(my_test_file)
    assert callable(reader)

    # make sure we're delivering the right format
    layer_data_list = reader(my_test_file)
    assert isinstance(layer_data_list, list) and len(layer_data_list) > 0
    layer_data_tuple = layer_data_list[0]
    assert isinstance(layer_data_tuple, tuple) and len(layer_data_tuple) > 0

    # make sure it's the same as it started
    np.testing.assert_allclose(original_data, layer_data_tuple[0])


def test_reader_accepts_tiff(tmp_path):
    # create a fake tiff file
    my_test_file = str(tmp_path / "myfile.tiff")
    original_data = np.random.rand(20, 20)
    tifffile.imwrite(my_test_file, original_data)

    # try to read it back in
    reader = napari_get_reader(my_test_file)
    assert callable(reader)

    # make sure we're delivering the right format
    layer_data_list = reader(my_test_file)
    assert isinstance(layer_data_list, list) and len(layer_data_list) > 0
    layer_data_tuple = layer_data_list[0]
    assert isinstance(layer_data_tuple, tuple) and len(layer_data_tuple) > 0

    # make sure it's the same as it started
    np.testing.assert_allclose(original_data, layer_data_tuple[0])


def test_reader_accepts_tiff_stack(tmp_path):
    # create a fake tiff stack
    test_files = []
    original_data = np.random.rand(10, 20, 20)
    for i in range(10):
        test_file = str(tmp_path / f"myfile_stack{i}.tiff")
        tifffile.imwrite(test_file, original_data[i])
        test_files.append(test_file)

    # try to read it back in
    reader = napari_get_reader(test_files)
    assert callable(reader)

    # make sure we're delivering the right format
    layer_data_list = reader(test_files)
    assert isinstance(layer_data_list, list) and len(layer_data_list) > 0
    layer_data_tuple = layer_data_list[0]
    assert isinstance(layer_data_tuple, tuple) and len(layer_data_tuple) > 0

    # make sure it's the same as it started
    np.testing.assert_allclose(original_data, layer_data_tuple[0])


def test_get_reader_pass():
    reader = napari_get_reader("fake.file")
    assert reader is None
