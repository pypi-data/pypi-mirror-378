def convert_to_date(df, cols):
    """Convert specified columns in a DataFrame to datetime format.
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing the columns to convert
    cols : list
        List of column names to convert to datetime
    Returns
    -------
    pd.DataFrame
        DataFrame with specified columns converted to datetime
    """
    import pandas as pd
    df_copy = df.copy()
    for col in cols:
        if col in df_copy.columns:
            df_copy[col] = pd.to_datetime(df_copy[col], errors='coerce')
    return df_copy

