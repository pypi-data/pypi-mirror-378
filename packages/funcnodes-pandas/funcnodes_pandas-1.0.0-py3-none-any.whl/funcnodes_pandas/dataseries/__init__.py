from typing import Union, Any, Optional
import funcnodes as fn
import numpy as np
import pandas
from ._str import SERIES_STR_SHELF
from ._str import *  # noqa: F401, F403


@fn.NodeDecorator(
    node_id="pd.ser_to_dict",
    name="To Dictionary",
    description="Converts a Series to a dictionary.",
    outputs=[{"name": "dict", "type": dict}],
)
def ser_to_dict(
    ser: pandas.Series,
) -> dict:
    return ser.to_dict()


@fn.NodeDecorator(
    node_id="pd.ser_to_df",
    name="To DataFrame",
    description="Converts a Series to a DataFrame.",
    outputs=[{"name": "df", "type": pandas.DataFrame}],
)
def ser_to_df(
    ser: pandas.Series,
    transposed: bool = True,
) -> pandas.DataFrame:
    df = ser.to_frame()
    if transposed:
        df = df.transpose()

    return df


@fn.NodeDecorator(
    node_id="pd.ser_values",
    name="Get Values",
    description="Gets the values of a Series.",
    outputs=[{"name": "values", "type": np.ndarray}],
)
def ser_values(
    ser: pandas.Series,
) -> np.ndarray:
    return ser.to_numpy(copy=True)


@fn.NodeDecorator(
    node_id="pd.ser_to_list",
    name="To List",
    description="Converts a Series to a list.",
    outputs=[{"name": "list", "type": list}],
)
def ser_to_list(
    ser: pandas.Series,
) -> list:
    return ser.to_list()


@fn.NodeDecorator(
    node_id="pd.ser_loc",
    name="Get Value",
    description="Gets a value from a Series by label.",
    outputs=[{"name": "value", "type": Any}],
    default_io_options={
        "ser": {
            "on": {
                "after_set_value": fn.decorator.update_other_io_options(
                    "label",
                    lambda x: list(x.index),
                )
            }
        },
    },
)
def ser_loc(
    ser: pandas.Series,
    label: str,
) -> str:
    # taransform label to the correct type
    label = ser.index.to_list()[0].__class__(label)
    return ser.loc[label]


@fn.NodeDecorator(
    node_id="pd.ser_iloc",
    name="Get Value by Index",
    description="Gets a value from a Series by index.",
    outputs=[{"name": "value", "type": Any}],
    default_io_options={
        "ser": {
            "on": {
                "after_set_value": fn.decorator.update_other_io_value_options(
                    "index", lambda result: dict(min=0, max=len(result) - 1, step=1)
                )
            }
        },
    },
)
def ser_iloc(
    ser: pandas.Series,
    index: int,
) -> Union[str]:
    return ser.iloc[int(index)]


@fn.NodeDecorator(
    node_id="pd.ser_from_dict",
    name="From Dictionary",
    description="Creates a Series from a dictionary.",
    outputs=[{"name": "series", "type": pandas.Series}],
)
def ser_from_dict(
    data: dict,
    name: Optional[str] = None,
) -> pandas.Series:
    return pandas.Series(data, name=name)


@fn.NodeDecorator(
    node_id="pd.ser_from_list",
    name="From List",
    description="Creates a Series from a list.",
    outputs=[{"name": "series", "type": pandas.Series}],
)
def ser_from_list(
    data: list,
    name: Optional[str] = None,
) -> pandas.Series:
    return pandas.Series(data, name=name)


NODE_SHELF = fn.Shelf(
    name="Series",
    nodes=[
        ser_to_dict,
        ser_values,
        ser_to_list,
        ser_loc,
        ser_iloc,
        ser_from_dict,
        ser_from_list,
    ],
    description="Pandas Series nodes",
    subshelves=[SERIES_STR_SHELF],
)
