#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import xarray as xr
import tifffile as tf

def read_geotiff(file_path):
    """Reads a GeoTIFF file into an xarray DataArray with coordinates.
    """
    if file_path[:2] == 's3':
        try:
            import s3fs
            fs = s3fs.S3FileSystem(anon=False)
            file_path = fs.open(file_path, 'rb')
        except ImportError:
            print('Error: s3fs must be installed to read S3 files.')
            return None
        except FileNotFoundError:
            print(f"Error: The file at {file_path} was not found.")
            return None
    try:
        with tf.TiffFile(file_path) as tif:
            image_data = tif.pages[0].asarray()
            tags = tif.pages[0].tags

            # Get the pixel scale and tie points from the GeoTIFF tags
            pixel_scale = tags['ModelPixelScaleTag'].value
            tie_points = tags['ModelTiepointTag'].value

            # Get the upper-left corner coordinates
            ulx, uly = tie_points[3], tie_points[4]

            # Get the pixel size
            px, py = pixel_scale[0], pixel_scale[1]

            # Get the dimensions of the image
            h, w = image_data.shape

            # Create the coordinate arrays
            x_coords = np.arange(ulx, ulx + w*px, px)
            y_coords = np.arange(uly, uly - h*py, -py)

            # Create the xarray DataArray
            data_array = xr.DataArray(image_data, dims=('y', 'x'), 
                                      coords={'y': y_coords, 'x': x_coords})

            return data_array

    except FileNotFoundError:
        print(f"Error: The file at {file_path} was not found.")
        return None
    except KeyError as e:
        print(f"Error: A required GeoTIFF tag was not found: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
