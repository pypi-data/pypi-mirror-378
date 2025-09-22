import zarr
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple, Union, Iterable, ClassVar
from dataclasses import dataclass
import copy
import numpy as np
import dask.array as da
from eubi_bridge.base.scale import Downscaler


def is_zarr_group(path: (str, Path)
                  ):
    try:
        _ = zarr.open_group(path, mode='r')
        return True
    except:
        return False


def generate_channel_metadata(num_channels,
                              dtype=np.uint16
                              ):
    # Standard distinct microscopy colors
    default_colors = [
        "FF0000",  # Red
        "00FF00",  # Green
        "0000FF",  # Blue
        "FF00FF",  # Magenta
        "00FFFF",  # Cyan
        "FFFF00",  # Yellow
        "FFFFFF",  # White
    ]

    channels = []
    import numpy as np

    if dtype is not None and np.issubdtype(dtype, np.integer):
        min, max = int(np.iinfo(dtype).min), int(np.iinfo(dtype).max)
    elif dtype is not None and np.issubdtype(dtype, np.floating):
        min, max = float(np.finfo(dtype).min), float(np.finfo(dtype).max)
    else:
        raise ValueError(f"Unsupported dtype {dtype}")

    for i in range(num_channels):
        color = default_colors[i] if i < len(
            default_colors) else f"{i * 40 % 256:02X}{i * 85 % 256:02X}{i * 130 % 256:02X}"
        channel = {
            "color": color,
            "coefficient": 1,
            "active": True,
            "label": f"Channel {i}",
            "window": {
                "min": min,
                "max": max,
                "start": min,
                "end": max
            },
            "family": "linear",
            "inverted": False
        }
        channels.append(channel)

    return {
        "omero": {
            "channels": channels,
            "rdefs": {
                "defaultT": 0,
                "model": "greyscale",
                "defaultZ": 0
            }
        }
    }


class NGFFMetadataHandler:
    """Class for handling NGFF metadata in zarr groups."""

    SUPPORTED_VERSIONS: ClassVar[List[str]] = ["0.4", "0.5"]

    def __init__(self) -> None:
        """Initialize an empty metadata handler."""
        self.zarr_group: Optional[zarr.Group] = None
        self.metadata: Optional[Dict[str, Any]] = None
        self._pending_changes: bool = False
        self.version: Optional[str] = None
        self.zarr_format: Optional[int] = None

    def __enter__(self) -> 'NGFFMetadataHandler':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._pending_changes:
            self.save_changes()

    @property
    def multiscales(self) -> Dict[str, Any]:
        """Get the multiscales metadata."""
        if not self.metadata or 'multiscales' not in self.metadata:
            raise RuntimeError("No multiscales metadata available")
        return self.metadata['multiscales'][0]

    @property
    def omero(self) -> Dict[str, Any]:
        """Get the multiscales metadata."""
        if not self.metadata or 'omero' not in self.metadata:
            raise RuntimeError("No omero metadata available")
        return self.metadata['omero']

    def _validate_version_and_format(self, version: str, zarr_format: int) -> None:
        """Validate version and zarr format compatibility."""
        if version not in self.SUPPORTED_VERSIONS:
            raise ValueError(f"Unsupported version {version}. Supported versions: {self.SUPPORTED_VERSIONS}")
        if zarr_format not in (2, 3):
            raise ValueError(f"Unsupported Zarr format: {zarr_format}")
        if version == "0.5" and zarr_format != 3:
            raise ValueError("NGFF version 0.5 requires Zarr format 3")

    def _validate_axis_inputs(self, axis_order: str, units: Optional[List[str]]) -> None:
        """Validate axis order and units inputs."""
        if not all(ax in 'tczyx' for ax in axis_order):
            raise ValueError("Invalid axis order. Must contain only t,c,z,y,x")
        if units is not None:
            if not (len(axis_order) - len(units)) in [0, 1]:
                raise ValueError("Number of units must match number of axes except channel")
            elif (len(axis_order) - len(units)) == 1:
                if 'c' not in axis_order:
                    raise ValueError("Only channel axis can be kept without a unit.")

    def _get_dataset(self, path: str) -> Optional[Dict[str, Any]]:
        """Helper method to find dataset by path."""
        path = str(path)
        for dataset in self.multiscales['datasets']:
            if dataset['path'] == path:
                return dataset
        return None

    def _update_coordinate_transformation(self,
                                          dataset: Dict[str, Any],
                                          transform_type: str,
                                          values: List[float]) -> None:
        """Update or add a coordinate transformation."""
        for transform in dataset['coordinateTransformations']:
            if transform['type'] == transform_type:
                transform[transform_type] = values
                break
        else:
            if transform_type == 'scale':
                dataset['coordinateTransformations'].insert(
                    0, {'type': transform_type, transform_type: values}
                )
            else:
                dataset['coordinateTransformations'].append(
                    {'type': transform_type, transform_type: values}
                )

    def get_metadata_state(self) -> Dict[str, Any]:
        """Get a copy of current metadata state."""
        if self.metadata is None:
            raise RuntimeError("No metadata loaded or created")
        return copy.deepcopy(self.metadata)

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the metadata."""
        if not self.metadata:
            raise RuntimeError("No metadata available")

        return {
            'version': self.version,
            'zarr_format': self.zarr_format,
            'axes': self._axis_names,
            'units': self._units,
            'n_datasets': len(self.multiscales['datasets']),
            'name': self.multiscales['name']
        }

    def create_new(self,
                   version: str = "0.5",
                   name: str = "Series 0") -> 'NGFFMetadataHandler':
        """Create a new metadata handler with empty metadata of specified version."""
        self._validate_version_and_format(version, 3 if version == "0.5" else 2)

        multiscale_metadata = {
            'name': name,
            'axes': [],
            'datasets': [],
            'metadata': {}
        }

        if version == "0.5":
            self.metadata = {
                'version': version,
                'multiscales': [multiscale_metadata],
                'omero': {
                    'channels': [],
                    'rdefs': {
                        'defaultT': 0,
                        'model': 'greyscale',
                        'defaultZ': 0
                    }
                },
                '_creator': {
                    'name': 'NGFFMetadataHandler',
                    'version': '1.0'
                }
            }
        else:  # version == "0.4"
            multiscale_metadata['version'] = version
            self.metadata = {
                '_creator': {
                    'name': 'NGFFMetadataHandler',
                    'version': '1.0'
                },
                'multiscales': [multiscale_metadata],
                'omero': {
                    'channels': [],
                    'rdefs': {
                        'defaultT': 0,
                        'model': 'greyscale',
                        'defaultZ': 0
                    }
                }
            }

        self.version = version
        self.zarr_format = 3 if version == "0.5" else 2
        self._pending_changes = True
        return self

    def connect_to_group(self, store: Union[zarr.Group, str, Path], mode: str = 'a') -> None:
        """Connect to a zarr group for reading/writing metadata."""
        if not isinstance(store, (zarr.Group, str, Path)):
            raise ValueError("Store must be a zarr group or path")
        if isinstance(store, zarr.Group):
            self.zarr_group = store
        else:  # isinstance(store, (str, Path))
            if is_zarr_group(store):
                self.zarr_group = zarr.open_group(store, mode=mode)
                # zarr_version = self.zarr_group.info._zarr_format
            else:
                zarr_version = self.zarr_format if self.zarr_format else 2
                self.zarr_group = zarr.open_group(store, mode=mode, zarr_version=zarr_version)
        # Update handler's format to match the created store
        store_format = self.zarr_group.info._zarr_format
        self.zarr_format = store_format
        # Update version based on zarr_format
        self.version = "0.5" if store_format == 3 else "0.4"
        self._validate_version_and_format(self.version, store_format)

    def read_metadata(self):
        """Read metadata from connected zarr group."""
        if self.zarr_group is None:
            raise RuntimeError("No zarr group connected. Call connect_to_group first.")

        if 'ome' in self.zarr_group.attrs:
            self.metadata = self.zarr_group.attrs['ome']
            self.version = self.metadata['version']
        elif 'multiscales' in self.zarr_group.attrs:
            self.metadata = {'multiscales': self.zarr_group.attrs['multiscales']}
            self.version = self.metadata['multiscales'][0]['version']
        else:
            raise ValueError("No valid metadata found in zarr group")

        if 'omero' in self.zarr_group.attrs:
            self.metadata['omero'] = self.zarr_group.attrs['omero']
        self.zarr_format = 3 if self.version == "0.5" else 2
        self._pending_changes = False
        return self

    def save_changes(self) -> None:
        """Save current metadata to connected zarr group."""

        if not self._pending_changes:
            return
        if self.zarr_group is None:
            raise RuntimeError("No zarr group connected. Call connect_to_group first.")

        if self.metadata.get('version', '') == '0.5':
            self.zarr_group.attrs['ome'] = self.metadata
        else:
            self.zarr_group.attrs['multiscales'] = self.metadata['multiscales']
            if 'omero' in self.metadata:
                self.zarr_group.attrs['omero'] = self.metadata['omero']
            if '_creator' in self.metadata:
                self.zarr_group.attrs['_creator'] = self.metadata['_creator']

        self._pending_changes = False

    def update_all_datasets(self,
                            scale: Optional[List[float]] = None,
                            translation: Optional[List[float]] = None
                            ) -> None:
        """Update all datasets with new scale and/or translation values."""
        for dataset in self.multiscales['datasets']:
            if scale is not None:
                self._update_coordinate_transformation(dataset, 'scale', scale)
            if translation is not None:
                self._update_coordinate_transformation(dataset, 'translation', translation)
        self._pending_changes = True

    def autocompute_omerometa(self,
                              n_channels: int,
                              dtype
                              ) -> None:
        """Add multiple channels to the OMERO metadata."""
        omero_meta = generate_channel_metadata(n_channels, dtype)
        self.metadata['omero'] = omero_meta['omero']
        self._pending_changes = True

    def add_channel(self,
                    color: str = "808080",
                    label: str = None,
                    dtype=None,
                    channel_idx = None
                    ) -> None:
        """Add a channel to the OMERO metadata."""
        assert dtype is not None, f"dtype cannot be None"
        min = 0
        if np.issubdtype(dtype, np.integer):
            max = int(np.iinfo(dtype).max)
        elif np.issubdtype(dtype, np.floating):
            max = float(np.finfo(dtype).max)
        else:
            raise ValueError(f"Unsupported dtype {dtype}")

        if 'omero' not in self.metadata:
            self.metadata['omero'] = {
                'channels': [],
                'rdefs': {
                    'defaultT': 0,
                    'model': 'greyscale',
                    'defaultZ': 0
                }
            }

        channel = {
            'color': color,
            'coefficient': 1,
            'active': True,
            'label': label or f"Channel {len(self.metadata['omero']['channels'])}",
            'window': {'min': min, 'max': max, 'start': min, 'end': max},
            'family': 'linear',
            'inverted': False
        }

        if channel_idx is None:
            self.metadata['omero']['channels'].append(channel)
        else:
            self.metadata['omero']['channels'][channel_idx] = channel
        self._pending_changes = True

    def get_channels(self) -> List[Dict[str, Any]]:
        """
        Get a list of all channels with their labels and colors.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, where each dictionary contains
                                 'label' and 'color' keys for a channel.
        """
        if 'omero' not in self.metadata or 'channels' not in self.metadata['omero']:
            return []

        return [
            {
                'label': channel.get('label', f"Channel {i}"),
                'color': channel.get('color', '808080')
            }
            for i, channel in enumerate(self.metadata['omero']['channels'])
        ]

    def parse_axes(self,  ###
                   axis_order: str,
                   units: Optional[List[str]] = None) -> None:
        """Update axes information with new axis order and units."""
        if self.metadata is None:
            raise RuntimeError("No metadata loaded or created.")

        self._validate_axis_inputs(axis_order, units)

        if units is None:
            units = [None] * len(axis_order)
        if len(axis_order) - len(units) == 1:
            if 'c' in axis_order:
                idx = axis_order.index('c')
                units.insert(idx, None)

        new_axes = []
        for ax_name, unit in zip(axis_order, units):
            axis_data = {
                'name': ax_name,
                'type': {'t': 'time', 'c': 'channel', 'z': 'space',
                         'y': 'space', 'x': 'space'}.get(ax_name, 'custom')
            }
            if unit is not None:
                axis_data['unit'] = unit
            new_axes.append(axis_data)

        self.metadata['multiscales'][0]['axes'] = new_axes
        self._pending_changes = True

    def add_dataset(self, path: Union[str, int],
                    scale: Iterable[Union[int, float]],
                    translation: Optional[Iterable[Union[int, float]]] = None,
                    overwrite: bool = False) -> None:
        """Add a dataset with scale and optional translation."""
        path = str(path)
        scale = list(map(float, scale))
        if translation is not None:
            translation = list(map(float, translation))

        dataset_data = {
            'path': path,
            'coordinateTransformations': [{'type': 'scale', 'scale': scale}]
        }
        if translation is not None:
            dataset_data['coordinateTransformations'].append(
                {'type': 'translation', 'translation': translation}
            )

        existing_paths = self.get_resolution_paths()
        if path in existing_paths:
            if not overwrite:
                raise ValueError(f"Dataset path '{path}' already exists")
            idx = existing_paths.index(path)
            self.metadata['multiscales'][0]['datasets'][idx] = dataset_data
        else:
            self.metadata['multiscales'][0]['datasets'].append(dataset_data)

        self.metadata['multiscales'][0]['datasets'].sort(
            key=lambda x: int(x['path']) if x['path'].isdigit() else float('inf')
        )
        self._pending_changes = True

    def update_scale(self,
                     path: Union[str, int],
                     scale: Iterable[Union[int, float]]) -> None:
        """Update scale for a specific dataset."""
        dataset = self._get_dataset(str(path))
        if dataset:
            self._update_coordinate_transformation(dataset, 'scale', list(map(float, scale)))
            self._pending_changes = True

    def update_translation(self, path: Union[str, int],
                           translation: Iterable[Union[int, float]]) -> None:
        """Update translation for a specific dataset."""
        dataset = self._get_dataset(str(path))
        if dataset:
            self._update_coordinate_transformation(dataset, 'translation', list(map(float, translation)))
            self._pending_changes = True

    def get_resolution_paths(self) -> List[str]:
        """Get paths to all resolution levels."""
        return [ds['path'] for ds in self.multiscales['datasets']]

    @property
    def _axis_names(self) -> List[str]:
        """Get list of axis names."""
        return [ax['name'] for ax in self.multiscales['axes']]

    @property
    def axis_order(self) -> str:
        """Get axis names as str."""
        return ''.join(self._axis_names)

    @property
    def _units(self) -> Dict[str, Optional[str]]:
        """Get dictionary of axis units."""
        return {ax['name']: ax.get('unit') for ax in self.multiscales['axes']}

    @property
    def unit_dict(self):
        return self._units

    @property
    def unit_list(self):
        return [self._units[ax] for ax in self._axis_names]

    @property
    def ndim(self) -> int:
        return len(self.axis_order)

    @property
    def resolution_paths(self) -> List[str]:
        return [item['path'] for item in self.multiscales['datasets']]

    @property
    def nlayers(self) -> int:
        return len(self.resolution_paths)

    @property
    def channels(self):
        return self.get_channels()

    def validate_metadata(self) -> bool:
        """Validate current metadata structure."""
        if not self.metadata:
            return False

        try:
            if self.version == "0.5":
                if not all(key in self.metadata for key in {'version', 'multiscales'}):
                    return False
            else:  # version == "0.4"
                if 'multiscales' not in self.metadata:
                    return False
                if 'version' not in self.metadata['multiscales'][0]:
                    return False

            required_keys = {'name', 'axes', 'datasets'}
            return all(key in self.multiscales for key in required_keys)

        except (KeyError, IndexError, TypeError):
            return False

    ###

    def get_scaledict(self,
                      pth: Union[str, int]
                      ):
        # pth = cnv.asstr(pth)
        idx = self.resolution_paths.index(pth)
        scale = self.multiscales['datasets'][idx]['coordinateTransformations'][0]['scale']
        return dict(zip(self.axis_order, scale))

    def get_base_scaledict(self):
        basepath = self.resolution_paths[0]
        return self.get_scaledict(basepath)

    def get_scale(self,
                  pth: Union[str, int]
                  ):
        scaledict = self.get_scaledict(pth)
        return [scaledict[ax] for ax in self.axis_order]

    def get_base_scale(self):
        basepath = self.resolution_paths[0]
        return self.get_scale(basepath)

    def set_scale(self,
                  pth: Union[str, int] = 'auto',
                  scale: Union[tuple, list, dict] = 'auto',
                  # hard=False
                  ):
        if isinstance(scale, tuple):
            scale = list(scale)
            ch_index = self.axis_order.index('c')
            scale[ch_index] = 1
        elif hasattr(scale, 'tolist'):
            scale = scale.tolist()
        elif isinstance(scale, dict):  # TODO: test this block further
            assert all([ax in self.axis_order for ax in scale])
            fullscale = self.get_scale(pth)
            scaledict = dict(zip(self.axis_order, fullscale))
            scaledict.update(**scale)
            scale = [scaledict[ax] for ax in self.axis_order]

        if pth == 'auto':
            pth = self.resolution_paths[0]
        if scale == 'auto':
            pth = self.scales[pth]
        idx = self.resolution_paths.index(pth)
        self.multiscales['datasets'][idx]['coordinateTransformations'][0]['scale'] = scale
        self._pending_changes = True
        # if hard:
        #     self.gr.attrs['multiscales'] = self.multimeta
        return

    def update_scales(self,
                      reference_scale: Union[tuple, list],  # , dict],
                      scale_factors: dict,
                      # hard=True
                      ):
        for pth, factor in scale_factors.items():
            new_scale = np.multiply(factor, reference_scale)
            self.set_scale(pth, new_scale)  # ,hard)
        return self

    def update_unitlist(self,
                        unitlist=None,
                        # hard=False
                        ):
        if isinstance(unitlist, tuple):
            unitlist = list(unitlist)
        assert isinstance(unitlist, list)
        self.parse_axes(self.axis_order, unitlist  # overwrite=True
                        )
        # if hard:
        #     self.gr.attrs['multiscales'] = self.multimeta
        return self

    @property
    def scales(self):
        scales = {}
        for pth in self.resolution_paths:
            scl = self.get_scale(pth)
            scales[pth] = scl
        return scales

    @property
    def scaledict(self):
        scales = {}
        for pth in self.resolution_paths:
            scl = self.get_scaledict(pth)
            scales[pth] = scl
        return scales

    def retag(self,
              new_tag: str,
              ):
        self.multiscales['name'] = new_tag
        self._pending_changes = True
        return self


def calculate_n_layers(shape: Tuple[int, ...],
                       scale_factor: Union[int, float, Tuple[Union[int, float], ...]],
                       min_dimension_size: int = 64) -> int:
    """
    Calculate the number of downscaling layers until one dimension becomes smaller than min_dimension_size.
    Only considers dimensions with scale_factor >= 2 for downscaling.

    Args:
        shape: Tuple of integers representing the shape of the array (e.g., (t, c, z, y, x))
        scale_factor: Either a single number (applied to all dimensions) or a tuple of numbers
                     (one per dimension) representing the downscaling factor for each dimension.
                     Dimensions with scale_factor < 2 will not limit the number of downscaling layers.
        min_dimension_size: Minimum size allowed for any dimension in the pyramid

    Returns:
        int: Number of downscaling layers possible before any dimension becomes smaller than min_dimension_size

    Example:
        >>> # Only z,y,x dimensions will be considered for downscaling (scale_factor >= 2)
        >>> calculate_n_layers((100, 3, 512, 512, 512), (1, 1, 2, 2, 2), min_dimension_size=64)
        3  # Because 512 -> 256 -> 128 -> 64 (stops before 32 which is < 64)

        >>> # If all scale factors are < 2, return 1 (just the original)
        >>> calculate_n_layers((100, 3, 512, 512, 512), (1, 1, 1.5, 1.5, 1.5), min_dimension_size=64)
        1
    """
    if isinstance(scale_factor, (int, float)):
        scale_factor = (scale_factor,) * len(shape)

    if len(scale_factor) != len(shape):
        raise ValueError(f"scale_factor length ({len(scale_factor)}) must match shape length ({len(shape)})")

    shape_array = np.array(shape, dtype=int)
    scale_array = np.array(scale_factor, dtype=float)

    # Identify dimensions that will be downscaled (scale_factor >= 2)
    downscale_dims = scale_array > 1

    # If no dimensions are being downscaled, return 1 (just the original)
    if not np.any(downscale_dims):
        return 1

    # Calculate layers only for dimensions that will be downscaled
    downscale_shapes = shape_array[downscale_dims]
    downscale_factors = scale_array[downscale_dims]

    # Calculate number of layers for each downscaled dimension
    n_layers_per_dim = np.floor(np.log(downscale_shapes / min_dimension_size) / np.log(downscale_factors))

    # Find the number of layers for the largest dimension
    if len(n_layers_per_dim) == 0:
        return 1
    argmax_largest_dim = np.argmax(downscale_shapes)
    n_layers_per_largest_dim = n_layers_per_dim[argmax_largest_dim]

    n_layers = int(n_layers_per_largest_dim) + 1
    # Ensure at least 1 layer (the original) is always returned
    return max(1, n_layers)


class Pyramid:
    def __init__(self,
                 gr: (zarr.Group, zarr.storage.StoreLike, Path, str) = None
                 # An NGFF group. This contains the multiscales metadata in attrs and image layers as
                 ):
        self.meta = None
        self.gr = None
        if gr is not None:
            self.from_ngff(gr)

    def __repr__(self):
        return f"NGFF with {self.nlayers} layers."

    def from_ngff(self, gr):
        self.meta = NGFFMetadataHandler()
        self.meta.connect_to_group(gr)
        self.meta.read_metadata()
        self.gr = self.meta.zarr_group
        return self

    def to_ngff(self,
                store: (zarr.Group, zarr.storage.StoreLike, Path, str),
                version: str = "0.5"
                ):
        newmeta = NGFFMetadataHandler()
        if is_zarr_group(store):
            self.gr = zarr.open_group(store, mode='a')
            newmeta.connect_to_group(self.gr)
        else:
            self.meta.create_new(version=version, name="Series 0")
        newmeta.save_changes()
        self.meta = newmeta
        return self

    @property
    def axes(self):
        return self.meta.axis_order

    @property
    def nlayers(self):
        return self.meta.nlayers

    @property
    def layers(self):
        return {path: self.gr[path] for path in self.gr.array_keys()}

    def get_dask_data(self):
        return {str(path): da.from_zarr(self.layers[path]) for path in self.gr.array_keys()}

    @property
    def dask_arrays(self):
        return self.get_dask_data()

    @property
    def base_array(self):
        return self.dask_arrays['0']

    # def shrink(self,
    #            hard=False
    #            ):
    #     """
    #     Delete all arrays except for the base array (zeroth array)
    #     :return:
    #     """
    #     for key in self.meta.resolution_paths:
    #         if key == '0':
    #             continue
    #         self.meta.del_dataset(key)
    #         if hard:
    #             del self.gr[key]
    #     if hard:
    #         self.meta.to_ngff(self.gr)
    #     return

    def update_scales(self,
                      **kwargs
                      ):
        """
        Automatically updates all pixel values for all layers based on
        provided pixel values for specific axes corresponding to
        the top resolution layer.
        :param kwargs:
        :return:
        """
        hard = kwargs.get('hard', False)

        new_scaledict = self.meta.get_base_scaledict()
        for ax in self.meta.axis_order:
            if ax in kwargs:
                new_scaledict[ax] = kwargs.get(ax)
        new_scale = [new_scaledict[ax] for ax in self.meta.axis_order]
        ###
        shapes = [self.layers[key].shape for key in self.meta.resolution_paths]
        scale_factors = np.divide(shapes[0], shapes)
        scale_factordict = {pth: scale
                            for pth, scale in
                            zip(self.meta.resolution_paths, scale_factors.tolist())}
        self.meta.update_scales(reference_scale=new_scale,
                                scale_factors=scale_factordict,
                                )
        if hard:
            self.meta.save_changes()
        return

    def update_units(self,
                     **kwargs
                     ):
        """
        Automatically updates all pixel units based on provided unit strings for each axis.
        :param kwargs:
        :return:
        """
        hard = kwargs.get('hard', False)

        new_unitdict = self.meta.unit_dict
        for ax in self.meta.axis_order:
            if ax in kwargs:
                new_unitdict[ax] = kwargs.get(ax)
        new_unitlist = [new_unitdict[ax] for ax in self.meta.axis_order]
        ###
        self.meta.update_unitlist(unitlist=new_unitlist,
                                  # hard=hard
                                  )

    @property
    def tag(self):
        return self.multimeta[0]['name']

    def retag(self,
              new_tag: str,
              hard=False
              ):
        self.meta.retag(new_tag)
        if hard:
            self.meta.save_changes()
        return self

    def update_downscaler(self,
                          scale_factor=None,
                          n_layers=1,
                          downscale_method='simple',
                          backend='numpy',
                          **kwargs
                          ):
        min_dimension_size = kwargs.get('min_dimension_size', 64)

        darr = self.base_array
        shape = darr.shape
        if n_layers in (None, 'default', 'auto'):
            n_layers = calculate_n_layers(shape, scale_factor, min_dimension_size)
        if scale_factor is None:
            scale_factor = tuple([defaults.scale_factor_map[key] for key in self.axes])
        scale = self.meta.scales['0']
        scale_factor = tuple(np.minimum(darr.shape, scale_factor))
        self.downscaler = Downscaler(array=darr,
                                     scale_factor=scale_factor,
                                     n_layers=n_layers,
                                     scale=scale,
                                     downscale_method=downscale_method,
                                     backend=backend
                                     )
        return self