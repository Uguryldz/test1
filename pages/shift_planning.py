import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils.shift_validator import ShiftValidator
from utils.shift_optimizer import ShiftOptimizer

st.title("Vardiya Planlama")

# Initialize validator and optimizer
validator = ShiftValidator()
optimizer = ShiftOptimizer()

# Date selection
planning_date = st.date_input(
    "Planlama Başlangıç Tarihi",
    min_value=datetime.now().date()
)

# Location selection
location = st.selectbox("Lokasyon", ["Amasya", "İstanbul"])

# Get relevant employees
location_employees = st.session_state.employees[
    st.session_state.employees['location'] == location
]

# Shift planning interface
st.subheader("Vardiya Ataması")

with st.form("shift_assignment"):
    # Employee selection
    employee_id = st.selectbox(
        "Çalışan",
        options=location_employees['id'].tolist(),
        format_func=lambda x: location_employees[
            location_employees['id'] == x
        ]['name'].iloc[0]
    )
    
    # Shift type selection based on location
    shift_types = {
        'Amasya': ['08:00-17:00', '09:00-18:00', '11:00-22:00'],
        'İstanbul': ['08:00-17:00', '15:00-00:00']
    }
    
    shift_type = st.selectbox(
        "Vardiya Tipi",
        options=shift_types[location]
    )
    
    if st.form_submit_button("Vardiya Ekle"):
        # Validate shift
        employee = location_employees[
            location_employees['id'] == employee_id
        ].iloc[0]
        
        # Check special conditions
        if employee['special_condition'] == 'Hamile' and shift_type != '09:00-18:00':
            st.error("Hamile çalışanlar sadece 09:00-18:00 vardiyasında çalışabilir!")
        else:
            # Add shift if valid
            new_shift = {
                'employee_id': employee_id,
                'date': planning_date,
                'shift_type': shift_type,
                'start_time': datetime.strptime(
                    shift_type.split('-')[0],
                    '%H:%M'
                ).time(),
                'end_time': datetime.strptime(
                    shift_type.split('-')[1],
                    '%H:%M'
                ).time()
            }
            
            st.session_state.shifts = pd.concat([
                st.session_state.shifts,
                pd.DataFrame([new_shift])
            ], ignore_index=True)
            
            st.success("Vardiya başarıyla eklendi!")

# Display current shifts
st.subheader("Mevcut Vardiyalar")
if len(st.session_state.shifts) > 0:
    # Filter shifts for selected location
    location_shifts = st.session_state.shifts.merge(
        location_employees[['id', 'name']],
        left_on='employee_id',
        right_on='id'
    )
    st.dataframe(location_shifts)
else:
    st.info("Henüz vardiya planı oluşturulmamış.")

# Optimization tools
if st.button("Vardiyaları Optimize Et"):
    optimized_shifts = optimizer.optimize_service_routes(
        st.session_state.employees,
        st.session_state.shifts
    )
    st.session_state.shifts = optimized_shifts
    st.success("Vardiyalar optimize edildi!")
