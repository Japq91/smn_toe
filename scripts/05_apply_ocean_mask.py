#!/usr/bin/env python3
"""Mascara oceano-tierra y su aplicacion a los modelos procesados
(paso 05).

Reescrito en Python (antes era CDO): la cadena anterior
('mulc,0 -> setmisstoc,-1 -> addc,1' sobre el timmean de ERSSTv5)
calculaba mal la mascara -- verificado: 'cdo mulc,0' multiplica el
propio valor de relleno (_FillValue ~ -9.97e+36) por 0, da ~0, y ese 0
ya no coincide con _FillValue, asi que los puntos de tierra dejan de
quedar marcados como faltantes. Resultado: mascara = 1 (oceano) en TODO
el dominio, incluida la tierra (confirmado con 'cdo infon': el timmean
trae 175 puntos faltantes de 2016, pero tras mulc,0 quedan 0).

Ahora todo el manejo de .nc se hace con xarray (mask_and_scale=True por
defecto convierte _FillValue a NaN, y .where() reinyecta el faltante al
escribir), sin tocar netCDF4 directamente.

Un punto se considera oceano si tiene al menos un valor valido en algun
mes del registro completo de ERSSTv5 (equivalente al criterio anterior:
solo es tierra si TODOS los meses estan faltantes ahi).

Uso:
    python3 05_apply_ocean_mask.py
"""
import shutil
import sys
from pathlib import Path

import numpy as np
import xarray as xr

NON_DATA_NAMES = {
    "lat", "lon", "x", "y", "time", "lat_bnds", "lon_bnds", "time_bnds", "bnds",
}

IN_DIR = Path("data/interim/processed")
OUT_DIR = Path("data/processed/masked")
MASK_FILE = Path("data/interim/ocean_mask.nc")

VALUE_LIMIT = 400.0  # cualquier punto con |valor| > esto se vuelve NaN


def _first_data_var(ds: xr.Dataset) -> str:
    for name, var in ds.data_vars.items():
        if name not in NON_DATA_NAMES and var.ndim >= 1:
            return name
    raise ValueError("No se encontro una variable de datos en el archivo")


def _spatial_dims(data: xr.DataArray) -> tuple:
    """Devuelve las (hasta) dos ultimas dimensiones espaciales."""
    return tuple(data.dims[-2:]) if data.ndim >= 2 else tuple(data.dims)


def build_ocean_mask(ersstv5_path: Path, mask_path: Path) -> None:
    with xr.open_dataset(ersstv5_path) as ds:
        varname = _first_data_var(ds)
        print(varname,"GAAAAAAAAAAAAAAAAAAA")
        data = ds[varname]
        # xarray decodifica _FillValue -> NaN por defecto (mask_and_scale=True).
        time_dim = "time" if "time" in data.dims else data.dims[0]
        land = data.isnull().all(dim=time_dim)          # faltante en TODOS los meses -> tierra
        ocean_mask = (~land).astype("int8").rename("ocean_mask")
        ocean_mask.attrs["long_name"] = "1 = oceano, 0 = tierra (derivada de ERSSTv5)"

    ocean_mask.to_dataset().to_netcdf(mask_path)

    n_ocean = int(ocean_mask.sum().item())
    total = int(ocean_mask.size)
    print(f"Mascara construida: {n_ocean}/{total} puntos de oceano", file=sys.stderr)


def apply_mask(infile: Path, outfile: Path, ocean_mask: xr.DataArray) -> None:
    # Escribe a un archivo temporal y recien lo renombra a outfile al
    # final, si todo salio bien -- escribir in place directo sobre
    # outfile dejaba, ante cualquier excepcion a mitad de camino, una
    # copia sin mascarar pero con el nombre y dimensiones finales, que
    # el chequeo de idempotencia de abajo daba por buena para siempre.
    tmp = outfile.with_suffix(".tmp.nc")
    try:
        with xr.open_dataset(infile) as ds:
            varname = _first_data_var(ds)
            data = ds[varname]

            # Verificacion por forma: la mascara y la grilla deben coincidir.
            mask_np = np.asarray(ocean_mask.values).astype(bool)
            if mask_np.ndim != 2:
                raise ValueError(f"ocean_mask debe ser 2D, tiene ndim={mask_np.ndim}")
            spatial_shape = tuple(data.shape[-2:])
            if mask_np.shape != spatial_shape:
                raise ValueError(
                    f"ocean_mask tiene forma {mask_np.shape}, pero {varname} "
                    f"tiene forma espacial {spatial_shape} en {infile.name}"
                )

            # Mascara posicional (broadcast a (time, lat, lon)), igual que antes.
            mask_da = xr.DataArray(
                np.broadcast_to(mask_np, data.shape),
                dims=data.dims,
                coords=data.coords,
            )

            # Ultima verificacion por valor: (FGOALS-f3-L) habia un punto
            # que ERSSTv5 considera oceano pero con un valor de relleno mal
            # propagado por el regrillado (~1e35). Cualquier grilla con
            # |valor| > VALUE_LIMIT se vuelve NaN, sin importar la mascara.
            invalid = np.abs(data) > VALUE_LIMIT
            n_invalid = int(invalid.sum().item())
            if n_invalid:
                print(
                    f"  {infile.name}: {n_invalid} puntos con |valor| > "
                    f"{VALUE_LIMIT:g}, vueltos NaN",
                    file=sys.stderr,
                )

            # .where() pone NaN (= _FillValue al escribir) donde la condicion es False.
            masked = data.where(mask_da & ~invalid)

            # Preservar _FillValue y dtype originales al reemplazar la variable.
            fill = ds[varname].encoding.get("_FillValue")
            orig_dtype = ds[varname].dtype

            ds[varname] = masked
            if fill is not None:
                ds[varname].encoding["_FillValue"] = fill
            ds[varname].encoding["dtype"] = orig_dtype

            ds.to_netcdf(tmp)
        tmp.replace(outfile)
    finally:
        # Si algo fallo antes del replace, no dejar basura.
        if tmp.exists() and not outfile.exists():
            tmp.unlink(missing_ok=True)


def main() -> None:
    ersstv5 = IN_DIR / "ersstv5_region.nc"
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    if not ersstv5.exists():
        sys.exit(
            f"FALTA {ersstv5} -- corre antes los pasos 03 (ERSSTv5) y 04 "
            f"(procesamiento)."
        )

    if not MASK_FILE.exists():
        print(
            "Construyendo mascara oceano-tierra a partir de ERSSTv5 ...",
            file=sys.stderr,
        )
        build_ocean_mask(ersstv5, MASK_FILE)

    with xr.open_dataset(MASK_FILE) as ds:
        ocean_mask = ds["ocean_mask"].load()

    for f in sorted(IN_DIR.glob("tos_*.nc")):
        outfile = OUT_DIR / f.name
        if outfile.exists():
            # No basta con que exista: si el paso 04 lo reproceso porque
            # detecto un merge incompleto, esta salida enmascarada queda
            # vieja/incompleta y una comparacion solo por existencia la
            # dejaria asi para siempre.
            with xr.open_dataset(f) as d_in, xr.open_dataset(outfile) as d_out:
                n_in = int(d_in.sizes["time"])
                n_out = int(d_out.sizes["time"])
            if n_in == n_out:
                print(f"Ya procesado, se omite: {f.name}", file=sys.stderr)
                continue
            print(
                f"  {f.name}: la salida enmascarada tenia {n_out} meses, "
                f"la entrada ahora tiene {n_in} -- se reprocesa",
                file=sys.stderr,
            )
        apply_mask(f, outfile, ocean_mask)

    out_ersst = OUT_DIR / "ersstv5_region.nc"
    if not out_ersst.exists():
        shutil.copyfile(ersstv5, out_ersst)


if __name__ == "__main__":
    main()