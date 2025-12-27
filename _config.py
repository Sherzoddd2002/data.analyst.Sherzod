import pandas as pd
import numpy as np
import streamlit as st
import datetime
import plotly.express as px

# 1. SAHIFA SOZLAMALARI
st.set_page_config(page_title="Call Center Analysis", layout="wide")

# 2. MA'LUMOTLARNI YUKLASH
@st.cache_data
def load_data():
    path = r"C:\Users\user\Downloads\Telegram Desktop\yakuniy_dashbord.xlsx"
    data = pd.read_excel(path)
    data['Название обзвона'] = data['Название обзвона'].astype(str).str.lower()
    data['datetime'] = pd.to_datetime(data['datetime'])
    # Statuslarni kichik harfga o'tkazamiz (taqqoslash oson bo'lishi uchun)
    data['Статус'] = data['Статус'].astype(str).str.lower()
    return data

# Ishonch kategoriyasini aniqlash funksiyasi
def categorize_ishonch(days):
    if days <= 5:
        return 'Ҳали ишонса бўлади'
    elif days <= 7:
        return 'Жиддий киришиш керак'
    else:
        return 'Номер хато ёки Суд'

try:
    df = load_data()
    st.title("✅ Completed Статусли Мижозлар Таҳлили")

    # --- UNIQUE MIJOZLAR (FAQAT COMPLETED) ---
    st.header("👥 Муваффақиятли боғланилган мижозlar")
    
    today = datetime.datetime.now()

    # Faqat statusi 'completed' bo'lganlarni ajratib olamiz
    completed_df = df[df['Статус'] == 'completed'].copy()

    if not completed_df.empty:
        # Guruhlash
        unique_completed = completed_df.groupby("Номер телефона", as_index=False).agg({
            "Название обзвона": "count",
            "datetime": "max",                # Oxirgi completed bo'lgan vaqti
            "Финальный результат": "first",
            "Статус": "first"
        })

        # Kun farqini hisoblash
        unique_completed['kun_farqi'] = (today - unique_completed['datetime']).dt.days
        unique_completed['Ишонч статуси'] = unique_completed['kun_farqi'].apply(categorize_ishonch)

        # Sidebar filtr
        st.sidebar.header("Фильтрлар")
        selected_ishonch = st.sidebar.multiselect("Ишонч статуси бўйича:", unique_completed['Ишонч статуси'].unique())
        
        if selected_ishonch:
            unique_completed = unique_completed[unique_completed['Ишонч статуси'].isin(selected_ishonch)]

        # Vizualizatsiya
        col_u1, col_u2 = st.columns([2, 1])
        with col_u1:
            st.subheader("Completed бўлган мижозлар рўйхати")
            # Kun farqini 'X kun oldin' ko'rinishida chiqarish
            unique_completed['Completed бўлганига (кун)'] = unique_completed['kun_farqi']
            st.dataframe(unique_completed.drop(columns=['kun_farqi']), use_container_width=True)
        
        with col_u2:
            st.subheader("Ишонч ҳолати (Completed кесимида)")
            fig_ishonch = px.pie(unique_completed, names='Ишонч статуси', 
                                 color='Ишонч статуси',
                                 color_discrete_map={'Ҳали ишонса бўлади':'#2ecc71', 
                                                   'Жиддий киришиш керак':'#f1c40f', 
                                                   'Номер хато ёки Суд':'#e74c3c'})
            st.plotly_chart(fig_ishonch, use_container_width=True)
            
            # O'rtacha necha kunda completed bo'lganini ko'rsatish
            avg_days = unique_completed['kun_farqi'].mean()
            st.metric("Ўртача 'Completed' вақти", f"{int(avg_days)} кун аввал")
    else:
        st.warning("Ҳозирча 'completed' статусли маълумотлар мавжуд эмас.")

    st.divider()

    # --- SKRIPTLAR BO'YICHA UMUMIY TAHLIL ---
    st.header("📋 Скриптлар кесимида умумий ҳолат")
    
    perekol_df = df[df['Название обзвона'].str.contains("перекол", na=False)]
    start_df   = df[df['Название обзвона'].str.contains("старт", na=False)]
    soft_df    = df[df['Название обзвона'].str.contains("софт", na=False)]

    tabs = st.tabs(["🔄 Перекол", "🚀 Старт", "🧸 Софт"])

    for tab, current_df, name in zip(tabs, [perekol_df, start_df, soft_df], ["Перекол", "Старт", "Софт"]):
        with tab:
            total = len(current_df)
            comp_count = len(current_df[current_df['Статус'] == 'completed'])
            comp_rate = (comp_count / total * 100) if total > 0 else 0
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Жами қўнғироқлар", total)
            m2.metric("Completed сони", comp_count)
            m3.metric("Muvaffaqiyat %", f"{comp_rate:.1f}%")
            
            st.dataframe(current_df, use_container_width=True)

except Exception as e:
    st.error(f"Хатолик юз берди: {e}")
