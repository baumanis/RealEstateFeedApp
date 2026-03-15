import streamlit as st



page_txt = {
    'English': ['Real Estate Feed - Home',
"""<p><b>Heatmap:</b> see all ads on ss.lv arranged in a hierarchy depending on ciy, district etc, as well as visually show cheapest and most expensive areas. Shows audit trail of changed prices.</p>
<p><b>Timeseries:</b> change of average price per sqm over time in each major area.</p>
                """],
    'Latviski': ['Real Estate Feed - Sākums',
"""<p><b>Kvadrātgrafiks:</b> parāda ss.lv sludinājumus hierarhiskā struktūrā pēc pilsētas, rajona utml., kā arī vizuāli parāda dārgākos un lētākos apgabalus. Parāda cenas izmaiņas sludinājumam.</p>
<p><b>Laika grafiks:</b> vidējās cenas par kvadrātmetru izmaiņas laika griezumā pa apabaliem.</p>
                                 """
                 ]

}


st.title(page_txt[st.session_state.lang][0])

st.write(page_txt[st.session_state.lang][1], unsafe_allow_html=True)