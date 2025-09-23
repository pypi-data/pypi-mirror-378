import rioxarray as rio
import xarray as xr


def geocode(ds: xr.DataArray, x_name: str, y_name: str, crs) -> xr.DataArray:
    """
    Geocodes an xarray DataArray.
    """
    ds.rio.set_spatial_dims(x_dim=x_name, y_dim=y_name, inplace=True)
    ds.rio.write_crs(crs, inplace=True)
    return ds
