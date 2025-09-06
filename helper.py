import boto3, json, os
import pandas as pd
import plotly.graph_objects as go

from plotly.subplots import make_subplots
from sqlalchemy import create_engine

# Load SQL database
def get_secret(secret_name, region_name="us-west-2"):
    client = boto3.client("secretsmanager", region_name=region_name)
    resp = client.get_secret_value(SecretId=secret_name)
    return json.loads(resp["SecretString"])

def get_engine(user_secret):
    # Opens connection to database
    creds = get_secret(user_secret)
    return create_engine(
        f"postgresql://{creds['DB_USER']}:{creds['DB_PASS']}@{creds['DB_HOST']}:{creds['DB_PORT']}/{creds['DB_NAME']}"
    )
    
def load_table(table_name):
    # Loads a table from the database
    engine = get_engine(user_secret="etl_readonly_pw")
    df = pd.read_sql_table(table_name, con=engine, index_col="Date", parse_dates=["Date"])
    return df


def plot_datasets(primary_df, secondary_df, primary_series, secondary_series, start_date, primary_range=None, secondary_range=None):
    # Initialize
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    # Adjust dates
    primary_df = primary_df[primary_df.index > start_date]
    secondary_df = secondary_df[secondary_df.index > start_date]
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


def basic_plot(df, series_name, start_date, series_range=None):
    # Adjust start date
    df = df[df.index > start_date]
    # Initialize
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df[series_name], name=series_name))
    # If range provided, update the axis
    if series_range:
        fig.update_yaxes(title_text=series_name, range=series_range)
    # Adjust the height/width of the chart
    fig.update_layout(width=1000, height=600, legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center",x=0.5), margin=dict(t=10, b=20, l=20, r=20))
    return fig


def plot_with_constant(df, series_name, constant_y, start_date, series_range=None):
    # Adjust start date
    df = df[df.index > start_date]
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