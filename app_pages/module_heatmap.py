import streamlit as st

from read_sql import get_all_rows, get_static
import plotly.express as px
# import plotly.graph_objects as go


page_txt = {
    'Latviski': ['Kvadrātgrafiks', 'Pārdod', 'Izīrē', 'Par datumu', 'Pilsēta',
                 'Darījuma veids', 'Rādīt tikai labotos sludinājumus', 'Cena uz kvadrātmetru'],
    'English': ['Heatmap', 'Sell', 'Rent', 'Study date', 'City',
                'Type of deal', 'Show amended ads only', 'Price per sqm']
}


@st.fragment
def page_runn():
    st.title(page_txt[st.session_state['lang']][0])

    cols = st.columns(2)

    with cols[0]:
        st.session_state.input_study_date = st.date_input(page_txt[st.session_state['lang']][3], value=None, min_value=st.session_state.min_date,
                                                          max_value=st.session_state.max_date)
        st.session_state.input_city = st.selectbox(page_txt[st.session_state['lang']][4], get_static('Pilseta') , index=None)

    with cols[1]:
        st.session_state.input_typeofdeal = st.selectbox(page_txt[st.session_state['lang']][5], [page_txt[st.session_state['lang']][1],
                                                         page_txt[st.session_state['lang']][2]], index=None)
        st.session_state.input_changesonly = st.checkbox(page_txt[st.session_state['lang']][6])


    if st.session_state.input_study_date is not None and st.session_state.input_typeofdeal is not None:
        # fig = go.Treemap()
        fig = px.treemap((dff:=get_all_rows(st.session_state.input_study_date.strftime('%Y-%m-%d'), 1 if st.session_state.input_typeofdeal in ['Sell', 'Pārdod'] else 0,
                                            city=st.session_state.input_city, price_changes_only=st.session_state.input_changesonly)),
                         path=[px.Constant("LV"), 'City', 'District', 'Street', 'custom_text'], values='Size',
                         color='Per_sqm',
                         color_continuous_scale=[[0, 'white'], [1, 'black']],
                         labels={'Per_sqm': page_txt[st.session_state['lang']][7]}
                         )

        fig.update_layout(hovermode=False)
        st.plotly_chart(fig)

page_runn()
