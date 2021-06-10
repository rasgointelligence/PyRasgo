import pandas as pd
from typing import List, Optional
import inspect

from pyrasgo.api.error import APIError
from pyrasgo.storage.dataframe.evaluate import Evaluate
from pyrasgo.utils.monitoring import track_experiment, track_usage

class Prune():

    def __init__(self, experiment_id = None):
        self._experiment_id = experiment_id
        self.evaluate = Evaluate(experiment_id=experiment_id)

    @track_usage
    @track_experiment
    def columns_with_missing_data(self, df: pd.DataFrame, 
                                  columns: List[str] = None, 
                                  threshold: float = 0) -> pd.DataFrame:
        """
        Returns a copy of your dataframe after removing columns 
        containing NULL or NaN values exceeding a threshold count
        
        Parameters
        ----------
            df: pandas DataFrame:
                Dataframe to operate on
            columns: (Optional) List[str]: 
                List of column names to check for null, Defaults to All
            threshold: (Optional) float: 
                Null percentage threshold above which a column will be dropped, Defaults to 0%
        
        Returns
        -------
            pandas DataFrame
        """
        df_out = df.copy(deep=True)
        column_with_nan = df_out.columns[df_out.isnull().any()]
        for column in column_with_nan:
            if columns:
                if column in columns:
                    if df_out[column].isnull().sum()*100.0/df_out.shape[0] >= threshold:
                        df_out = df_out.drop(column, 1)
                        print(f'Column deleted: {column}')
            else:
                if df_out[column].isnull().sum()*100.0/df_out.shape[0] >= threshold:
                    df_out = df_out.drop(column, 1)
                    print(f'Column deleted: {column}')
        return df_out

    @track_usage
    @track_experiment
    def duplicate_rows(self, df: pd.DataFrame, 
                       columns: List[str] = None
                       ) -> pd.DataFrame:
        """ 
        Returns a copy of your DataFrame with duplicate rows removed

        Parameters
        ----------
            df: pandas DataFrame:
                Dataframe to operate on
            columns: (Optional) List[str]: 
                List of column names to check for duplicates in
        
        Returns
        -------
            pandas DataFrame
        """
        df_out = df.copy(deep=True)
        #df_out = df_out.reset_index(drop=False)
        #df_out.rename(columns = {'index':'indexInOrigDF'}, inplace = True)
        if columns:
            drop_us = pd.Int64Index([])
            for column in columns:
                drop_us = drop_us.append(df_out[df_out.duplicated([column])].index)
        else:
            drop_us = df_out.index[df_out.duplicated()]
        print(f'Dropping {drop_us.shape[0]} rows')
        df_out = pd.DataFrame(df_out.drop(drop_us, 0))
        return df_out

    @track_usage
    @track_experiment
    def features(self, df: pd.DataFrame, 
                 target_column: str, 
                 timeseries_index: str = None,
                 exclude_columns: List[str] = None, 
                 top_n: int = None,
                 top_n_pct: float = None,
                 pct_of_top_feature: float = None
                 ) -> pd.DataFrame:
        """
        Drops columns from a dataframe that are below a threshold of feature importance

        Parameters
        ----------
            df: pandas DataFrame:
                Dataframe to operate on
            target_columns: str: 
                Column name of target feature
            timeseries_index: (Optional) str:
                Name of column to use as timeseries index. 
                If passed, rows will be ordered by column and split.
                If None is passed, rows will be split randomly.
            top_n: int: 
                The number of features to keep, ordered by feature importance
            top_n_pct: float: 
                The percentage of features to keep, ordered by feature importance
            pct_of_top_feature: float: 
                The percentage of importance of the most import feature, any columns with importance below this percentage will be dropped
            exclude_columns: List[str]: 
                Column names of features to be filered out from calculation
        
        Returns
        -------
            pandas DataFrame
        """
        # Runtime checks
        if top_n is not None:
            method = 'TOPN'
            print(f'Prune Method: Keeping top {top_n} features')
        elif top_n_pct is not None:
            method = 'TOPPCT'
            print(f'Prune Method: Keeping top {top_n_pct} of features')
        elif pct_of_top_feature is not None:
            method = 'PCTOF'
            print(f'Prune Method: Keeping features with importance above {pct_of_top_feature} pct of max feature')
        else:
            raise APIError('Must pass in one of the following parameters: top_n=#, top_n_pct=.#, pct_of_top_feature=.#')

        # Copy df so we can alter it without impacting source data
        p_df = df.copy(deep=True)
        
        # Calculate feature_importance and return the result as a dict
        fi_dict = self.evaluate.feature_importance(df=p_df, target_column=target_column, timeseries_index=timeseries_index, exclude_columns=exclude_columns, return_cli_only=True)
        fi_s = pd.Series(fi_dict.get("featureImportance"))
        fi_df = pd.DataFrame({'Feature':fi_s.index, 'Importance':fi_s.values})
        fi_df.sort_values(by='Importance', ascending=False, inplace=True)
        
        if method == 'TOPN':
            row_threshold = top_n+1
            low_importance_features = fi_df.iloc[row_threshold:]['Feature']
            print(f'Dropped features not in top {top_n}:', low_importance_features.to_list())
        if method == 'TOPPCT':
            row_threshold = round(fi_df.shape[0] * top_n_pct)
            low_importance_features = fi_df.iloc[row_threshold:]['Feature']
            print(f'Dropped features not in top {top_n_pct} pct:', low_importance_features.to_list())
        if method == 'PCTOF':
            max_fi = fi_df['Importance'].max()
            importance_cutoff = max_fi * pct_of_top_feature
            low_importance_features = fi_df[fi_df['Importance'] <= importance_cutoff]['Feature']
            print(f'Dropped features below importance threshold {importance_cutoff}:', low_importance_features.to_list())

        p_df = p_df.drop(columns=low_importance_features)
        return p_df

    @track_usage
    @track_experiment
    def rows_with_missing_data(self, df: pd.DataFrame, 
                               columns: List[str] = None
                               ) -> pd.DataFrame:
        """
        Returns a copy of your DataFrame after removing all rows 
        containing NULL or NaN values in any of their columns
        
        Parameters
        ----------
            df: pandas DataFrame:
                Dataframe to operate on
            columns: (Optional) List[str]: 
                List of column names to check for nulls, Defaults to All
        
        Returns
        -------
            pandas DataFrame
        """
        df_out = df.copy(deep=True)
        if columns:
            index_with_nan = pd.Int64Index([])
            for column in columns:
                index_with_nan = index_with_nan.append(df_out[df_out[column].isnull()].index)
        else:
            index_with_nan = df_out.index[df_out.isnull().any(axis=1)]
        print(f'Dropping {index_with_nan.shape[0]} rows')
        df_out = pd.DataFrame(df_out.drop(index_with_nan))
        return df_out
