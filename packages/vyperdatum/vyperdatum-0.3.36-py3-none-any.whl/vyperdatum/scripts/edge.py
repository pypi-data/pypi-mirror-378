from vyperdatum.transformer import Transformer
from glob import glob
import numpy as np
from osgeo import gdal
import os
import tempfile
import shutil

gdal.UseExceptions()


crs_from = "EPSG:6347+EPSG:5703"
crs_to = "EPSG:6347+NOAA:98"

input_files = glob(r"C:\Users\mohammad.ashkezari\Documents\projects\vyperdatum\untrack\data\raster\PBE\edge\Original\**\*.tif", recursive=True)
for i, input_file in enumerate(input_files):
    print(f"Processing ({i}/{len(input_files)}): {input_file}")
    output_file = input_file.replace("Original", "Manual")
    tf = Transformer(crs_from=crs_from,
                    crs_to=crs_to,
                    )
    tf.transform(input_file=input_file,
                output_file=output_file,
                pre_post_checks=True,
                vdatum_check=False
                )
