# module_timeseries.py
import streamlit as st
from read_sql import avg_price_timeline
import plotly.express as px

page_txt = {
    'English': ['Timeseries', 'Type of deal', 'Sell', 'Rent', 'Price per sqm, EUR',
                'City', 'Study date'],
    'Latviski': ['Laika grafiks', 'Darījuma veids', 'Pārdod', 'Izīrē', 'Cena uz kvadrātmetru, EUR',
                 'Pilsēta', 'Par datumu']
}



st.title(page_txt[st.session_state.lang][0])

input_typeofdeal = st.selectbox(page_txt[st.session_state.lang][1],
                                [page_txt[st.session_state.lang][2], page_txt[st.session_state.lang][3]], index=None,
                                width=150)

if input_typeofdeal is not None:




    df = avg_price_timeline(1 if input_typeofdeal in ['Sell', 'Pārdod'] else 0)

    fig = px.line(df, x=df.index, y=df.columns, labels={
        'value': page_txt[st.session_state.lang][4],
        'City': page_txt[st.session_state.lang][5],
        'StudyDate': page_txt[st.session_state.lang][6],
    }
                  )

    st.plotly_chart(fig, width=2000, height=500)

# st.line_chart(df, x='StudyDate', y=[ x for x in df.columns if x != 'StudyDate'])