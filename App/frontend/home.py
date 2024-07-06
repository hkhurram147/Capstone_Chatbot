import streamlit as st

st.set_page_config(
    page_title="Welcome to PhoenixAI!",
    page_icon="👋",
)

st.write("# Welcome to PhoenixAI 👋")

st.sidebar.success("Select a demo above.")

st.markdown(
    """
    Phoenix AI is a platform to make your office work easier, by automating the repetitive tasks.
    //data analysis, document generation, ppt generation, form filler etc.

    1. **📊 Data Analysis:** Analyze your data with ease.

    2. **📈 Data Visualization:** Visualize your data with interactive charts.

    3. **📑 PPT Maker:** Create a PowerPoint presentation with your data.

    4. **📝 Form Filler:** Fill out forms with your data. 

"""
)

st.write("## Select a demo from the sidebar to get started.")


