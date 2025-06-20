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

# ===============================
# KONEKSI DATABASE & LOAD DATA
# ===============================

def create_connection():
    """Membuat koneksi ke database MySQL"""
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",  
            password="",
            database="playstoredb",
            port=3306
        )
    except Exception as e:
        print(f"Error koneksi database: {e}")
        return None

def load_data_from_db():
    """Memuat data dari database MySQL"""
    try:
        engine = create_engine("mysql+mysqlconnector://root:@localhost:3306/playstoredb")
        query = """
        SELECT 
            f.fact_id,
            a.app_name,
            a.category,
            a.genres,
            a.current_ver,
            p.price_value,
            p.price_type,
            c.content_rating,
            d.android_version,
            d.size_mb,
            dt.release_date,
            dt.release_month,
            dt.release_year,
            f.rating,
            f.total_reviews,
            f.total_installs
        FROM fact_app_reviews f
        JOIN dim_app a ON f.app_id = a.app_id
        JOIN dim_price p ON f.price_id = p.price_id
        JOIN dim_contentrating c ON f.contentrating_id = c.contentrating_id
        JOIN dim_device d ON f.device_id = d.device_id
        JOIN dim_date dt ON f.date_id = dt.date_id
        """
        df = pd.read_sql_query(query, engine)
        engine.dispose()
        return df
    except Exception as e:
        print(f"Error memuat data: {e}")
        # Fallback ke CSV
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            csv_path = os.path.join(base_dir, "../tables/fact_app_reviews.csv")
            if os.path.exists(csv_path):
                return pd.read_csv(csv_path)
        except:
            pass
        return pd.DataFrame()

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

# ===============================
# KOMPONEN LAYOUT
# ===============================

def create_header():
    return html.Div([
        html.Div([
            html.H1([
                html.I(className="fab fa-google-play", style={'marginRight': '15px', 'color': '#01875f'}),
                "Dashboard Analisis Google Play Store"
            ], className="header-title"),
            html.P("Insight untuk Pengembang Aplikasi", className="header-subtitle"),
        ], className="header-content"),
        
        # Kartu Metrik Utama
        html.Div([
            html.Div([
                html.Div([
                    html.I(className="fas fa-mobile-alt", style={'fontSize': '2rem', 'color': '#01875f'}),
                ], className="metric-icon"),
                html.Div([
                    html.H3(f"{len(df):,}", className="metric-number"),
                    html.P("Total Aplikasi", className="metric-label")
                ], className="metric-content")
            ], className="metric-card"),
            
            html.Div([
                html.Div([
                    html.I(className="fas fa-star", style={'fontSize': '2rem', 'color': '#ffa500'}),
                ], className="metric-icon"),
                html.Div([
                    html.H3(f"{df['rating'].mean():.2f}" if not df.empty else "0", className="metric-number"),
                    html.P("Rating Rata-rata", className="metric-label")
                ], className="metric-content")
            ], className="metric-card"),
            
            html.Div([
                html.Div([
                    html.I(className="fas fa-download", style={'fontSize': '2rem', 'color': '#4285f4'}),
                ], className="metric-icon"),
                html.Div([
                    html.H3(f"{df['total_installs'].sum()/1e9:.1f}M" if not df.empty else "0", className="metric-number"),
                    html.P("Total Install", className="metric-label")
                ], className="metric-content")
            ], className="metric-card"),
            
            html.Div([
                html.Div([
                    html.I(className="fas fa-tags", style={'fontSize': '2rem', 'color': '#ea4335'}),
                ], className="metric-icon"),
                html.Div([
                    html.H3(f"{df['category'].nunique()}" if 'category' in df.columns else "0", className="metric-number"),
                    html.P("Kategori", className="metric-label")
                ], className="metric-content")
            ], className="metric-card"),
        ], className="metrics-container"),
    ], className="main-header")

def create_filters():
    if df.empty:
        return html.Div("Tidak ada data yang tersedia untuk filter")
        
    return html.Div([
        html.H3("🔍 Filter Data", className="section-title"),
        
        html.Div([
            # Filter Kategori
            html.Div([
                html.Label("Pilih Kategori:", className="filter-label"),
                dcc.Dropdown(
                    id='category-filter',
                    options=[{'label': cat, 'value': cat} for cat in sorted(df['category'].unique())],
                    value=sorted(df['category'].unique())[:5],  # Default 5 kategori pertama
                    multi=True,
                    className="custom-dropdown"
                )
            ], className="filter-item"),
            
            # Filter Tipe Harga
            html.Div([
                html.Label("Tipe Aplikasi:", className="filter-label"),
                dcc.RadioItems(
                    id='price-type-filter',
                    options=[
                        {'label': 'Semua Aplikasi', 'value': 'all'},
                        {'label': 'Aplikasi Gratis', 'value': 'Free'},
                        {'label': 'Aplikasi Berbayar', 'value': 'Paid'}
                    ],
                    value='all',
                    className="custom-radio"
                )
            ], className="filter-item"),
            
            # Range Rating
            html.Div([
                html.Label("Range Rating:", className="filter-label"),
                dcc.RangeSlider(
                    id='rating-range',
                    min=df['rating'].min() if not df.empty else 0,
                    max=df['rating'].max() if not df.empty else 5,
                    step=0.1,
                    value=[df['rating'].min() if not df.empty else 0, 
                           df['rating'].max() if not df.empty else 5],
                    marks={i: f'{i}⭐' for i in range(1, 6)},
                    className="custom-slider"
                )
            ], className="filter-item"),
        ], className="filters-grid"),
    ], className="filters-section")

def create_data_input():
    """Form untuk menambah data aplikasi baru"""
    return html.Div([
        html.H3("➕ Tambah Data Aplikasi Baru", className="section-title"),
        html.Div([
            html.Div([
                html.Label("Nama Aplikasi:", className="input-label"),
                dcc.Input(id='input-app-name', placeholder='Masukkan nama aplikasi', className="data-input"),
            ], className="input-group"),
            
            html.Div([
                html.Label("Kategori:", className="input-label"),
                dcc.Dropdown(
                    id='input-category',
                    options=[{'label': cat, 'value': cat} for cat in sorted(df['category'].unique())] if not df.empty else [],
                    placeholder='Pilih kategori',
                    className="data-input"
                ),
            ], className="input-group"),
            
            html.Div([
                html.Label("Rating (1-5):", className="input-label"),
                dcc.Input(id='input-rating', placeholder='4.5', type='number', 
                         min=1, max=5, step=0.1, className="data-input"),
            ], className="input-group"),
            
            html.Div([
                html.Label("Jumlah Install:", className="input-label"),
                dcc.Input(id='input-installs', placeholder='1000000', type='number', className="data-input"),
            ], className="input-group"),
            
            html.Div([
                html.Label("Ukuran (MB):", className="input-label"),
                dcc.Input(id='input-size', placeholder='25', type='number', className="data-input"),
            ], className="input-group"),
            
            html.Button('Tambah Data', id='add-app-btn', className="add-btn", n_clicks=0),
            html.Div(id='add-app-output', className="input-feedback")
        ], className="input-container")
    ], className="input-section")

# Layout Utama
app.layout = html.Div([
    create_header(),
    
    html.Div([
        # Sidebar dengan filter
        html.Div([
            create_filters(),
            create_data_input()
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
    if not stored_data:
        return []
    
    dff = pd.DataFrame(stored_data)
    
    # Terapkan filter
    if categories:
        dff = dff[dff['category'].isin(categories)]
    
    if price_type != 'all':
        dff = dff[dff['price_type'] == price_type]
    
    if rating_range:
        dff = dff[(dff['rating'] >= rating_range[0]) & (dff['rating'] <= rating_range[1])]
    
    return dff.to_dict('records')

@app.callback(
    [Output('app-data-store', 'data'),
     Output('add-app-output', 'children')],
    [Input('add-app-btn', 'n_clicks')],
    [State('input-app-name', 'value'),
     State('input-category', 'value'),
     State('input-rating', 'value'),
     State('input-installs', 'value'),
     State('input-size', 'value'),
     State('app-data-store', 'data')]
)
def add_new_app(n_clicks, app_name, category, rating, installs, size, current_data):
    if n_clicks == 0:
        return current_data, ""
    
    if not all([app_name, category, rating, installs, size]):
        return current_data, html.Div("❌ Harap isi semua field yang diperlukan", className="error-message")
    
    if not (1 <= rating <= 5):
        return current_data, html.Div("❌ Rating harus antara 1 dan 5", className="error-message")
    
    if installs < 0:
        return current_data, html.Div("❌ Jumlah install tidak boleh negatif", className="error-message")
    
    if size < 0:
        return current_data, html.Div("❌ Ukuran tidak boleh negatif", className="error-message")
    
    # Buat entri aplikasi baru
    new_app = {
        'fact_id': len(current_data) + 1,
        'app_name': app_name,
        'category': category,
        'genres': category,  # Disederhanakan
        'current_ver': '1.0',
        'price_value': 0,
        'price_type': 'Free',
        'content_rating': 'Everyone',
        'android_version': '5.0',
        'size_mb': size,
        'release_date': datetime.now().strftime('%Y-%m-%d'),
        'release_month': datetime.now().strftime('%B'),
        'release_year': datetime.now().year,
        'rating': rating,
        'total_reviews': max(1, installs // 10),  # Estimasi dengan minimum 1
        'total_installs': installs
    }
    
    updated_data = current_data + [new_app]
    success_msg = html.Div([
        html.I(className="fas fa-check-circle", style={'marginRight': '8px'}),
        f"Berhasil menambahkan '{app_name}' ke dataset"
    ], className="success-message")
    
    return updated_data, success_msg

@app.callback(
    Output('tab-content', 'children'),
    [Input('main-tabs', 'value'),
     Input('filtered-data-store', 'data')]
)
def render_tab_content(active_tab, filtered_data):
    if not filtered_data:
        return html.Div("Tidak ada data yang tersedia untuk filter yang dipilih", className="no-data-message")
    
    dff = pd.DataFrame(filtered_data)
    
    if active_tab == 'overview':
        return create_overview_content(dff)
    elif active_tab == 'success-factors':
        return create_success_factors_content(dff)
    elif active_tab == 'revenue-insights':
        return create_revenue_insights_content(dff)

def create_overview_content(dff):
    # Hitung target rating per kategori (rata-rata + 0.2 untuk menjadi kompetitif)
    category_targets = dff.groupby('category')['rating'].mean().add(0.2).reset_index()
    category_targets.columns = ['Kategori', 'Target Rating']
    
    # Visualisasi distribusi kategori
    category_dist = px.pie(
        dff, names='category', 
        title='<b>Distribusi Kategori Aplikasi</b><br><span style="font-size:14px">Persentase aplikasi per kategori</span>',
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.Teal
    )
    category_dist.update_traces(textposition='inside', textinfo='percent+label')
    category_dist.update_layout(template='plotly_white', height=500)
    
    # Visualisasi target rating
    target_fig = px.bar(
        category_targets.sort_values('Target Rating', ascending=False),
        x='Kategori',
        y='Target Rating',
        title='<b>Target Rating per Kategori</b><br><span style="font-size:14px">Rating yang harus dicapai untuk bersaing</span>',
        color='Target Rating',
        color_continuous_scale='Teal'
    )
    target_fig.update_layout(template='plotly_white', height=400, xaxis_tickangle=45)
    
    # Visualisasi distribusi rating
    rating_dist = px.histogram(
        dff, x='rating', nbins=20,
        title='<b>Distribusi Rating Aplikasi</b><br><span style="font-size:14px">Sebagian besar aplikasi memiliki rating 4.0-4.5</span>',
        color_discrete_sequence=['#01875f']
    )
    rating_dist.update_layout(template='plotly_white', height=400)
    
    return html.Div([
        html.Div([
            html.Div([
                dcc.Graph(figure=category_dist),
                html.P("Distribusi kategori membantu memahami persaingan pasar.", className="chart-description")
            ], className="chart-container"),
            
            html.Div([
                dcc.Graph(figure=target_fig),
                html.P("Target rating yang harus dicapai untuk bersaing di setiap kategori.", className="chart-description")
            ], className="chart-container"),
        ], className="row-charts"),
        
        html.Div([
            html.Div([
                dcc.Graph(figure=rating_dist),
                html.P("Distribusi rating menunjukkan standar kualitas di pasar.", className="chart-description")
            ], className="chart-container"),
        ], className="row-charts")
    ])

def create_success_factors_content(dff):
    # Hitung skor kesuksesan (kombinasi rating dan installs)
    dff['skor_kesuksesan'] = (dff['rating'] * 0.6) + (np.log10(dff['total_installs']) * 0.4)
    
    # Visualisasi faktor kesuksesan
    success_fig = px.scatter(
        dff,
        x='rating',
        y='total_installs',
        color='skor_kesuksesan',
        size='total_reviews',
        log_y=True,
        title='<b>Faktor Kesuksesan Aplikasi</b><br><span style="font-size:14px">Aplikasi sukses memiliki rating tinggi dan banyak install</span>',
        hover_data=['app_name', 'category'],
        labels={'rating': 'Rating', 'total_installs': 'Total Install (log)'}
    )
    success_fig.update_layout(template='plotly_white', height=600)
    
    # 10 aplikasi teratas
    top_apps = dff.nlargest(10, 'skor_kesuksesan')[['app_name', 'category', 'rating', 'total_installs']]
    top_apps['Installs'] = top_apps['total_installs'].apply(lambda x: f"{x/1e6:.1f} Juta" if x >= 1e6 else f"{x/1e3:.0f} Ribu")
    
    return html.Div([
        html.Div([
            html.Div([
                dcc.Graph(figure=success_fig),
                html.P("Analisis hubungan antara rating, jumlah install, dan ulasan.", className="chart-description")
            ], className="chart-container"),
        ], className="row-charts"),
        
        html.Div([
            html.H4("10 Aplikasi Paling Sukses", className="table-title"),
            dash_table.DataTable(
                data=top_apps.to_dict('records'),
                columns=[
                    {"name": "Nama Aplikasi", "id": "app_name"},
                    {"name": "Kategori", "id": "category"},
                    {"name": "Rating", "id": "rating"},
                    {"name": "Installs", "id": "Installs"}
                ],
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'left', 'padding': '10px'},
                style_header={
                    'backgroundColor': '#01875f',
                    'color': 'white',
                    'fontWeight': 'bold'
                }
            ),
            html.P("Pelajari aplikasi top untuk memahami pola kesuksesan.", className="chart-description")
        ], className="table-container")
    ])

def create_revenue_insights_content(dff):
    # Fokus pada aplikasi berbayar
    paid_apps = dff[dff['price_type'] == 'Paid']
    
    if len(paid_apps) == 0:
        return html.Div([
            html.Div("Tidak ada aplikasi berbayar dalam data yang difilter", className="no-data-message"),
            html.Div([
                dcc.Graph(figure=px.histogram(dff, x='price_type', title='Distribusi Tipe Harga')),
                html.P("Sebagian besar aplikasi gratis - pertimbangkan model pendapatan lain.", className="chart-description")
            ], className="chart-container")
        ])
    
    # Analisis sensitivitas harga
    price_fig = px.scatter(
        paid_apps,
        x='price_value',
        y='total_installs',
        color='rating',
        log_y=True,
        title='<b>Sensitivitas Harga</b><br><span style="font-size:14px">Aplikasi dengan harga lebih tinggi perlu rating lebih baik</span>',
        labels={'price_value': 'Harga ($)', 'total_installs': 'Install (log)'}
    )
    price_fig.update_layout(template='plotly_white', height=500)
    
    # Perbandingan performa gratis vs berbayar
    comparison = dff.groupby('price_type').agg({
        'rating': 'mean',
        'total_installs': 'median',
        'total_reviews': 'median'
    }).reset_index()
    
    comp_fig = make_subplots(rows=1, cols=3, subplot_titles=('Rating Rata-rata', 'Median Install', 'Median Ulasan'))
    
    metrics = ['rating', 'total_installs', 'total_reviews']
    for i, metric in enumerate(metrics):
        comp_fig.add_trace(
            go.Bar(
                x=comparison['price_type'],
                y=comparison[metric],
                name=metric.replace('_', ' ').title(),
                marker_color=['#01875f', '#764ba2']
            ),
            row=1, col=i+1
        )
    
    comp_fig.update_layout(
        title='<b>Perbandingan Aplikasi Gratis vs Berbayar</b>',
        template='plotly_white',
        height=400,
        showlegend=False
    )
    
    return html.Div([
        html.Div([
            html.Div([
                dcc.Graph(figure=price_fig),
                html.P("Hubungan antara harga aplikasi dan jumlah install.", className="chart-description")
            ], className="chart-container"),
        ], className="row-charts"),
        
        html.Div([
            html.Div([
                dcc.Graph(figure=comp_fig),
                html.P("Perbedaan performa antara aplikasi gratis dan berbayar.", className="chart-description")
            ], className="chart-container"),
        ], className="row-charts")
    ])

# ===============================
# STYLING CSS
# ===============================

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            /* Global Styles */
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            :root {
                --primary-color: #01875f;
                --secondary-color: #00b894;
                --accent-color: #4285f4;
                --warning-color: #ffa500;
                --danger-color: #ea4335;
                --success-color: #34c759;
                --light-bg: #f8f9fa;
                --white: #ffffff;
                --gray-100: #f1f3f4;
                --gray-200: #e8eaed;
                --gray-300: #dadce0;
                --gray-400: #9aa0a6;
                --gray-500: #5f6368;
                --gray-700: #3c4043;
                --gray-900: #202124;
                --shadow-sm: 0 2px 4px rgba(0,0,0,0.05);
                --shadow-md: 0 4px 12px rgba(0,0,0,0.1);
                --shadow-lg: 0 8px 25px rgba(0,0,0,0.15);
                --shadow-xl: 0 12px 35px rgba(0,0,0,0.2);
                --radius-sm: 8px;
                --radius-md: 12px;
                --radius-lg: 16px;
                --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            }

            body {
                font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
                background: var(--light-bg);
                min-height: 100vh;
                line-height: 1.6;
                color: var(--gray-700);
                overflow-x: hidden;
            }

            .dashboard-container {
                min-height: 100vh;
                background: linear-gradient(135deg, var(--light-bg) 0%, #e8f4f8 100%);
                position: relative;
            }

            .dashboard-container::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 300px;
                background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 50%, var(--accent-color) 100%);
                z-index: -1;
                clip-path: polygon(0 0, 100% 0, 100% 70%, 0 100%);
            }

            /* Header Styles with Enhanced Design */
            .main-header {
                background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 50%, var(--accent-color) 100%);
                color: white;
                padding: 3rem 2rem;
                position: relative;
                overflow: hidden;
            }

            .main-header::before {
                content: '';
                position: absolute;
                top: -50%;
                left: -50%;
                width: 200%;
                height: 200%;
                background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
                animation: shimmer 8s ease-in-out infinite;
            }

            @keyframes shimmer {
                0%, 100% { transform: rotate(0deg) translate(-50%, -50%); }
                50% { transform: rotate(180deg) translate(-50%, -50%); }
            }

            .header-content {
                position: relative;
                z-index: 2;
                max-width: 1200px;
                margin: 0 auto;
            }

            .header-title {
                font-size: clamp(2rem, 4vw, 3rem);
                font-weight: 800;
                margin-bottom: 0.5rem;
                text-shadow: 0 2px 10px rgba(0,0,0,0.2);
                letter-spacing: -0.02em;
            }

            .header-title i {
                animation: pulse 2s ease-in-out infinite;
            }

            @keyframes pulse {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.05); }
            }

            .header-subtitle {
                font-size: 1.25rem;
                opacity: 0.9;
                font-weight: 400;
            }

            /* Enhanced Metrics Cards */
            .metrics-container {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 1.5rem;
                margin-top: 2.5rem;
                position: relative;
                z-index: 2;
            }

            .metric-card {
                background: rgba(255,255,255,0.95);
                backdrop-filter: blur(20px);
                border: 1px solid rgba(255,255,255,0.3);
                border-radius: var(--radius-lg);
                padding: 2rem;
                display: flex;
                align-items: center;
                gap: 1.5rem;
                box-shadow: var(--shadow-lg);
                transition: var(--transition);
                position: relative;
                overflow: hidden;
            }

            .metric-card::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 4px;
                background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
            }

            .metric-card:hover {
                transform: translateY(-5px) scale(1.02);
                box-shadow: var(--shadow-xl);
                background: rgba(255,255,255,1);
            }

            .metric-icon {
                display: flex;
                align-items: center;
                justify-content: center;
                width: 60px;
                height: 60px;
                background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                border-radius: 50%;
                color: white;
                transition: var(--transition);
            }

            .metric-card:hover .metric-icon {
                transform: rotate(5deg) scale(1.1);
            }

            .metric-content {
                flex: 1;
            }

            .metric-number {
                font-size: 2.5rem;
                font-weight: 800;
                margin-bottom: 0.25rem;
                color: var(--gray-900);
                background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }

            .metric-label {
                font-size: 1rem;
                color: var(--gray-500);
                font-weight: 500;
            }

            /* Dashboard Body Layout */
            .dashboard-body {
                display: flex;
                min-height: calc(100vh - 200px);
                max-width: 1600px;
                margin: 0 auto;
                gap: 2rem;
                padding: 2rem;
            }

            /* Enhanced Sidebar */
            .sidebar {
                width: 380px;
                background: var(--white);
                border-radius: var(--radius-lg);
                box-shadow: var(--shadow-md);
                padding: 2rem;
                height: fit-content;
                position: sticky;
                top: 2rem;
                transition: var(--transition);
            }

            .sidebar:hover {
                box-shadow: var(--shadow-lg);
            }

            /* Filter Section */
            .filters-section {
                margin-bottom: 2rem;
            }

            .section-title {
                color: var(--gray-900);
                margin-bottom: 1.5rem;
                font-size: 1.4rem;
                font-weight: 700;
                position: relative;
                padding-left: 1rem;
            }

            .section-title::before {
                content: '';
                position: absolute;
                left: 0;
                top: 50%;
                transform: translateY(-50%);
                width: 4px;
                height: 20px;
                background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                border-radius: 2px;
            }

            .filters-grid {
                display: flex;
                flex-direction: column;
                gap: 1.5rem;
            }

            .filter-item {
                background: var(--gray-100);
                padding: 1.5rem;
                border-radius: var(--radius-md);
                transition: var(--transition);
            }

            .filter-item:hover {
                background: var(--gray-200);
                transform: translateX(5px);
            }

            .filter-label {
                display: block;
                margin-bottom: 0.75rem;
                font-weight: 600;
                color: var(--gray-700);
            }

            /* Custom Dropdown Styles */
            .custom-dropdown .Select-control {
                border: 2px solid var(--gray-300);
                border-radius: var(--radius-sm);
                min-height: 45px;
                transition: var(--transition);
            }

            .custom-dropdown .Select-control:hover {
                border-color: var(--primary-color);
            }

            .custom-dropdown .Select-control.is-focused {
                border-color: var(--primary-color);
                box-shadow: 0 0 0 3px rgba(1, 135, 95, 0.1);
            }

            /* Radio Items */
            .custom-radio {
                display: flex;
                flex-direction: column;
                gap: 0.75rem;
            }

            .custom-radio label {
                display: flex;
                align-items: center;
                gap: 0.75rem;
                cursor: pointer;
                padding: 0.75rem;
                border-radius: var(--radius-sm);
                transition: var(--transition);
            }

            .custom-radio label:hover {
                background: rgba(1, 135, 95, 0.05);
            }

            /* Range Slider */
            .custom-slider .rc-slider-track {
                background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
                height: 6px;
            }

            .custom-slider .rc-slider-handle {
                border: 3px solid var(--primary-color);
                width: 20px;
                height: 20px;
                background: var(--white);
                box-shadow: var(--shadow-md);
            }

            /* Input Section */
            .input-section {
                background: linear-gradient(135deg, rgba(1, 135, 95, 0.05) 0%, rgba(66, 133, 244, 0.05) 100%);
                border-radius: var(--radius-md);
                padding: 1.5rem;
                border: 1px solid rgba(1, 135, 95, 0.1);
            }

            .input-container {
                display: flex;
                flex-direction: column;
                gap: 1rem;
            }

            .input-group {
                display: flex;
                flex-direction: column;
                gap: 0.5rem;
            }

            .input-label {
                font-weight: 600;
                color: var(--gray-700);
            }

            .data-input {
                padding: 0.75rem;
                border: 2px solid var(--gray-300);
                border-radius: var(--radius-sm);
                font-size: 1rem;
                transition: var(--transition);
            }

            .data-input:focus {
                outline: none;
                border-color: var(--primary-color);
                box-shadow: 0 0 0 3px rgba(1, 135, 95, 0.1);
            }

            .add-btn {
                background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                color: white;
                border: none;
                padding: 1rem 2rem;
                border-radius: var(--radius-sm);
                font-size: 1rem;
                font-weight: 600;
                cursor: pointer;
                transition: var(--transition);
                box-shadow: var(--shadow-md);
            }

            .add-btn:hover {
                transform: translateY(-2px);
                box-shadow: var(--shadow-lg);
            }

            .add-btn:active {
                transform: translateY(0);
            }

            /* Main Content Area */
            .main-content {
                flex: 1;
                background: var(--white);
                border-radius: var(--radius-lg);
                box-shadow: var(--shadow-md);
                overflow: hidden;
                display: flex;
                flex-direction: column;
            }

            /* Enhanced Tabs */
            .custom-tabs {
                background: var(--white);
                border-bottom: 1px solid var(--gray-200);
                padding: 0;
            }

            .custom-tabs .tab-content {
                border: none;
            }

            .custom-tab {
                padding: 1rem 2rem !important;
                font-weight: 600 !important;
                color: var(--gray-500) !important;
                border-bottom: 3px solid transparent !important;
                transition: var(--transition) !important;
                background: none !important;
            }

            .custom-tab:hover {
                color: var(--primary-color) !important;
                background: rgba(1, 135, 95, 0.05) !important;
            }

            .custom-tab--selected {
                color: var(--primary-color) !important;
                border-bottom-color: var(--primary-color) !important;
                background: rgba(1, 135, 95, 0.05) !important;
            }

            /* Tab Content */
            .tab-content {
                padding: 2rem;
                flex: 1;
                overflow-y: auto;
            }

            /* Chart Containers */
            .row-charts {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
                gap: 2rem;
                margin-bottom: 2rem;
            }

            .chart-container {
                background: var(--white);
                border-radius: var(--radius-lg);
                box-shadow: var(--shadow-md);
                padding: 2rem;
                transition: var(--transition);
                border: 1px solid var(--gray-200);
            }

            .chart-container:hover {
                box-shadow: var(--shadow-lg);
                transform: translateY(-2px);
            }

            .chart-description {
                color: var(--gray-500);
                font-size: 0.95rem;
                margin-top: 1rem;
                padding: 1rem;
                background: var(--gray-100);
                border-radius: var(--radius-sm);
                border-left: 4px solid var(--primary-color);
            }

            /* Table Styles */
            .table-container {
                background: var(--white);
                border-radius: var(--radius-lg);
                box-shadow: var(--shadow-md);
                padding: 2rem;
                margin: 2rem 0;
                border: 1px solid var(--gray-200);
            }

            .table-title {
                color: var(--gray-900);
                margin-bottom: 1.5rem;
                font-size: 1.3rem;
                font-weight: 700;
            }

            /* Data Table Styles */
            .dash-table-container {
                border-radius: var(--radius-md);
                overflow: hidden;
                box-shadow: var(--shadow-sm);
            }

            .dash-table-container table {
                width: 100%;
            }

            .dash-table-container .cell {
                padding: 1rem !important;
                border-bottom: 1px solid var(--gray-200) !important;
            }

            .dash-table-container .header {
                background: linear-gradient(135deg, var(--primary-color), var(--secondary-color)) !important;
                color: white !important;
                font-weight: 600 !important;
                text-transform: uppercase !important;
                font-size: 0.85rem !important;
                letter-spacing: 0.5px !important;
            }

            /* Feedback Messages */
            .success-message {
                background: linear-gradient(135deg, var(--success-color), #40e0d0);
                color: white;
                padding: 1rem;
                border-radius: var(--radius-sm);
                margin-top: 1rem;
                display: flex;
                align-items: center;
                font-weight: 500;
                box-shadow: var(--shadow-md);
            }

            .error-message {
                background: linear-gradient(135deg, var(--danger-color), #ff6b6b);
                color: white;
                padding: 1rem;
                border-radius: var(--radius-sm);
                margin-top: 1rem;
                display: flex;
                align-items: center;
                font-weight: 500;
                box-shadow: var(--shadow-md);
            }

            .no-data-message {
                text-align: center;
                padding: 3rem;
                color: var(--gray-500);
                font-size: 1.1rem;
                background: var(--gray-100);
                border-radius: var(--radius-lg);
                margin: 2rem;
            }

            /* Loading States */
            .loading-spinner {
                display: inline-block;
                width: 20px;
                height: 20px;
                border: 3px solid rgba(1, 135, 95, 0.3);
                border-radius: 50%;
                border-top-color: var(--primary-color);
                animation: spin 1s ease-in-out infinite;
            }

            @keyframes spin {
                to { transform: rotate(360deg); }
            }

            /* Responsive Design */
            @media (max-width: 1400px) {
                .row-charts {
                    grid-template-columns: 1fr;
                }
            }

            @media (max-width: 1200px) {
                .dashboard-body {
                    flex-direction: column;
                    gap: 1rem;
                }
                
                .sidebar {
                    width: 100%;
                    position: static;
                }
                
                .metrics-container {
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                }
            }

            @media (max-width: 768px) {
                .dashboard-body {
                    padding: 1rem;
                }
                
                .main-header {
                    padding: 2rem 1rem;
                }
                
                .header-title {
                    font-size: 1.8rem;
                }
                
                .metrics-container {
                    grid-template-columns: 1fr;
                    gap: 1rem;
                }
                
                .metric-card {
                    padding: 1.5rem;
                }
                
                .sidebar {
                    padding: 1.5rem;
                }
                
                .tab-content {
                    padding: 1rem;
                }
                
                .chart-container {
                    padding: 1.5rem;
                }
            }

            @media (max-width: 480px) {
                .metric-card {
                    flex-direction: column;
                    text-align: center;
                    gap: 1rem;
                }
                
                .metric-number {
                    font-size: 2rem;
                }
                
                .header-title i {
                    display: block;
                    margin-bottom: 0.5rem;
                }
            }

            /* Custom Scrollbar */
            ::-webkit-scrollbar {
                width: 8px;
            }

            ::-webkit-scrollbar-track {
                background: var(--gray-100);
                border-radius: 4px;
            }

            ::-webkit-scrollbar-thumb {
                background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                border-radius: 4px;
            }

            ::-webkit-scrollbar-thumb:hover {
                opacity: 0.8;
            }

            /* Focus States for Accessibility */
            button:focus,
            input:focus,
            select:focus {
                outline: 2px solid var(--primary-color);
                outline-offset: 2px;
            }

            /* Print Styles */
            @media print {
                .sidebar {
                    display: none;
                }
                
                .main-content {
                    width: 100%;
                }
                
                .chart-container {
                    break-inside: avoid;
                    box-shadow: none;
                    border: 1px solid var(--gray-300);
                }
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# ===============================
# JALANKAN APLIKASI
# ===============================

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8050)