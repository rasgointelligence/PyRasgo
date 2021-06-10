import datetime
import numpy as np
import pandas as pd
import sys
from tqdm import tqdm
from typing import List, Optional
import webbrowser

from pyrasgo.api.error import APIError
from pyrasgo.api.create import Create
from pyrasgo.api.session import Environment
from pyrasgo.schemas.feature import featureImportanceStats, ColumnProfiles
from pyrasgo.storage.dataframe.utils import set_df_id, map_pandas_df_type, DataframeDataTypes
from pyrasgo.utils.monitoring import track_experiment, track_usage

class Evaluate():

    def __init__(self, experiment_id = None):
        self._experiment_id = experiment_id
        self._environment = Environment.from_environment()
        self.create = Create()

    @track_usage
    def duplicate_rows(self, df: pd.DataFrame, 
                       columns: List[str] = None) -> pd.DataFrame:
        """ 
        Returns a DataFrame of rows that are duplicated in your original DataFrame 
        
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
        if columns:
            df_out = df.iloc[:0].copy()
            for column in columns:
                df_out = df_out.append(df[df.duplicated([column])])
        else:
            df_out = df[df.duplicated()]
        return df_out

    @track_usage
    @track_experiment
    def feature_importance(self, df: pd.DataFrame, 
                           target_column: str,
                           timeseries_index: Optional[str] = None,
                           exclude_columns: List[str] = None,
                           return_cli_only: bool = False
                           ) -> dict:
        """
        Calculates importance of a target feature using Shapley values. 
        Uses an 80% training sample of data.
        Opens interactive graph in the Rasgo WebApp or returns raw json of feature importance.

        Parameters
        ----------
            df: pandas DataFrame:
                Dataframe to operate on
            target_column: str: 
                Column name of target feature
            timeseries_index: (Optional) str:
                Name of column to use as timeseries index. 
                If passed, rows will be ordered by column and split.
                If None is passed, rows will be split randomly.
            exclude_columns: (Optional) List[str]: 
                Column names of features to be filered out from profile
            return_cli_only: (Optional) bool:
                Instructs function to not open Rasgo WebApp and return json in the CLI only
        
        Returns
        -------
            dict
        """
        # Check if we can run this
        try:
            import shap
            import catboost
            from sklearn.metrics import mean_squared_error
            from sklearn.metrics import r2_score
        except ModuleNotFoundError:
            raise APIError('Missing dependencies needed to run this function. '
                           'Run `pip install pyrasgo[df]` to install shap, catboost and sklearn packages.')

        if target_column not in df.columns:
            raise APIError(f'Column {target_column} does not exist in DataFrame')
        if timeseries_index and timeseries_index not in df.columns:
            raise APIError(f'Column {timeseries_index} does not exist in DataFrame')

        # Start progress bar
        with tqdm(desc='Calculating Feature Importance', total=8, unit='step', file=sys.stdout, leave=False) as progress:
            
            # assign a unique id to the DF before we alter it
            rasgo_df_id = set_df_id(df, self._experiment_id)
            progress.update()

            # Run profile for df
            timestamp = str(datetime.datetime.now())
            self.profile(df, exclude_columns=exclude_columns, return_cli_only=True, timestamp_override=timestamp)
            progress.update()

            # Copy df so we can alter it without impacting source data
            fi_df = df.copy(deep=True)
            progress.update()

            # Split data into train, test sets
            train_df, test_df = self.train_test_split(fi_df, training_percentage=0.8, timeseries_index=timeseries_index)            
            if timeseries_index:
                train_df = train_df.drop(timeseries_index, 1)
                test_df = test_df.drop(timeseries_index, 1)
            progress.update()

            # Prep DataFrame
            if exclude_columns:
                if timeseries_index and timeseries_index in exclude_columns:
                    exclude_columns.remove(timeseries_index)
                if target_column in exclude_columns:
                    exclude_columns.remove(target_column)
                for col in exclude_columns:
                    if col not in train_df.columns:
                        raise APIError(f'Column {col} does not exist in DataFrame')
                    train_df = train_df.drop(col, 1)
                    test_df = test_df.drop(col, 1)
            
            # NOTE: Nulls cause a problem with the importance calc:
            train_df.dropna(axis=1, how='all', inplace=True)
            train_df.dropna(inplace=True)
            test_df.dropna(axis=1, how='all', inplace=True)
            test_df.dropna(inplace=True)
            # NOTE: Dates cause a problem with the importance cals:
            train_df = train_df.select_dtypes(exclude=['datetime'])
            test_df = test_df.select_dtypes(exclude=['datetime'])

            # Create x and y df's based off target column
            train_x = train_df.loc[:, train_df.columns != target_column]
            train_y = train_df.loc[:, train_df.columns == target_column]
            test_x = test_df.loc[:, test_df.columns != target_column]
            test_y = test_df.loc[:, test_df.columns == target_column]

            # Get categorical feature indices to pass to catboost
            train_cat_features = np.where(train_x.dtypes != np.number)[0]
            test_cat_features = np.where(test_x.dtypes != np.number)[0]
            progress.update()

            # Create the catboost dataset
            try:
                train_dataset = catboost.Pool(data=train_x, label=train_y, cat_features=train_cat_features)
                test_dataset = catboost.Pool(data=test_x, label=test_y, cat_features=test_cat_features)
            except TypeError as e:
                raise APIError(f"Catboost error: {e}: "
                            f"One or more of the fields in your dataframe is a date that cannot be automatically filtered out. "
                            f"You can use the exclude_columns=[''] parameter to exclude these manually and re-run this fuction.")
            model = catboost.CatBoostRegressor(iterations=300, random_seed=123)
            model.fit(train_dataset, eval_set=test_dataset, use_best_model=True, verbose=False, plot=False)
            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(train_dataset)
            df_shap = pd.DataFrame(shap_values, columns=train_x.columns)
            # TODO: Alternative importance Calc for later use
            #df_comp = pd.DataFrame({'feature_importance': model.get_feature_importance(train_dataset), 
            #                        'feature_names': train_x.columns
            #                        }).sort_values(by=['feature_importance'], ascending=False)            
            progress.update()

            # Start building output json
            c_data = {}
            c_data["targetFeature"] = target_column

            # Histogram binning of shapley values
            c_data['featureShapleyDistributions'] = {}
            for column in df_shap:
                try:
                    b = min(10, train_df[column].nunique())
                    H, xedges, yedges = np.histogram2d(x=train_df[column], y=df_shap[column], bins=b)
                    df_hist = pd.DataFrame(zip(H.tolist(), xedges, yedges), columns=['Histogram','feature_edges','shap_edges'])
                    fhist = df_hist.to_dict(orient="list")
                    c_data['featureShapleyDistributions'][column] = fhist
                except:
                    list_of_counts = []
                    list_of_values = []
                    col_min = np.nanmin(df_shap[column])
                    col_max = np.nanmax(df_shap[column])
                    unique_values = train_df[column].value_counts().index.astype(str).tolist()
                    if len(unique_values) > 10:
                        top_10_values = unique_values[:10]
                    else:
                        top_10_values = unique_values
                    df_combined = pd.concat([train_df[column], df_shap[column]], axis=1, join='inner')
                    shapcol = column+"_shap"
                    df_combined.columns = [column, shapcol]
                    for val in top_10_values:
                        count, division = np.histogram(df_combined.query('{0}==@val'.format(column))[shapcol], bins=10, range=(col_min, col_max), density=False)
                        list_of_counts.append(count.tolist())
                        list_of_values.append(val)
                    df_hist = pd.DataFrame(zip(list_of_counts, list_of_values, division), columns=['Histogram','feature_edges','shap_edges'])
                    fhist = df_hist.to_dict(orient="list")
                    c_data['featureShapleyDistributions'][column] = fhist
            progress.update()
            
            # Mean absolute value by feature
            c_data['featureImportance'] = df_shap.abs().mean().to_dict()
            # TODO: Expand featureImportance to include multiple versions:
            #c_data['featureImportance']['shapley'] = df_shap.abs().mean().to_dict()
            #c_data['featureImportance']['default'] = df_comp.abs().mean().to_dict()

            # Model performance
            c_data['modelPerformance'] = {}
            pred = model.predict(test_x)
            rmse = (np.sqrt(mean_squared_error(test_y, pred)))
            r2 = r2_score(test_y, pred)
            c_data['modelPerformance']['RMSE'] = rmse
            c_data['modelPerformance']['R2'] = r2
            progress.update()

            # Prepare the response
            url = f'{self._environment.app_path}/dataframes/{rasgo_df_id}/importance'
            response = {
                "targetFeature": target_column,
                "featureShapleyDistributions": c_data['featureShapleyDistributions'],
                "featureImportance": c_data['featureImportance'],
                "modelPerformance": c_data['modelPerformance'],
                "timestamp": timestamp
            }
            json_payload = featureImportanceStats(**response)
            self.create.column_importance_stats(id = rasgo_df_id, payload = json_payload)

            if not return_cli_only:
                webbrowser.open(url)
            progress.close()
            print('Importance URL:', url)
        return response

    @track_usage
    def missing_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """ 
        Print all columns in a Dataframe with null values
        and return rows with null values
        
        Parameters
        ----------
            df: pandas DataFrame:
                Dataframe to operate on
        
        Returns
        -------   
            'Columns with null values:'
            '-------------------------'
            'column, count of rows'
            '-------------------------'
            'List[index of rows with null values]'
        """
        column_with_nan = df.columns[df.isnull().any()]
        template="%-20s %-6s"
        print(template % ("Column", "Count of Nulls"))
        print("-"*35)
        for column in column_with_nan:
            print(template % (column, df[column].isnull().sum()))
        print("-"*35)
        return df[df.isnull().any(axis=1)]

    @track_usage
    def profile(self, df: pd.DataFrame, 
                exclude_columns: List[str] = None,
                return_cli_only: bool = False,
                timestamp_override: str = None) -> dict:
        """
        Profile a DataFrame locally, and push metadata to rasgo to display.

        Parameters
        ----------
            df: pandas DataFrame:
                Dataframe to operate on
            exclude_columns: List[str]: 
                Column names of features to be filered out from profile
            return_cli_only: (Optional) bool:
                Instructs function to not open Rasgo WebApp and return json in the CLI only
        
        Returns
        -------
            dict
        """
        # NOTE: List of optimizations post-mvp:
        # - add frequency and outlier data to commonValues

        # assign a unique id to the DF before we alter it
        rasgo_df_id = set_df_id(df, self._experiment_id)

        # Get timestamp
        timestamp = timestamp_override or str(datetime.datetime.now())

        # Copy df so we can alter it without impacting source data
        p_df = df.copy(deep=True)
        # Remove columns before profiling
        if exclude_columns:
            for col in exclude_columns:
                if col not in p_df.columns:
                    raise APIError(f'Column {col} does not exist in DataFrame')
                p_df = p_df.drop(col, 1)

        # Create an object to hold intermediate data calculated via pandas
        profile_data = {}
        for col_label in p_df:
            profile_data[col_label] = {}

        # Calculate count stats before dropping nulls
        for col_label in p_df:
            profile_data[col_label]["recCt"] = p_df[col_label].count() + p_df[col_label].isna().sum()
            profile_data[col_label]["distinctCt"] = p_df[col_label].nunique()
            profile_data[col_label]["nullRecCt"] = p_df[col_label].isna().sum()
            profile_data[col_label]["zeroValRecCt"] = (p_df[col_label] == 0).astype(int).sum()


        # NOTE: Nulls cause a problem with the importance calc:
        p_df.dropna(axis=1, how='all', inplace=True)
        p_df.dropna(inplace=True)

        # label is the name of the attribute in the api request/response
        # mean is the name of the pandas function that calculates it
        # last item is any kwargs required for the function
        labels_and_functions = [
            ('meanVal', 'mean', {'axis': 0, 'numeric_only': True}),
            ('medianVal', 'median', {'axis': 0, 'numeric_only': True}),
            ('maxVal', 'max', {'axis': 0, 'numeric_only': True}),
            ('minVal', 'min', {'axis': 0, 'numeric_only': True}),
            ('sumVal', 'sum', {'axis': 0, 'numeric_only': True}),
            ('stdDevVal', 'std', {'axis': 0, 'numeric_only': True}),
            ('varianceVal', 'var', {'axis': 0, 'numeric_only': True}),
            ('skewVal', 'skew', None),
            ('kurtosisVal', 'kurtosis', None),
            ('q1Val', 'quantile', {'q': .25, 'axis': 0, 'numeric_only': True}),
            ('q3Val', 'quantile', {'q': .75, 'axis': 0, 'numeric_only': True}),
            ('pct5Val', 'quantile', {'q': .05, 'axis': 0, 'numeric_only': True}),
            ('pct95Val', 'quantile', {'q': .95, 'axis': 0, 'numeric_only': True})
        ]
        for label, func_name, extra_args in labels_and_functions:
            results = self._evaluate_df(p_df, func_name, extra_args)
            for col_label in p_df:
                try:
                    # store under key name for column, if the value exists
                    profile_data[col_label][label] = results[col_label]
                except KeyError:
                    pass
        
        # Warning: any data types not in the DataframeDataTypes enum will
        # default to string in the below logic. New data types will need
        # to be added to the enum
        # Generate values histogram
        histo_data = {}
        common_values = {}
        for col_label in p_df:
            # Set column data type and compare against enum
            try:
                col_type = DataframeDataTypes[str(p_df[col_label].dtypes).upper()].value
            except (AttributeError, KeyError):
                col_type = "string"
            # Histogram for numeric
            if col_type == "number":
                counts, edges = np.histogram(p_df[col_label], bins='auto', density=False)
                df_hist = pd.DataFrame(zip(counts, edges), columns=['height','bucketFloor'])
                df_hist['bucketCeiling']  = df_hist['bucketFloor']
                fhist = df_hist.to_dict(orient="records")
                # Common values for numeric
                ch = p_df[col_label].value_counts().rename_axis('val').reset_index(name='recCt')
                top5 = ch.head(10).to_dict(orient="records")
                total_rec = profile_data[col_label]["recCt"]
                for entry in top5:
                    entry["freq"] = entry["recCt"]/total_rec

            elif col_type == "string":
                p_df[col_label] = p_df[col_label].astype(str)
                dh = p_df[col_label].apply(str).value_counts().rename_axis('bucketFloor').reset_index(name='height')
                dh['bucketCeiling'] = dh['bucketFloor']
                fhist = []
                ch = dh.rename(columns={"bucketFloor":"val", "height":"recCt"}).drop(columns=["bucketCeiling"])
                top5 = ch.head(10).to_dict(orient="records")
                total_rec = profile_data[col_label]["recCt"]
                for entry in top5:
                    entry["freq"] = entry["recCt"]/total_rec

            # TODO: currently handling any non-numeric or string types as strings. Expand later
            else:
                p_df[col_label] = p_df[col_label].astype(str)
                dh = p_df[col_label].apply(str).value_counts().rename_axis('bucketFloor').reset_index(name='height')
                dh['bucketCeiling'] = dh['bucketFloor']
                fhist = []
                ch = dh.rename(columns={"bucketFloor":"val", "height":"recCt"}).drop(columns=["bucketCeiling"])
                top5 = ch.head(10).to_dict(orient="records")
                total_rec = profile_data[col_label]["recCt"]
                for entry in top5:
                    entry["freq"] = entry["recCt"]/total_rec

            histo_data[col_label] = fhist
            common_values[col_label] = top5

        # Prepare response
        response = {
            'columnProfiles': [],
            'timestamp': timestamp
        }
        for col_label in profile_data:
            column_stats = {
                'columnName': col_label,
                'dataType': map_pandas_df_type(p_df[col_label].dtype.name),
                'featureStats': profile_data[col_label],
                'commonValues': common_values[col_label]
            }
            if histo_data[col_label]:
                column_stats["histogram"] = histo_data[col_label]
            response['columnProfiles'].append(column_stats)

        url = f'{self._environment.app_path}/dataframes/{rasgo_df_id}/features'
        response['url'] = url
        json_payload = ColumnProfiles(**response)
        self.create.dataframe_profile(id=rasgo_df_id, payload=json_payload)

        if not return_cli_only:
            # open the feature profiles in a web page
            webbrowser.open(url)
            print('Profile URL:', url)
        return response

    @track_usage
    def timeseries_gaps(self, df: pd.DataFrame, 
                        datetime_column: str,
                        partition_columns: List[str] = []) -> pd.DataFrame:
        """
        Returns a dataframe of rows before and after timeseries gaps
        
        Parameters
        ----------
            df: pandas DataFrame:
                Dataframe to operate on
            datetime_column: str: 
                Name of column to check for timeseries gaps
            partition_columns: List[str]:
                Column names to group by

        Returns
        -------
            pandas DataFrame
        """
        # NOTE: List of optimizations post-mvp:
        # - Check that datetime_column can convert to_datetime without error
        # - Support non-date grains

        # Check for columns
        sort_columns = partition_columns.copy()
        sort_columns.append(datetime_column)
        for col in sort_columns:
            if col not in df.columns:
                raise APIError(f'Column {col} does not exist in DataFrame')

        # Calculate lags and sort
        ts_df = df.copy(deep=True)
        ts_df.sort_values(by=sort_columns, inplace=True)
        ts_df['TSGAPDateCol'] = pd.to_datetime(ts_df[datetime_column], infer_datetime_format=True)
        ts_df['TSGAPLastDate'] = ts_df.groupby(partition_columns)['TSGAPDateCol'].shift(1)
        ts_df['TSGAPNextDate'] = ts_df.groupby(partition_columns)['TSGAPDateCol'].shift(-1)

        # NOTE: This assumes a day grain in the timeseries column, we'll need to expand this to support more grains 
        # Select the rows for output
        df_out = ts_df[(ts_df['TSGAPNextDate'] - ts_df['TSGAPDateCol'] != '1 days') 
                     | (ts_df['TSGAPDateCol'] - ts_df['TSGAPLastDate'] != '1 days')]
        df_out.drop(['TSGAPDateCol'], axis=1, inplace=True)
        #df_out.drop(['TSGAPNextDate', 'TSGAPLastDate'], axis=1, inplace=True)

        return df_out

    @track_usage
    @track_experiment
    def train_test_split(self, df: pd.DataFrame, 
                         training_percentage: float = .8,
                         timeseries_index: Optional[str] = None) -> pd.DataFrame:
        """
        Splits a single dataframe into training and test dataframes based on input percentage
        
        Timeseries: orders rows by input datetime index and returns a precise split
        Non-Timeseries: randomly orders rows and returns an approximate split

        Parameters
        ----------
            df: pandas DataFrame:
                    Dataframe to operate on
            training_percentage: float: 
                Percentage of rows to use as training set (default = 80%)
            timeseries_index: (Optional) str: 
                Name of column to use as timeseries index. 
                If passed, rows will be ordered by column and split.
                If None is passed, rows will be split randomly.
        
        Returns
        -------
            pandas DataFrame, pandas DataFrame
        """
        if timeseries_index is None:
            # Non-timeseries data: Split randomly
            msk = np.random.rand(len(df)) <= training_percentage
            train_df = df[msk]
            test_df = df[~msk]
        
        else:
            # Timeseries data: Split in date order
            if timeseries_index not in df.columns:
                raise APIError(f'Column {timeseries_index} does not exist in DataFrame')
        
            # order the frame by date
            df.sort_values(by=[timeseries_index], inplace=True)

            # split into 2 frames based on training percentage
            row_ct = df.shape[0]
            train_ct = round(row_ct * training_percentage)
            test_ct = round(row_ct * (1-training_percentage))
            train_df = df.head(train_ct)
            test_df = df.tail(test_ct)
        return train_df, test_df

    @track_usage
    def type_mismatches(self, df: pd.DataFrame, 
                        column: str, 
                        data_type: str) -> pd.DataFrame:
        """ 
        Return a copy of your DataFrame with a column cast to another datatype
        
        Parameters
        ----------
            df: pandas DataFrame:
                Dataframe to operate on
            column: str:
                The column name in the DataFrame to cast
            data_type: str:
                The data type to cast to Accepted Values: ['datetime', 'numeric']
        
        Returns
        -------
            pandas DataFrame
        """
        new_df = pd.DataFrame()
        if data_type == 'datetime':
            new_df[column] = pd.to_datetime(df[column], errors='coerce', infer_datetime_format=True)
        elif data_type == 'numeric':
            new_df[column] = pd.to_numeric(df[column], errors='coerce')
        else:
            return "Supported data_type values are: 'datetime' or 'numeric'"
        total = df[column].count()
        cant_convert = new_df[column].isnull().sum()
        print(f"{(total - cant_convert) / total}%: {cant_convert} rows of {total} rows cannot convert.")
        new_df.rename(columns = {column:f'{column}CastTo{data_type.title()}'}, inplace = True)
        return new_df

    @classmethod
    def _evaluate_df(cls, df: pd.DataFrame, func_name: str, extra_args: dict):
        extra_args = extra_args or {}
        # Get the correct DataFrame function by name
        results = getattr(df, func_name)(**extra_args)
        return results
