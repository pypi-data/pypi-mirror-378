import pandas as pd
import numpy as np
from deepdiff import DeepDiff

def validate_columns(df_ref, df, option_verbose=True):
    columns_ref = df_ref.columns
    columns = df.columns
    if columns_ref.all() != columns.all():
        if option_verbose:
            print(f"columns_ref: {columns_ref}")
            print(f"columns: {columns}")
        return False
    return True

def validate_shape(df_ref, df, option_verbose=True):
    shape_ref = df_ref.shape
    shape = df.shape
    if shape_ref != shape:
        if option_verbose:
            print(f"shape_ref: {shape_ref}")
            print(f"shape: {shape}")
        return False
    return True

def validate_dtypes(df_ref, df, option_verbose=True):
    dtypes_ref = df_ref.dtypes
    dtypes = df.dtypes
    if not dtypes_ref.equals(dtypes):
        if option_verbose:
            print(f"dtypes_ref: {dtypes_ref}")
            print(f"dtypes: {dtypes}")
        return False
    return True

def validate_index(df_ref, df, option_verbose=True):
    index_ref = df_ref.index
    index = df.index
    if not index_ref.equals(index):
        if option_verbose:
            print(f"index_ref: {index_ref}")
            print(f"index: {index}")
        return False
    return True

def validate_index_string(df_ref, df, option_verbose=True):
    """Enhanced datetime index validation for pseudo isomorphism stability"""
    try:
        # Handle datetime indices with improved stability
        if isinstance(df_ref.index, pd.DatetimeIndex) and isinstance(df.index, pd.DatetimeIndex):
            # For datetime indices, compare normalized timestamps
            index_ref_normalized = pd.to_datetime(df_ref.index).normalize()
            index_normalized = pd.to_datetime(df.index).normalize()
            if not index_ref_normalized.equals(index_normalized):
                if option_verbose:
                    print(f"datetime index_ref: {index_ref_normalized}")
                    print(f"datetime index: {index_normalized}")
                return False
        else:
            # For non-datetime indices, use string comparison
            index_ref = df_ref.index.astype(str)
            index = df.index.astype(str)
            if not index_ref.equals(index):
                if option_verbose:
                    print(f"index_ref: {index_ref}")
                    print(f"index: {index}")
                return False
        return True
    except Exception as e:
        if option_verbose:
            print(f"Index validation error: {e}")
        # Fallback to basic string comparison
        try:
            index_ref = df_ref.index.astype(str)
            index = df.index.astype(str)
            return index_ref.equals(index)
        except:
            return False

def is_missing(x):
    return pd.isna(x)

def validate_values(df_ref, df):
    values_ref = df_ref.values
    values = df.values
    equal_mask = values_ref == values
    # both_nan_mask = np.logical_and(is_missing(values_ref), is_missing(values))
    # result_mask = np.logical_or(equal_mask, both_nan_mask)
    # return result_mask.all()
    return equal_mask.all()

def validate_values_strict(df_ref, df):
    values_ref = df_ref.values
    values = df.values
    return np.array_equal(values_ref, values)

def validate_df_isomorphism(df_ref, df, option_verbose=True):
    return (
        validate_columns(df_ref, df, option_verbose) 
        and validate_index(df_ref, df, option_verbose) 
        and validate_shape(df_ref, df, option_verbose) 
        and validate_dtypes(df_ref, df, option_verbose) 
        and validate_values(df_ref, df)
    )

def validate_df_pseudo_isomorphism(df_ref, df, option_verbose=True):
    return (
        validate_shape(df_ref, df, option_verbose) 
        and validate_columns(df_ref, df, option_verbose) 
        and validate_index_string(df_ref, df, option_verbose) 
    )

def validate_df_strict_isomorphism(df_ref, df):
    return (df_ref.equals(df))

def validate_data_isomorphism(data_ref, data):
    diff = DeepDiff(data_ref, data, ignore_order=True, significant_digits=12, ignore_nan_inequality=True)
    is_equal = (diff == {})
    return is_equal
