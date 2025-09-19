import pandas as pd
import funcnodes as fn
from pandas.api.typing import DataFrameGroupBy
from typing import List


@fn.NodeDecorator(
    node_id="pd.gr.groupby_column",
    name="Group By Column",
    description="Groups a DataFrame by a column.",
    outputs=[{"name": "group"}],
    default_io_options={
        "df": {
            "on": {
                "after_set_value": fn.decorator.update_other_io_options(
                    "column",
                    lambda x: list(x.columns),
                )
            }
        },
    },
)
def GroupByColumnNode(
    df: pd.DataFrame,
    column: str,
    as_index: bool = True,
) -> pd.Series:
    df = df.copy()
    return df.groupby(column, as_index=as_index)


@fn.NodeDecorator(
    node_id="pd.gr.groupby",
    name="Group By",
    description="Groups a DataFrame by a list of columns (comma separated)",
    outputs=[{"name": "grouped", "type": pd.DataFrame}],
)
def group_by(
    df: pd.DataFrame,
    by: str,
    as_index: bool = True,
) -> DataFrameGroupBy:
    sep = [s.strip() for s in by.split(",")]
    df = df.copy()
    return df.groupby(sep, as_index=as_index)


@fn.NodeDecorator(
    node_id="pd.gr.mean",
    name="Mean",
    description="Calculates the mean of a DataFrameGroup.",
    outputs=[{"name": "mean", "type": pd.DataFrame}],
)
def gr_mean(
    group: DataFrameGroupBy,
    transform: bool = False,
) -> pd.DataFrame:
    if transform:
        return group.transform("mean")
    return group.mean()


@fn.NodeDecorator(
    node_id="pd.gr.sum",
    name="Sum",
    description="Calculates the sum of a DataFrameGroup.",
    outputs=[{"name": "sum", "type": pd.DataFrame}],
)
def gr_sum(
    group: DataFrameGroupBy,
    transform: bool = False,
) -> pd.DataFrame:
    if transform:
        return group.transform("sum")
    return group.sum()


@fn.NodeDecorator(
    node_id="pd.gr.max",
    name="Max",
    description="Calculates the max of a DataFrameGroup.",
    outputs=[{"name": "max", "type": pd.DataFrame}],
)
def gr_max(
    group: DataFrameGroupBy,
    transform: bool = False,
) -> pd.DataFrame:
    if transform:
        return group.transform("max")
    return group.max()


@fn.NodeDecorator(
    node_id="pd.gr.min",
    name="Min",
    description="Calculates the min of a DataFrameGroup.",
    outputs=[{"name": "min", "type": pd.DataFrame}],
)
def gr_min(
    group: DataFrameGroupBy,
    transform: bool = False,
) -> pd.DataFrame:
    if transform:
        return group.transform("min")
    return group.min()


@fn.NodeDecorator(
    node_id="pd.gr.std",
    name="Standard Deviation",
    description="Calculates the standard deviation of a DataFrameGroup.",
    outputs=[{"name": "std", "type": pd.DataFrame}],
)
def gr_std(
    group: DataFrameGroupBy,
    transform: bool = False,
) -> pd.DataFrame:
    if transform:
        return group.transform("std")
    return group.std()


@fn.NodeDecorator(
    node_id="pd.gr.var",
    name="Variance",
    description="Calculates the variance of a DataFrameGroup.",
    outputs=[{"name": "var", "type": pd.DataFrame}],
)
def gr_var(
    group: DataFrameGroupBy,
    transform: bool = False,
) -> pd.DataFrame:
    if transform:
        return group.transform("var")
    return group.var()


@fn.NodeDecorator(
    node_id="pd.gr.count",
    name="Count",
    description="Calculates the count of a DataFrameGroup.",
    outputs=[{"name": "count", "type": pd.DataFrame}],
)
def gr_count(
    group: DataFrameGroupBy,
    transform: bool = False,
) -> pd.DataFrame:
    if transform:
        return group.transform("count")
    return group.count()


@fn.NodeDecorator(
    node_id="pd.gr.median",
    name="Median",
    description="Calculates the median of a DataFrameGroup.",
    outputs=[{"name": "median", "type": pd.DataFrame}],
)
def gr_median(
    group: DataFrameGroupBy,
    transform: bool = False,
) -> pd.DataFrame:
    if transform:
        return group.transform("median")
    return group.median()


@fn.NodeDecorator(
    node_id="pd.gr.sem",
    name="Standard Error of Mean",
    description="Calculates the standard error of mean of a DataFrameGroup.",
    outputs=[{"name": "sem", "type": pd.DataFrame}],
)
def gr_sem(
    group: DataFrameGroupBy,
    transform: bool = False,
) -> pd.DataFrame:
    if transform:
        return group.transform("sem")
    return group.sem()


@fn.NodeDecorator(
    node_id="pd.gr.nunique",
    name="Number of Unique Values",
    description="Calculates the number of unique values of a DataFrameGroup.",
    outputs=[{"name": "nunique", "type": pd.DataFrame}],
)
def gr_nunique(
    group: DataFrameGroupBy,
    transform: bool = False,
) -> pd.DataFrame:
    if transform:
        return group.transform("nunique")
    return group.nunique()


@fn.NodeDecorator(
    node_id="pd.gr.first",
    name="First",
    description="Calculates the first non-NA value in a DataFrameGroup.",
    outputs=[{"name": "first", "type": pd.DataFrame}],
)
def gr_first(
    group: DataFrameGroupBy,
    transform: bool = False,
) -> pd.DataFrame:
    if transform:
        return group.transform("first")
    return group.first()


@fn.NodeDecorator(
    node_id="pd.gr.last",
    name="Last",
    description="Calculates the last non-NA value in a DataFrameGroup.",
    outputs=[{"name": "last", "type": pd.DataFrame}],
)
def gr_last(
    group: DataFrameGroupBy,
    transform: bool = False,
) -> pd.DataFrame:
    if transform:
        return group.transform("last")
    return group.last()


@fn.NodeDecorator(
    node_id="pd.gr.describe",
    name="Describe",
    description="Describes a DataFrameGroup.",
    outputs=[
        {
            "name": "description",
        }
    ],
)
def gr_describe(
    group: DataFrameGroupBy,
) -> pd.DataFrame:
    return group.describe()


@fn.NodeDecorator(
    node_id="pd.gr.group_to_list",
    name="Group to List",
    description="Converts a DataFrameGroup to a list of DataFrames.",
    outputs=[{"name": "list", "type": list}],
)
def group_to_list(
    group: DataFrameGroupBy,
) -> List[pd.DataFrame]:
    return [group for _, group in group]


@fn.NodeDecorator(
    node_id="pd.gr.get_df_from_group",
    name="Get DataFrame from Group",
    description="Gets a DataFrame from a DataFrameGroup.",
    outputs=[{"name": "df"}],
    default_io_options={
        "group": {
            "on": {
                "after_set_value": fn.decorator.update_other_io_options(
                    "name",
                    lambda x: list(x.groups.keys()),
                )
            }
        },
    },
)
def GetDFfromGroupNode(
    group: DataFrameGroupBy,
    name: str,
) -> pd.DataFrame:
    df = group.get_group(name).copy()
    return df


NODE_SHELF = fn.Shelf(
    nodes=[
        GroupByColumnNode,
        group_by,
        gr_mean,
        gr_sum,
        gr_max,
        gr_min,
        gr_std,
        gr_var,
        gr_count,
        gr_describe,
        group_to_list,
        GetDFfromGroupNode,
        gr_median,
        gr_sem,
        gr_nunique,
        gr_first,
        gr_last,
    ],
    name="Grouping",
    description="Pandas grouping nodes",
    subshelves=[],
)
