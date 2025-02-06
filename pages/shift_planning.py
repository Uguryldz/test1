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

# Create weekly schedule button
if st.button("Haftalık Vardiya Planı Oluştur"):
    if len(st.session_state.employees) == 0:
        st.error("Önce çalışan ekleyin!")
    else:
        # Convert date to datetime
        start_datetime = datetime.combine(planning_date, datetime.min.time())

        # Create weekly schedule
        weekly_schedule = optimizer.create_weekly_schedule(
            st.session_state.employees,
            start_datetime
        )

        # Store in session state
        st.session_state.shifts = weekly_schedule

        st.success("Haftalık vardiya planı oluşturuldu!")

# Display current schedule
if len(st.session_state.shifts) > 0:
    st.subheader("Vardiya Planı")

    # Get employee names
    employee_names = st.session_state.employees.set_index('id')['name'].to_dict()

    # Add employee names to shifts
    display_shifts = st.session_state.shifts.copy()
    display_shifts['Çalışan'] = display_shifts['employee_id'].map(employee_names)

    # Format for display
    display_shifts['Tarih'] = pd.to_datetime(display_shifts['date']).dt.strftime('%Y-%m-%d')
    display_shifts['Vardiya'] = display_shifts['shift_type']

    # Show shifts grouped by date
    for date in sorted(display_shifts['Tarih'].unique()):
        st.write(f"### {date}")
        day_shifts = display_shifts[display_shifts['Tarih'] == date]

        # Group by shift type
        for shift_type in sorted(day_shifts['Vardiya'].unique()):
            if shift_type != 'OFF':
                shift_employees = day_shifts[day_shifts['Vardiya'] == shift_type]
                st.write(f"**{shift_type}** ({len(shift_employees)} kişi)")
                st.write(", ".join(shift_employees['Çalışan'].tolist()))

        # Show OFF employees
        off_employees = day_shifts[day_shifts['Vardiya'] == 'OFF']
        if len(off_employees) > 0:
            st.write("**OFF**")
            st.write(", ".join(off_employees['Çalışan'].tolist()))

        st.write("---")

else:
    st.info("Henüz vardiya planı oluşturulmamış.")