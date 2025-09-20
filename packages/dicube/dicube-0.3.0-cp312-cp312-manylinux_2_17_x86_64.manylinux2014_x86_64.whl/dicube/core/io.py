import struct
import warnings
import os
from typing import Optional, Union

import numpy as np
from spacetransformer import Space, get_space_from_nifti

from ..dicom import (
    CommonTags,
    DicomMeta,
    DicomStatus,
    SortMethod,
    get_dicom_status,
    get_space_from_DicomMeta,
)
from ..dicom.dicom_meta import _parse_dicom_dir
from ..dicom.dicom_builder import DicomBuilder, save_dicom
from ..storage.dcb_file import DcbSFile, DcbFile, DcbAFile, DcbLFile
from ..storage.pixel_utils import derive_pixel_header_from_array, determine_optimal_nifti_dtype
from .pixel_header import PixelDataHeader

from ..validation import (
    validate_not_none,
    validate_file_exists,
    validate_folder_exists,
    validate_parameter_type,
    validate_string_not_empty,
    validate_numeric_range
)
from ..exceptions import (
    InvalidCubeFileError,
    CodecError,
    MetaDataError,
    DataConsistencyError
)
import os


class DicomCubeImageIO:
    """Static I/O utility class responsible for DicomCubeImage file operations.
    
    Responsibilities:
    - Provides unified file I/O interface
    - Automatically detects file formats
    - Handles conversion between various file formats
    """
    

    
    @staticmethod
    def save(
        image: "DicomCubeImage",
        file_path: str,
        file_type: str = "s",
    ) -> None:
        """Save DicomCubeImage to a file.
        
        Args:
            image (DicomCubeImage): The DicomCubeImage object to save.
            file_path (str): Output file path.
            file_type (str): File type, "s" (speed priority), "a" (compression priority), 
                             or "l" (lossy compression). Defaults to "s".
            
        Raises:
            InvalidCubeFileError: If the file_type is not supported.
        """
        # Validate required parameters
        validate_not_none(image, "image", "save operation", DataConsistencyError)
        validate_string_not_empty(file_path, "file_path", "save operation", InvalidCubeFileError)
        
        # Validate file_type parameter
        if file_type not in ("s", "a", "l"):
            raise InvalidCubeFileError(
                f"Unsupported file type: {file_type}",
                context="save operation",
                details={"file_type": file_type, "supported_types": ["s", "a", "l"]},
                suggestion="Use 's' for speed priority, 'a' for compression priority, or 'l' for lossy compression"
            )
        
        try:
            # Choose appropriate writer based on file type
            # The writer will automatically ensure correct file extension
            if file_type == "s":
                writer = DcbSFile(file_path, mode="w")
            elif file_type == "a":
                writer = DcbAFile(file_path, mode="w")
            elif file_type == "l":
                writer = DcbLFile(file_path, mode="w")
            
            # Update file_path to the corrected path from writer
            file_path = writer.filename
            
            # Write to file
            writer.write(
                images=image.raw_image,
                pixel_header=image.pixel_header,
                dicom_meta=image.dicom_meta,
                space=image.space,
                dicom_status=image.dicom_status,
            )
        except Exception as e:
            if isinstance(e, (InvalidCubeFileError, CodecError)):
                raise
            raise InvalidCubeFileError(
                f"Failed to save file: {str(e)}",
                context="save operation",
                details={"file_path": file_path, "file_type": file_type}
            ) from e
    

    @staticmethod
    def _get_reader(file_path: str) -> DcbFile:
        """Get the appropriate reader based on the file path.
        
        Args:
            file_path (str): Path to the input file.
        """
        # Validate required parameters
        validate_not_none(file_path, "file_path", "load operation", InvalidCubeFileError)
        validate_file_exists(file_path, "load operation", InvalidCubeFileError)
        
        try:
            # Read file header to determine format
            header_size = struct.calcsize(DcbFile.HEADER_STRUCT)
            with open(file_path, "rb") as f:
                header_data = f.read(header_size)
            magic = struct.unpack(DcbFile.HEADER_STRUCT, header_data)[0]
            
            # Choose appropriate reader based on magic number
            if magic == DcbAFile.MAGIC:
                reader = DcbAFile(file_path, mode="r")
            elif magic == DcbSFile.MAGIC:
                reader = DcbSFile(file_path, mode="r")
            else:
                raise InvalidCubeFileError(
                    f"Unsupported file format",
                    context="load operation",
                    details={"file_path": file_path, "magic_number": magic},
                    suggestion="Ensure the file is a valid DicomCube file"
                )
            return reader
        
        except Exception as e:
            if isinstance(e, (InvalidCubeFileError, CodecError)):
                raise
            raise InvalidCubeFileError(
                f"Failed to load file: {str(e)}",
                context="load operation",
                details={"file_path": file_path}
            ) from e

    @staticmethod
    def load_meta(file_path: str) -> DicomMeta:
        """Load the metadata from a file.
        
        Args:
            file_path (str): Path to the input file.
        """
        reader = DicomCubeImageIO._get_reader(file_path)
        return reader.read_meta()
    
    @staticmethod
    def load(file_path: str, skip_meta: bool = False) -> 'DicomCubeImage':
        """Load DicomCubeImage from a file.
        
        Args:
            file_path (str): Input file path.
            
        Returns:
            DicomCubeImage: The loaded object from the file.
            
        Raises:
            ValueError: When the file format is not supported.
        """
        reader = DicomCubeImageIO._get_reader(file_path)
        try:
            # Read file contents
            dicom_meta = None if skip_meta else reader.read_meta()
            space = reader.read_space()
            pixel_header = reader.read_pixel_header()
            dicom_status = reader.read_dicom_status()
            
            images = reader.read_images()
            if isinstance(images, list):
                # Convert list to ndarray if needed
                images = np.stack(images)
            
            # Use lazy import to avoid circular dependency
            from .image import DicomCubeImage
            
            return DicomCubeImage(
                raw_image=images,
                pixel_header=pixel_header,
                dicom_meta=dicom_meta,
                space=space,
                dicom_status=dicom_status,
            )
        except Exception as e:
            if isinstance(e, (InvalidCubeFileError, CodecError)):
                raise
            raise InvalidCubeFileError(
                f"Failed to load file: {str(e)}",
                context="load operation",
                details={"file_path": file_path}
            ) from e
    
    @staticmethod
    def load_from_dicom_folder(
        folder_path: str,
        sort_method: SortMethod = SortMethod.INSTANCE_NUMBER_ASC,
    ) -> 'DicomCubeImage':
        """Load DicomCubeImage from a DICOM folder.
        
        Args:
            folder_path (str): Path to the DICOM folder.
            sort_method (SortMethod): Method to sort DICOM files. 
                                      Defaults to SortMethod.INSTANCE_NUMBER_ASC.
            
        Returns:
            DicomCubeImage: The object created from the DICOM folder.
            
        Raises:
            ValueError: When the DICOM status is not supported.
        """
        # Validate required parameters
        validate_not_none(folder_path, "folder_path", "load_from_dicom_folder operation", InvalidCubeFileError)
        validate_folder_exists(folder_path, "load_from_dicom_folder operation", InvalidCubeFileError)
        
        try:
            # Read DICOM folder
            meta, datasets = _parse_dicom_dir(folder_path, sort_method=sort_method)
            
            # Get slopes and intercepts for all slices (handles both shared and non-shared)
            slopes = meta.get_values(CommonTags.RescaleSlope)
            intercepts = meta.get_values(CommonTags.RescaleIntercept)
            
            # Process each image with its corresponding slope/intercept
            real_values = []
            for i, ds in enumerate(datasets):
                img = ds.pixel_array
                
                # Get slope and intercept for this slice (handle None values and lists safely)
                slope_val = slopes[i] if i < len(slopes) else None
                intercept_val = intercepts[i] if i < len(intercepts) else None
                
                # Handle case where values might be lists (DICOM multi-value fields)
                if slope_val is not None:
                    if isinstance(slope_val, list) and len(slope_val) > 0:
                        slope = float(slope_val[0])
                    else:
                        slope = float(slope_val)
                else:
                    slope = 1.0
                    
                if intercept_val is not None:
                    if isinstance(intercept_val, list) and len(intercept_val) > 0:
                        intercept = float(intercept_val[0])
                    else:
                        intercept = float(intercept_val)
                else:
                    intercept = 0.0
                
                # Apply transformation (optimize: skip multiplication if slope=1)
                if slope == 1.0:
                    if intercept != 0.0:
                        real_val = img + intercept
                    else:
                        real_val = img
                else:
                    real_val = img * slope + intercept
                
                real_values.append(real_val)
            
            # Stack and regenerate pixel header with unified storage
            stacked_array = np.stack(real_values)
            raw_image, pixel_header = derive_pixel_header_from_array(stacked_array)
            
            # Get DICOM status for space calculation
            status = get_dicom_status(meta)
            
            if status in (
                DicomStatus.MISSING_DTYPE,
                DicomStatus.MISSING_SHAPE,
                DicomStatus.INCONSISTENT,
            ):
                raise MetaDataError(
                    f"Unsupported DICOM status: {status}",
                    context="load_from_dicom_folder operation",
                    details={"dicom_status": status, "folder_path": folder_path},
                    suggestion="Ensure DICOM files have consistent metadata and proper format"
                )
            
            if status in (
                DicomStatus.MISSING_SPACING,
                DicomStatus.NON_UNIFORM_SPACING,
                DicomStatus.MISSING_ORIENTATION,
                DicomStatus.NON_UNIFORM_ORIENTATION,
                DicomStatus.MISSING_LOCATION,
                DicomStatus.REVERSED_LOCATION,
                DicomStatus.DWELLING_LOCATION,
                DicomStatus.GAP_LOCATION,
            ):
                warnings.warn(f"DICOM status: {status}, cannot calculate space information")
                space = None
            else:
                if get_space_from_DicomMeta is not None:
                    space = get_space_from_DicomMeta(meta, axis_order="zyx")
                else:
                    space = None
            
            # Get window parameters with fallback for non-shared values
            def get_window_value(tag):
                if not meta.is_missing(tag):
                    values = meta.get_values(tag)
                    return values[0] if values else None
                return None
            
            def normalize_window_value(value):
                if value is None:
                    return None
                try:
                    # Handle multi-value arrays (e.g., [40.0, 40.0])
                    if isinstance(value, (list, tuple)) and len(value) > 0:
                        return float(value[0])
                    return float(value)
                except (ValueError, TypeError):
                    return None
            
            wind_center = normalize_window_value(get_window_value(CommonTags.WindowCenter))
            wind_width = normalize_window_value(get_window_value(CommonTags.WindowWidth))
            
            # Update pixel_header with window values
            pixel_header.WindowCenter = wind_center
            pixel_header.WindowWidth = wind_width
            
            # Validate PixelDataHeader initialization success
            if pixel_header is None:
                raise MetaDataError(
                    "PixelDataHeader initialization failed",
                    context="load_from_dicom_folder operation",
                    suggestion="Check DICOM metadata for required pixel data information"
                )
            
            # Use lazy import to avoid circular dependency
            from .image import DicomCubeImage
            
            return DicomCubeImage(
                raw_image=raw_image,
                pixel_header=pixel_header,
                dicom_meta=meta,
                space=space,
                dicom_status=status
            )
        except Exception as e:
            if isinstance(e, (InvalidCubeFileError, MetaDataError)):
                raise
            raise MetaDataError(
                f"Failed to load DICOM folder: {str(e)}",
                context="load_from_dicom_folder operation",
                details={"folder_path": folder_path}
            ) from e
    
    @staticmethod
    def load_from_nifti(file_path: str) -> 'DicomCubeImage':
        """Load DicomCubeImage from a NIfTI file.
        
        Args:
            file_path (str): Path to the NIfTI file.
            
        Returns:
            DicomCubeImage: The object created from the NIfTI file.
            
        Raises:
            ImportError: When nibabel is not installed.
        """
        # Validate required parameters
        validate_not_none(file_path, "file_path", "load_from_nifti operation", InvalidCubeFileError)
        validate_file_exists(file_path, "load_from_nifti operation", InvalidCubeFileError)
        
        try:
            import nibabel as nib
        except ImportError:
            raise ImportError("nibabel is required to read NIfTI files")
        
        try:
            nii = nib.load(file_path)
            nii_arr = np.asarray(nii.dataobj, dtype=nii.dataobj.dtype) 
            space = get_space_from_nifti(nii)
            if nii_arr.flags.fortran:   
                # this is fortran-order, need to convert to c-order
                nii_arr = nii_arr.transpose(2, 1, 0)
                space = space.reverse_axis_order() # adapt for transpose of nii_arr
            
            # Fix numpy array warning
            raw_image, header = derive_pixel_header_from_array(
                nii_arr
            )
            
            # Use lazy import to avoid circular dependency
            from .image import DicomCubeImage
            
            return DicomCubeImage(raw_image, header, space=space)
        except Exception as e:
            if isinstance(e, ImportError):
                raise
            raise InvalidCubeFileError(
                f"Failed to load NIfTI file: {str(e)}",
                context="load_from_nifti operation",
                details={"file_path": file_path},
                suggestion="Ensure the file is a valid NIfTI format and nibabel is installed"
            ) from e
    
    @staticmethod
    def save_to_dicom_folder(
        image: 'DicomCubeImage',
        folder_path: str,
    ) -> None:
        """Save DicomCubeImage as a DICOM folder.
        
        Args:
            image (DicomCubeImage): The DicomCubeImage object to save.
            folder_path (str): Output directory path.
        """
        # Validate required parameters
        validate_not_none(image, "image", "save_to_dicom_folder operation", DataConsistencyError)
        validate_string_not_empty(folder_path, "folder_path", "save_to_dicom_folder operation", InvalidCubeFileError)
        
        if image.dicom_meta is None:
            warnings.warn("dicom_meta is None, initializing with default values")
            image.init_meta()
        
        # Prepare output directory
        prepare_output_dir(folder_path)

        raw_images = image.raw_image
        if raw_images.ndim == 2:
            raw_images = raw_images[np.newaxis, ...]
        
        for idx in range(len(raw_images)):
            # Build DICOM dataset using unified builder
            ds = DicomBuilder.build(
                meta_dict=image.dicom_meta.index(idx),
                pixel_header=image.pixel_header,
                pixel_data=raw_images[idx],
                is_compressed_data=False,
            )

            # Save to file
            output_path = os.path.join(
                folder_path, f"slice_{idx:04d}.dcm"
            )
            save_dicom(ds, output_path) 
        
    @staticmethod
    def save_to_nifti(
        image: 'DicomCubeImage',
        file_path: str,
    ) -> None:
        """Save DicomCubeImage as a NIfTI file.
        
        Args:
            image (DicomCubeImage): The DicomCubeImage object to save.
            file_path (str): Output file path.
            
        Raises:
            ImportError: When nibabel is not installed.
            InvalidCubeFileError: When saving fails.
        """
        # Validate required parameters
        validate_not_none(image, "image", "save_to_nifti operation", DataConsistencyError)
        validate_string_not_empty(file_path, "file_path", "save_to_nifti operation", InvalidCubeFileError)
        
        try:
            import nibabel as nib
        except ImportError:
            raise ImportError("nibabel is required to write NIfTI files")
        
        try:
            if image.space is None:
                raise InvalidCubeFileError(
                    "Cannot save to NIfTI without space information",
                    context="save_to_nifti operation",
                    suggestion="Ensure the DicomCubeImage has valid space information"
                )
            
            # Get affine matrix from space
            affine = image.space.reverse_axis_order().to_nifti_affine()
            
            # 根据像素数据和metadata确定最佳的数据类型
            optimal_data, dtype_name = determine_optimal_nifti_dtype(image.raw_image.transpose(2, 1, 0), image.pixel_header)
            
            # Create NIfTI image with optimized data type
            nii = nib.Nifti1Image(optimal_data, affine)
            
            # Save to file
            nib.save(nii, file_path)
        except Exception as e:
            if isinstance(e, (ImportError, InvalidCubeFileError)):
                raise
            raise InvalidCubeFileError(
                f"Failed to save NIfTI file: {str(e)}",
                context="save_to_nifti operation",
                details={"file_path": file_path},
                suggestion="Check file permissions and ensure space information is valid"
            ) from e


def prepare_output_dir(output_dir: str):
    """Prepare output directory"""
    if os.path.exists(output_dir):
        import shutil

        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)

