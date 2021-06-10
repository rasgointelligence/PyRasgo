from typing import List

import pandas as pd

from pyrasgo.storage.dataframe._base_transform import BaseTransform


class Transform:
    def rolling_average(self, df: pd.DataFrame, window_size: int, columns: List[str] = None, aliases: List[str] = None):
        """Calculate mean over a window size in by number of rows"""
        if aliases:
            for column, alias in zip(columns, aliases):
                BaseTransform.rolling_average(df, window_size, column, alias)
        else:
            for column in columns:
                BaseTransform.rolling_average(df, window_size, column)
        return df

    def cumulative_average(self, df: pd.DataFrame, columns: List[str] = None, aliases: List[str] = None):
        """Calculate mean over window from beginning of df to current location"""
        if aliases:
            for column, alias in zip(columns, aliases):
                BaseTransform.cumulative_average(df, column, alias)
        else:
            for column in columns:
                BaseTransform.cumulative_average(df, column)
        return df

    def add(self, df: pd.DataFrame, value: float, columns: List[str] = None, aliases: List[str] = None):
        """Add a number to each value of a dataframe"""
        if aliases:
            for column, alias in zip(columns, aliases):
                BaseTransform.add(df, value, column, alias)
        else:
            for column in columns:
                BaseTransform.add(df, value, column)
        return df

    def subtract(self, df: pd.DataFrame, value: float, columns: List[str] = None, aliases: List[str] = None):
        """Subtract a number from each element of a dataframe"""
        if aliases:
            for column, alias in zip(columns, aliases):
                BaseTransform.subtract(df, value, column, alias)
        else:
            for column in columns:
                BaseTransform.subtract(df, value, column)
        return df

    def divide(self, df: pd.DataFrame, value: float, columns: List[str] = None, aliases: List[str] = None):
        """Divide each element in a dataframe by a value"""
        if aliases:
            for column, alias in zip(columns, aliases):
                BaseTransform.divide(df, value, column, alias)
        else:
            for column in columns:
                BaseTransform.divide(df, value, column)
        return df

    def multiply(self, df: pd.DataFrame, value: float, columns: List[str] = None, aliases: List[str] = None):
        """Multiply dataframe by a value"""
        if aliases:
            for column, alias in zip(columns, aliases):
                BaseTransform.multiply(df, value, column, alias)
        else:
            for column in columns:
                BaseTransform.multiply(df, value, column)
        return df

    def mult(self, df: pd.DataFrame, value: float, columns: List[str] = None, aliases: List[str] = None):
        """Alias for multiply"""
        return self.multiply(df, value)
