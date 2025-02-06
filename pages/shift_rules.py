import streamlit as st
import pandas as pd

st.title("Vardiya Kuralları")

# Location specific rules
st.header("Lokasyon Bazlı Kurallar")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Amasya")
    st.write("Vardiya Tipleri:")
    st.write("- 08:00-17:00")
    st.write("- 09:00-18:00")
    st.write("- 11:00-22:00")
    
    st.write("Kurallar:")
    st.write("- Minimum 3-4 kişi sabah vardiyası")
    st.write("- Maksimum günlük 45 vardiya")
    st.write("- 20:00 sonrası servis var")

with col2:
    st.subheader("İstanbul")
    st.write("Vardiya Tipleri:")
    st.write("- 08:00-17:00")
    st.write("- 15:00-00:00")
    
    st.write("Kurallar:")
    st.write("- Cumartesi-Pazar Home Office")
    st.write("- Pazar günü OFF")
    st.write("- Servis kısıtlamaları")

# Legal requirements
st.header("Yasal Gereklilikler")
st.write("- Vardiyalar arası minimum 11 saat")
st.write("- Maksimum yıllık 270 saat fazla mesai")
st.write("- Haftada zorunlu 1 OFF")
st.write("- Maksimum vardiya süresi 11 saat")

# Special conditions
st.header("Özel Durumlar")
special_conditions = {
    "Hamile": ["09:00-18:00 vardiyası"],
    "Engelli": ["Gece vardiyası yok", "Maksimum 45 saat/hafta"],
    "Doğum Sonrası": ["1 yıl gündüz vardiyası"]
}

for condition, rules in special_conditions.items():
    st.subheader(condition)
    for rule in rules:
        st.write(f"- {rule}")
