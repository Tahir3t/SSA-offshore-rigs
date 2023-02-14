import pandas as pd
from pandas.api.types import (
    is_categorical_dtype,
    is_numeric_dtype)
import streamlit as st
import numpy as np
st.set_page_config(layout='wide', page_title="SSA Offshore Rigs", initial_sidebar_state="expanded")
import gspread
from gspread_dataframe import get_as_dataframe

st.markdown(
    """
<style>
[data-testid="stMetricValue"] {
    font-size: 20px;
}
#MainMenu {visibility: hidden;}
footer {visibility: visible;}
footer:after{content:'Made by Tahir Elfaki'; display:block; position:relative}
</style>
""",
    unsafe_allow_html=True,
)

st.title("🌍 Sub Sahara Africa Offshore Rigs")
gc = gspread.service_account("credentials.json")
ws = gc.open("InfieldRigs").worksheet("info")
g_sheet = get_as_dataframe(ws)
wanted_status = ["Cold Stacked", "Enroute", "Operational", "Ready Stacked"]
data = g_sheet[g_sheet['operating_status'].isin(wanted_status)]
data = data.replace(",", "", regex=True)
data['drawworks_hp'] = data['drawworks_hp'].replace("--", 0)
data['operating_company'] = data['operating_company'].replace(np.nan, "--")
# data[["max_water_depth_ft", "max_drill_depth_ft", "drawworks_hp", "hookload_cap_lbs"]] = data[["max_water_depth_ft", "max_drill_depth_ft", "drawworks_hp", "hookload_cap_lbs"]].apply(pd.to_numeric, errors='ignore')
to_numeric_col = ["max_water_depth_ft", "max_drill_depth_ft", "drawworks_hp", "hookload_cap_lbs"]
for x in to_numeric_col:
    data[x] = pd.to_numeric(data[x])



df = data.copy()
df = df.drop(["current_region"], axis=1)
new_cols = ["Rig Name", "Rig Owner", "Year Built", "Rig Manager", "Rig Type", "Rig Subtype", "Jackup Type", "Max Water Depth (ft)", "Max Drill Depth (ft)",
                 "Drawworks Type", "Drawworks HP", "Mud Pumps", "Top Drive", "Hookload Capacity (lb)", "Current Country", "Operational Status", "Operating Company"]
df.columns = new_cols

modification_container = st.container()
with modification_container:
    st.sidebar.header("🌍 Rigs Filter")
    st.markdown("##")
    to_filter_columns = st.sidebar.multiselect("Filter on:", df.columns)
    for column in to_filter_columns:
        left, right = st.sidebar.columns((1,20))
        left.write("↳")
        if is_categorical_dtype(df[column]) or df[column].nunique()<=10:
            user_cat_input = right.multiselect(
                f"Values for {column}",
                df[column].unique(),
                default=list(df[column].unique())
            )
            df = df[df[column].isin(user_cat_input)]

        elif is_numeric_dtype(df[column]):
            _min = int(df[column].min())
            _max = int(df[column].max())
            user_num_input = right.slider(
                f"Values for {column}",
                _min,
                _max,
                (_min, _max)
            )
            df = df[df[column].between(*user_num_input)]
        else:
            user_text_input = right.text_input(
                f"Substring or regex in {column}"
            )
            if user_text_input:
                df = df[df[column].str.contains(user_text_input)]

rigs_number = df['Rig Name'].nunique()
countries_number = df['Current Country'].nunique()
op_rigs = df[df['Operational Status'] == 'Operational']['Operational Status'].value_counts().sum()
cstacked_rigs = df[df['Operational Status'] == 'Cold Stacked']['Operational Status'].value_counts().sum()
rstacked_rigs = df[df['Operational Status'] == 'Ready Stacked']['Operational Status'].value_counts().sum()
enroute_rigs = df[df['Operational Status'] == 'Enroute']['Operational Status'].value_counts().sum()
drillship_rigs = df[df['Rig Type'] == 'Drillship']['Rig Type'].value_counts().sum()
jackup_rigs = df[df['Rig Type'] == 'Jackup']['Rig Type'].value_counts().sum()
semi_tender = df[df['Rig Type'] == 'Semi-Tender']['Rig Type'].value_counts().sum()
semisub_rigs = df[df['Rig Type'] == 'Semisub']['Rig Type'].value_counts().sum()
tender_rigs = df[df['Rig Type'] == 'Tender Rig']['Rig Type'].value_counts().sum()



a1, a2 = st.columns(2)
with a1:
    st.metric("No. of Offshore Rigs", rigs_number)
with a2:
    st.metric("Current Countries", countries_number)  
st.markdown("---")
st.markdown("#### Status")
b1, b2, b3, b4 = st.columns(4)
with b1:
    st.metric("🚀 Operational", op_rigs)
with b2:
    st.metric("⏳ Ready Stacked", rstacked_rigs)
with b3:
    st.metric("❄️ Cold Stacked", cstacked_rigs)
with b4:
    st.metric("🚢 Enroute", enroute_rigs)
st.markdown("---")
st.markdown("#### Type")
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.metric("🔵 Drillship", drillship_rigs)
with c2:
    st.metric("🔰 Jackup", jackup_rigs)
with c3:
    st.metric("🔴 Semi-Tender", semi_tender)
with c4:
    st.metric("🔷 Semisub", semisub_rigs)
with c5:
    st.metric("🔘Tender Rig", tender_rigs)
st.markdown("---")
st.markdown("#### Specifications")
d1, d2, d3, d4 = st.columns(4)
with d1:
    st.metric("🔵 Min. Water Depth (ft)", df['Max Water Depth (ft)'].min())
    st.metric("🔵 Max. Water Depth (ft)", df['Max Water Depth (ft)'].max())
with d2:
    st.metric("🔴 Min. Drill Depth (ft)", df['Max Drill Depth (ft)'].min())
    st.metric("🔴 Max. Drill Depth (ft)", df['Max Drill Depth (ft)'].max())
with d3:
    st.metric("🔵 Min. Drawworks HP", df[df['Drawworks HP'] > 0]['Drawworks HP'].min())
    st.metric("🔵 Max. Drawworks HP", df['Drawworks HP'].max())
with d4:
    st.metric("🔴 Min. Hookload Capacity (lb)", df['Hookload Capacity (lb)'].min())
    st.metric("🔴 Max. Hookload Capacity (lb)", df['Hookload Capacity (lb)'].max())
st.markdown("---")
st.markdown("#### Operating Companies")
client_df = df[['Operating Company', 'Current Country' ,'Rig Name', 'Rig Type', 'Operational Status']].copy()
client_df = client_df[client_df['Operating Company'] != "--"].sort_values(by=['Operating Company']).reset_index(drop=True)

if client_df['Operating Company'].nunique() > 0:
    st.write(f"There are {client_df['Operating Company'].nunique()} operating companies working in {client_df['Current Country'].nunique()} countries with total of {client_df['Rig Name'].nunique()} offshore rigs.")
    st.dataframe(client_df)
else:
    st.write(f"There are no operating companies. However, the {df['Rig Name'].nunique()} offshore rigs are in {df['Current Country'].nunique()} countries.")
    st.dataframe(df[['Operating Company', 'Current Country' ,'Rig Name', 'Rig Type', 'Operational Status']].sort_values(by=['Current Country']).reset_index(drop=True))
# st.write(df['Operating Company'].unique())

st.markdown("---")
st.markdown("#### Details Card")
for index, row in df.iterrows():
    with st.expander(row['Rig Name']):
        x1, x2 = st.columns(2)
        with x1:
            st.metric("Operational Status", row['Operational Status'])
            st.metric("Year Built", row['Year Built'])
            st.metric("Rig Owner", row['Rig Owner'])
            st.metric("Rig Manager", row['Rig Manager'])
            st.metric("Rig Type", row['Rig Type'])
            st.metric("Rig Sub-Type", row['Rig Subtype'])
            st.metric("Max Water Depth (ft)", row['Max Water Depth (ft)'])
            st.metric("Max Drill Depth (ft)", row['Max Drill Depth (ft)'])
        with x2:
            st.metric("Drawworks Type", row['Drawworks Type'])
            st.metric("Drawworks HP", row['Drawworks HP'])
            st.metric("Mud Pumps", row['Mud Pumps'])
            st.metric("Top Drive", row['Top Drive'])
            st.metric("Hookload Capacity (lb)", row['Hookload Capacity (lb)'])
            st.metric("Current Country", row['Current Country'])
            st.metric("Operating Company", row['Operating Company'])
