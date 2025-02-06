import streamlit as st
import pandas as pd
from datetime import datetime

st.title("Çalışan Yönetimi")

def add_employee():
    with st.form("new_employee"):
        name = st.text_input("İsim")
        location = st.selectbox("Lokasyon", ["Amasya", "İstanbul"])
        
        district = None
        if location == "İstanbul":
            district = st.selectbox("Bölge", ["Anadolu", "Avrupa"])
        
        special_condition = st.selectbox(
            "Özel Durum",
            ["Yok", "Hamile", "Engelli", "Doğum Sonrası"]
        )
        
        service_route = st.text_input("Servis Güzergahı")
        
        if st.form_submit_button("Çalışan Ekle"):
            new_employee = {
                'id': len(st.session_state.employees) + 1,
                'name': name,
                'location': location,
                'district': district,
                'special_condition': special_condition if special_condition != "Yok" else None,
                'service_route': service_route,
                'hire_date': datetime.now()
            }
            
            st.session_state.employees = pd.concat([
                st.session_state.employees,
                pd.DataFrame([new_employee])
            ], ignore_index=True)
            
            st.success(f"{name} başarıyla eklendi!")

# Employee management interface
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Mevcut Çalışanlar")
    if len(st.session_state.employees) > 0:
        st.dataframe(st.session_state.employees)
    else:
        st.info("Henüz çalışan eklenmemiş.")

with col2:
    st.subheader("Yeni Çalışan Ekle")
    add_employee()
