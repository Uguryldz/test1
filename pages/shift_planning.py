import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils.advanced_optimizer import AdvancedShiftOptimizer
from io import BytesIO
import psycopg2
from psycopg2.extras import RealDictCursor
import os

st.title("Shift Planlama")

# Database connection
def get_database_connection():
    return psycopg2.connect(os.environ["DATABASE_URL"])

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
            try:
                # Convert date to datetime
                start_datetime = datetime.combine(planning_date, datetime.min.time())

                # Create weekly schedule using advanced optimizer
                weekly_schedule = optimizer.optimize_weekly_schedule(
                    st.session_state.employees,
                    start_datetime
                )

                # Store in session state
                st.session_state.shifts = weekly_schedule

                # Save to database
                with get_database_connection() as conn:
                    with conn.cursor() as cur:
                        for _, shift in weekly_schedule.iterrows():
                            cur.execute("""
                                INSERT INTO employee_shifts (employee_id, shift_type_id, shift_date, start_time, end_time)
                                VALUES (%s, %s, %s, %s, %s)
                            """, (shift['employee_id'], shift['shift_type'], shift['date'], shift['start_time'], shift['end_time']))
                    conn.commit()

                st.success("Haftalık vardiya planı oluşturuldu!")
            except Exception as e:
                st.error(f"Vardiya planı oluşturulurken hata: {str(e)}")

# Display current schedule
if hasattr(st.session_state, 'shifts') and not st.session_state.shifts.empty:
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
        index=['name', 'hire_date', 'location', 'employee_id'],
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

    # Get available shift types from database
    with get_database_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT DISTINCT shift_name FROM shift_types ORDER BY shift_name")
            shift_types = [row['shift_name'] for row in cur.fetchall()]
            shift_types.append('OFF')  # Add OFF option
            
    # Create column configuration for data editor
    column_config = {
        'İsim - Soyisim': st.column_config.TextColumn(disabled=True),
        'İşe Giriş': st.column_config.TextColumn(disabled=True),
        'Yaka': st.column_config.TextColumn(disabled=True),
        'employee_id': st.column_config.TextColumn(disabled=True)
    }
    
    # Add configuration for date columns
    for col in shift_table.columns:
        if col not in ['İsim - Soyisim', 'İşe Giriş', 'Yaka', 'employee_id']:
            column_config[col] = st.column_config.SelectboxColumn(
                'Vardiya',
                options=shift_types,
                required=True
            )

    edited_df = st.data_editor(
        shift_table,
        column_config=column_config,
        use_container_width=True
    )

    if st.button("Vardiya Değişikliklerini Kaydet"):
        try:
            with get_database_connection() as conn:
                with conn.cursor() as cur:
                    for _, row in edited_df.iterrows():
                        for date_col in edited_df.columns[4:]:  # Skip the first 4 columns (name, hire_date, location, employee_id)
                            if row[date_col] != 'OFF':
                                cur.execute("""
                                    UPDATE employee_shifts 
                                    SET shift_type = %s,
                                        start_time = %s,
                                        end_time = %s
                                    WHERE employee_id = %s 
                                    AND shift_date = %s
                                """, (row[date_col], row[f'start_time'][date_col], row[f'end_time'][date_col], 
                                     row['employee_id'], datetime.strptime(date_col, '%d/%m/%Y')))
                conn.commit()
            st.success("Vardiya değişiklikleri kaydedildi!")
        except Exception as e:
            st.error(f"Hata oluştu: {str(e)}")

else:
    st.info("Henüz vardiya planı oluşturulmamış.")

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