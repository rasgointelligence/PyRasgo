import pandas as pd


class BaseTransform:
    @classmethod
    def rolling_average(cls, df: pd.DataFrame, window_size, column: str, alias: str = None):
        new_col_name = alias or f"{column}_roll_avg"
        df[new_col_name] = df[column].rolling(window=window_size).mean()
        return df

    @classmethod
    def cumulative_average(cls, df: pd.DataFrame, column: str, alias: str = None):
        new_col_name = alias or f"{column}_cum_avg"
        df[new_col_name] = df[column].expanding().mean()
        return df

    @classmethod
    def add(cls, df: pd.DataFrame, value, column: str, alias: str = None):
        """Perform addition to each value in the dataframe"""
        new_col_name = alias or f"{column}_add_{value}"
        df[new_col_name] = df[column] + value
        return df

    @classmethod
    def subtract(cls, df: pd.DataFrame, value, column: str, alias: str = None):
        new_col_name = alias or f"{column}_subtract_{value}"
        df[new_col_name] = df[column] - value
        return df


    @classmethod
    def divide(cls, df: pd.DataFrame, value: float, column, alias: str = None):
        """Divide each element in a dataframe by a value"""
        new_col_name = alias or f"{column}_divide_{value}"
        df[new_col_name] = df[column] / value
        return df

    @classmethod
    def multiply(cls, df: pd.DataFrame, value: float, column, alias: str = None):
        """Multiply dataframe by a value"""
        new_col_name = alias or f"{column}_mult_{value}"
        df[new_col_name] = df[column] * value
        return df
