import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Vardiya Planlama Sistemi",
    page_icon="📅",
    layout="wide"
)

st.title("Vardiya Planlama Sistemi")

# Session state initialization
if 'employees' not in st.session_state:
    st.session_state.employees = pd.DataFrame({
        'id': [],
        'name': [],
        'location': [],
        'special_condition': [],
        'district': [],
        'service_route': []
    })

if 'shifts' not in st.session_state:
    st.session_state.shifts = pd.DataFrame({
        'employee_id': [],
        'date': [],
        'shift_type': [],
        'start_time': [],
        'end_time': []
    })

# Main dashboard
col1, col2 = st.columns(2)

with col1:
    st.subheader("Sistem Özeti")
    st.metric("Toplam Çalışan", len(st.session_state.employees))
    st.metric("Aktif Vardiya", len(st.session_state.shifts))

with col2:
    st.subheader("Hızlı Erişim")
    if st.button("Çalışan Yönetimi"):
        st.switch_page("pages/employee_management.py")
    if st.button("Vardiya Planla"):
        st.switch_page("pages/shift_planning.py")
    if st.button("Vardiya Kuralları"):
        st.switch_page("pages/shift_rules.py")

# Quick view of current week's shifts
st.subheader("Bu Haftanın Vardiyaları")
if len(st.session_state.shifts) > 0:
    st.dataframe(st.session_state.shifts)
else:
    st.info("Henüz vardiya planı oluşturulmamış.")
