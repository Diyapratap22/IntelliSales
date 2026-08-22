import pandas as pd
from ydata_profiling import ProfileReport


def profile_data(df):
    """
    Generate an automated profiling report for a sales dataset.
    """

    profile = ProfileReport(
        df,
        title="IntelliSales - Sales Data Profile",
        explorative=True
    )

    return profile