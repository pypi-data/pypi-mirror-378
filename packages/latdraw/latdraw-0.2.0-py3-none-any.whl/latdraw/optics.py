import os

import pandas as pd

import latdraw.lattice as lattice

try:
    import tfs

    TFS = True
except ImportError:
    TFS = False

try:
    import pand8

    MAD8 = True
except ImportError:
    MAD8 = False


COMMON_OPTICS_NAMES = {
    "s": ["s", "SUML", "z"],
    "beta_x": ["BETX", "beta_x"],
    "beta_y": ["BETY", "beta_y"],
    "alpha_x": ["ALFX", "alpha_x"],
    "alpha_y": ["ALFY", "alpha_y"],
    "dx": ["DX", "disp_x", "Dx"],
    "dy": ["DY", "disp_y", "Dy"],
}


class UnknownOpticsAccessor(RuntimeError):
    pass


def _get_optics_from_object(obj, key):
    for name in COMMON_OPTICS_NAMES[key]:
        try:
            return obj[name]
        except KeyError:
            continue
    raise UnknownOpticsAccessor(f"Unknown Optics key: {key}")


def coerce_optics(some_optics) -> tuple[list, list, list]:
    assert not isinstance(some_optics, lattice.Beamline)

    try:
        some_optics = os.fspath(some_optics)
    except TypeError:
        pass
    else:
        some_optics = _load_optics(some_optics)

    result = {}
    for key, keylist in COMMON_OPTICS_NAMES.items():
        for key2 in keylist:
            result[key] = _get_optics_from_object(some_optics, key)
    return pd.DataFrame.from_dict(result)


def _load_optics(some_optics):
    try:
        return tfs.read(some_optics)
    except tfs.errors.TfsFormatError:
        pass

    return pand8.read(some_optics)
