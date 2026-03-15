# app.py
# IDEAS FOR GUI
# 1. Metrics arranged in a grid showing price change across different locations



import streamlit as st
from read_sql import get_dates
#from read_sql import avg_price_timeline

st.session_state.min_date, st.session_state.max_date = get_dates()

page_txt = {'English': ['Home', 'Timeseries', 'Heatmap'],
            'Latviski': ['Sākums', 'Laika grafiks', 'Kvadrātgrafiks']}

with st.sidebar:
    st.session_state['lang'] = st.selectbox('Language', ['English', 'Latviski'], index=0, width=150)

pages = [st.Page('app_pages/module_home.py', title=page_txt[st.session_state['lang']][0], icon="🏡"),
        st.Page('app_pages/module_timeseries.py', title=page_txt[st.session_state['lang']][1], icon="🗓️"),
        st.Page('app_pages/module_heatmap.py', title=page_txt[st.session_state['lang']][2], icon="🧱")]

pg = st.navigation(pages, position='sidebar', expanded=True)

pg.run()





#df = avg_price_timeline().reset_index()

#st.sidebar.write('This is a sidebar')
#st.line_chart(df, x='StudyDate', y=[ x for x in df.columns if x != 'StudyDate'])