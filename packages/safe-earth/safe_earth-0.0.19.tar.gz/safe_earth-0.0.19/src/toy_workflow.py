# TO RUN:
# 1. move the file to src/ directory
# 2. cd src/
# 3. python -m toy_workflow


import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import safe_earth.data.climate.era5
from safe_earth.data.climate.era5 import ERA5Var
import safe_earth.data.climate.wb2
import safe_earth.metrics.losses
import safe_earth.metrics.errors
import pandas as pd
import numpy as np
import pickle
import time
import pdb
import platform

model = 'graphcast'
resolution = '240x121'
lead_times = [np.timedelta64(x, 'h') for x in range(12, 49, 12)]
variables = [ERA5Var('2m_temperature', name='T2M')]

print('about to load data')

era5 = safe_earth.data.climate.era5.get_era5(resolution, variables=variables)
preds = safe_earth.data.climate.wb2.get_wb2_preds(model, resolution, lead_times, variables=variables)

print('about to run losses')

loss_gdf = safe_earth.metrics.losses.climate_weighted_l2(
    data=preds, 
    ground_truth=era5, 
    lon_dim='longitude', 
    lat_dim='latitude',
    lead_time_dim='prediction_timedelta'
)

print('about to run errors')

metrics = safe_earth.metrics.errors.stratified_rmse(
    loss_gdf,
    loss_metrics=['weighted_l2'],
    strata_groups='all',
    added_cols={'model': model}
)

pdb.set_trace()

# TODO: graph landcover metrics
