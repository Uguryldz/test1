import streamlit as st
import pandas as pd
from datetime import datetime
import random

# Turkish names for random generation
TURKISH_NAMES = [
    "Ahmet", "Mehmet", "Ali", "Ayşe", "Fatma", "Zeynep", "Can", "Deniz", "Ece", 
    "Figen", "Gökhan", "Hakan", "İrem", "Jale", "Kemal", "Leyla", "Mustafa", 
    "Nur", "Okan", "Pınar", "Ramazan", "Selin", "Tamer", "Ufuk", "Volkan", 
    "Yasemin", "Zehra", "Berk", "Canan", "Derya", "Emre", "Fulya", "Gamze", 
    "Hande", "İlker", "Kaan", "Lale", "Mine", "Nalan", "Orhan", "Pelin", 
    "Rüzgar", "Selim", "Tuğba", "Uğur", "Yılmaz", "Zeki", "Aslı", "Burak", "Çiğdem"
]

TURKISH_SURNAMES = [
    "Yılmaz", "Kaya", "Demir", "Şahin", "Çelik", "Yıldız", "Yıldırım", "Öztürk",
    "Aydın", "Özdemir", "Arslan", "Doğan", "Kılıç", "Aslan", "Çetin", "Şen", "Kurt",
    "Özkan", "Şimşek", "Ay", "Kaplan", "Tekin", "Güneş", "Bilgin", "Koç", "Kartal",
    "Akkaya", "Korkmaz", "Türk", "Aktaş"
]

def generate_random_employees(count=50):
    employees = []

    # Amasya locations
    amasya_locations = ["Amasya-1", "Amasya 2-A", "Amasya 2-B", "Amasya 3"]

    for i in range(count):
        # Random location distribution
        location = random.choice(amasya_locations)

        # Generate name
        name = f"{random.choice(TURKISH_NAMES)} {random.choice(TURKISH_SURNAMES)}"

        # Special conditions (15% chance)
        special_condition = random.choice([
            None, None, None, None, None, None, None, None, None,
            "Hamile", "Engelli", "Doğum Sonrası"
        ])

        employee = {
            'id': i + 1,
            'name': name,
            'location': location,
            'district': None,  # Only for Istanbul
            'special_condition': special_condition,
            'service_route': location,  # Using location as service route
            'hire_date': datetime.now()
        }

        employees.append(employee)

    return pd.DataFrame(employees)

st.title("Çalışan Yönetimi")

# Add button to generate random employees
if st.button("50 Rastgele Çalışan Ekle") and len(st.session_state.employees) == 0:
    st.session_state.employees = generate_random_employees(50)
    st.success("50 rastgele çalışan başarıyla eklendi!")

def add_employee():
    with st.form("new_employee"):
        name = st.text_input("İsim")
        location = st.selectbox("Lokasyon", ["Amasya-1", "Amasya 2-A", "Amasya 2-B", "Amasya 3"])

        special_condition = st.selectbox(
            "Özel Durum",
            ["Yok", "Hamile", "Engelli", "Doğum Sonrası"]
        )

        if st.form_submit_button("Çalışan Ekle"):
            new_employee = {
                'id': len(st.session_state.employees) + 1,
                'name': name,
                'location': location,
                'district': None,
                'special_condition': special_condition if special_condition != "Yok" else None,
                'service_route': location,
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
        st.dataframe(st.session_state.employees.style.set_properties(**{
            'background-color': 'lightgreen',
            'color': 'black'
        }, subset=pd.IndexSlice[st.session_state.employees['special_condition'].notna(), :]))
    else:
        st.info("Henüz çalışan eklenmemiş.")

with col2:
    st.subheader("Yeni Çalışan Ekle")
    add_employee()