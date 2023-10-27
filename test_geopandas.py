# %%
import geopandas as gpd
import pandas as pd
import numpy as np

# %%
gdf = gpd.read_file(filename='/home/holger/Downloads/SharedFiles_ProfJames/Results_Scripts/GGPF_gis_polygon_sc_v001.gpkg')
gdf

# %%
gdf.drop(columns=['dat_file', 'csv_file'], inplace=True)
gdf

# %%
type(gdf)

# %%
gdf.to_file(filename='/home/holger/Downloads/SharedFiles_ProfJames/Results_Scripts/GGPF_gis_polygon_sc_v001.gpkg', driver='GPKG', crs='EPSG:28356')

# %%
