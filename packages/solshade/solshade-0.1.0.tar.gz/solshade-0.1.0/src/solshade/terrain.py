import json
import warnings
from pathlib import Path
from typing import Callable, Optional, cast

import numpy as np
import rioxarray as rxr
import xarray as xr
from joblib import Parallel, delayed
from numba import njit, prange
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn, TimeRemainingColumn
from scipy.interpolate import CubicSpline, interp1d
from scipy.ndimage import map_coordinates

from solshade.utils import get_logger

log = get_logger(__name__)


def load_dem(path: str | Path) -> xr.DataArray:
    """
    Load a single-band Digital Elevation Model (DEM) from a GeoTIFF file.

    Uses rioxarray to preserve CRS and coordinate metadata.

    Parameters
    ----------
    path : str or Path
        Path to a single-band GeoTIFF file containing elevation data.
        The file must contain exactly one raster band.

    Returns
    -------
    dem : xarray.DataArray
        A 2D array of elevation values with dimensions (y, x),
        including CRS, transform, and coordinate metadata.

    Raises
    ------
    TypeError
        If the input file contains more than one band or does not reduce to a DataArray.

    Notes
    -----
    - Elevation units are inherited from the input file (typically meters).
    - The spatial reference (CRS) must be projected (not geographic/latlon).
    - Squeezes band dimension if present.
    - Logging: this function logs basic file/metadata information at INFO level.
    """
    log.debug(f"Loading DEM from {path}")
    raw = cast(xr.Dataset, rxr.open_rasterio(path, masked=True))
    squeezed = raw.squeeze()

    if not isinstance(squeezed, xr.DataArray):
        log.error(f"DEM at {path} has multiple bands or is not a DataArray")
        raise TypeError("DEM is not a single-band raster.")

    try:
        crs_str = squeezed.rio.crs.to_string() if squeezed.rio.crs else "None"
        res = squeezed.rio.resolution()
    except Exception:  # pragma: no cover (very defensive)
        crs_str, res = "Unknown", ("?", "?")

    log.info(f"Loaded DEM: shape={squeezed.shape}, CRS={crs_str}, resolution={res}")
    return squeezed


def compute_slope_aspect_normals(
    dem: xr.DataArray,
) -> tuple[xr.DataArray, xr.DataArray, xr.DataArray]:
    """
    Compute slope, aspect, and ENU unit normal vectors from a DEM.

    Slope and aspect follow GIS conventions:
    - Slope: angle from horizontal (0° flat, 90° vertical).
    - Aspect: compass direction of steepest descent, clockwise from North (0°=N, 90°=E).

    Parameters
    ----------
    dem : xarray.DataArray
        2D DEM with projected CRS and linear units (e.g., meters).

    Returns
    -------
    slope : xarray.DataArray (y, x)
        Slope in degrees.
    aspect : xarray.DataArray (y, x)
        Aspect in degrees clockwise from North.
    normal_enu : xarray.DataArray (3, y, x)
        ENU unit normal vectors. Bands: [east, north, up].

    Notes
    -----
    Normal vector components:
        E = sin(slope) * sin(aspect)
        N = sin(slope) * cos(aspect)
        U = cos(slope)

    Logging
    -------
    - DEBUG: DEM shape and pixel resolution.
    - INFO: completion of slope/aspect/normal computation.
    """
    log.debug(f"Computing slope/aspect/normals for DEM with shape={dem.shape}")
    z = dem.values
    dy, dx = dem.rio.resolution()
    dx = abs(dx)
    dy = abs(dy)
    log.debug(f"DEM resolution: dx={dx:.6f}, dy={dy:.6f}")

    dzdy, dzdx = np.gradient(z, dy, dx)

    slope_rad = np.arctan(np.hypot(dzdx, dzdy))
    slope_deg = np.degrees(slope_rad)

    aspect_rad = np.arctan2(-dzdx, dzdy)
    aspect_deg = (np.degrees(aspect_rad) + 360) % 360

    slope = xr.DataArray(
        slope_deg,
        coords=dem.coords,
        dims=dem.dims,
        attrs={"units": "degrees", "long_name": "slope"},
    )

    aspect = xr.DataArray(
        aspect_deg,
        coords=dem.coords,
        dims=dem.dims,
        attrs={"units": "degrees", "long_name": "aspect"},
    )

    # Convert to radians
    slope_r = np.deg2rad(slope_deg)
    aspect_r = np.deg2rad(aspect_deg)

    # ENU normal components
    east = np.sin(slope_r) * np.sin(aspect_r)
    north = np.sin(slope_r) * np.cos(aspect_r)
    up = np.cos(slope_r)

    normal_vec = np.stack([east, north, up], axis=0)  # (3, y, x)

    # Normalize
    norms = np.linalg.norm(normal_vec, axis=0, keepdims=True)
    normal_vec = np.divide(normal_vec, norms, out=np.zeros_like(normal_vec), where=norms > 0)

    normal_enu = xr.DataArray(
        normal_vec,
        coords={"band": ["east", "north", "up"], dem.dims[0]: dem[dem.dims[0]], dem.dims[1]: dem[dem.dims[1]]},
        dims=("band", *dem.dims),
        attrs={"description": "Terrain normal unit vector in ENU coordinates"},
    )

    log.info("Computed slope/aspect/normals")
    return slope, aspect, normal_enu


def compute_hillshade(
    slope: xr.DataArray,
    aspect: xr.DataArray,
    azimuth_deg: float = 315.0,
    altitude_deg: float = 45.0,
) -> xr.DataArray:
    """
    Compute a hillshade array using slope and aspect with Lambertian illumination.

    Parameters
    ----------
    slope : xarray.DataArray
        Slope in degrees.
    aspect : xarray.DataArray
        Aspect in degrees clockwise from north.
    azimuth_deg : float, optional
        Azimuth angle of the sun (0° = north, 90° = east). Default is 315°.
    altitude_deg : float, optional
        Altitude angle of the sun above the horizon. Default is 45°.

    Returns
    -------
    hillshade : xarray.DataArray
        Normalized hillshade values from 0 (dark) to 1 (bright),
        preserving coordinates and CRS metadata.

    Notes
    -----
    - Uses a Lambertian reflection model.
    - All input and output arrays are 2D.

    Logging
    -------
    - DEBUG: sun azimuth/altitude inputs.
    - INFO: completion of hillshade.
    """
    log.debug(f"Computing hillshade: azimuth={azimuth_deg:.2f}°, altitude={altitude_deg:.2f}°")
    slope_rad = np.radians(slope)
    aspect_rad = np.radians(aspect)
    az_rad = np.radians(azimuth_deg)
    alt_rad = np.radians(altitude_deg)

    shaded = np.sin(alt_rad) * np.cos(slope_rad) + np.cos(alt_rad) * np.sin(slope_rad) * np.cos(az_rad - aspect_rad)
    hillshade = np.clip(shaded, 0, 1)

    log.info("Computed hillshade")
    return xr.DataArray(
        hillshade,
        coords=slope.coords,
        dims=slope.dims,
        attrs={"units": "unitless", "long_name": "hillshade"},
    )


def compute_horizon_map(
    dem: xr.DataArray,
    n_directions: int = 360,
    max_distance: float = 5000,
    step: float = 20,
    chunk_size: int = 32,
    n_jobs: int = -1,
    progress: bool = True,
) -> xr.DataArray:
    """
    Compute a per-pixel horizon angle map from a digital elevation model (DEM)
    using chunked ray tracing.

    For each pixel, rays are cast in `n_directions` azimuthal directions
    and sampled up to `max_distance` away. The maximum elevation angle
    encountered along each ray is recorded as the local horizon.

    Parallel processing is done with Joblib, and a rich progress bar can
    optionally be shown.

    Parameters
    ----------
    dem : xr.DataArray
        Input digital elevation model with a defined CRS and affine transform.
        Must be a 2D array with shape (y, x) and spatial coordinates.
    n_directions : int, optional
        Number of azimuthal directions to trace (default is 64).
    max_distance : float, optional
        Maximum distance (in meters) to trace each ray from each pixel
        (default is 5000 m).
    step : float, optional
        Distance step (in meters) between ray samples (default is 20 m).
    chunk_size : int, optional
        Size (in pixels) of square chunks to process independently
        (default is 32).
    n_jobs : int, optional
        Number of parallel jobs to run. Use -1 to use all available cores
        (default is -1).
    progress : bool, optional
        If True, display a rich progress bar (default is True).

    Returns
    -------
    xr.DataArray
        A 3D xarray DataArray with dimensions (azimuth, y, x), representing
        the local horizon angle (in degrees) in each direction for each pixel.
        The azimuthal directions are stored in the `azimuth` coordinate.

    Logging
    -------
    - INFO: parameters used and final shape.
    - DEBUG: chunking details, dispatching jobs, pixel sizes.
    - WARN: defensive warnings if a None chunk were returned.
    """
    if dem.rio.crs is None or dem.rio.transform() is None:
        log.error("DEM missing CRS or affine transform")
        raise ValueError("DEM must have CRS and affine transform defined.")

    log.info(
        "Computing horizon map (n_directions=%d, max_distance=%.1f, step=%.1f, chunk_size=%d, n_jobs=%d, progress=%s)",
        n_directions,
        max_distance,
        step,
        chunk_size,
        n_jobs,
        progress,
    )

    transform = dem.rio.transform()
    res_x, res_y = transform.a, -transform.e
    ny, nx = dem.shape
    log.debug(f"DEM size: nx={nx}, ny={ny}; pixel size: ({res_x:.6f}, {res_y:.6f})")

    azimuths = np.linspace(0, 360, n_directions, endpoint=False)
    distances = np.arange(0, max_distance + step, step)
    ns = len(distances)

    dx_pix = np.cos(np.deg2rad(azimuths))[:, np.newaxis] * distances / res_x
    dy_pix = -np.sin(np.deg2rad(azimuths))[:, np.newaxis] * distances / res_y
    dx_pix = dx_pix[np.newaxis, np.newaxis, :, :]
    dy_pix = dy_pix[np.newaxis, np.newaxis, :, :]

    @njit(parallel=True)  # pragma: no cover
    def _compute_horizon(elev_prof, distances, out_arr):
        nyc, nxc, nd, ns = elev_prof.shape
        for iy in prange(nyc):
            for ix in prange(nxc):
                for idir in range(nd):
                    elev0 = elev_prof[iy, ix, idir, 0]
                    if np.isnan(elev0):
                        out_arr[iy, ix, idir] = np.nan
                        continue
                    max_ang = -np.inf
                    for idist in range(1, ns):
                        elev_sample = elev_prof[iy, ix, idir, idist]
                        if np.isnan(elev_sample):
                            continue
                        dz = elev_sample - elev0
                        angle = np.arctan2(dz, distances[idist])
                        max_ang = max(max_ang, angle)
                    out_arr[iy, ix, idir] = np.nan if max_ang == -np.inf else np.rad2deg(max_ang)

    def process_chunk(x0, y0):
        y1 = min(y0 + chunk_size, ny)
        x1 = min(x0 + chunk_size, nx)

        iy, ix = np.mgrid[y0:y1, x0:x1]
        iy = iy[..., np.newaxis, np.newaxis]
        ix = ix[..., np.newaxis, np.newaxis]

        sample_y = iy + dy_pix
        sample_x = ix + dx_pix
        sample_coords = np.stack([sample_y, sample_x], axis=0)

        elev_profiles = map_coordinates(
            dem.values,
            sample_coords.reshape(2, -1),
            order=1,
            mode="constant",
            cval=np.nan,
        ).reshape(y1 - y0, x1 - x0, n_directions, ns)

        chunk_out = np.full((y1 - y0, x1 - x0, n_directions), np.nan, dtype=np.float32)
        _compute_horizon(elev_profiles, distances, chunk_out)

        return y0, y1, x0, x1, chunk_out

    tasks = [(x0, y0) for y0 in range(0, ny, chunk_size) for x0 in range(0, nx, chunk_size)]
    log.debug(f"Prepared {len(tasks)} chunks")
    horizon_data = np.full((n_directions, ny, nx), np.nan, dtype=np.float32)

    warnings.filterwarnings(
        "ignore", category=UserWarning, message=".*worker stopped while some jobs were given to the executor.*"
    )

    def run_all():
        return Parallel(n_jobs=n_jobs, return_as="generator")(delayed(process_chunk)(x0, y0) for x0, y0 in tasks)

    log.debug(f"Dispatching {len(tasks)} jobs with n_jobs={n_jobs}")
    if progress:
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]Computing horizon map"),
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.0f}%",
            TimeElapsedColumn(),
            TimeRemainingColumn(),
        ) as bar:
            task_id = bar.add_task("computing", total=len(tasks))
            results = run_all()
            for result in results:
                if result is not None:
                    y0, y1, x0, x1, chunk = result
                    horizon_data[:, y0:y1, x0:x1] = np.moveaxis(chunk, -1, 0)
                else:  # pragma: no cover (defensive)
                    log.warning("Received None result for a chunk")
                bar.advance(task_id)
    else:
        for result in run_all():
            if result is not None:
                y0, y1, x0, x1, chunk = result
                horizon_data[:, y0:y1, x0:x1] = np.moveaxis(chunk, -1, 0)
            else:  # pragma: no cover (defensive)
                log.warning("Received None result for a chunk (no-progress mode)")

    horizon_da = xr.DataArray(
        horizon_data,
        dims=("azimuth", "y", "x"),
        coords={"azimuth": azimuths, "y": dem.y, "x": dem.x},
        name="horizon_angle",
        attrs={"units": "degrees"},
    )
    horizon_da.rio.write_crs(dem.rio.crs, inplace=True)
    horizon_da.rio.set_spatial_dims(x_dim="x", y_dim="y", inplace=True)
    horizon_da.rio.write_transform(dem.rio.transform(), inplace=True)
    horizon_da.attrs.update(
        {
            "max_distance_m": max_distance,
            "step_m": step,
            "n_directions": n_directions,
            "azimuth_meaning": "Azimuthal directions clockwise from North",
            "azimuths_deg": json.dumps(azimuths.tolist()),
        }
    )

    log.info(f"Horizon map computed: shape={horizon_da.shape} (azimuth,y,x) with {n_directions} directions")
    return horizon_da


def horizon_interp(
    azimuths: np.ndarray,
    horizon_vals: np.ndarray,
    fallback_frac: float = 0.5,
) -> Optional[Callable]:
    """
    Interpolate horizon angles as a function of azimuth using cubic interpolation,
    ensuring periodic continuity. Falls back to linear if data is sparse or if
    cubic interpolation yields unphysical results.

    Parameters
    ----------
    azimuths : np.ndarray
        1D array of azimuth angles in degrees [0, 360).
    horizon_vals : np.ndarray
        1D array of horizon angles (in degrees), same shape as azimuths.
        May contain NaNs.
    fallback_frac : float, optional
        Threshold fraction of NaNs above which to fall back to linear interpolation.

    Returns
    -------
    interp_func : callable or None
        A function that takes azimuth(s) in degrees and returns interpolated
        horizon angle(s). Returns None if no valid data.

    Logging
    -------
    - DEBUG: data completeness, ranges, and interpolation path taken.
    - INFO: chosen interpolation (cubic vs linear) and output range when applicable.
    - WARN: cubic spline unphysical output fallback.
    """
    log.debug(f"Building horizon interpolation (fallback_frac={fallback_frac:.2f})")
    az_valid = azimuths[~np.isnan(horizon_vals)]
    vals_valid = horizon_vals[~np.isnan(horizon_vals)]

    if len(vals_valid) == 0:
        log.info("No valid horizon data — returning None.")
        return None

    nan_frac = np.isnan(horizon_vals).sum() / len(horizon_vals)
    log.debug(
        "Valid points: %d / %d (%.1f%% valid); azimuth range=[%.2f, %.2f]; value range=[%.2f, %.2f]",
        len(vals_valid),
        len(horizon_vals),
        (1 - nan_frac) * 100,
        float(az_valid.min()),
        float(az_valid.max()),
        float(vals_valid.min()),
        float(vals_valid.max()),
    )

    # Enforce periodicity only if we already have a valid value at 0.0 deg
    if az_valid[0] == 0.0:
        log.debug("Enforcing periodicity by copying value at 0.0° to 360.0°")
        az_valid = np.append(az_valid, 360.0)
        vals_valid = np.append(vals_valid, vals_valid[0])

    # Attempt cubic interpolation if data is sufficiently complete
    if nan_frac <= fallback_frac:
        try:
            interp_func = CubicSpline(az_valid, vals_valid, bc_type="periodic")
            test_vals = interp_func(np.arange(361))
            min_val, max_val = np.nanmin(test_vals), np.nanmax(test_vals)

            if min_val < -90 or max_val > 90:
                log.warning(
                    f"CubicSpline produced unphysical output: min={min_val:.2f}, max={max_val:.2f} — falling back to linear"
                )
                raise ValueError("Unphysical cubic spline result")

            log.info(f"Using CubicSpline interpolation; output range=[{min_val:.2f}, {max_val:.2f}]")
        except Exception as e:
            log.debug(f"CubicSpline interpolation failed: {e} — using linear interp1d")
            interp_func = interp1d(
                az_valid,
                vals_valid,
                kind="linear",
                bounds_error=False,
                fill_value="extrapolate",  # type: ignore[arg-type]
            )
    else:
        log.info(f"Too many NaNs ({nan_frac * 100:.1f}%) — using linear interp1d")
        interp_func = interp1d(
            az_valid,
            vals_valid,
            kind="linear",
            bounds_error=False,
            fill_value="extrapolate",  # type: ignore[arg-type]
        )

    def wrapped_interp(query_az):
        return interp_func(np.mod(query_az, 360))

    return wrapped_interp
