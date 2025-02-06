import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Vardiya Planlama Sistemi",
    page_icon="📅",
    layout="wide"
)

st.title("Anasayfa")

# Session state initialization
if 'employees' not in st.session_state:
    st.session_state.employees = pd.DataFrame({
        'id': [],
        'name': [],
        'location': [],
        'special_condition': [],
        'district': [],
        'service_route': [],
        'hire_date': [] # Added hire_date column
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
    st.subheader("Hızlı İstatistikler")
    st.write("Bugünkü Vardiya Sayısı: ", len(st.session_state.shifts))
    st.write("Aktif Çalışan Sayısı: ", len(st.session_state.employees))

# Quick view of current week's shifts
st.subheader("Bu Haftanın Vardiyaları")
if len(st.session_state.shifts) > 0:
    # Sort shifts by date
    sorted_shifts = st.session_state.shifts.sort_values('date')
    
    # Format the date column
    sorted_shifts['date'] = pd.to_datetime(sorted_shifts['date']).dt.strftime('%d/%m/%Y')
    
    # Reorder columns to move date to the right
    columns = ['employee_id', 'shift_type', 'start_time', 'end_time', 'date']
    st.dataframe(sorted_shifts[columns])
else:
    st.info("Henüz vardiya planı oluşturulmamış.")