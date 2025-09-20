import json
from typing import Optional, Tuple

import numpy as np
import xarray as xr
from joblib import Parallel, delayed
from more_itertools import chunked
from numba import njit
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)

from solshade.solar import nearest_horizon_indices
from solshade.utils import get_logger

log = get_logger(__name__)


@njit(parallel=False)  # pragma: no cover
def _compute_flux_single_timestep(
    sun_alt: float,
    sun_enu: np.ndarray,  # shape (3,), dtype matches inputs
    h_slice: np.ndarray,  # (ny, nx), dtype matches inputs
    e: np.ndarray,  # (ny, nx), dtype matches inputs
    n: np.ndarray,  # (ny, nx), dtype matches inputs
    u: np.ndarray,  # (ny, nx), dtype matches inputs
    toa: float,
    dtype,
) -> np.ndarray:
    """
    Compute terrain-aware solar flux for a single timestep (Numba-accelerated).

    The kernel applies:
      - shadowing via `sun_alt >= horizon`,
      - Lambertian cosine via `max(0, n·s)`,
      - NaN propagation from horizon samples.

    All inputs should be the desired output dtype already for best performance.
    """
    ny, nx = h_slice.shape
    nan_mask = np.isnan(h_slice)

    # All-zeros if Sun below astronomical horizon; still propagate NaNs.
    if sun_alt < 0.0:
        result = np.zeros((ny, nx), dtype=dtype)
        # Branchless NaN propagation
        for j in range(ny):
            for i in range(nx):
                if nan_mask[j, i]:
                    result[j, i] = np.nan
        return result

    # Terrain horizon test (treat NaNs as blocked/False)
    # mask as float (0 or 1) for cheap multiplication
    result = np.empty((ny, nx), dtype=dtype)
    se, sn, su = sun_enu[0], sun_enu[1], sun_enu[2]

    for j in range(ny):
        for i in range(nx):
            if nan_mask[j, i]:
                result[j, i] = np.nan
                continue
            if sun_alt < h_slice[j, i]:
                result[j, i] = 0.0
                continue
            # Lambertian cosine
            dot = e[j, i] * se + n[j, i] * sn + u[j, i] * su
            if dot > 0.0:
                result[j, i] = dot * toa
            else:
                result[j, i] = 0.0

    return result


def compute_flux_timeseries(
    horizon: xr.DataArray,
    sun_alt_deg: np.ndarray,
    sun_az_deg: np.ndarray,
    sun_au: np.ndarray,
    sun_enu: np.ndarray,
    normal_enu: xr.DataArray,
    times_utc: np.ndarray,
    *,
    toa: float = 1361.0,
    dtype: np.dtype = np.dtype(np.float32),
    n_jobs: int = -1,
    batch_size: int = 512,
    backend: str = "threading",
    prefer: Optional[str] = "threads",
) -> xr.DataArray:
    """
    Compute horizon-masked, Lambertian irradiance time series over a DEM in parallel.

    Overview
    --------
    Per time step t:
      1) Sun direction `sun_enu[t]` (unit vector in ENU).
      2) Terrain unit normals per pixel from `normal_enu` bands (east, north, up).
      3) Sample horizon at nearest azimuth to `sun_az_deg[t]` to get skyline elevation per pixel.
      4) Shadow: if `sun_alt_deg[t] < horizon`, irradiance = 0; else Lambertian `max(0, n·s)`.
      5) Scale by TOA (`toa`) and propagate NaNs from horizon.

    Parallel Execution
    ------------------
    Time steps are processed in parallel with joblib. You can control:
      - `n_jobs`: number of workers (use -1 for all cores),
      - `batch_size`: number of time steps batched per dispatch,
      - `backend`: "threading" (recommended here) or "loky",
      - `prefer`: scheduler hint; "threads" helps nudge thread pool behavior.

    TOA and units
    -------------
    `toa` is the top-of-atmosphere solar irradiance in W·m⁻² (default 1361).
    Output irradiance is `toa * max(0, n · s_enu)` with no atmospheric correction.

    NaN propagation
    ---------------
    If horizon is NaN for a pixel at time t, the output flux at that (t, y, x)
    is set to NaN — regardless of Sun altitude.

    Parameters
    ----------
    horizon : xarray.DataArray
        Horizon elevation angles (deg), shape (azimuth|band, y, x).
        The azimuth dimension is either "azimuth" or "band" (GeoTIFF).
    sun_alt_deg : np.ndarray, shape (T,)
        Sun altitude in degrees per time step.
    sun_az_deg : np.ndarray, shape (T,)
        Sun azimuth in degrees (CW from North) per time step.
    sun_au : np.ndarray, shape (T,)
        Sun distance in Astronomical Units (au).
    sun_enu : np.ndarray, shape (T, 3)
        Unit Sun direction vectors (E, N, U).
    normal_enu : xarray.DataArray, shape (band=3, y, x)
        Terrain unit normal components with bands ["east","north","up"].
    times_utc : np.ndarray
        Numpy datetime64 array which is attached as the
        DataArray coordinate and also stored as ISO UTC strings in attrs.

    Other Parameters
    ----------------
    toa : float, default 1361.0
        Top-of-atmosphere irradiance in W·m⁻².
    dtype : dtype, default np.float32
        Output dtype (and the computation dtype for inputs we cast below).
    n_jobs : int, default -1
        Parallel workers (via joblib). -1 = all cores.
    batch_size : int, default 128
        Number of time steps per joblib batch.
    backend : {"threading","loky"}, default "threading"
        Joblib backend. "threading" is typically best here.
    prefer : {"threads","processes",None}, default "threads"
        Scheduler hint for joblib.

    Returns
    -------
    flux : xarray.DataArray (time, y, x), dtype=`dtype`
        Irradiance (W·m⁻²), horizon-masked Lambertian model.
        attrs:
          - "units": "W m^-2"
          - "note": description
          - "time_utc_iso": JSON list of ISO UTC strings (if `times_utc` provided)
          - "toa_W_m2": float

    Raises
    ------
    ValueError
        On mismatched shapes, missing dims or missing attributes
    KeyError
        If `normal_enu` lacks bands "east","north","up".

    Logging
    -------
    - INFO: Problem size and parallel execution parameters.
    - DEBUG: shape checks, dtype casting, AU scaling, batching progress.
    """
    # Validate horizon dims
    az_dim = "azimuth" if "azimuth" in horizon.dims else ("band" if "band" in horizon.dims else None)
    if az_dim is None:
        log.error("`horizon` missing 'azimuth'/'band' dimension")
        raise ValueError("`horizon` must have a leading 'azimuth' or 'band' dimension.")
    if not {"y", "x"}.issubset(horizon.dims):
        log.error("`horizon` missing spatial dims")
        raise ValueError("`horizon` must have spatial dims ('y','x').")
    if not {"band", "y", "x"}.issubset(normal_enu.dims):
        log.error("`normal_enu` missing required dims ('band','y','x')")
        raise ValueError("`normal_enu` must have dims ('band','y','x').")

    # horizon azimuths must be present in attrs
    try:
        horizon_az_deg = np.asarray(json.loads(horizon.attrs["azimuths_deg"]), dtype=float)
    except Exception as exc:  # noqa: BLE001
        log.error("`horizon` missing attrs['azimuths_deg']")
        raise ValueError("`horizon` is missing attrs['azimuths_deg'] with uniform azimuth samples.") from exc

    y_dim, x_dim = horizon.sizes["y"], horizon.sizes["x"]
    n_times = int(sun_alt_deg.size)
    if sun_az_deg.size != n_times or sun_enu.shape != (n_times, 3):
        log.error("Length mismatch among sun_alt_deg, sun_az_deg, and sun_enu")
        raise ValueError("Length mismatch among sun_alt_deg, sun_az_deg, and sun_enu.")

    # validate sun_au
    sun_au = np.asarray(sun_au, dtype=np.float32)
    if sun_au.shape != (n_times,):
        log.error("`sun_au` wrong shape: %s", sun_au.shape)
        raise ValueError("`sun_au` must have shape (T,) matching time axis.")
    if not np.isfinite(sun_au).all():
        log.error("`sun_au` contains non-finite values")
        raise ValueError("`sun_au` contains non-finite values.")
    sun_au = np.maximum(sun_au, np.float32(1e-6))  # guard

    # Extract normals; cast once to target dtype & ensure contiguity.
    try:
        e = np.ascontiguousarray(normal_enu.sel(band="east").values, dtype=dtype)
        n = np.ascontiguousarray(normal_enu.sel(band="north").values, dtype=dtype)
        u = np.ascontiguousarray(normal_enu.sel(band="up").values, dtype=dtype)
    except Exception as exc:  # noqa: BLE001
        log.error("`normal_enu` must contain bands ['east','north','up']")
        raise KeyError("`normal_enu` must contain bands ['east','north','up'].") from exc

    horizon_np = np.ascontiguousarray(horizon.values)
    az_idx = nearest_horizon_indices(sun_az_deg, horizon_az_deg)

    log.info(
        f"Flux timeseries: T={n_times}, grid=({y_dim}x{x_dim}), dtype={dtype}, "
        f"n_jobs={n_jobs}, batch_size={batch_size}, backend={backend}, prefer={prefer}"
    )

    flux_data = np.empty((n_times, y_dim, x_dim), dtype=dtype)

    # Optional time coordinate & attrs-strings
    time_coord: Optional[np.ndarray] = None
    time_iso: Optional[list[str]] = None
    if isinstance(times_utc, np.ndarray) and np.issubdtype(times_utc.dtype, np.datetime64):
        time_coord = times_utc.astype("datetime64[s]")
        time_iso = np.datetime_as_string(time_coord, unit="s", timezone="UTC").tolist()  # type: ignore
        log.debug("Attached time coordinate with %d samples", time_coord.size)

    # 1/r^2 scaling per time (float32 to match inner ops)
    toa_scaled = np.asarray(toa, dtype=np.float32) / (sun_au**2)
    log.debug("Prepared TOA scaling with AU^-2; range: [%.6f, %.6f]", float(toa_scaled.min()), float(toa_scaled.max()))

    def compute_single(t: int) -> Tuple[int, np.ndarray]:
        h_slice = np.ascontiguousarray(horizon_np[az_idx[t]].astype(dtype, copy=False))
        s_enu = np.asarray(sun_enu[t], dtype=dtype)
        toa_t = float(toa_scaled[t])
        res = _compute_flux_single_timestep(
            float(sun_alt_deg[t]),
            s_enu,
            h_slice,
            e,
            n,
            u,
            toa_t,
            dtype,
        )
        return t, res

    log.debug("Dispatching batch of %d timesteps", batch_size)
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]Computing irradiance"),
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        TimeElapsedColumn(),
        TimeRemainingColumn(),
    ) as bar:
        task = bar.add_task("irradiance", total=n_times)
        for batch in chunked(range(n_times), batch_size):
            results = Parallel(n_jobs=n_jobs, backend=backend, prefer=prefer)(delayed(compute_single)(t) for t in batch)
            for t, result_slice in results:  # type: ignore
                flux_data[t] = result_slice
            bar.update(task, advance=len(batch))

    attrs = {
        "units": "W m^-2",
        "note": "Lambertian, horizon-masked; TOA scaling (1/AU^2) only; no atmosphere.",
        "toa_W_m2": float(toa),  # solar constant at 1 AU
    }
    if time_iso is not None:
        attrs["time_utc_iso"] = json.dumps(time_iso)

    log.info("Flux timeseries computed: shape=%s, dtype=%s", flux_data.shape, flux_data.dtype)

    return xr.DataArray(
        flux_data,
        dims=("time", "y", "x"),
        coords={
            "time": time_coord if time_coord is not None else np.arange(n_times),
            "y": horizon["y"],
            "x": horizon["x"],
        },
        name="irradiance",
        attrs=attrs,
    )


def compute_energy_metrics(flux: xr.DataArray) -> tuple[xr.DataArray, xr.DataArray, xr.DataArray, xr.DataArray]:
    """
    Compute daily, total, peak energy, and day-of-peak from a time series of flux.

    Strategy:
    - Daily integration uses trapezoidal rule over time per day.
    - If *any* NaNs are present in a day's flux values for a pixel, that day's energy is set to NaN.
    - If *any* daily energy is NaN for a pixel, all metrics for that pixel are set to NaN.

    Returns
    -------
    daily_energy : xr.DataArray   # units: J m^-2
    total_energy : xr.DataArray   # units: J m^-2
    peak_energy  : xr.DataArray   # units: J m^-2
    day_of_peak  : xr.DataArray   # integer DoY (1–366)

    Logging
    -------
    - INFO: reports daily integration and masks.
    - DEBUG: shapes and dtype of outputs.
    """
    log.info("Computing energy metrics from flux: dims=%s, dtype=%s", flux.sizes, flux.dtype)

    # Strict daily integration: NaN if *any* timestep that day is NaN
    def safe_integrate_day(da):
        # da: (time, y, x) for a single day
        nanmask = da.isnull().any(dim="time")
        integrated = da.integrate("time", datetime_unit="s")
        return integrated.where(~nanmask)

    # Group by day and apply strict integration
    daily_energy = flux.resample(time="1D").map(safe_integrate_day).astype("float32")
    invalid_mask = daily_energy.isnull().any(dim="time")

    total_energy = daily_energy.sum(dim="time", skipna=True).where(~invalid_mask)
    peak_energy = daily_energy.max(dim="time", skipna=True).where(~invalid_mask)
    peak_dates = daily_energy.astype("float64").idxmax(dim="time", skipna=True).where(~invalid_mask)
    day_of_peak = peak_dates.dt.dayofyear.where(~invalid_mask)

    log.debug(
        "Energy metrics shapes: daily=%s, total=%s, peak=%s, day_of_peak=%s",
        daily_energy.sizes,
        total_energy.sizes,
        peak_energy.sizes,
        day_of_peak.sizes,
    )

    return daily_energy, total_energy, peak_energy, day_of_peak
