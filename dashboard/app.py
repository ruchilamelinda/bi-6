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
        # Sidebar dengan filter (tanpa visualisasi)
        html.Div([
            create_filters(df),
            create_data_input(df)  # Form input tetap di sidebar
        ], className="sidebar"),
        
        # Area konten utama yang diperluas
        html.Div([
            # Tab untuk berbagai analisis
            dcc.Tabs(id="main-tabs", value='overview', children=[
                dcc.Tab(label='📊 Gambaran Pasar', value='overview', className="custom-tab"),
                dcc.Tab(label='🚀 Faktor Kesuksesan', value='success-factors', className="custom-tab"),
                dcc.Tab(label='💰 Monetisasi', value='revenue-insights', className="custom-tab"),
                dcc.Tab(label='🔍 Analisis Aplikasi Baru', value='app-analysis', className="custom-tab"),
            ], className="custom-tabs"),
            
            # Area konten yang berubah berdasarkan tab
            dcc.Loading(
                id="loading-tab-content",
                type="circle",
                children=html.Div(id='tab-content', className="tab-content")
            )
        ], className="main-content")
    ], className="dashboard-body"),
    
    # Komponen penyimpanan data
    dcc.Store(id='filtered-data-store'),
    dcc.Store(id='app-data-store', data=df.to_dict('records') if not df.empty else []),
    dcc.Store(id='analysis-results-store'),  # Store baru untuk hasil analisis
], className="dashboard-container")

# ===============================
# FUNGSI CALLBACK UTAMA
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

@app.callback(
    [
        Output('app-data-store', 'data'),
        Output('add-app-output', 'children'),
        Output('analysis-results-store', 'data')
    ],
    [Input('add-app-btn', 'n_clicks')],
    [
        State('input-app-name', 'value'),
        State('input-category', 'value'),
        State('input-rating', 'value'),
        State('input-installs', 'value'),
        State('input-size', 'value'),
        State('app-data-store', 'data')
    ],
    prevent_initial_call=True
)
def analyze_new_app(n_clicks, app_name, category, rating, installs, size, current_data):
    if n_clicks is None or n_clicks == 0:
        raise dash.exceptions.PreventUpdate
    
    try:
        # Validasi input
        if not all([app_name, category, rating, installs, size]):
            return [
                dash.no_update,
                html.Div("⚠️ Harap isi semua field yang diperlukan!", className="error-message"),
                dash.no_update
            ]
        
        # Konversi tipe data
        rating = float(rating)
        installs = int(installs)
        size = float(size)
        
        if not (1 <= rating <= 5):
            return [
                dash.no_update,
                html.Div("⚠️ Rating harus antara 1 sampai 5!", className="error-message"),
                dash.no_update
            ]
        
        # Buat entri aplikasi baru
        new_app = {
            'app_name': app_name,
            'category': category,
            'rating': rating,
            'total_installs': installs,
            'size_mb': size,
            'price_type': 'Free',
            'release_year': datetime.now().year,
            'fact_id': len(current_data) + 1 if current_data else 1
        }
        
        # Update data store
        updated_data = current_data + [new_app] if current_data else [new_app]
        
        # Buat semua visualisasi
        analysis_results = {
            'app_name': app_name,
            'rating_fig': create_rating_comparison(new_app, current_data),
            'installs_fig': create_installs_comparison(new_app, current_data),
            'radar_fig': create_radar_analysis(new_app, current_data),
            'trend_fig': create_category_trend(new_app, current_data),
            'comparison_table': create_comparison_table(new_app, current_data)
        }
        
        # Pesan sukses
        success_msg = html.Div([
            html.I(className="fas fa-check-circle", style={'color': '#01875f'}),
            f" Analisis untuk '{app_name}' berhasil dibuat!"
        ], className="success-message")
        
        return [
            updated_data,
            success_msg,
            analysis_results
        ]
        
    except Exception as e:
        error_msg = html.Div([
            html.I(className="fas fa-exclamation-triangle", style={'color': '#ea4335'}),
            f" Error: {str(e)}"
        ], className="error-message")
        
        return [
            dash.no_update,
            error_msg,
            dash.no_update
        ]

@app.callback(
    Output('tab-content', 'children'),
    [Input('main-tabs', 'value'),
     Input('filtered-data-store', 'data'),
     Input('analysis-results-store', 'data')],
    [State('app-data-store', 'data')]
)
def render_tab_content(active_tab, filtered_data, analysis_results, app_data):
    ctx = dash.callback_context
    
    # Handle ketika tab analysis dipilih dan ada hasil analisis
    if active_tab == 'app-analysis' and analysis_results:
        # Buat layout dari hasil analisis yang tersimpan
        return html.Div([
            html.H3(f"Analisis Aplikasi: {analysis_results['app_name']}", className="analysis-header"),
            
            # Baris pertama visualisasi
            html.Div([
                html.Div([
                    dcc.Graph(figure=analysis_results['rating_fig'], className="analysis-graph"),
                    html.P("Perbandingan Rating", className="analysis-description")
                ], className="analysis-card"),
                
                html.Div([
                    dcc.Graph(figure=analysis_results['installs_fig'], className="analysis-graph"),
                    html.P("Perbandingan Jumlah Install", className="analysis-description")
                ], className="analysis-card"),
            ], className="analysis-row"),
            
            # Baris kedua visualisasi
            html.Div([
                html.Div([
                    dcc.Graph(figure=analysis_results['radar_fig'], className="analysis-graph"),
                    html.P("Analisis Komprehensif", className="analysis-description")
                ], className="analysis-card"),
                
                html.Div([
                    dcc.Graph(figure=analysis_results['trend_fig'], className="analysis-graph"),
                    html.P("Trend Kategori", className="analysis-description")
                ], className="analysis-card"),
            ], className="analysis-row"),
            
            # Tabel perbandingan
            html.Div([
                html.H4("Ringkasan Perbandingan", className="table-header"),
                analysis_results['comparison_table']
            ], className="analysis-table-container")
        ], className="analysis-main-content")
    
    # Handle untuk tab lainnya
    if not filtered_data:
        return html.Div("Tidak ada data yang tersedia dengan filter saat ini.", className="no-data-message")
    
    try:
        df = pd.DataFrame(filtered_data)
        
        if active_tab == 'overview':
            return create_overview_content(df)
        elif active_tab == 'success-factors':
            return create_success_factors_content(df)
        elif active_tab == 'revenue-insights':
            return create_revenue_insights_content(df)
        elif active_tab == 'app-analysis':
            return html.Div([
                html.H3("Analisis Aplikasi Baru", className="analysis-header"),
                html.P("Masukkan detail aplikasi baru di sidebar untuk melihat analisis perbandingan.", 
                      className="analysis-description")
            ], className="analysis-main-content")
        else:
            return html.Div("Tab tidak dikenali", className="error-message")
            
    except Exception as e:
        return html.Div([
            html.I(className="fas fa-exclamation-triangle", style={'color': '#ea4335'}),
            f" Error: {str(e)}"
        ], className="error-message")

# Set the index string with our custom styles
app.index_string = HTML_TEMPLATE

# ===============================
# JALANKAN APLIKASI
# ===============================

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8050)