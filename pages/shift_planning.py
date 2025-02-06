import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils.advanced_optimizer import AdvancedShiftOptimizer
from io import BytesIO

st.title("Vardiya Planlama")

# Initialize optimizer
optimizer = AdvancedShiftOptimizer()

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
        with st.spinner('Vardiya planı oluşturuluyor...'):
            # Convert date to datetime
            start_datetime = datetime.combine(planning_date, datetime.min.time())

            # Create weekly schedule using advanced optimizer
            weekly_schedule = optimizer.optimize_weekly_schedule(
                st.session_state.employees,
                start_datetime
            )

            # Store in session state
            st.session_state.shifts = weekly_schedule

            st.success("Haftalık vardiya planı oluşturuldu!")

# Display current schedule
if len(st.session_state.shifts) > 0:
    st.subheader("Vardiya Planı")

    # Get employee information
    employees_info = st.session_state.employees.copy()

    # Create pivot table for shift display
    pivot_data = st.session_state.shifts.copy()
    pivot_data['Tarih'] = pd.to_datetime(pivot_data['date']).dt.strftime('%d/%m/%Y')

    # Merge with employee information
    display_data = pivot_data.merge(
        employees_info[['id', 'name', 'location', 'hire_date']],
        left_on='employee_id',
        right_on='id'
    )

    # Create pivot table
    shift_table = pd.pivot_table(
        display_data,
        values='shift_type',
        index=['name', 'hire_date', 'location'],
        columns='Tarih',
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

    # Format dates
    shift_table['İşe Giriş'] = pd.to_datetime(shift_table['İşe Giriş']).dt.strftime('%d/%m/%Y')

    # Display table
    st.dataframe(shift_table, use_container_width=True)

    # Excel download button
    def to_excel(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Vardiya_Plani')
        return output.getvalue()

    excel_data = to_excel(shift_table)
    st.download_button(
        label="Excel Olarak İndir",
        data=excel_data,
        file_name=f'vardiya_plani_{planning_date.strftime("%d_%m_%Y")}.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

else:
    st.info("Henüz vardiya planı oluşturulmamış.")