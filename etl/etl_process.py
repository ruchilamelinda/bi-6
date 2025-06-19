import pandas as pd
import mysql.connector
from datetime import datetime
import os

def create_connection():
    """Create new MySQL database connection"""
    return mysql.connector.connect(
        host="localhost",
        user="root",              
        password="",  
        database="playstoredb",    
        port=3306                 
    )

def get_id_safe(conn, table, column, value):
    """Safely get ID with individual transaction - FIXED untuk sesuai database schema"""
    cur = conn.cursor()
    try:
        # FIXED: Sesuaikan dengan nama kolom ID di database Anda
        id_column_map = {
            'dim_app': 'app_id',
            'dim_price': 'price_id', 
            'dim_contentRating': 'contentRating_id',
            'dim_device': 'device_id',
            'dim_date': 'date_id'
        }
        id_column = id_column_map.get(table, 'id')
        
        cur.execute(f"SELECT {id_column} FROM {table} WHERE {column} = %s", (value,))
        result = cur.fetchone()
        return result[0] if result else None
    except Exception as e:
        conn.rollback()
        print(f"Error getting ID from {table} for value '{value}': {e}")
        return None
    finally:
        try:
            cur.fetchall()  # Tambahkan ini agar hasil SELECT dibersihkan
        except:
            pass
        cur.close()

def insert_dimension_safe(conn, table, columns, values):
    """Safely insert to dimension table"""
    cur = conn.cursor()
    try:
        placeholders = ', '.join(['%s'] * len(values))
        column_names = ', '.join(columns)
        query = f"INSERT IGNORE INTO {table} ({column_names}) VALUES ({placeholders})"
        cur.execute(query, values)
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error inserting to {table}: {e}")
        return False
    finally:
        cur.close()

# === MAIN ETL PROCESS ===
try:
    # === 1. EXTRACT dari CSV ===
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(BASE_DIR, "../data/app-playstore.csv")
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip() 

    print("Kolom yang tersedia:", df.columns.tolist())
    print(f"Total records sebelum cleaning: {len(df)}")

    # === 2. TRANSFORM & CLEAN DATA ===
    print("Starting data transformation and cleaning...")

    # HAPUS baris yang mengandung "Varies with device" di kolom Size
    print("Removing rows with 'Varies with device' in Size column...")
    initial_count = len(df)
    df = df[df['Size'] != 'Varies with device'].copy()
    df = df[df['Android Ver'] != 'Varies with device'].copy()
    print(f"Removed {initial_count - len(df)} rows with 'Varies with device'")

    # HAPUS baris yang mengandung "Unknown" di kolom Category atau Genres
    print("Removing rows with 'Unknown' values...")
    initial_count = len(df)
    df = df[df['Category'] != 'Unknown'].copy()
    df = df[df['Genres'] != 'Unknown'].copy()
    print(f"Removed {initial_count - len(df)} rows with 'Unknown' values")

    # HAPUS baris dengan nilai NaN di kolom penting
    print("Removing rows with critical missing values...")
    initial_count = len(df)
    df = df.dropna(subset=['App', 'Category', 'Genres']).copy()
    print(f"Removed {initial_count - len(df)} rows with critical missing values")

    df['App'] = df['App'].astype(str).str.encode('ascii', errors='ignore').str.decode('ascii')  # buang emoji/simbol aneh
    df['App'] = df['App'].str.replace(r'[^\w\s\-&]', '', regex=True)  # buang simbol aneh tapi tetap pertahankan huruf, angka, spasi, &, -
    df['App'] = df['App'].str.strip()  # buang spasi depan-belakang

    for col in ['Category', 'Genres', 'Content Rating']:
        df[col] = df[col].astype(str).str.strip()
        df[col] = df[col].str.title()  # konsisten kapitalisasi (misal 'Everyone' bukan 'everyone')


    # Clean kolom Size (sekarang tidak ada 'Varies with device')
    print("Cleaning Size column...")
    df['Size'] = df['Size'].astype(str).str.replace('M', '', regex=False).str.replace('k', '', regex=False).str.replace('+', '', regex=False)
    df['Size'] = pd.to_numeric(df['Size'], errors='coerce').fillna(0)
   

    # Clean kolom Price
    print("Cleaning Price column...")
    df['Price'] = df['Price'].astype(str).str.replace('$', '', regex=False)
    df['Price'] = pd.to_numeric(df['Price'], errors='coerce').fillna(0)

    # Buat kolom Type berdasarkan Price
    df['Type'] = df['Price'].apply(lambda x: 'Free' if x == 0 else 'Paid')

    # Clean kolom Installs
    print("Cleaning Installs column...")
    df['Installs'] = df['Installs'].astype(str).str.replace(',', '', regex=False).str.replace('+', '', regex=False)
    df['Installs'] = pd.to_numeric(df['Installs'], errors='coerce').fillna(0)

    # Clean Rating dan Reviews
    print("Cleaning Rating and Reviews...")
    df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce')
    mean_rating = df['Rating'].mean()
    df['Rating'] = df['Rating'].fillna(mean_rating)
    df['Reviews'] = pd.to_numeric(df['Reviews'], errors='coerce').fillna(0)

    # Fill missing values dengan nilai default yang masuk akal
    df['Content Rating'] = df['Content Rating'].fillna('Everyone')
    df['Current Ver'] = df['Current Ver'].fillna('1.0')
    df['Android Ver'] = df['Android Ver'].fillna('4.0 and up')
    df['Android Ver'] = df['Android Ver'].astype(str).str.strip()
    df['Android Ver'] = df['Android Ver'].str.replace('and up', '', regex=False).str.strip()  # buang "and up"

    # Process dates
    print("Processing date columns...")
    df['Released'] = pd.to_datetime(df['Released'], errors='coerce')
    default_date = pd.Timestamp('2018-01-01')
    df['release_date'] = df['Released'].fillna(default_date)
    df['release_month'] = df['release_date'].dt.strftime('%B')
    df['release_year'] = df['release_date'].dt.year

    string_cols = df.select_dtypes(include='object').columns
    for col in string_cols:
        if col == 'Content Rating':  # Skip Content Rating agar tanda + tidak dihilangkan
            continue
        df[col] = df[col].astype(str)
        df[col] = df[col].str.encode('ascii', errors='ignore').str.decode('ascii')
        df[col] = df[col].str.replace(r'[^\w\s.\-@&]', '', regex=True)
        df[col] = df[col].str.strip()

    print(f"Final record count after all cleaning: {len(df)}")
    print("Data transformation completed!")
    
    # Show sample of cleaned data
    print("\nSample cleaned data:")
    sample_cols = ['App', 'Category', 'Price', 'Type', 'Size', 'Rating', 'Android Ver']
    print(df[sample_cols].head())


    # === 3. CREATE DIMENSIONS ===
    print("\nCreating dimension dataframes...")
    dim_app = df.groupby('App', as_index=False).agg({
    'Category': 'first',
    'Genres': 'first',
    'Current Ver': 'first'
})
    dim_price = df[['Price', 'Type']].drop_duplicates().reset_index(drop=True)
    dim_content = df[['Content Rating']].drop_duplicates().reset_index(drop=True)
    dim_device = df[['Android Ver', 'Size']].drop_duplicates().reset_index(drop=True)
    dim_date = df[['release_date', 'release_month', 'release_year']].drop_duplicates().reset_index(drop=True)

    print(f"Dimension sizes:")
    print(f"- App: {len(dim_app)}")
    print(f"- Price: {len(dim_price)}")
    print(f"- Content: {len(dim_content)}")
    print(f"- Device: {len(dim_device)}")
    print(f"- Date: {len(dim_date)}")

    # === 4. LOAD DIMENSIONS ===
    print("\nLoading dimension tables...")
    conn = create_connection()

    # Load dim_app
    print("Loading dim_app...")
    app_success = 0
    for _, row in dim_app.iterrows():
        if insert_dimension_safe(conn, 'dim_app', 
                                ['app_name', 'category', 'genres', 'current_ver'],
                                [str(row['App']), str(row['Category']), str(row['Genres']), str(row['Current Ver'])]):
            app_success += 1
    print(f"dim_app: {app_success}/{len(dim_app)} inserted")

    # Load dim_price
    print("Loading dim_price...")
    price_success = 0
    for _, row in dim_price.iterrows():
        if insert_dimension_safe(conn, 'dim_price',
                                ['price_value', 'price_type'],
                                [float(row['Price']), str(row['Type'])]):
            price_success += 1
    print(f"dim_price: {price_success}/{len(dim_price)} inserted")

    # Load dim_contentRating
    print("Loading dim_contentRating...")
    content_success = 0
    for _, row in dim_content.iterrows():
        if insert_dimension_safe(conn, 'dim_contentRating',
                                ['content_rating'],
                                [str(row['Content Rating'])]):
            content_success += 1
    print(f"dim_contentRating: {content_success}/{len(dim_content)} inserted")

    # Load dim_device
    print("Loading dim_device...")
    device_success = 0
    for _, row in dim_device.iterrows():
        if insert_dimension_safe(conn, 'dim_device',
                                ['android_version', 'size_mb'],
                                [str(row['Android Ver']), float(row['Size'])]):
            device_success += 1
    print(f"dim_device: {device_success}/{len(dim_device)} inserted")

    # Load dim_date
    print("Loading dim_date...")
    date_success = 0
    for _, row in dim_date.iterrows():
        if insert_dimension_safe(conn, 'dim_date',
                                ['release_date', 'release_month', 'release_year'],
                                [row['release_date'], str(row['release_month']), int(row['release_year'])]):
            date_success += 1
    print(f"dim_date: {date_success}/{len(dim_date)} inserted")

    # === 5. LOAD FACT TABLE ===
    print("\nLoading fact table...")
    successful_loads = 0
    skipped_loads = 0

    # Process in smaller batches untuk performa yang lebih baik
    batch_size = 100
    total_batches = (len(df) + batch_size - 1) // batch_size

    for batch_num in range(total_batches):
        start_idx = batch_num * batch_size
        end_idx = min(start_idx + batch_size, len(df))
        batch_df = df.iloc[start_idx:end_idx]
        
        print(f"Processing batch {batch_num + 1}/{total_batches} (rows {start_idx+1}-{end_idx})")
        
        for _, row in batch_df.iterrows():
            try:
                # Get IDs for each dimension
                app_id = get_id_safe(conn, 'dim_app', 'app_name', str(row['App']))
                price_id = get_id_safe(conn, 'dim_price', 'price_value', float(row['Price']))
                content_id = get_id_safe(conn, 'dim_contentRating', 'content_rating', str(row['Content Rating']))
                device_id = get_id_safe(conn, 'dim_device', 'android_version', str(row['Android Ver']))
                date_id = get_id_safe(conn, 'dim_date', 'release_date', row['release_date'])

                # Check if all IDs are found
                if None in [app_id, price_id, content_id, device_id, date_id]:
                    missing_ids = []
                    if app_id is None: missing_ids.append("app")
                    if price_id is None: missing_ids.append("price") 
                    if content_id is None: missing_ids.append("content")
                    if device_id is None: missing_ids.append("device")
                    if date_id is None: missing_ids.append("date")
                    
                    print(f"Missing IDs for app '{row['App']}': {', '.join(missing_ids)}")
                    skipped_loads += 1
                    continue

                # Insert fact record
                cur = conn.cursor()
                try:
                    cur.execute("""
                        INSERT INTO fact_app_reviews (
                            app_id, device_id, date_id,
                            price_id, contentRating_id,
                            rating, total_reviews, total_installs
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        app_id, device_id, date_id,
                        price_id, content_id,
                        float(row['Rating']), int(row['Reviews']), int(row['Installs'])
                    ))
                    conn.commit()
                    successful_loads += 1
                except Exception as e:
                    conn.rollback()
                    print(f"Error inserting fact for app '{row['App']}': {e}")
                    skipped_loads += 1
                finally:
                    cur.close()
                    
            except Exception as e:
                print(f"Error processing app '{row['App']}': {e}")
                skipped_loads += 1

        # Progress update setiap 20 batch
        if (batch_num + 1) % 20 == 0:
            print(f"Progress: {batch_num + 1}/{total_batches} batches completed")


    conn.close()

    print(f"\n🎉 ETL Process Completed Successfully!")
    print(f"📊 Successfully loaded: {successful_loads} records")
    print(f"⚠️  Skipped records: {skipped_loads} records")
    if (successful_loads + skipped_loads) > 0:
        success_rate = successful_loads/(successful_loads+skipped_loads)*100
        print(f"📈 Success rate: {success_rate:.1f}%")
    else:
        print("📈 No records processed")
    
    print(f"\n📋 Data Summary:")
    print(f"- Original records: {len(pd.read_csv(csv_path))}")
    print(f"- After cleaning: {len(df)}")
    print(f"- Successfully loaded to fact table: {successful_loads}")

except Exception as e:
    print(f"❌ Fatal error during ETL process: {e}")
    import traceback
    traceback.print_exc()

print("\n🏁 ETL process finished.")

def export_table_to_csv(table_name, filename):
    try:
        conn = create_connection()
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        conn.close()
        export_dir = os.path.join(BASE_DIR, "../tables")
        os.makedirs(export_dir, exist_ok=True)
        export_path = os.path.join(export_dir, filename)
        df.to_csv(export_path, index=False)
        print(f"✅ Exported {table_name} to {filename}")
    except Exception as e:
        print(f"❌ Failed to export {table_name}: {e}")

# Panggil fungsi ekspor
export_table_to_csv("dim_app", "dim_app.csv")
export_table_to_csv("dim_price", "dim_price.csv")
export_table_to_csv("dim_contentRating", "dim_contentRating.csv")
export_table_to_csv("dim_device", "dim_device.csv")
export_table_to_csv("dim_date", "dim_date.csv")
export_table_to_csv("fact_app_reviews", "fact_app_reviews.csv")