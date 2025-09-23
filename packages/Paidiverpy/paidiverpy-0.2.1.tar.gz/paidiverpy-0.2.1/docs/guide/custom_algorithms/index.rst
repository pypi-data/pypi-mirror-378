.. _guide_custom_algorithms:

Custom Algorithm
================

In `paidiverpy`, you have the flexibility to add your own algorithm to the suite of available algorithms. This guide walks you through the steps to create, implement, and configure a custom algorithm.

Creating a Custom Algorithm
---------------------------

To create a custom algorithm, start by creating a new file that contains a class inheriting from the `CustomLayer` class. This base class is located in the `paidiverpy.custom_layer.custom_layer` module, shown below:

.. literalinclude:: ../../../src/paidiverpy/custom_layer/custom_layer.py

Your custom algorithm class should extend `CustomLayer` and implement a new method to it with a chosen name (e.g., `multiply_data`, `process`, etc.). This method will contain the logic of your algorithm.
You can see below an example of a custom class that multiplies each image by a parameter:

.. code-block:: python

    from paidiverpy.custom_layer.custom_layer import CustomLayer

    class MyCustomClass(CustomLayer):

        @staticmethod
        def multiply_data(image_data, params, **kwargs):
            return image_data * params.some_param


Your method can be a static method or an instance method, depending on he processing type:

**Image-level processing** (default):

- It needs to be a `@staticmethod`.
- It processes one image at a time.
- It receives the following parameters:
  - `image_data`: a single NumPy or Dask array with shape `(height, width, channels)`
  - `params`: an object with algorithm-specific parameters
  - `kwargs`: a dictionary that contains the metadata of the whole dataset and the filename of the current image being processed (kwargs["metadata"] and kwargs["filename"])
- **Returns**: a NumPy or Dask array with the processed image.

**Dataset-level processing**:

- It can be a regular instance method (without the `@staticmethod` decorator).
- It processes the entire dataset at once.
- It receives the following parameters:
  - `images`: an `xarray.Dataset` containing all images in the dataset. The images are represented as a variable named `images` within the dataset, with dimensions `(filename, y, x, band)`.
  - `params`: an object with algorithm-specific parameters
- **Returns**: an updated `xarray.Dataset` with the processed images and dimensions `(filename, y, x, band)`.
- You can access the metadata by using `self.get_metadata()`.
- In this case, if you are working with images with different sizes, you will need to handle the padding and cropping of images manually. Please refer to the :ref:`images_layer` section for more details.

.. admonition:: Important

   - Each `image_data` (or `image_data[i]`) is a 3D array, even for grayscale images (singleton channel dimension).
   - Multi-channel images follow RGB or RGBA conventions.

.. note::

   If your algorithm requires external libraries, import them directly within the file containing your custom class.


Configuration File
------------------

After creating your custom algorithm, specify it in the configuration file as a pipeline step. Below is an example configuration:

.. code-block:: text

  general:
    # General configurations here

  steps:
    # Steps before the custom algorithm

    - custom:
        name: "my_custom_algorithm"   # Name of the algorithm and the method in the class
        file_path: "/path/to/file.py" # Path to the module implementing the custom algorithm
        class_name: "MyCustomClass"        # Name of the custom algorithm class
        dependencies: "marimba,scikit-learn==0.24.2"
        dependencies_path: "/path/to/requirements.txt"  # Optional path to a requirements file
        params:                       # Algorithm parameters
          some_param: 10
          another_param: 0.5

    # Steps following the custom algorithm

In this example:

* The custom algorithm, named `my_custom_algorithm`, is defined in the file `/path/to/file.py` and implemented in the class `MyCustomClass`.
* The algorithm accepts parameters such as `some_param` (set to 10) and `another_param` (set to 0.5).
* External dependencies are declared in two ways:

  * As a comma-separated string in the `dependencies` field (e.g., `marimba`, `scikit-learn==0.24.2`).
  * Via a `requirements.txt` file specified with the `dependencies_path` field.
* There is no preferred method for declaring dependencies—either or both can be used. If both are provided, **both sets** will be installed before executing the algorithm.
* Since the `processing_type` parameter is not explicitly set, the algorithm defaults to **image-level processing**, meaning each image will be processed individually.

.. admonition:: Important

  You only need to specify external packages as dependencies; packages already available in your environment or included with `paidiverpy` do not need to be listed and will be ignored.

Dataset-level Processing
-------------------------

If your custom algorithm processes the entire dataset at once, you can set the `processing_type` parameter to `dataset` in the configuration file.
This will ensure that the `process` method receives a list of images instead of a single image. Here's how to configure it:

.. code-block:: text

  general:
    # General configurations here

  steps:
    # Steps before the custom algorithm

    - custom:
        name: "my_custom_algorithm"
        file_path: "/path/to/file.py"
        class_name: "MyCustomClass"
        dependencies: "marimba,scikit-learn==0.24.2"
        dependencies_path: "/path/to/requirements.txt"
        processing_type: "dataset"  # Set to 'dataset' for dataset-level processing
        params:
          some_param: 10
          another_param: 0.5

    # Steps following the custom algorithm



Real Example
------------

For a more concrete example, consider the following code snippet (available in `examples/custom_algorithms files <https://github.com/paidiver/paidiverpy/blob/main/src/paidiverpy/custom_layer/_custom_algorithm_example.py>`_ of the `paidiverpy` package):

.. literalinclude:: ../../../src/paidiverpy/custom_layer/_custom_algorithm_example.py

In this example, the custom algorithm accepts an image and a `feature_range` parameter. Using `sklearn`'s `MinMaxScaler`, it normalizes the image data within the specified range, then returns the processed data.

The corresponding configuration file might look like this:

.. code-block:: text

  general:
    # General configurations here

  steps:
    # Steps before the custom algorithm

    - custom:
        name: "min_max_data"
        file_path: "/path/to/file.py"
        class_name: "MyCustomClass"
        dependencies:
          - "scikit-learn"
        params:
          feature_range: (0, 1)

    # Steps following the custom algorithm

In this setup:

* The custom algorithm `min_max_data` resides in `/path/to/file.py`, with the class name `MyCustomClass`.
* The algorithm has one parameter, `feature_range`, set to `(0, 1)`.
* The dependency `scikit-learn` is installed before the algorithm runs.

To execute, run your application with the configuration file above, and the custom algorithm will be applied accordingly.

Example configuration files for custom algorithms can be found in the `example/config_files <https://github.com/paidiver/paidiverpy/tree/main/examples/config_files>`_ directory of the repository. You can also run an example notebook with a custom algorithm by exploring the :ref:`gallery` section.

Run in Docker
-------------

To pass the custom algorithm to the Docker container, you need to mount the custom algorithm file to the container. The following steps show how to run the container with a custom algorithm:

.. code-block:: text

  docker run --rm \
  -v <INPUT_PATH>:/app/input/ \
  -v <OUTPUT_PATH>:/app/output/ \
  -v <FULL_PATH_OF_CONFIGURATION_FILE_WITHOUT_FILENAME>:/app/config_files \
  -v <METADATA_PATH_WITHOUT_FILENAME>:/app/metadata/ \
  -v <FULL_PATH_OF_CUSTOM_ALGORITHM_FILE_AND_REQUIREMENTS_FILE>:/app/custom_algorithms \
  paidiverpy \
  paidiverpy -c /app/examples/config_files/<CONFIGURATION_FILE_FILENAME>

In this command:

* `<INPUT_PATH>`: The input path defined in your configuration file, where the input images are located.
* `<OUTPUT_PATH>`: The output path defined in your configuration file.
* `<FULL_PATH_OF_CONFIGURATION_FILE_WITHOUT_FILENAME>`: The local directory of your configuration file.
* `<CONFIGURATION_FILE_FILENAME>`: The name of the configuration file.
* `<FULL_PATH_OF_CUSTOM_ALGORITHM_FILE_AND_REQUIREMENTS_FILE>`: The local directory of your custom algorithm file and requirements file (if any).

The output images will be saved to the specified `output_path`.
