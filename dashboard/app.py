import dash
from dash import dcc, html, Input, Output, State, callback_context, dash_table
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, date
import os
import mysql.connector
from sqlalchemy import create_engine
import warnings
warnings.filterwarnings('ignore')

# Import functions and styles from other files
from functions import *
from styles import *

# ===============================
# KONEKSI DATABASE & LOAD DATA
# ===============================

# Memuat data awal
df = load_data_from_db()

# ===============================
# INISIALISASI APLIKASI DASH
# ===============================

app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Dashboard Analisis Google Play Store"

# CSS kustom
external_stylesheets = ['https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Layout Utama
app.layout = html.Div([
    create_header(df),
    
    html.Div([
        # Sidebar dengan filter
        html.Div([
            create_filters(df),
            create_data_input(df)
        ], className="sidebar"),
        
        # Area konten utama
        html.Div([
            # Tab untuk berbagai analisis
            dcc.Tabs(id="main-tabs", value='overview', children=[
                dcc.Tab(label='📊 Gambaran Pasar', value='overview', className="custom-tab"),
                dcc.Tab(label='🚀 Faktor Kesuksesan', value='success-factors', className="custom-tab"),
                dcc.Tab(label='💰 Monetisasi', value='revenue-insights', className="custom-tab"),
            ], className="custom-tabs"),
            
            # Area konten yang berubah berdasarkan tab
            html.Div(id='tab-content', className="tab-content")
        ], className="main-content")
    ], className="dashboard-body"),
    
    # Komponen penyimpanan data
    dcc.Store(id='filtered-data-store'),
    dcc.Store(id='app-data-store', data=df.to_dict('records') if not df.empty else []),
], className="dashboard-container")

# ===============================
# FUNGSI CALLBACK
# ===============================

@app.callback(
    Output('filtered-data-store', 'data'),
    [Input('category-filter', 'value'),
     Input('price-type-filter', 'value'),
     Input('rating-range', 'value'),
     Input('app-data-store', 'data')]
)
def update_filtered_data(categories, price_type, rating_range, stored_data):
    return filter_data(categories, price_type, rating_range, stored_data)

# Update the callback decorator to match your component IDs
@app.callback(
    [
        Output('app-data-store', 'data'),
        Output('add-app-output', 'children'),
        Output('success-analysis', 'children')  # This now matches the layout
    ],
    [Input('add-app-btn', 'n_clicks')],
    [
        State('input-app-name', 'value'),
        State('input-category', 'value'),
        State('input-rating', 'value'),
        State('input-installs', 'value'),
        State('input-size', 'value'),
        State('app-data-store', 'data')
    ]
)
def handle_add_app_callback(n_clicks, app_name, category, rating, installs, size, current_data):
    # Default returns
    if n_clicks == 0:
        raise dash.exceptions.PreventUpdate
    
    current_data = current_data or []
    
    try:
        updated_data, output_message, analysis_result = handle_add_app(
            n_clicks, app_name, category, rating, installs, size, current_data
        )
        
        return [
            updated_data,
            output_message or "",
            analysis_result or ""
        ]
    except Exception as e:
        return [
            current_data,
            html.Div(f"Error: {str(e)}", className="error-message"),
            ""
        ]
    
@app.callback(
    Output('tab-content', 'children'),
    [Input('main-tabs', 'value'),
     Input('filtered-data-store', 'data')]
)
def render_tab_content(active_tab, filtered_data):
    return render_content(active_tab, filtered_data)

# Set the index string with our custom styles
app.index_string = HTML_TEMPLATE

# ===============================
# JALANKAN APLIKASI
# ===============================

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8050)