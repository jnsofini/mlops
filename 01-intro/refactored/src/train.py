
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error


root_dir = Path(__file__).parent.parent
source_data_dir = root_dir/ "data/preprocess"
dest_data_dir = root_dir / "data/train" 

def read_data(cols=None)-> Tuple[pd.DataFrame, pd.DataFrame]:
    """Loads train and test data.

    With optional columns the test and train data is loaded.

    Args:
        cols (List[str], optional): Columns to return. Defaults to None.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: _description_
    """
    train_data = pd.read_parquet(source_data_dir/"train.parquet") 
    test_data = pd.read_parquet(source_data_dir/"test.parquet") 
    if cols:
        return train_data[cols], test_data[cols]
    
    return train_data, test_data

def train_model(df_train:pd.DataFrame, df_test:pd.DataFrame, categorial_features: List[str], target: str = "duration"):
    """Train a Linear Regression and calculate the RMSE on the validation dataframe

    Args:
        df_train (pd.DataFrame): Training data
        df_test (pd.DataFrame): Test data
        categorial_features (List[str]): List of categorical features
        target (str, optional): Target column. Defaults to "duration".

    Returns:
        Dict[str, float]: Dict of mse for train and test
    """ 
    
    dv = DictVectorizer()   
    train_dicts = df_train[categorial_features].to_dict(orient='records')
    test_dicts = df_test[categorial_features].to_dict(orient='records')
    
    X_train = dv.fit_transform(train_dicts)
    X_test = dv.transform(test_dicts)
    
    y_train = df_train[target].values
    y_test = df_test[target].values

    lr = LinearRegression()
    lr.fit(X_train, y_train)

    y_pred_train = lr.predict(X_train)
    y_pred_test = lr.predict(X_test)


    mse = {
        "train-mse": mean_squared_error(y_train, y_pred_train, squared=False),
        "test-mse": mean_squared_error(y_test, y_pred_test, squared=False)
        }
    
    return dv, mse 

def save_model():
    pass

def main():
    categorical = ['PULocationID', 'DOLocationID']
    TARGET = 'duration'
    train_data, test_data = read_data(['PULocationID', 'DOLocationID'] + [TARGET])

    dv, mse = train_model(train_data, test_data, categorial_features=categorical, target=TARGET)

    print(mse)

if __name__ == "__main__":
    main()