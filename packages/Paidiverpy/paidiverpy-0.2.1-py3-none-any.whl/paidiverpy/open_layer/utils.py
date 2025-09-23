"""Open Layer utils module."""

import logging
from io import BytesIO
from pathlib import Path
from typing import Any
import cv2
import dask.array as da
import numpy as np
import rawpy
from PIL import Image
from PIL.ExifTags import TAGS
from paidiverpy.models.open_params import SUPPORTED_EXIF_IMAGE_TYPES
from paidiverpy.models.open_params import SUPPORTED_OPENCV_IMAGE_TYPES
from paidiverpy.models.open_params import SUPPORTED_RAWPY_IMAGE_TYPES
from paidiverpy.utils.data import EIGHT_BITS
from paidiverpy.utils.data import NUM_CHANNELS_RGB
from paidiverpy.utils.data import NUM_CHANNELS_RGBA
from paidiverpy.utils.data import NUM_DIMENSIONS
from paidiverpy.utils.data import NUM_DIMENSIONS_GREY
from paidiverpy.utils.data import SIXTEEN_BITS
from paidiverpy.utils.exceptions import raise_value_error
from paidiverpy.utils.object_store import get_file_from_bucket

logger = logging.getLogger("paidiverpy")


def open_image_remote(
    img_path: str, image_type: str, image_open_args: dict[str, Any], **kwargs: dict[str, Any]
) -> tuple[np.ndarray[Any, Any] | da.core.Array, dict[str, Any], str]:
    """Open an image file.

    Args:
        img_path (str): The path to the image file
        image_type (str): The image type
        image_open_args (dict[str, Any]): The image open arguments
        **kwargs (dict[str, Any]): Additional keyword arguments. The following are supported:
            - storage_options (dict[str, Any]): The storage options for reading metadata file.

    Raises:
        ValueError: Failed to open the image

    Returns:
        tuple[np.ndarray[Any, Any] | da.core.Array, dict[str, Any], str]: The image data, the EXIF data, and the filename
    """
    exif = {}
    try:
        img_bytes = get_file_from_bucket(img_path, kwargs.get("storage_options"))
        if image_type in SUPPORTED_OPENCV_IMAGE_TYPES:
            img_array = np.frombuffer(img_bytes, image_open_args.get("dtype", np.uint8))
            img = cv2.imdecode(img_array, image_open_args.get("flags", cv2.IMREAD_UNCHANGED))
            exif = extract_exif_single(BytesIO(img_bytes), image_type=image_type, image_name=img_path.split("/")[-1])
        else:
            img = load_raw_image(BytesIO(img_bytes), image_type=image_type, image_open_args=image_open_args, remote=True)
            exif = extract_exif_single(BytesIO(img_bytes), image_type=image_type, image_name=img_path.split("/")[-1])
    except (FileNotFoundError, OSError, TypeError) as e:
        img = None
        logger.warning("Failed to open %s: %s", img_path, e)

    img = correct_image_dims_and_format(img, image_type=image_type)
    filename = str(img_path).split("/")[-1]
    return img, exif, filename


def open_image_local(
    img_path: str, image_type: str, image_open_args: dict[str, Any], **_kwargs: dict[str, Any]
) -> tuple[np.ndarray[Any, Any] | da.core.Array, dict[str, Any], str]:
    """Open an image file.

    Args:
        img_path (str): The path to the image file
        image_type (str): The image type
        image_open_args (dict): The image open arguments
        **_kwargs (dict): Additional keyword arguments. This is just a place holder for the code

    Raises:
        ValueError: Failed to open the image

    Returns:
        tuple[np.ndarray[Any, Any] | da.core.Array, dict, str]: The image data, the EXIF data, and the filename
    """
    exif = extract_exif_single(img_path=img_path, image_type=image_type)
    if image_type in SUPPORTED_OPENCV_IMAGE_TYPES:
        img = cv2.imread(str(img_path), image_open_args.get("flags", cv2.IMREAD_UNCHANGED))
    else:
        img = load_raw_image(img_path, image_type=image_type, image_open_args=image_open_args)
    img = correct_image_dims_and_format(img, image_type=image_type)
    filename = Path(img_path).name
    return img, exif, filename


def correct_image_dims_and_format(img: np.ndarray[Any, Any] | da.core.Array, image_type: str | None = None) -> np.ndarray[Any, Any] | da.core.Array:
    """Correct the image dimensions and format.

    Args:
        img (np.ndarray[Any, Any] | da.core.Array): The image data
        image_type (str | None): The image type

    Returns:
        np.ndarray[Any, Any] | da.core.Array: The corrected image data
    """
    if img is None:
        return img
    if image_type == "png":
        # this section was necessary because cv2.imread was not reading alpha channel for some png images in Windows
        if img.ndim == NUM_DIMENSIONS_GREY:  # grayscale
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGRA)
        elif img.shape[2] == NUM_CHANNELS_RGB:  # RGB
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGRA)
        if img.shape[2] != NUM_CHANNELS_RGBA:
            img = np.dstack((img, np.full(img.shape[:2], 255, dtype=img.dtype)))

    if img.ndim == NUM_DIMENSIONS_GREY:
        img = np.expand_dims(img, axis=-1)
    elif img.ndim == NUM_DIMENSIONS and img.shape[2] == NUM_CHANNELS_RGBA and image_type in SUPPORTED_OPENCV_IMAGE_TYPES:
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)
    elif img.ndim == NUM_DIMENSIONS and img.shape[2] == NUM_CHANNELS_RGB and image_type in SUPPORTED_OPENCV_IMAGE_TYPES:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img


def pad_image(img: np.ndarray[Any, Any] | da.core.Array, target_height: int, target_width: int) -> np.ndarray[Any, Any] | da.core.Array:
    """Pad the image to the target height and width.

    Args:
        img (np.ndarray[Any, Any] | da.core.Array): The image data
        target_height (int): The target height
        target_width (int): The target width

    Returns:
        np.ndarray[Any, Any] | da.core.Array: The padded image
    """
    height, width = img.shape[:2]
    pad_bottom = target_height - height
    pad_right = target_width - width
    pad_cfg = [(0, pad_bottom), (0, pad_right)]
    if img.ndim > NUM_DIMENSIONS_GREY:
        pad_cfg.append((0, 0))  # don't pad channels

    return np.pad(img, pad_cfg, mode="constant", constant_values=0)

    # mask = np.zeros((target_height, target_width), dtype=bool)
    # mask[:h, :w] = True

    # return padded, mask


def load_raw_image(
    img_path: str | BytesIO, image_type: str, image_open_args: dict[str, Any], remote: bool = False
) -> np.ndarray[Any, Any] | da.core.Array:
    """Load a raw image file.

    Args:
        img_path (str | BytesIO): The path to the image file or a BytesIO object
        image_type (str | None): The image type
        image_open_args (dict | None): The image open arguments
        remote (bool): Whether the image is remote or local. Defaults to False.

    Raises:
        ValueError: Failed to open the image

    Returns:
        np.ndarray[Any, Any]: The loaded image data
    """
    img = None
    img_bytes = img_path if remote else str(img_path)
    if image_type in SUPPORTED_RAWPY_IMAGE_TYPES:
        try:
            with rawpy.imread(img_bytes) as raw:
                img = raw.postprocess(**image_open_args)
        except rawpy.LibRawFileUnsupportedError as e:
            logger.warning("Failed to open %s using rawpy: %s. Trying using raw loader", img_path, e)
    else:
        try:
            img = load_raw_image_using_path_open(img_bytes, image_open_args, remote)
        except (FileNotFoundError, OSError, TypeError, ValueError, NotImplementedError) as e:
            logger.warning("Failed to open %s: %s", img_path, e)
    return img


def load_raw_image_using_path_open(
    img_path: str | BytesIO, image_open_args: dict[str, Any], remote: bool = False
) -> np.ndarray[Any, Any] | da.core.Array:
    """Load a raw image file using the open function.

    Args:
        img_path (str): The path to the image file or a BytesIO object
        image_open_args (dict | None): The image open arguments
        remote (bool): Whether the image is remote or local. Defaults to False.

    Raises:
        ValueError: Failed to open the image

    Returns:
        np.ndarray[Any, Any]: The loaded image data
    """
    width = image_open_args.get("width")
    height = image_open_args.get("height", 2048)
    bit_depth = image_open_args.get("bit_depth", 8)
    endianess = image_open_args.get("endianness")
    layout = image_open_args.get("layout")
    image_misc = image_open_args.get("image_misc", "").split(",")
    bayer_pattern = image_open_args.get("bayer_pattern")
    file_header_size = image_open_args.get("file_header_size")
    channels = image_open_args.get("channels")
    if remote:
        img_path.seek(file_header_size)
        raw_data = img_path.read()
    else:
        with Path(img_path).open("rb") as file:
            file.seek(file_header_size)
            raw_data = file.read()
    if bit_depth == EIGHT_BITS:
        img = np.frombuffer(raw_data, dtype=np.uint8)
        img = decode_8bpp(img, image_misc, width, height, channels, bayer_pattern)
    elif bit_depth == SIXTEEN_BITS:
        dtype = np.dtype("<u2") if endianess == "little" else np.dtype(">u2")
        img = np.frombuffer(raw_data, dtype=dtype)
        img = decode_16bpp(img, layout, width, height, endianess)
    else:
        msg = "Failed to load the image. Unsupported bit depth"
        raise ValueError(msg)
    if "vertical_flip" in image_misc:
        img = np.flipud(img)

    return img


def decode_8bpp(
    img: np.ndarray[Any, Any], image_misc: list[str], width: int, height: int, channels: int, bayer_pattern: str | None = None
) -> np.ndarray[Any, Any]:
    """Decode 8-bit per channel image data.

    Args:
        img (np.ndarray[Any, Any]): The image data.
        image_misc (list[str]): The image metadata.
        width (int): The width of the image.
        height (int): The height of the image.
        channels (int): The number of channels in the image.
        bayer_pattern (str | None): The Bayer pattern if the image is in Bayer format. Defaults to None.

    Returns:
        np.ndarray[Any, Any]: The decoded image data.
    """
    if "bayer" in image_misc:
        img = img.reshape((height, width))
        code = {"BG": cv2.COLOR_BayerBG2RGB, "GB": cv2.COLOR_BayerGB2RGB, "RG": cv2.COLOR_BayerRG2RGB, "GR": cv2.COLOR_BayerGR2RGB}[bayer_pattern]
        img = cv2.cvtColor(img, code)
    else:
        img = img.reshape((height, width, channels)) if channels > 1 else img.reshape((height, width))
    return img


def decode_16bpp(
    img: np.ndarray[Any, Any], layout: str = "5:6:5", width: int = 2448, height: int = 2048, endianess: str | None = None
) -> np.ndarray[Any, Any]:
    """Decode 16-bit packed RGB into 8-bit per channel RGB based on layout.

    Args:
        img (np.ndarray[Any, Any]): The packed 16-bit image data.
        layout (str): The layout of the packed data. Valid options include "5:6:5", "5:5:5", "5:5:6".
        width (int): The width of the image.
        height (int): The height of the image.
        endianess (bool): Whether to swap the byte order.

    Returns:
        np.ndarray[Any, Any]: The unpacked 8-bit RGB image data.
    """
    try:
        if endianess == "big":
            img = img.byteswap()
        img = img.reshape((height, width))
        if layout == "5:6:5":
            r = (img & 0xF800) >> 11
            g = (img & 0x07E0) >> 5
            b = img & 0x001F
            r = (r * 255) // 31
            g = (g * 255) // 63
            b = (b * 255) // 31
        elif layout == "5:5:5":
            r = (img & 0x7C00) >> 10
            g = (img & 0x03E0) >> 5
            b = img & 0x001F
            r = (r * 255) // 31
            g = (g * 255) // 31
            b = (b * 255) // 31
        elif layout == "5:5:6":
            r = (img & 0x7C00) >> 10
            g = (img & 0x03F0) >> 4
            b = img & 0x000F
            r = (r * 255) // 31
            g = (g * 255) // 63
            b = (b * 255) // 15
        elif layout == "6:5:5":
            r = (img & 0xFC00) >> 10
            g = (img & 0x03E0) >> 5
            b = img & 0x001F
            r = (r * 255) // 63
            g = (g * 255) // 31
            b = (b * 255) // 31
        else:
            msg = f"Unsupported layout: {layout}"
            raise_value_error(msg)
    except (KeyError, ValueError) as e:
        msg = f"Unsupported options. Error: {e}"
        raise ValueError(msg) from e
    return np.stack([r, g, b], axis=-1)


def extract_exif_single(img_path: str | BytesIO, image_type: str, image_name: str | None = None) -> dict[str, Any]:
    """Extract EXIF data from a single image file.

    Args:
        img_path (str | BytesIO): The path to the image file or a BytesIO object.
        image_type (str): The image type.
        image_name (str, optional): The name of the image file. Defaults to None.

    Returns:
        dict: The EXIF data.
    """
    exif: dict[str, Any] = {}
    if image_type and image_type not in SUPPORTED_EXIF_IMAGE_TYPES:
        logger.debug("Image type %s not supported for EXIF extraction", image_type)
        return exif
    try:
        img_pil = Image.open(img_path)
        exif_data = img_pil.getexif()
        if exif_data:
            if image_name:
                exif["filename"] = image_name
            elif isinstance(img_path, Path):
                exif["filename"] = img_path.name
            else:
                raise_value_error("Image name must be provided if img_path is not a Path object")
            for tag, value in exif_data.items():
                tag_name = TAGS.get(tag, tag)
                exif[str(tag_name)] = value
    except FileNotFoundError as e:
        logger.debug("Failed to open %s: %s", img_path, e)
    except OSError as e:
        logger.debug("Failed to open %s: %s", img_path, e)
    except Exception as e:  # noqa: BLE001
        logger.debug("Failed to extract EXIF data from %s: %s", img_path, e)
    return exif
