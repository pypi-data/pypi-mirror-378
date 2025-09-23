import geopandas as gpd
import pandas as pd
import numpy as np
from shapely import wkt
from typing import List
from safe_earth.utils.errors import *
from safe_earth.data.strata.generate_gdf import *
import pdb

def stratified_rmse(
        losses: gpd.GeoDataFrame,
        loss_metrics: List[str],
        strata_groups: List[str] = 'all',
        added_cols: dict[str, str] = None
    ) -> dict[str, pd.DataFrame]:
    '''
    Get the RMSE of each strata group across gridpoints (the unique geometries
    in losses) belonging to each group.

    Parameters
    ----------
    losses: gpd.GeoDataFrame
        Dataframe where each entry is a unique combination of gridpoint, varialbe,
        and any other coordinates (e.g., prediction_leadtime for climatic data).
    loss_metrics: List[str]
        The name of the columns in losses for which to calculate RMSE over.
    strata_groups: List[str]
        The list of strata types to calculate RMSE for. The RMSE for each group
        within the strata type will be calculated. Options:
            - 'all': will include everything
            - 'territory': territorial boundaries defined by pygeoboundaries from geoLab
            - 'subregion': UN-defined subregions for each territory plus Antarctica
            - 'income': World Bank income group classification of each territory, if available
    added_cols: dict[str, str]
        For each entry in the dictionary, a column with the key as the name will
        be added to the output dataframe with the constant value.

    Returns
    -------
    dict[str, pd.DataFrame]
        The string key will be the name of the stratum type (i.e., landcover,
        income, etc) and the dataframe will include the RMSE for each group
        within the stratum. The RMSE of every prediction will also be included
        in a dataframe with the key 'baseline'.
    '''
    output = {}

    if need_to_download_gdf_file():
        generate_gdf_file()

    if os.path.exists(os.getcwd()+'/gdf_territory_region_income.csv'):
        path = os.getcwd()+'/gdf_territory_region_income.csv'
    elif os.path.exists('safe_earth/data/strata/gdf_territory_region_income.csv'):
        path = 'safe_earth/data/strata/gdf_territory_region_income.csv'
    elif os.path.exists(os.getcwd()+'src/safe_earth/data/strata/gdf_territory_region_income.csv'):
        path = os.getcwd()+'src/safe_earth/data/strata/gdf_territory_region_income.csv'
    elif os.path.exists('src/safe_earth/data/strata/gdf_territory_region_income.csv'):
        path = 'src/safe_earth/data/strata/gdf_territory_region_income.csv'
    else:
        raise OSError('Ill specified path for strata data')

    gdf = gpd.GeoDataFrame(gpd.read_file(path))
    gdf['geometry'] = gdf['geometry'].apply(wkt.loads)
    gdf = gpd.GeoDataFrame(gdf, geometry=gdf['geometry'])
    gdf = gdf.set_geometry('geometry').set_crs(4326)

    baseline = rmse_wrapper(losses, losses.variable.unique(), losses.lead_time.unique(), loss_metrics, added_cols)
    # TODO: get rmse at each individual point
    output.update({'baseline': baseline})

    joined_gdf = gpd.sjoin(losses, gdf, how="left", predicate="intersects").reset_index(drop=True)

    if 'territory' in strata_groups or 'all' in strata_groups:
        df = pd.DataFrame()
        for territory in joined_gdf['shapeName'].unique():
            trimmed_gdf = joined_gdf[joined_gdf.shapeName==territory]
            data = rmse_wrapper(trimmed_gdf, trimmed_gdf.variable.unique(), trimmed_gdf.lead_time.unique(), loss_metrics, added_cols)
            data['territory'] = territory
            df = pd.concat([df, data], ignore_index=True)
        output.update({'territory': df})

    if 'subregion' in strata_groups or 'all' in strata_groups:
        df = pd.DataFrame()
        for subregion in joined_gdf['UNSDG-subregion'].unique():
            trimmed_gdf = joined_gdf[joined_gdf['UNSDG-subregion']==subregion]

            # gdf is based on territory, don't double count data twice within the same subregion
            trimmed_gdf = trimmed_gdf[~trimmed_gdf.duplicated(subset=['geometry', 'variable', 'lead_time', 'UNSDG-subregion'], keep='last')]
            
            data = rmse_wrapper(trimmed_gdf, trimmed_gdf.variable.unique(), trimmed_gdf.lead_time.unique(), loss_metrics, added_cols)
            data['subregion'] = subregion
            df = pd.concat([df, data], ignore_index=True)
        output.update({'subregion': df})

    if 'income' in strata_groups or 'all' in strata_groups:
        df = pd.DataFrame()
        incomes = joined_gdf['worldBankIncomeGroup'].unique()
        incomes = [x for x in incomes if not x == 'No income group available']
        for income in incomes:
            trimmed_gdf = joined_gdf[joined_gdf['worldBankIncomeGroup']==income]

            # gdf is based on territory, don't double count data twice within the same income group
            trimmed_gdf = trimmed_gdf[~trimmed_gdf.duplicated(subset=['geometry', 'variable', 'lead_time', 'worldBankIncomeGroup'], keep='last')]
            
            data = rmse_wrapper(trimmed_gdf, trimmed_gdf.variable.unique(), trimmed_gdf.lead_time.unique(), loss_metrics, added_cols)
            data['income'] = income
            df = pd.concat([df, data], ignore_index=True)
        output.update({'income': df})

    if 'landcover' in strata_groups or 'all' in strata_groups:
        df = pd.DataFrame()
        land_gdf = joined_gdf[~pd.isna(joined_gdf.shapeName)]
        land_gdf = land_gdf[~land_gdf.duplicated(subset=['geometry', 'variable', 'lead_time'], keep='last')]
        land_data = rmse_wrapper(land_gdf, land_gdf.variable.unique(), land_gdf.lead_time.unique(), loss_metrics, added_cols)
        land_data['landcover'] = 'land'
        water_gdf = joined_gdf[pd.isna(joined_gdf.shapeName)]
        water_gdf = water_gdf[~water_gdf.duplicated(subset=['geometry', 'variable', 'lead_time'], keep='last')]
        water_data = rmse_wrapper(water_gdf, water_gdf.variable.unique(), water_gdf.lead_time.unique(), loss_metrics, added_cols)
        water_data['landcover'] = 'water'
        df = pd.concat([df, land_data, water_data], ignore_index=True)
        output.update({'landcover': df})

    return output
