import pandas as pd
import numpy as np
from datetime import datetime
import mysql.connector
from sqlalchemy import create_engine
import os
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import html, dcc, dash_table

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

def create_header(df):
    return html.Div([
        html.Div([
            html.H1([
                html.I(className="fab fa-google-play", style={'marginRight': '15px', 'color': '#01875f'}),
                "Dashboard Analisis Google Play Store"
            ], className="header-title"),
            html.P("Insight untuk Pengembang Aplikasi", className="header-subtitle"),
        ], className="header-content"),
        
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

def create_filters(df):
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

def create_data_input(df):
    """Form Analisis Aplikasi dengan Visualisasi di Main Content"""
    return html.Div([
        html.H3("➕ Analisis Aplikasi Baru", className="section-title"),
        html.Div([
            # Form Input
            html.Div([
                html.Div([
                    html.Label("Nama Aplikasi:", className="input-label"),
                    dcc.Input(id='input-app-name', placeholder='Contoh: Aplikasi Toko Online', className="data-input"),
                ], className="input-group"),
                
                html.Div([
                    html.Label("Kategori:", className="input-label"),
                    dcc.Dropdown(
                        id='input-category',
                        options=[{'label': cat, 'value': cat} for cat in sorted(df['category'].unique())] if not df.empty else [],
                        placeholder='Pilih kategori...',
                        className="data-input"
                    ),
                ], className="input-group"),
                
                html.Div([
                    html.Label("Rating (1-5):", className="input-label"),
                    dcc.Input(
                        id='input-rating',
                        placeholder='4.2',
                        type='number',
                        min=1,
                        max=5,
                        step=0.1,
                        className="data-input"
                    ),
                ], className="input-group"),
                
                html.Div([
                    html.Label("Jumlah Install:", className="input-label"),
                    dcc.Input(
                        id='input-installs',
                        placeholder='1000000',
                        type='number',
                        className="data-input"
                    ),
                ], className="input-group"),
                
                html.Div([
                    html.Label("Ukuran (MB):", className="input-label"),
                    dcc.Input(
                        id='input-size',
                        placeholder='15.5',
                        type='number',
                        step=0.1,
                        className="data-input"
                    ),
                ], className="input-group"),
                
                html.Button(
                    'Analisis Sekarang',
                    id='add-app-btn',
                    className="add-btn",
                    n_clicks=0
                ),
                
                html.Div(id='add-app-output', className="input-feedback"),
            ], className="input-container"),
            
            # Area Visualisasi - Disederhanakan tanpa tabs
            html.Div(id='app-analysis-results', style={'marginTop': '30px'})
        ], className="main-container")
    ], className="input-section")
def create_rating_comparison(new_app, existing_data):
    df = pd.DataFrame(existing_data) if existing_data else pd.DataFrame()
    
    # Hitung rata-rata
    category_avg = df[df['category'] == new_app['category']]['rating'].mean() if not df.empty else 0
    overall_avg = df['rating'].mean() if not df.empty else 0
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=['Aplikasi Baru', 'Rata-rata Kategori', 'Rata-rata Global'],
        y=[new_app['rating'], category_avg, overall_avg],
        marker_color=['#01875f', '#4285f4', '#ea4335'],
        text=[f"{y:.2f}" for y in [new_app['rating'], category_avg, overall_avg]],
        textposition='auto'
    ))
    
    fig.update_layout(
        title='<b>Perbandingan Rating</b>',
        yaxis_title='Rating',
        yaxis_range=[0, 5.2],
        template='plotly_white',
        height=400
    )
    
    return fig


def filter_data(categories, price_type, rating_range, stored_data):
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

def predict_app_success(new_app_data, existing_data):
    """
    Memprediksi kesuksesan aplikasi baru berdasarkan data yang ada
    Mengembalikan skor kesuksesan (0-100) dan rekomendasi
    """
    if not existing_data:
        return 50, "Tidak ada data referensi yang cukup"
    
    df = pd.DataFrame(existing_data)
    
    # Hitung parameter referensi dari data yang ada
    avg_rating = df['rating'].mean()
    median_installs = df['total_installs'].median()
    category_stats = df.groupby('category').agg({
        'rating': ['mean', 'std'],
        'total_installs': ['median', 'std']
    }).reset_index()
    
    # Dapatkan statistik kategori aplikasi baru
    app_category = new_app_data['category']
    category_mask = df['category'] == app_category
    category_data = df[category_mask]
    
    if len(category_data) == 0:
        # Jika kategori tidak ditemukan, gunakan rata-rata keseluruhan
        cat_avg_rating = avg_rating
        cat_median_installs = median_installs
    else:
        cat_avg_rating = category_data['rating'].mean()
        cat_median_installs = category_data['total_installs'].median()
    
    # Hitung skor kesuksesan (0-100)
    rating_score = min(100, (new_app_data['rating'] / cat_avg_rating) * 50)
    install_score = min(50, (np.log10(new_app_data['total_installs'] + 1) / 
                      np.log10(cat_median_installs + 1) * 50))
    success_score = rating_score + install_score
    
    # Hasilkan rekomendasi
    recommendations = []
    
    # Analisis rating
    if new_app_data['rating'] < cat_avg_rating:
        recommendations.append(
            f"Rating aplikasi ({new_app_data['rating']:.1f}) di bawah rata-rata kategori ({cat_avg_rating:.1f}). "
            "Pertimbangkan untuk meningkatkan kualitas aplikasi."
        )
    else:
        recommendations.append(
            f"Rating aplikasi ({new_app_data['rating']:.1f}) di atas rata-rata kategori ({cat_avg_rating:.1f}). "
            "Ini adalah indikator positif untuk kesuksesan."
        )
    
    # Analisis installs
    if new_app_data['total_installs'] < cat_median_installs:
        recommendations.append(
            f"Perkiraan install ({new_app_data['total_installs']:,}) di bawah median kategori ({cat_median_installs:,}). "
            "Pertimbangkan strategi pemasaran yang lebih agresif."
        )
    else:
        recommendations.append(
            f"Perkiraan install ({new_app_data['total_installs']:,}) di atas median kategori ({cat_median_installs:,}). "
            "Ini menunjukkan potensi kesuksesan yang baik."
        )
    
    # Analisis ukuran
    size_stats = df.groupby('category')['size_mb'].median().reset_index()
    median_size = size_stats[size_stats['category'] == app_category]['size_mb'].values[0] if not size_stats[size_stats['category'] == app_category].empty else df['size_mb'].median()
    
    if new_app_data['size_mb'] > median_size * 1.5:
        recommendations.append(
            f"Ukuran aplikasi ({new_app_data['size_mb']}MB) lebih besar dari median kategori ({median_size:.1f}MB). "
            "Ukuran yang lebih kecil biasanya lebih disukai pengguna."
        )
    
    return min(100, max(0, success_score)), recommendations

def handle_add_app(n_clicks, app_name, category, rating, installs, size, current_data):
    if n_clicks == 0:
        return current_data, "", None
    
    if not all([app_name, category, rating, installs, size]):
        return current_data, html.Div("❌ Harap isi semua field yang diperlukan", className="error-message"), None
    
    if not (1 <= rating <= 5):
        return current_data, html.Div("❌ Rating harus antara 1 dan 5", className="error-message"), None
    
    if installs < 0:
        return current_data, html.Div("❌ Jumlah install tidak boleh negatif", className="error-message"), None
    
    if size < 0:
        return current_data, html.Div("❌ Ukuran tidak boleh negatif", className="error-message"), None
    
    # Buat entri aplikasi baru
    new_app = {
        'fact_id': len(current_data) + 1,
        'app_name': app_name,
        'category': category,
        'genres': category,
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
        'total_reviews': max(1, installs // 10),
        'total_installs': installs
    }
    
    # Prediksi kesuksesan
    success_score, recommendations = predict_app_success(new_app, current_data)
    
    # Buat visualisasi hasil analisis
    analysis_result = html.Div([
        html.H4(f"Analisis Potensi Kesuksesan: {app_name}", className="analysis-title"),
        html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        html.Div(style={
                            'width': f'{success_score}%',
                            'height': '100%',
                            'backgroundColor': '#01875f',
                            'borderRadius': '20px'
                        })
                    ], style={
                        'width': '100%',
                        'height': '30px',
                        'backgroundColor': '#f0f0f0',
                        'borderRadius': '20px',
                        'overflow': 'hidden',
                        'marginBottom': '10px'
                    }),
                    html.Div(f"Skor Kesuksesan: {success_score:.1f}/100", className="score-text"),
                    html.Div([
                        "0-40: Risiko Tinggi",
                        html.Br(),
                        "40-70: Potensi Sedang", 
                        html.Br(),
                        "70-100: Potensi Tinggi"
                    ], className="score-legend")
                ], className="score-container"),
                
                html.Div([
                    html.H5("Rekomendasi:", className="recommendation-title"),
                    html.Ul([html.Li(rec) for rec in recommendations], className="recommendation-list")
                ], className="recommendation-container")
            ], className="analysis-content"),
            
            html.Div([
                html.H5("Detail Aplikasi:", className="detail-title"),
                html.Table([
                    html.Tr([html.Td("Nama Aplikasi:"), html.Td(app_name)]),
                    html.Tr([html.Td("Kategori:"), html.Td(category)]),
                    html.Tr([html.Td("Rating:"), html.Td(f"{rating:.1f}")]),
                    html.Tr([html.Td("Perkiraan Install:"), html.Td(f"{installs:,}")]),
                    html.Tr([html.Td("Ukuran:"), html.Td(f"{size} MB")])
                ], className="detail-table")
            ], className="detail-container")
        ], className="analysis-grid")
    ], className="analysis-section")
    
    updated_data = current_data + [new_app]
    success_msg = html.Div([
        html.I(className="fas fa-check-circle", style={'marginRight': '8px'}),
        f"Berhasil menambahkan '{app_name}' ke dataset"
    ], className="success-message")
    
    return updated_data, success_msg, analysis_result

# [Previous imports remain the same...]

# ==================================================================
# NEW VISUALIZATION FUNCTIONS (ADDED TO EXISTING FILE)
# ==================================================================

def create_installs_comparison(new_app, existing_data):
    """
    Membuat bar chart perbandingan install (skala logaritmik)
    """
    df = pd.DataFrame(existing_data) if existing_data else pd.DataFrame()
    
    # Hitung statistik
    category_mask = (df['category'] == new_app['category']) if not df.empty else []
    category_median = df.loc[category_mask, 'total_installs'].median() if not df.empty and any(category_mask) else 0
    overall_median = df['total_installs'].median() if not df.empty else 0
    
    # Format teks
    def format_installs(num):
        if num >= 1e6:
            return f"{num/1e6:.1f}M"
        elif num >= 1e3:
            return f"{num/1e3:.0f}K"
        return str(num)
    
    # Buat figure
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=['Aplikasi Baru', 'Median Kategori', 'Median Global'],
        y=[new_app['total_installs'], category_median, overall_median],
        marker_color=['#01875f', '#4285f4', '#ea4335'],
        text=[format_installs(y) for y in [new_app['total_installs'], category_median, overall_median]],
        textposition='outside'
    ))
    
    fig.update_layout(
        title={
            'text': "<b>Perbandingan Jumlah Install</b>",
            'y':0.9,
            'x':0.5,
            'xanchor': 'center'
        },
        yaxis_title='Jumlah Install',
        yaxis_type='log',
        plot_bgcolor='rgba(0,0,0,0)',
        height=400,
        margin={'t': 60, 'b': 40, 'l': 60, 'r': 20}
    )
    
    return fig

def create_radar_analysis(new_app, existing_data):
    """
    Membuat radar chart untuk analisis 4 faktor utama
    """
    df = pd.DataFrame(existing_data) if existing_data else pd.DataFrame()
    category_mask = (df['category'] == new_app['category']) if not df.empty else []
    
    # Normalisasi data (0-1)
    max_installs = df['total_installs'].max() if not df.empty else 1
    max_size = df['size_mb'].max() if not df.empty else 1
    
    # Hitung metrik
    metrics = {
        'Rating': (
            new_app['rating'] / 5,
            df.loc[category_mask, 'rating'].mean() / 5 if any(category_mask) else 0
        ),
        'Installs': (
            min(1, new_app['total_installs'] / max_installs),
            min(1, df.loc[category_mask, 'total_installs'].median() / max_installs) if any(category_mask) else 0
        ),
        'Ukuran': (
            1 - (new_app['size_mb'] / max_size),
            1 - (df.loc[category_mask, 'size_mb'].median() / max_size) if any(category_mask) else 0
        ),
        'Kepuasan': (
            (new_app['rating'] / 5) * 0.7 + (min(1, new_app['total_installs'] / max_installs) * 0.3),
            (df.loc[category_mask, 'rating'].mean() / 5 * 0.7 + 
             min(1, df.loc[category_mask, 'total_installs'].median() / max_installs) * 0.3) if any(category_mask) else 0
        )
    }
    
    # Buat figure
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=[val[0] for val in metrics.values()],
        theta=list(metrics.keys()),
        fill='toself',
        name='Aplikasi Baru',
        line={'color': '#01875f', 'width': 2},
        opacity=0.8
    ))
    
    fig.add_trace(go.Scatterpolar(
        r=[val[1] for val in metrics.values()],
        theta=list(metrics.keys()),
        fill='toself',
        name='Rata-rata Kategori',
        line={'color': '#4285f4', 'width': 2},
        opacity=0.5
    ))
    
    fig.update_layout(
        polar={
            'radialaxis': {
                'visible': True,
                'range': [0, 1],
                'tickvals': [0, 0.5, 1],
                'ticktext': ['Rendah', 'Sedang', 'Tinggi']
            },
            'bgcolor': 'rgba(0,0,0,0)'
        },
        title={
            'text': "<b>Analisis Komprehensif</b><br><span style='font-size:12px'>Skala Normalisasi (0-1)</span>",
            'y': 0.95,
            'x': 0.5
        },
        legend={
            'orientation': 'h',
            'yanchor': 'bottom',
            'y': -0.2
        },
        height=500,
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def create_category_trend(new_app, existing_data):
    """
    Membuat line chart trend rating kategori per tahun
    """
    df = pd.DataFrame(existing_data) if existing_data else pd.DataFrame()
    
    if df.empty or 'release_year' not in df.columns:
        return go.Figure()
    
    # Hitung trend
    trend_data = df[df['category'] == new_app['category']]
    if trend_data.empty:
        return go.Figure()
    
    trend_data = trend_data.groupby('release_year')['rating'].agg(['mean', 'count']).reset_index()
    
    # Buat figure
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=trend_data['release_year'],
        y=trend_data['mean'],
        mode='lines+markers',
        name='Rating Rata-rata',
        line={'color': '#01875f', 'width': 3},
        marker={'size': 8},
        text=[
            f"Tahun: {year}<br>Rating: {rating:.2f}<br>Jumlah Aplikasi: {count}" 
            for year, rating, count in zip(
                trend_data['release_year'],
                trend_data['mean'],
                trend_data['count']
            )
        ],
        hoverinfo='text'
    ))
    
    fig.add_hline(
        y=df['rating'].mean(),
        line={'dash': 'dash', 'color': '#ea4335', 'width': 2},
        annotation_text="Rata-rata Global",
        annotation_position="bottom right"
    )
    
    fig.update_layout(
        title={
            'text': f"<b>Trend Rating Kategori {new_app['category']}</b>",
            'y':0.9,
            'x':0.5
        },
        xaxis_title='Tahun',
        yaxis_title='Rating Rata-rata',
        yaxis_range=[0, 5.2],
        plot_bgcolor='rgba(0,0,0,0)',
        height=400,
        hovermode='x unified'
    )
    
    return fig

def create_comparison_table(new_app, existing_data):
    """
    Membuat tabel perbandingan metrik utama
    """
    df = pd.DataFrame(existing_data) if existing_data else pd.DataFrame()
    category_mask = (df['category'] == new_app['category']) if not df.empty else []
    
    # Hitung statistik
    is_category_exist = any(category_mask) if not df.empty else False
    
    category_stats = {
        'rating_mean': df.loc[category_mask, 'rating'].mean() if is_category_exist else '-',
        'installs_median': df.loc[category_mask, 'total_installs'].median() if is_category_exist else '-',
        'size_median': df.loc[category_mask, 'size_mb'].median() if is_category_exist else '-',
        'free_percentage': round(
            df.loc[category_mask, 'price_type'].value_counts(normalize=True).get('Free', 0) * 100
        ) if is_category_exist else '-'
    }
    
    # Format data
    comparison_data = [
        {
            'Metrik': 'Rating',
            'Aplikasi Baru': f"{new_app['rating']:.1f}",
            'Rata-rata Kategori': f"{category_stats['rating_mean']:.1f}" if isinstance(category_stats['rating_mean'], float) else '-',
            'Keterangan': get_rating_feedback(new_app['rating'], category_stats['rating_mean'])
        },
        {
            'Metrik': 'Jumlah Install',
            'Aplikasi Baru': f"{new_app['total_installs']:,}",
            'Rata-rata Kategori': f"{category_stats['installs_median']:,}" if isinstance(category_stats['installs_median'], (int, float)) else '-',
            'Keterangan': get_installs_feedback(new_app['total_installs'], category_stats['installs_median'])
        },
        {
            'Metrik': 'Ukuran (MB)',
            'Aplikasi Baru': f"{new_app['size_mb']:.1f}",
            'Rata-rata Kategori': f"{category_stats['size_median']:.1f}" if isinstance(category_stats['size_median'], float) else '-',
            'Keterangan': "✅ Ideal" if new_app['size_mb'] <= 15 else "⚠️ Terlalu besar"
        },
        {
            'Metrik': 'Model Harga',
            'Aplikasi Baru': 'Gratis',
            'Rata-rata Kategori': f"{category_stats['free_percentage']}% Gratis" if isinstance(category_stats['free_percentage'], int) else '-',
            'Keterangan': "✅ Dominan" if isinstance(category_stats['free_percentage'], int) and category_stats['free_percentage'] > 50 else "⚠️ Berbayar lebih umum"
        }
    ]
    
    # Buat tabel
    table = dash_table.DataTable(
        data=comparison_data,
        columns=[
            {"name": "Metrik", "id": "Metrik", "type": "text"},
            {"name": "Aplikasi Baru", "id": "Aplikasi Baru", "type": "text"},
            {"name": "Rata-rata Kategori", "id": "Rata-rata Kategori", "type": "text"},
            {"name": "Keterangan", "id": "Keterangan", "type": "text"}
        ],
        style_table={
            'overflowX': 'auto',
            'borderRadius': '8px',
            'boxShadow': '0 2px 5px rgba(0,0,0,0.1)'
        },
        style_cell={
            'textAlign': 'left',
            'padding': '12px',
            'minWidth': '100px',
            'backgroundColor': 'white'
        },
        style_header={
            'backgroundColor': '#01875f',
            'color': 'white',
            'fontWeight': 'bold',
            'border': 'none'
        },
        style_data_conditional=[
            {
                'if': {'column_id': 'Aplikasi Baru'},
                'fontWeight': 'bold',
                'borderLeft': '2px solid #01875f'
            },
            {
                'if': {'filter_query': '{Keterangan} contains "⚠️"'},
                'backgroundColor': 'rgba(234,67,53,0.1)'
            }
        ]
    )
    
    return table

def get_rating_feedback(app_rating, category_avg):
    if not isinstance(category_avg, float):
        return "Tidak ada data pembanding"
    
    diff = app_rating - category_avg
    if diff > 0.5:
        return "✅ Sangat kompetitif"
    elif diff > 0:
        return "👍 Lebih baik dari rata-rata"
    elif diff > -0.5:
        return "⚠️ Perlu peningkatan"
    else:
        return "❌ Jauh di bawah rata-rata"

def get_installs_feedback(app_installs, category_median):
    if not isinstance(category_median, (int, float)):
        return "Tidak ada data pembanding"
    
    ratio = app_installs / category_median if category_median > 0 else 1
    if ratio > 2:
        return "🚀 Potensi viral"
    elif ratio > 1:
        return "✅ Di atas rata-rata"
    elif ratio > 0.5:
        return "📈 Cukup kompetitif"
    else:
        return "⚠️ Perlu strategi marketing"

def _get_rating_feedback(app_rating, category_avg):
    if not isinstance(category_avg, float):
        return "Tidak ada data pembanding"
    
    diff = app_rating - category_avg
    if diff > 0.5:
        return "✅ Sangat kompetitif"
    elif diff > 0:
        return "👍 Lebih baik dari rata-rata"
    elif diff > -0.5:
        return "⚠️ Perlu peningkatan"
    else:
        return "❌ Jauh di bawah rata-rata"

def _get_installs_feedback(app_installs, category_median):
    if not isinstance(category_median, (int, float)):
        return "Tidak ada data pembanding"
    
    ratio = app_installs / category_median if category_median > 0 else 1
    if ratio > 2:
        return "🚀 Potensi viral"
    elif ratio > 1:
        return "✅ Di atas rata-rata"
    elif ratio > 0.5:
        return "📈 Cukup kompetitif"
    else:
        return "⚠️ Perlu strategi marketing"

# [Rest of your existing functions remain unchanged...]

def render_content(active_tab, filtered_data):
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
    try:
        # Pastikan dff adalah DataFrame
        if not isinstance(dff, pd.DataFrame):
            dff = pd.DataFrame(dff)
            
        # Validasi kolom yang diperlukan
        required_columns = ['rating', 'total_installs', 'total_reviews', 'app_name', 'category']
        for col in required_columns:
            if col not in dff.columns:
                raise ValueError(f"Kolom '{col}' tidak ditemukan dalam data")
        
        # Hitung skor kesuksesan (kombinasi rating dan installs)
        # Handle missing values jika ada
        dff['total_installs'] = pd.to_numeric(dff['total_installs'], errors='coerce').fillna(0)
        dff['rating'] = pd.to_numeric(dff['rating'], errors='coerce').fillna(0)
        dff['total_reviews'] = pd.to_numeric(dff['total_reviews'], errors='coerce').fillna(0)
        
        # Hitung skor dengan penanganan jika total_installs = 0
        dff['skor_kesuksesan'] = (dff['rating'] * 0.6) + (np.log10(dff['total_installs'].replace(0, 1)) * 0.4)
        
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
        top_apps = dff.nlargest(10, 'skor_kesuksesan')[['app_name', 'category', 'rating', 'total_installs']].copy()
        top_apps['Installs'] = top_apps['total_installs'].apply(
            lambda x: f"{x/1e6:.1f} Juta" if x >= 1e6 else f"{x/1e3:.0f} Ribu" if x >= 1e3 else f"{x:.0f}"
        )
        
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
        
    except Exception as e:
        return html.Div([
            html.I(className="fas fa-exclamation-triangle", style={'color': '#ea4335'}),
            f" Error dalam membuat konten faktor kesuksesan: {str(e)}"
        ], className="error-message")
    
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