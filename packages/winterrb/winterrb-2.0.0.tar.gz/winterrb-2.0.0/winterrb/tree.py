import numpy as np
import pandas as pd

TRAIN_FEATURES = [
    "distpsnr1",
    "nmtchtm",
    "chipsf",
    "fwhm",
    "mindtoedge",
    "aimage",
    "bimage",
    'aimagerat',
    'bimagerat',
    'elong',
    'nneg',
    'nbad',
    'sumrat',
    'scorr',
    'nmtchps',
    "distgaiabright",
    "rb"
]

NANFILL_MAP = {
    "distgaiabright": 100.0,
    "distpsnr1": 100.0
}


def get_numpy_from_df(table: pd.DataFrame) -> np.ndarray:
    """
    Get a numpy array from a table

    :param table: DataFrame
    :return: Numpy array
    """
    df = table.copy(deep=True)
    df.replace([np.inf, -np.inf], np.nan, inplace=True)

    for key, value in NANFILL_MAP.items():
        if key in df.columns:
            df[key] = df[key].fillna(value)

    return df[TRAIN_FEATURES].to_numpy()