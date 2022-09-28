# Changelog
All notable changes to this project will be documented in this file.

## [2.1.0] - Sep 16, 2022
### Add
- Added Google drive to BiqQuery scope (only applies to customers hosting on Google BigQuery)
### Change
- All transform chains now build CTEs instead of views until they are published. Publishing a dataset will create a view or table from the CTE.
- Changed pydantic schemas to make more fields optional
### Remove
- Removed deprecated accelerator functions
- Removed `render_only` param from `Dataset.transform()` function. No replacement

## [2.0.2] - Sep 8, 2022
### Fix
- Fixed `get.dataset()` function to raise the correct error if a dataset is not found

## [2.0.1] - Sep 7, 2022
### Change
- Bumped rasgotransforms version requirement
### Fix
- Fixed `publish.dataset()` function to correctly pass in table type when republishing an existing Dataset

## [2.0.0] - Sep 3, 2022
### Add
- Added `rasgo.get.draft_datasets()` function to return draft datasets
- Added `rasgo.publish.dataset_from_dict()` function to create a new dataset using a Rasgo-compliant dict format
- Added `if_exists` param to `rasgo.publish.dataset()` function (pass in 'overwrite' to republish an existing dataset, default is 'fail')
- Added warning message on startup to inform users when a newer version of pyrsago is available
### Change
- Changed dataset versioning:
  - Datasets will no longer create parallel fqtns to represent different versions
  - Datasets will now always refer to a single fqtn
  - Datasets can be "republished" to change the SQL definition of the view
  - Datasets can be "versioned" by storing offline copies of the dataset as yaml in your git repo
- Changed `aggregation_type` param to `type` in `rasgo.create.metric()` and `rasgo.update.metric()` functions
- Bumped rasgotransforms version requirement
### Remove
- Removed `version` param from `get.dataset()` and `get.dataset_offline_version()` functions. No replacement.
- Removed `generate_stats` param from `publish.dataset()`, `publish.table()`, `publish.df()` functions. Stats are now run dynamically in the app, no replacement.
- Removed from `snapshot_index` param from `read.dataset()` and `Dataset.to_df()` functions. No replacement.
- Removed `status` and `version` properties from `Dataset` primitive. No replacement.
- Removed `run_stats` and `take_snapshot` methods from `Dataset` primitive. No replacement.
- Removed `time_index` param from `rasgo.publish.dataset()` function. No replacement.
- Removed `dataset_table_name` param from `rasgo.publish.df()` function. Use `fqtn` param instead.
- Removed `published_only` param from `rasgo.get.dataset()` function. Now only published datasets will be returned by default.

## [1.11.1] - Aug 3, 2022
### Add
- Added docstrings for methods added in v1.11.0. Be sure to document your code, folks.

## [1.11.0] - Jul 29, 2022
### Add
- Added methods to support:
   1. Creating Rasgo metrics for a dataset `rasgo.create.metric()`
   2. Getting Rasgo metrics attached to a dataset `rasgo.get.metrics(dataset_id)`
   3. Updating a Rasgo metric `rasgo.update.metric()`
   4. Deleting a Rasgo metric `rasgo.delete.metric(metric_id)`

## [1.10.0] - Jul 27, 2022
### Change
- Changed `publish.table` function to accept `if_exists` parameter.
  - `if_exists="fail"` (default) will return an exception if a Dataset matching this fqtn exists, or create one if it does not
  -  `if_exists="return"` will return the Dataset matching this fqtn if it exists, or create one if it does not
  - `if_exists="update"` will update the Dataset matching this fqtn if it exists, or create one if it does not

## [1.9.6] - Jul 26, 2022
### Fix
- Fixed `get.dataset` function to hit correct endpoint when passing in `resource_key` and `version` params (e.g. `rasgo.get.dataset(resource_key='xxx', version=1)`)

## [1.9.5] - Jul 22, 2022
### Fix
- Fixed issue with rendering when `Dataset` objects are passed as args to transform
- Change offline yaml contract to replace table ids with fqtns

## [1.9.4] - Jul 19, 2022
### Fix
- Fixed the `apply` transform

## [1.9.3] - Jul 19, 2022
### Fix
- Fixed bug causing transforms to fail when rendering with `Dataset` objects passed as args
### Add
- Added `create.dataset_from_dict()` function to create a new version of a Rasgo dataset from a valid Rasgo v2 offline schema
  - sample usage: <br><code>with open('test.yml', 'r') as yaml_file:
    <br>&nbsp;&nbsp;json=yaml.safe_load(yaml_file)
    <br>ds = rasgo.create.dataset_from_dict(json)</code>
### Change
- Changed `Dataset.generate_yaml()` method on Dataset class:
  - Added `file_path` parameter - when passed, method will write data to this file location
  - Updated yaml contract to reprsent new Rasgo v2 offline schema

## [1.9.2] - Jul 13, 2022
### Fix
- Fixed bug in the `publish.dbt_project()` method that caused metrics without a filter to raise compile errors in dbt

## [1.9.1] - Jul 12, 2022
### Fix
- Fixed bug in the `publish.dbt_project()` method that was causing model.sql files to print as simple select statements instead of expanding SQL views

## [1.9.0] - Jul 12, 2022
### Change
- Changed how "offline" datasets are rendered: render operations as a single CTE and don't write interim views to the DW unless the dataset is published
  - Rendering happens locally using RasgoTransforms package, removed calls to api

## [1.8.0] - Jul 8, 2022
### Add
- Added metrics to the schema.yml file generated by the `publish.dbt_project()` method

## [1.7.0] - Jul 7, 2022
### Change
- Changed default behavior of `publish.dbt_project()` method to write 1 schema.yml file per model (containing metadata for only 1 model) and 1 schema.yml file for all sources (containing all sources in the project).  Previously, this method wrote 1 schema.yml file per project that contained all models and sources in a the project.

## [1.6.0] - Jun 6, 2022
### Add
- Added `Dataset.take_snapshot()` method on Dataset primitive
- Added `rasgo.create.dataset_snapshot(id)` function

## [1.5.2] - May 31, 2022
### Fix
- Fixed Dataset from Accelerator info logging

## [1.5.1] - May 31, 2022
### Change
- Changed pyrasgo core package to install Snowflake dependencies (again)

## [1.5.0] - May 27, 2022
### Add
- Added support for BigQuery
- Added custom error types to replace APIError
### Change
- Changed package setup:
  - Database-specific dependencies have been removed from the core package requirements Running `pip install pyrasgo` will now only install rasgo's core dependencies.
  - Two extras packages are now available to support separate datawarehouses: `pyrasgo[snowflake]` and `pyrasgo[bigbquery]`
  Going forward, users should download the extras package that matches their datawarehouse. For all legacy Rasgo users this will be: `pip install "pyrasgo[snowflake]"`
- Changed behavior of `fqtn` param on `publish.df`: `dataset_table_name` is now fully redundant to `fqtn`. Either can be used to specify the target table to write your df. In a future release `dataset_table_name` will be deprecated and replaced by `fqtn`
### Fix
- Fixed `publish.df` to handle column names that start with non-SQL-compliant values. An underscore ("_") will not be appended to these columns. e.g. `2B` will be converted to `_2B` in SQL to avoid errors.

## [1.4.5] - May 27, 2022
### Change
- Internal tweaks to create functions
- Increase max polling time for dataset publish to an hour

## [1.4.4] - May 24, 2022
### Change
- Changed "GENERIC" to "UNSET" for dw_types with transforms

## [1.4.3] - May 23, 2022
### Change
- Added auto docs generation to `dataset.to_accelerator()`

## [1.4.2] - May 19, 2022
### Add
- Added support for joins in `dataset.to_accelerator()`

## [1.4.1] - May 19, 2022
### Change
- Changed `dataset.refresh_table()` to use new backend polling logic

## [1.4.0] - May 17, 2022
### Add
- Added `dw_type` to transform create and update

## [1.3.1] - May 9, 2022
### Change
- Fixed duplicate parent operations sent through API in edge case on dataset publish call
- Updated new `dataset.profile()` URL

## [1.3.0] - May 6, 2022
### Add
- Added `rasgo.publish.dbt_project()` function to convert datasets into dbt project files
- Added `Dataset.to_accelerator()` to make it easier to turn a published dataset into an Accelerator definition
### Remove
- Removed `Dataset.to_dbt` method. Replaced by `rasgo.publish.dbt_project()`.

## [1.2.0] - Apr 26, 2022
### Add
- Added `rasgo.create.accelerator_from_yml()` to support creating accelerators from offline yml definitions

## [1.1.0] - Apr 26, 2022
### Add
- Added `.dw_sync()` method to Dataset class. This method will synchronize any changes from the Snowflake table schema to the Dataset metadata

## [1.0.2] - Apr 22, 2022
### Add
- Added support for Accelerators version 2
   - `rasgo.create.accelerator()`
   - `rasgo.get.accelerator()`
   - `rasgo.get.accelerators()`
   - `rasgo.delete.accelerator()`
   - `rasgo.create.dataset_from_accelerator()`

## [1.0.1] - Apr 22, 2022
### Add
- Added property `source_type` to dataset primitive
### Change
- Changed behavior of source functions. When hitting Rasgo API on `rasgo.publish.<source_type>()` calls specify dataset `source_type` in request

## [1.0.0] - Apr 21, 2022
### Add
- Added `resource_key` parameter to `publish.df` and `publish.table` methods
- Added `resource_key` property to Dataset class
### Change
- Changed `pulish.dataset` method to run async by default to address endpoint timeouts on large datasets
### Remove
  - Deprecated all legacy feature, collection & dataframe functionality

## [0.5.4] - Apr 15, 2022
### Add
  - Added `to_sql()` method to `Dataset` to get a pure sql statement that can be used to create the dataset
  - Added `table_type` attribute to `Dataset`. Values: (`VIEW`, `TABLE`)

## [0.5.3] - Apr 6, 2022
### Fix
  - Fixed Transform creation functionality

## [0.5.2] - Apr 5, 2022
### Add
  - Added param `table_name` for `rasgo.publish.dataset()` for specifying the table name you want to set for the dataset

## [0.5.1] - Apr 4, 2022
### Add
  - Added deprecation warnings for pre-1.0 functions

## [0.5.0] - Mar 23, 2022
### Change
  - Updated Snowflake connection to use correct role

## [0.4.36] - Mar 22, 2022
  - Make `ds.refresh_table()` complete refresh when function finishes running always

## [0.4.35] - Mar 16, 2022
   - Adds a PyRasgo Primitive for an Accelerator
   - Adds the following methods for working with Accelerators in PyRasgo
     - `rasgo.get.accelerator()`
     - `rasgo.get.accelerators()`
     - `rasgo.create.accelerator()`
     - `rasgo.delete.accelerator()`
     - `rasgo.create.dataset_from_accelerator()`
     - `Accelerator.apply()`

## [0.4.34] - Mar 11, 2022
   - Add `to_dbt()` function to `Datasets`
      - Use this method to export a published Dataset as a DBT Model
   - Support tracking of dataset dependencies passed transforms that accept lists of datasets (multi-join)

## [0.4.33] - Mar 11, 2022
   - Handles long running `ds.refresh_table()` process

## [0.4.32] - Mar 10, 2022
   - Fixed uses of apply transform

## [0.4.31] - Mar 04, 2022
   - Raise an error if you supply an arg to transform which doesn't exist
   - Fix dependency management for transform arguments of type `table_list`

## [0.4.30] - Mar 01, 2022
   - Cache and return dataset columns if not set when calling `ds.columns` and ds from API
   - New method `rasgo.update.column()` to set/update metadata about a ds column

## [0.4.29] - Mar 01, 2022
   - Bugfixes

## [0.4.28] - Feb 28, 2022
  - Fetches **all** datasets on a call to `rasgo.get.datasets()`

## [0.4.27] - Feb 25, 2022
  - Adds ability to set `tags` when creating a transform in the function `rasgo.create.transform()`

## [0.4.26] - Feb 22, 2022
  - Allow published datasets with tables as their output to be refreshed using `dataset.refresh_table()`

## [0.4.25] - Feb 22, 2022
  - Creates more informative generated Data Warehouse Table names; Now tables/views names made in PyRasgo will look like the following below
    - `RASGO_SDK__OP<op_num>__<transform_name>_transform__<guid>`
  - Adds proper error message with steps to take to fix, when publishing a DF with incompatible pandas date types

## [0.4.24] - Feb 21, 2022
  - Adds the optional parameter `generate_stats` to toggle stats generation when publishing with `rasgo.publish.table/df()` (defaults to True if not passed)

## [0.4.23] - Feb 17, 2022
  - Adds the parameter `parents` to specify parent dataset dependencies of table or pandas dataframe when publishing with `rasgo.publish.table/df()`

## [0.4.22] - Feb 15, 2022
  - Allows users to get the PyRasgo code used to generate a dataset with the function `dataset.generate_py()`

## [0.4.21] - Feb 08, 2022
   - Enable users to append to an existing Rasgo Dataset using `rasgo.publish.df(fqtn="MY.FQTN.STRING", if_exists="append")`

## [0.4.20] - Feb 07, 2022
   - Add `render_only` optional parameter to `Dataset.transform()` to support printing the SQL that will be executed by an applied transform instead of creating a new Dataset.
      - This option allows testing of transform arguments without having to execute the transform

## [0.4.19] - Feb 02, 2022
   - Bug fixes

## [0.4.18] - Feb 02, 2022
   - Add optional `rasgo.publish.dataset()` parameter `table_type` to support materializing a dataset as a table instead of a view.

## [0.4.17] - Feb 01, 2022
   - Add `Dataset.generate_yaml()` to allow users to export their datasets and associated operation sets as a YAML string
   - Add `Dataset.versions` attribute to support retrieving all versions of a Dataset

## [0.4.16] - Jan 31, 2022
   - Add `Dataset.run_stats()` to allow users to trigger stats generation for a dataset
   - Add `Dataset.profile()` to give users a link to the Rasgo UI, where they can view details on their Dataset, including any generated stats

## [0.4.15] - Jan 27, 2022
   - Update timeseries tracking attribute name to `time_index` to match keyword

## [0.4.14] - Jan 26, 2022
   - Remove unnecessary import

## [0.4.13] - Jan 26, 2022
   - Add the ability to publish dataset attributes when publishing a dataset

## [0.4.12] - Jan 21, 2022
  - Change `experimental_async` to `async_compute`, default to `True`

## [0.4.11] - Jan 25, 2022
  - Bug fixes

## [0.4.10] - Jan 24, 2022
  - Adds dataset `snapshot` information to `Dataset.snapshots` and provides a hook to return a snapshot's data with `Dataset.to_df(snapshot_index=<int>)`

## [0.4.9] - Jan 17, 2022
  - Adds parameters `filters`, `order_by`, and `columns` to dataset.to_df() and dataset.preview() methods

## [0.4.8] - Jan 14, 2022
  - Adds `experimental_async` flag to transforms to take advantage of experimental long-running operation creation

## [0.4.7] - Jan 13, 2022
  - Return errors for operation creation

## [0.4.6] - Jan 12, 2022
  - Adds support for long running operation creations

## [0.4.5] - Dec 21, 2021
  - Fixes dependency installation

## [0.4.4] - Dec 21, 2021
  - Adds support for Python versions `3.7.12`, `3.8`, `3.9`, and `3.10`

## [0.4.3] - Dec 17, 2021
  -  Method added `rasgo.update.transform()` to update a transform


## [0.4.2] - Dec 15, 2021
   - Adds the ability to reference Dataset attributes directly
      - `Dataset.id`
      - `Dataset.name`
      - `Dataset.description`
      - `Dataset.status`
      - `Dataset.fqtn`
      - `Dataset.columns`
      - `Dataset.created_date`
      - `Dataset.update_date`
      - `Dataset.attributes`
      - `Dataset.dependencies`
      - `Dataset.sql`
   - Adds ability function for getting Datasets by `fqtn`
      - `rasgo.get.dataset(fqtn='MY_FQTN'>)`


## [0.4.1] - Dec 13, 2021
   - "Updates"


## [0.4.0] - Dec 07, 2021
   - Add Rasgo Datasets
      - Datasets are the new, single primitive available in Rasgo. Users can explore, transform, and create new data warehouse tables using this single primitive object.
      - Transforming a previously saved Dataset will produce a new Dataset definition that builds on top of the transformed Dataset. This new dataset will consist of a new operation that references the transformed Dataset as the `source_table` in the applied transform. Further transforms will add to the list of operations until `.save` is called to persist the created operations as a new Dataset in Rasgo.
      - New Rasgo Functions:
         - `rasgo.get.datasets` - Get a list of all available Datasets
         - `rasgo.get.dataset` - Get a single Dataset by ID, including the list of operations that created it (if they exist)
         - `rasgo.update.dataset` - Update name and description
         - `rasgo.delete.dataset` - Delete a Dataset
         - `rasgo.publish.dataset` - Save a new dataset to Rasgo. Can only save new Datasets that have been created by transforming old Datasets
         - `rasgo.publish.df` - Publish a Pandas DataFrame as a Rasgo Dataset
         - `rasgo.publish.table` - Publish an existing table as a Rasgo dataset
      - Dataset Primitive Functions:
         - `Dataset.transform` - Transform a previously existing Dataset with a given Transform to create a new Dataset definition
            - You can also reference transforms by name directly.
            - e.g. `dataset.join(...)` as opposed to `dataset.transform(transform_name='join', ...)`
         - `Dataset.to_df` - Read a Dataset into a Pandas DataFrame
         - `Dataset.preview` - Get a Pandas DataFrame consisting of the top 10 rows produced by this Dataset
      - Dataset Attributes:
         - `Dataset.sql` - A sql string representation of the operations that produce this dataset (if they exist)


## [0.3.4] - Dec 03, 2021
   - Temporary hotfix: DataSource.to_dict() returns `sourceTable` attribute as a table name, instead of fqtn. Plan is to revert to fqtn in a future version when publish methods offer first-class handling of fqtn.


## [0.3.3] - Nov 08, 2021
   - Added detailed Transform Argument Definitions during Transform creation
   - Allow null values for User Defined Transform arguments


## [0.3.2] - Oct 13, 2021
   - Adds [Jinja](https://jinja.palletsprojects.com/) as the templating engine for User Defined Transforms
   	- Source transforms may now be previewed, tested and deleted to enable a full creation experience.
   	- Adds Rasgo template functions to enable dynamic template building


## [0.3.1] - Sept 27, 2021
   - Adds `filter` and `limit` params to `read.collection_snapshot_data` function
   - Fixes Collection response model bug


## [0.3.0] - Sept 22, 2021
   - Deprecates FeatureSet primitive (see docs for migration path: https://docs.rasgoml.com/rasgo-docs/pyrasgo-version-log/version-0.3)
   - Adds support for creating features using python source code
   - Adds support for user-defined transformation functionality
   - Adds methods to interact with Collection snapshots (DEPRECATED):
     - `get.collection_snapshots()`
     - `read.collection_snapshot_data()`
   - Adds methods to Collection primitive:
     - `.preview()` to view data in a pandas df
     - `.get_compatible_features()` to list features available to join
   - Adds `.to_dict` and `.to_yml` methods to DataSource primitive

## [0.2.5] - Aug 18, 2021
   - adds handling and user notification for highly null dataframes which would otherwise not function well with `evaluate.profile` or `evaluate.feature_importance`

## [0.2.4] - Aug 4, 2021
   - supports tables named as restricted Snowflake keywords (e.g. ACCOUNT, CASE, ORDER) to be registered as Rasgo Sources

## [0.2.3] - July 30, 2021
   - introduces `publish.features_from_source_code()` function. This function allows users to pass a custom SQL string to create a view in Snowflake using their own code. This function will: register a child source based off the parent source provided as input, register features from the new child source table.
   - introduces new workflow to `publish.source_data()` function. Pass in `source_type="sql", sql_definition="<valid sql select string>"` to create a new Rasgo DataSource as a view in Snowflake using custom SQL.
   - makes the `features` parameter optional in `publish.features_from_source()` function. If param is not passed, all columns in the underlying table that are not in the `dimensions` list will be registered as features
   - adds `trigger_stats` parameter to all publish method. When set to False, statistical profiling will not run for the data objects being published. Default = True
   - adds `verbose` parameter to all publish methods. When set to True, prints status messages to stdout to update users on progress of the function. Default = False.
   - introduces `.sourceCode` property on Rasgo DataSource and FeatureSet classes to display the SQL or python source code used to build the underlying table
   - introduces `.render_sql_definition()` method on Collection class to display the SQL used to create the underlying collection view
   - introduces `.dimensions` property on Rasgo Collection class to display all unique dimension columns in a Collection
   - introduces `trigger_stats` parameter in `collection.generate_training_data()` method to allow users to generate a sql view without kicking off correlation and join stats. Set to False to suppress stats jobs. Default=True.
   - Add support for optional catboost parameter `train_dir` in `evaluate.feature_importance()` function, which allows users to dictate where temporary training files are generated

## [0.2.2(July 14, 2021
   - Allow for consistency in `evaluate.feature_importance()` evaluation metrics for unchanged dataframes
   - Allow users to control certain CatBoost parameters when running `evaluate.feature_importance()`

## [0.2.1(July 01, 2021
   - expand `evaluate.feature_importance()` to support calculating importance for collections

## [0.2.0(June 24, 2021
   - introduce `publish.experiment()` method to fast track dataframes to Rasgo objects
   - fix register bug

## [0.1.14(June 17, 2021
   - improve new user signup experience in `register()` method
   - fix dataframe bug when experiment wasn't set

## [0.1.13(June 16, 2021
   - intelligently run Regressor or Classifier model in `evaluate.feature_importance()`
   - improve model performance statistics in `evaluate.feature_importance()`: include AUC, Logloss, precision, recall for classification

## [0.1.12(June 11, 2021
   - support fqtn in `publish.source_data(table)` parameter
   - trim timestamps in dataframe profiles to second grain

## [0.1.11(June 9, 2021
   - hotfix for unexpected histogram output

## [0.1.10(June 8, 2021
   - pin pyarrow dependency to < version 4.0 to prevent segmentation fault errors

## [0.1.9(June 8, 2021
   - improve model performance in `evaluate.feature_importance()` by adding test set to catboost eval

## [0.1.8(June 7, 2021
   - `evaluate.train_test_split()` function supports non-timeseries dataframes
   - `evaluate.feature_importance()` function now runs on an 80% training set
   - adds `timeseries_index` parameter to `evaluate.feature_importance()` & `prune.features()` functions

## [0.1.7(June 2, 2021
   - expands dataframe series type recognition for profiling

## [0.1.6(June 2, 2021
   - cleans up dataframe profiles to enhance stats and visualization for non-numeric data

## [0.1.5(June 2, 2021
   - introduces `pip install "pyrasgo[df]"` option which will install: shap, catboost, & scikit-learn

## [0.1.4(June 2, 2021
   ## [various improvements to dataframe profiles & feature_importance

## [0.1.3(May 27, 2021
   - introduces experiment tracking on dataframes
   - fixes errors when running feature_importance on dataframes with NaN values

## [0.1.2(May 26, 2021
   - generates column profile automatically when running feature_importance

## [0.1.1(May 24, 2021
   - supports sharing public dataframe profiles
   - enforces assignment of granularity to dimensions in Publish methods based on list ordering

## [0.1.0(May 17, 2021
   - introduces dataframe methods: evaluate, prune, transform
   - supports free pyrasgo trial registration

## [0.0.79(April 19, 2021
   - support additional datetime data types on Features
   - resolve import errors

## [0.0.78(April 5, 2021
   - adds include_shared param to get_collections() method

## [0.0.77(April 5, 2021
   - adds convenience method to rename a Feature’s displayName
   - adds convenience method to promote a Feature from Sandbox to Production status
   - fixes permissions bug when trying to read Community data sources from a public org

## [0.0.76(April 5, 2021
   - adds columns to DataSource primitive
   - adds verbose error message to inform users when a Feature name conflict is preventing creation

## [0.0.75(April 5, 2021
   - introduce interactive Rasgo primitives

## [0.0.74(March 25, 2021
   - upgrade Snowflake python connector dependency to 2.4.0
   - upgrade pyarrow dependency to 3.0


[2.1.0]: https://pypi.org/project/pyrasgo/2.1.0/
[2.0.2]: https://pypi.org/project/pyrasgo/2.0.2/
[2.0.1]: https://pypi.org/project/pyrasgo/2.0.1/
[2.0.0]: https://pypi.org/project/pyrasgo/2.0.0/
[1.11.0]: https://pypi.org/project/pyrasgo/1.11.0/
[1.10.0]: https://pypi.org/project/pyrasgo/1.10.0/
[1.9.6]: https://pypi.org/project/pyrasgo/1.9.6/
[1.9.5]: https://pypi.org/project/pyrasgo/1.9.5/
[1.9.4]: https://pypi.org/project/pyrasgo/1.9.4/
[1.9.3]: https://pypi.org/project/pyrasgo/1.9.3/
[1.9.2]: https://pypi.org/project/pyrasgo/1.9.2/
[1.9.1]: https://pypi.org/project/pyrasgo/1.9.1/
[1.9.0]: https://pypi.org/project/pyrasgo/1.9.0/
[1.8.0]: https://pypi.org/project/pyrasgo/1.8.0/
[1.7.0]: https://pypi.org/project/pyrasgo/1.7.0/
[1.6.0]: https://pypi.org/project/pyrasgo/1.6.0/
[1.5.2]: https://pypi.org/project/pyrasgo/1.5.2/
[1.5.1]: https://pypi.org/project/pyrasgo/1.5.1/
[1.5.0]: https://pypi.org/project/pyrasgo/1.5.0/
[1.4.5]: https://pypi.org/project/pyrasgo/1.4.5/
[1.4.4]: https://pypi.org/project/pyrasgo/1.4.4/
[1.4.3]: https://pypi.org/project/pyrasgo/1.4.3/
[1.4.2]: https://pypi.org/project/pyrasgo/1.4.2/
[1.4.1]: https://pypi.org/project/pyrasgo/1.4.1/
[1.4.0]: https://pypi.org/project/pyrasgo/1.4.0/
[1.3.1]: https://pypi.org/project/pyrasgo/1.3.1/
[1.3.0]: https://pypi.org/project/pyrasgo/1.3.0/
[1.2.0]: https://pypi.org/project/pyrasgo/1.2.0/
[1.1.0]: https://pypi.org/project/pyrasgo/1.1.0/
[1.0.0]: https://pypi.org/project/pyrasgo/1.0.0/
[0.5.4]: https://pypi.org/project/pyrasgo/0.5.4/
[0.5.3]: https://pypi.org/project/pyrasgo/0.5.3/
[0.5.2]: https://pypi.org/project/pyrasgo/0.5.2/
[0.5.1]: https://pypi.org/project/pyrasgo/0.5.1/
[0.5.0]: https://pypi.org/project/pyrasgo/0.5.0/
