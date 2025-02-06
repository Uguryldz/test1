
import streamlit as st
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
import os

def get_database_connection():
    return psycopg2.connect(os.environ["DATABASE_URL"])

st.title("Vardiya Kuralları Yönetimi")

# Tab oluştur
tab1, tab2, tab3 = st.tabs(["Genel Kurallar", "Lokasyon Kuralları", "Özel Durumlar"])

with tab1:
    st.subheader("Genel Vardiya Kuralları")
    
    with st.form("genel_kurallar"):
        min_rest = st.number_input("Vardiyalar Arası Minimum Süre (Saat)", min_value=8, max_value=24, value=11)
        max_weekly = st.number_input("Haftalık Maksimum Çalışma (Saat)", min_value=30, max_value=60, value=45)
        max_yearly_overtime = st.number_input("Yıllık Maksimum Fazla Mesai (Saat)", min_value=0, max_value=500, value=270)
        
        if st.form_submit_button("Genel Kuralları Güncelle"):
            try:
                with get_database_connection() as conn:
                    with conn.cursor() as cur:
                        cur.execute("""
                            UPDATE general_rules SET 
                            min_rest_hours = %s,
                            max_weekly_hours = %s,
                            max_yearly_overtime = %s
                        """, (min_rest, max_weekly, max_yearly_overtime))
                    conn.commit()
                st.success("Genel kurallar güncellendi!")
            except Exception as e:
                st.error(f"Hata: {str(e)}")

with tab2:
    st.subheader("Lokasyon Bazlı Kurallar")
    
    location = st.selectbox(
        "Lokasyon Seç",
        ["Amasya-1", "Amasya 2-A", "Amasya 2-B", "Amasya 3"]
    )
    
    with st.form("lokasyon_kurallari"):
        min_morning = st.number_input("Minimum Sabah Vardiyası Personeli", min_value=1, value=3)
        has_service = st.checkbox("Servis Var", value=True)
        service_time = st.time_input("Servis Saati") if has_service else None
        weekend_policy = st.selectbox(
            "Hafta Sonu Politikası",
            ["Normal Mesai", "Home Office", "Kapalı"]
        )
        
        if st.form_submit_button("Lokasyon Kurallarını Güncelle"):
            try:
                with get_database_connection() as conn:
                    with conn.cursor() as cur:
                        cur.execute("""
                            UPDATE location_rules SET 
                            min_morning_staff = %s,
                            has_service = %s,
                            service_time = %s,
                            weekend_policy = %s
                            WHERE location = %s
                        """, (min_morning, has_service, service_time, weekend_policy, location))
                    conn.commit()
                st.success("Lokasyon kuralları güncellendi!")
            except Exception as e:
                st.error(f"Hata: {str(e)}")

with tab3:
    st.subheader("Özel Durum Kuralları")
    
    special_condition = st.selectbox(
        "Özel Durum",
        ["Hamile", "Engelli", "Doğum Sonrası"]
    )
    
    with st.form("ozel_durum_kurallari"):
        allowed_shifts = st.multiselect(
            "İzin Verilen Vardiyalar",
            ["08:00-17:00", "09:00-18:00", "11:00-20:00", "15:00-00:00"],
            default=["09:00-18:00"]
        )
        max_hours = st.number_input("Maksimum Çalışma Saati (Haftalık)", min_value=20, max_value=45, value=40)
        special_notes = st.text_area("Özel Notlar")
        
        if st.form_submit_button("Özel Durum Kurallarını Güncelle"):
            try:
                with get_database_connection() as conn:
                    with conn.cursor() as cur:
                        cur.execute("""
                            UPDATE special_condition_rules SET 
                            allowed_shifts = %s,
                            max_weekly_hours = %s,
                            notes = %s
                            WHERE condition_type = %s
                        """, (allowed_shifts, max_hours, special_notes, special_condition))
                    conn.commit()
                st.success("Özel durum kuralları güncellendi!")
            except Exception as e:
                st.error(f"Hata: {str(e)}")

# Mevcut kuralları göster
st.subheader("Mevcut Kural Özetleri")

try:
    with get_database_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Genel kuralları getir
            cur.execute("SELECT * FROM general_rules")
            general_rules = cur.fetchone()
            
            # Lokasyon kurallarını getir
            cur.execute("SELECT * FROM location_rules")
            location_rules = cur.fetchall()
            
            # Özel durum kurallarını getir
            cur.execute("SELECT * FROM special_condition_rules")
            special_rules = cur.fetchall()
            
            if general_rules:
                st.write("### Genel Kurallar")
                st.dataframe(pd.DataFrame([general_rules]))
            
            if location_rules:
                st.write("### Lokasyon Kuralları")
                st.dataframe(pd.DataFrame(location_rules))
                
            if special_rules:
                st.write("### Özel Durum Kuralları")
                st.dataframe(pd.DataFrame(special_rules))
                
except Exception as e:
    st.error(f"Kural özetleri getirilirken hata: {str(e)}")
