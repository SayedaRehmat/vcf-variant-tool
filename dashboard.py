
import streamlit as st
import pandas as pd
import plotly.express as px

st.header("📊 Variant Summary Dashboard")

if "df" in st.session_state:
    df = st.session_state["df"]

    # Pie chart of ACMG
    pie = px.pie(df, names="ACMG", title="ACMG Classification Distribution")
    st.plotly_chart(pie)

    # Bar chart of ClinVar significance
    bar = px.bar(df["ClinVar"].value_counts().reset_index(),
                 x="index", y="ClinVar", title="ClinVar Classification Frequency")
    st.plotly_chart(bar)
else:
    st.warning("No data loaded yet. Upload a VCF file in the main app.")
