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
    # Get employee information and merge with shifts
    display_data = st.session_state.shifts.merge(
        st.session_state.employees[['id', 'name', 'location', 'hire_date']],
        left_on='employee_id',
        right_on='id'
    )
    
    # Format dates
    display_data['date'] = pd.to_datetime(display_data['date']).dt.strftime('%d/%m/%Y')
    display_data['hire_date'] = pd.to_datetime(display_data['hire_date']).dt.strftime('%d/%m/%Y')
    
    # Create pivot table
    shift_table = pd.pivot_table(
        display_data,
        values='shift_type',
        index=['name', 'hire_date', 'location'],
        columns='date',
        aggfunc='first',
        fill_value='OFF'
    ).reset_index()
    
    # Rename columns
    shift_table.columns.name = None
    shift_table = shift_table.rename(columns={
        'name': 'İsim - Soyisim',
        'hire_date': 'İşe Giriş',
        'location': 'Yaka'
    })
    
    st.dataframe(shift_table, use_container_width=True)
else:
    st.info("Henüz vardiya planı oluşturulmamış.")