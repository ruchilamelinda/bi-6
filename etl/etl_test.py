import mysql.connector

try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",                  
        password="",  
        database="playstoredb",       
        port=3306
    )
    print("✅ Koneksi sukses ke MySQL!")
    conn.close()
except mysql.connector.Error as e:
    print("❌ Gagal konek ke MySQL:", e)
