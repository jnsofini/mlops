""" Data Preprocessing
Here we runs the following preprocessing steps.

"""

from pathlib import Path
from typing import Dict, List

import pandas as pd

root_dir = Path(__file__).parent.parent
source_data_dir = (
    root_dir.parent.parent / "data/raw_data"
)  # "../../data/raw_data"
dest_data_dir = root_dir / "data/preprocess"  # "./data/preprocess2"

dest_dir = Path(dest_data_dir)
dest_dir.mkdir(parents=True, exist_ok=True)


def load_data(path: Path, file_name: str) -> pd.DataFrame:
    """Load parquet onjext from file into a DataFrame.

    Args:
        path (Path): The base path of the data
        file_name (str): The parquet data file name

    Returns:
        pd.DataFrame: DataFrame of  raw data
    """

    return pd.read_parquet(Path(path) / f"{file_name}.parquet")


def add_trip_duration(
    df: pd.DataFrame,
    pick_up_time: str = "tpep_pickup_datetime",
    drop_off_time: str = "tpep_dropoff_datetime",
) -> pd.DataFrame:
    """Adds the column `duration` to the DataFrame.

    The column duration is derived from the pickup and drop off time stamps.

    Args:
        df (pd.DataFrame): Raw data of the taxi trip data
        pick_up_time (str, optional): The pickup time. Defaults to "tpep_pickup_datetime".
        drop_off_time (str, optional): Dropoff time. Defaults to "tpep_dropoff_datetime".

    Returns:
        pd.DataFrame: The taxi data with duration added
    """
    df[pick_up_time] = pd.to_datetime(df[pick_up_time])
    df[drop_off_time] = pd.to_datetime(df[drop_off_time])
    df = df.assign(
        duration=df[drop_off_time] - df[pick_up_time]
        )
    df.duration = df.duration.apply(lambda td: td.total_seconds() / 60)

    return df


def remove_outliers(
    df: pd.DataFrame, strategy: Dict[str, Dict[str, float]]
) -> pd.DataFrame:
    """Removes outliers defined as a strategy.

    The strategy is defined as the a dict with columns as keys and the key is another dict
    with keys min and max whose values depict the cutoff of the outliers

    Args:
        df (pd.DataFrame): DataFrame with outliers present.
        strategy (Dict[str, Dict[str, float]]): The strategy to remove outliers

    Returns:
        pd.DataFrame: The processed data with ourliers removed.
    """
    # mask = pd.Series(df.shape[0]*[True])

    for column, outlier in strategy.items():
        # TODO: Make the following mask to only run on series and filter outside the loop
        # print(column, outlier)
        mask = (df[column] >= outlier.get("min", df[column].min())) & (
            df[column] <= outlier.get("max", df[column].max())
        )
        # print(mask)
        df = df[mask]

    return df


def categorial_feature_prepocessing(
    df: pd.DataFrame, categorical_features: List[str]
) -> pd.DataFrame:
    """Preprocess categorical features.

    Here we simply preprocess them by casting them as strings.

    Args:
        df (pd.DataFrame): Data with both numerical and categorical columns
        categorical_features (List[str]): List of ategorical feature

    Returns:
        pd.DataFrame: Process dataframe
    """
    df[categorical_features] = df[categorical_features].astype(str)

    return df


def preprocess_taxi_data(
    df: pd.DataFrame,
    pickup_dropoff: Dict[str, str],
    strategy: Dict[str, Dict[str, float]],
    categorical_features: List[str],
) -> pd.DataFrame:
    """Adds duration data using `add_trip_duration` and removes outliers using `remove_outliers.`

    Args:
        df (pd.DataFrame): DataFrame with outliers present.
        strategy (Dict[str, Dict[str, float]]): The strategy to remove outliers
        categorical_features (List[str]): List of categorical features to pass to categoricla feature processing

    Returns:
        pd.DataFrame: The processed data with ourliers removed.
    """
    print(df.columns)
    if not "duration" in df.columns:
        df = add_trip_duration(
            df=df,
            pick_up_time=pickup_dropoff["pickup"],
            drop_off_time=pickup_dropoff["dropoff"],
        )
    df = remove_outliers(df=df, strategy=strategy)
    df = categorial_feature_prepocessing(
        df, categorical_features=categorical_features
    )

    return df


def main():
    raw_train_data = load_data(
        Path(source_data_dir), file_name="yellow_tripdata_2022-01"
    )
    raw_test_data = load_data(
        Path(source_data_dir), file_name="yellow_tripdata_2022-02"
    )

    # Preprocess
    categorical = ["PULocationID", "DOLocationID"]
    processed_train_data = preprocess_taxi_data(
        df=raw_train_data,
        pickup_dropoff={
            "pickup": "tpep_pickup_datetime",
            "dropoff": "tpep_dropoff_datetime",
        },
        strategy={"duration": {"min": 1, "max": 60}},
        categorical_features=categorical,
    )
    processed_test_data = preprocess_taxi_data(
        df=raw_test_data,
        pickup_dropoff={
            "pickup": "tpep_pickup_datetime",
            "dropoff": "tpep_dropoff_datetime",
        },
        strategy={"duration": {"min": 1, "max": 60}},
        categorical_features=categorical,
    )

    # Save data
    processed_train_data.to_parquet(dest_dir / "train.parquet")
    processed_test_data.to_parquet(dest_dir / "test.parquet")


if __name__ == "__main__":
    main()
