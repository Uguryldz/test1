import streamlit as st
import pandas as pd
from datetime import time
import psycopg2
from psycopg2.extras import RealDictCursor
import os

st.title("Vardiya Planlaması")

# Database connection
def get_database_connection():
    return psycopg2.connect(os.environ["DATABASE_URL"])

# Vardiya tipi ekleme formu
with st.form("vardiya_tipi_ekle"):
    st.subheader("Yeni Vardiya Tipi Ekle")
    
    location = st.selectbox(
        "Lokasyon",
        ["Amasya-1", "Amasya 2-A", "Amasya 2-B", "Amasya 3"]
    )
    
    shift_name = st.text_input("Vardiya Adı", placeholder="Örn: Sabah Vardiyası")
    
    col1, col2 = st.columns(2)
    with col1:
        start_time = st.time_input("Başlangıç Saati", time(8, 0))
    with col2:
        end_time = st.time_input("Bitiş Saati", time(17, 0))
        
    min_staff = st.number_input("Minimum Personel Sayısı", min_value=1, value=3)
    
    if st.form_submit_button("Vardiya Tipi Ekle"):
        try:
            with get_database_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO shift_types 
                        (location, shift_name, start_time, end_time, min_staff)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (location, shift_name, start_time, end_time, min_staff))
                conn.commit()
            st.success("Vardiya tipi başarıyla eklendi!")
        except Exception as e:
            st.error(f"Hata oluştu: {str(e)}")

# Mevcut vardiya tiplerini göster
st.subheader("Mevcut Vardiya Tipleri")

try:
    with get_database_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT * FROM shift_types
                ORDER BY location, start_time
            """)
            shift_types = cur.fetchall()
            
    if shift_types:
        df = pd.DataFrame(shift_types)
        st.dataframe(
            df[['location', 'shift_name', 'start_time', 'end_time', 'min_staff']],
            use_container_width=True
        )
    else:
        st.info("Henüz vardiya tipi eklenmemiş.")
        
except Exception as e:
    st.error(f"Veritabanı bağlantısında hata: {str(e)}")
