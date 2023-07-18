# Translate hub height wind speeds to capacity factor timeseries

from utils_from_CESM2energy import *
from multiprocessing import Pool


class CF_computation:
    """
    Class to enable parallel execution of wind power conversion
    """

    def __init__(self, ins, experiment):
        self.P = Power(
            1
        )  # Instantiate turbine SWT120-3600 (i.e., the median turbine at 7m/s)
        self.ins = ins
        self.experiment = experiment

    def compute_CF(self, year):
        # Open hub height winds
        ds_wind = xr.open_dataset(
            (
                "../output/hub_height_wind/S_hub_"
                + self.ins
                + "_"
                + year
                + "_"
                + self.experiment
                + ".nc"
            )
        )
        # Convert to capacity factor
        wind_power = xr.apply_ufunc(
            self.P.power_conversion,
            ds_wind["S_hub"],
            vectorize=True,
            dask="allowed",
        ).to_dataset()
        # Save
        wind_power.to_netcdf(
            "../output/generation/"
            + self.ins
            + "_"
            + self.P.turbine_name
            + "_"
            + year
            + "_"
            + self.experiment
            + ".nc"
        )


def run_parallel():
    """
    Loop over institutions and experiments and compute capacity factor for 30y in parallel
    """
    for ins in ["GERICS", "IDL"]:
        for experiment in ["GRASS", "FOREST"]:
            print(ins + " " + experiment)
            CF = CF_computation(ins, experiment)
            with Pool(30) as pool:  # 1 worker per year
                pool.map(CF.compute_CF, np.arange(1986, 2016))


if __name__ == "__main__":
    run_parallel()
