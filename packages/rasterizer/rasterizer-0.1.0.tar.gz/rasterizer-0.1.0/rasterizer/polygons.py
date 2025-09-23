import geopandas as gpd
import numpy as np
import xarray as xr

from .numba_impl import _rasterize_polygons_engine
from .rasterizer import geocode


def compute_exterior(gdf_poly: gpd.GeoDataFrame) -> np.ndarray:
    """
    Computes the exterior coordinates of a GeoDataFrame of polygons.
    """
    return gdf_poly.geometry.exterior.get_coordinates().reset_index().values


def compute_interiors(gdf_poly: gpd.GeoDataFrame) -> np.ndarray:
    """
    Computes the interior coordinates of a GeoDataFrame of polygons.
    """
    interiors = gdf_poly.geometry.interiors
    ret = interiors.explode(ignore_index=False).dropna().rename("geometry").reset_index()
    if ret.empty:
        return np.empty((0, 4), dtype=np.float32)

    temp_df = ret.reset_index()
    temp_df["sub_index"] = ret.groupby("index").cumcount()
    ret["sub_index"] = temp_df["sub_index"].values

    ret = gpd.GeoDataFrame(geometry=ret.geometry, data=ret[["index", "sub_index"]])
    return ret.set_index(["index", "sub_index"]).get_coordinates().reset_index().values


def rasterize_polygons(
    polygons: gpd.GeoDataFrame,
    x: np.ndarray,
    y: np.ndarray,
    crs,
    mode: str = "area",
) -> xr.DataArray:
    """
    Rasterizes a GeoDataFrame of Polygon and MultiPolygon on a regular grid.

    Args:
        polygons (gpd.GeoDataFrame): GeoDataFrame containing the polygon geometries.
        x (np.ndarray): 1D array of x-coordinates of the cell centers.
        y (np.ndarray): 1D array of y-coordinates of the cell centers.
        crs: The coordinate reference system of the output grid.
        mode (str, optional): 'binary' or 'area'. Defaults to 'area'.
            - 'binary': the cell is True if covered, False otherwise.
            - 'area': the cell contains the area of the polygon that covers it.

    Returns:
        xr.DataArray: A rasterized DataArray.
    """
    if mode not in ["binary", "area"]:
        raise ValueError("Mode must be 'binary' or 'area'")

    polygons = polygons.copy()
    polygons.geometry = polygons.geometry.force_2d()

    geom_types = polygons.geometry.geom_type
    polygons = polygons[geom_types.isin(["Polygon", "MultiPolygon"])]

    polygons_proj = polygons.to_crs(crs)

    if polygons_proj.empty or len(x) < 2 or len(y) < 2:
        if mode == "binary":
            raster_data = np.full((len(y), len(x)), False, dtype=bool)
        else:
            raster_data = np.zeros((len(y), len(x)), dtype=np.float32)
        raster = xr.DataArray(raster_data, coords={"y": y, "x": x}, dims=["y", "x"])
        return geocode(raster, "x", "y", crs)

    dx = x[1] - x[0]
    dy = y[1] - y[0]
    half_dx = dx / 2.0
    half_dy = dy / 2.0

    x_grid_min, x_grid_max = x[0] - half_dx, x[-1] + half_dx
    y_grid_min, y_grid_max = y[0] - half_dy, y[-1] + half_dy

    polygons_proj = polygons_proj.explode(index_parts=False, ignore_index=True)
    num_polygons = len(polygons_proj)

    if num_polygons == 0:
        if mode == "binary":
            raster_data = np.full((len(y), len(x)), False, dtype=bool)
        else:
            raster_data = np.zeros((len(y), len(x)), dtype=np.float32)
        raster = xr.DataArray(raster_data, coords={"y": y, "x": x}, dims=["y", "x"])
        return geocode(raster, "x", "y", crs)

    exteriors = compute_exterior(polygons_proj)
    interiors = compute_interiors(polygons_proj)

    exteriors_coords = np.ascontiguousarray(exteriors[:, 1:3]).astype(np.float32)
    ext_boundaries = np.where(exteriors[:-1, 0] != exteriors[1:, 0])[0] + 1
    exteriors_offsets = np.concatenate(([0], ext_boundaries, [exteriors.shape[0]]))

    interiors_coords = np.empty((0, 2), dtype=np.float32)
    interiors_ring_offsets = np.array([0], dtype=np.intp)
    interiors_poly_offsets = np.full(num_polygons + 1, 0, dtype=np.intp)

    if interiors.shape[0] > 0:
        interiors_coords = np.ascontiguousarray(interiors[:, 2:4]).astype(np.float32)
        int_ids = interiors[:, :2]
        int_ring_boundaries = np.where((int_ids[:-1, 0] != int_ids[1:, 0]) | (int_ids[:-1, 1] != int_ids[1:, 1]))[0] + 1
        interiors_ring_offsets = np.concatenate(([0], int_ring_boundaries, [int_ids.shape[0]]))

        int_ring_poly_idx = interiors[interiors_ring_offsets[:-1], 0].astype(np.intp)

        # Create offsets for interiors per polygon. This finds the start index
        # for each polygon's run of interior rings.
        interiors_poly_offsets = np.searchsorted(
            int_ring_poly_idx, np.arange(num_polygons + 1), side="left"
        )


    raster_data_float = _rasterize_polygons_engine(
        num_polygons,
        exteriors_coords,
        exteriors_offsets,
        interiors_coords,
        interiors_ring_offsets,
        interiors_poly_offsets,
        x,
        y,
        half_dx,
        half_dy,
        x_grid_min,
        x_grid_max,
        y_grid_min,
        y_grid_max,
        mode == "binary",
    )

    if mode == "binary":
        raster_data = raster_data_float.astype(bool)
    else:
        raster_data = raster_data_float

    raster = xr.DataArray(raster_data, coords={"y": y, "x": x}, dims=["y", "x"])

    return geocode(raster, "x", "y", crs)
