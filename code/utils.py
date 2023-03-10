import cartopy.crs as ccrs
import cartopy.feature as cf
import numpy as np
from params import approximate_heights


SUBPLOT_KW = {
    "subplot_kw": {"projection": ccrs.PlateCarree(), "extent": [-15, 50, 35, 70]}
}

FIG_PARAMS = {
    "dpi": 300,
    "facecolor": "w",
    "transparent": False,
}

TEXT_PARAMS = {
    "horizontalalignment": "left",
    "verticalalignment": "center",
}


def add_coast_boarders(ax):
    ax.add_feature(cf.COASTLINE)
    ax.add_feature(cf.BORDERS)


vertical_dim_dic = {
    "IDL": "mlev",
    "ETH": "pressure",
    "GERICS": "lev",
    "OUR": "plev",
    "BCCR": "plev",
}


def constrain_vertical_range(ds, institution):
    """
    Restrict 3D data to height levels that are of interest for this analysis.
        GERICS: 22 - 27
        IDL: 0-5
    And sort entries in decreasing order. Initially:
        from high to low: GERICS, BCCR, ETH
        from low to high: OUR, IDL
    BCCR needs no specific handling
    """
    if institution in ["GERICS", "IDL"]:
        ranges = {"GERICS": np.arange(22, 28), "IDL": np.arange(6)}
        dim_name = vertical_dim_dic[institution]
        ds = ds.sel({dim_name: ranges[institution]})
    if institution in ["OUR", "IDL"]:
        vertical_dim = vertical_dim_dic[institution]
        ds = ds.reindex(vertical_dim=list(reversed(ds[vertical_dim])))
    return ds


def get_focus_area(ds, area_name):
    assert area_name in ["Sweden", "Germany", "Spain"]
    if area_name == "Sweden":
        rlat = slice(7, 8)
        rlon = slice(-3, -2)
    elif area_name == "Germany":
        rlon = slice(-6.5, -5.5)
        rlat = slice(1, 2)
    elif area_name == "Spain":
        rlon = slice(-18, -17)
        rlat = slice(-8, -7)
    return ds.sel(rlon=rlon, rlat=rlat).mean(dim=["rlat", "rlon"])


def replace_vertical_coordinate(ds, ins):
    initial_name = vertical_dim_dic[ins]
    ds[initial_name] = [approximate_heights[ins][x] for x in ds[initial_name].values]
    ds = ds.rename({initial_name: "approximate height"})
    ds["approximate height"].attrs = {"unit": "m"}
    return ds
