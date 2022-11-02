import cartopy.crs as ccrs
import cartopy.feature as cf

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
