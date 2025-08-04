import os
import pandas as pd
import plotly.graph_objects as go

from dotenv import load_dotenv
from plotly.subplots import make_subplots
from sqlalchemy import create_engine

# Load key for SQL database
load_dotenv()
POSTGRES_PW = os.getenv('POSTGRES_PW')

def get_engine():
    # Opens connection to database
    return create_engine(
        f"postgresql://postgres:{POSTGRES_PW}@localhost:5432/macro_data"
    )
    
def load_table(table_name):
    # Loads a table from the database
    engine = get_engine()
    df = pd.read_sql_table(table_name, con=engine, index_col="Date", parse_dates=["Date"])
    return df


def plot_datasets(primary_df, secondary_df, primary_series, secondary_series, primary_range=None, secondary_range=None):
    # Initialize
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    # Primary Y-axis
    fig.add_trace(go.Scatter(x=primary_df.index, y=primary_df[primary_series], name=primary_series), secondary_y=False)
    # Secondary Y-axis
    fig.add_trace(go.Scatter(x=secondary_df.index, y=secondary_df[secondary_series], name=secondary_series, line=dict(color="orange")), secondary_y=True)
    # Add axis titles
    if primary_range:
        fig.update_yaxes(title_text=primary_series, secondary_y=False, range=primary_range)
    else:
        fig.update_yaxes(title_text=primary_series, secondary_y=False)
    if secondary_range:
        fig.update_yaxes(title_text=secondary_series, secondary_y=True, range=secondary_range)
    else:
        fig.update_yaxes(title_text=secondary_series, secondary_y=True)
    # Adjust the height/width of the chart and position of the legend
    fig.update_layout(width=1000, height=600, legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center",x=0.5), margin=dict(t=10, b=20, l=20, r=20))
    return fig


def basic_plot(df, series_name, series_range=None):
    # Initialize
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df[series_name], name=series_name))
    # If range provided, update the axis
    if series_range:
        fig.update_yaxes(title_text=series_name, range=series_range)
    # Adjust the height/width of the chart
    fig.update_layout(width=1000, height=600, legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center",x=0.5), margin=dict(t=10, b=20, l=20, r=20))
    return fig


def plot_with_constant(df, series_name, constant_y, series_range=None):
    # Initialize
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df[series_name], name=series_name))
    # If range provided, update the axis
    if series_range:
        fig.update_yaxes(title_text=series_name, range=series_range)
    # Add horizontal line at y=constant_y
    fig.add_shape(type="line",x0=df.index.min(), x1=df.index.max(),y0=constant_y, y1=constant_y,line=dict(color="white", width=1, dash="dash"),name="Zero Line")
    # Adjust the height/width of the chart
    fig.update_layout(width=1000, height=600, legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center",x=0.5), margin=dict(t=10, b=20, l=20, r=20))
    return fig