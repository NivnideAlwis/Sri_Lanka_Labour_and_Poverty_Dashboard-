import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_extras.metric_cards import style_metric_cards

# Load data
df = pd.read_csv("Cleaned_lka_data.csv")

# --- Beautify Function ---
def beautify_label(label):
    return label.replace("By Sex And Age", "") \
                .replace("ILO Modelled Estimates, Nov. 2024", "") \
                .replace("SDG Indicator 1.1.1 -", "") \
                .replace("(Thousands)", "") \
                .replace("(%)", "") \
                .replace("Percentage Of Employed Living Below US$2.15 PPP", "Poverty Rate") \
                .replace("Not In Employment, Education Or Training", "NEET") \
                .replace("Total Weekly Hours Worked Of Employed Persons", "Total Weekly Hours Worked") \
                .replace("Employment-To-Population Ratio", "Employment-Population Ratio") \
                .replace("Mean Weekly Hours Actually Worked Per Employee", "Mean Weekly Hours") \
                .replace("Full-Time Equivalent Employment", "Full-Time Employment") \
                .strip()

# --- Indicator Groups ---
indicator_groups = {
    "Employment": [
        "Employment By Sex And Age (Thousands)",
        "Employment By Sex, Age And Economic Activity (Thousands)",
        "Employment-To-Population Ratio By Sex And Age (%)",
        "Full-Time Equivalent Employment By Sex -- Ilo Modelled Estimates, Nov. 2024 (Thousands)"
    ],
    "Unemployment": [
        "Unemployment By Sex And Age (Thousands)",
        "Unemployment Rate By Sex And Age (%)"
    ],
    "Labour Force": [
        "Labour Force By Sex And Age (Thousands)",
        "Labour Force Participation Rate By Sex And Age (%)",
        "Inactivity Rate By Sex And Age (%)",
        "Working-Age Population By Sex And Age (Thousands)",
        "Persons Outside The Labour Force By Sex And Age (Thousands)"
    ],
    "Working Hours": [
        "Mean Weekly Hours Actually Worked Per Employee By Sex And Age",
        "Total Weekly Hours Worked Of Employed Persons, By Sex -- Ilo Modelled Estimates, Nov. 2024 (Thousands)",
        "Ratio Of Total Weekly Hours Worked To Population Aged 15-64, By Sex -- Ilo Modelled Estimates, Nov. 2024"
    ],
    "Poverty and Youth": [
        "Sdg Indicator 1.1.1 - Working Poverty Rate (Percentage Of Employed Living Below Us$2.15 Ppp) (%)",
        "Youth Not In Employment, Education Or Training (Neet) By Sex And Age (Thousands)",
        "Share Of Youth Not In Employment, Education Or Training (Neet) By Sex And Age (%)"
    ]
}

# --- Classification1 Groupings ---
classification_groups = {
    "Aggregate Bands": ["Age (Aggregate bands): 15-24","Age (Aggregate bands): 25-54","Age (Aggregate bands): 55-64","Age (Aggregate bands): 65+","Age (Aggregate bands): Total"],
    "10-Year Bands": ["Age (10-year bands): 15-24","Age (10-year bands): 25-34","Age (10-year bands): 35-44","Age (10-year bands): 45-54","Age (10-year bands): 55-64","Age (10-year bands): 65+","Age (10-year bands): Total"],
    "5-Year Bands": ["Age (5-year bands): 15-19","Age (5-year bands): 20-24", "Age (5-year bands): 25-29", "Age (5-year bands): 30-34", "Age (5-year bands): 35-39", "Age (5-year bands): 40-44", "Age (5-year bands): 45-49", "Age (5-year bands): 50-54", "Age (5-year bands): 55-59", "Age (5-year bands): 60-64","Age (5-year bands): 65+","Age (5-year bands): Total"],
    "Youth/Adult Bands": ["Age (Youth, adults): 15-24","Age (Youth, adults): 15-64","Age (Youth, adults): 15+","Age (Youth, adults): 25+"],
    "Full-Time Equivalence Bands": ["Full-time equivalence: Based on 40 hours per week", "Full-time equivalence: Based on 48 hours per week"]
}

# --- Classification2 Groupings ---
classification2_groups = {
    "Broad Sectors": [
        "Economic activity (Broad sector): Agriculture",
        "Economic activity (Broad sector): Non-agriculture",
        "Economic activity (Broad sector): Industry",
        "Economic activity (Broad sector): Services"
    ],
    "Aggregate Sectors": [
        "Economic activity (Aggregate): Total",
        "Economic activity (Aggregate): Agriculture",
        "Economic activity (Aggregate): Manufacturing",
        "Economic activity (Aggregate): Construction",
        "Economic activity (Aggregate): Mining and quarrying; Electricity, gas and water supply",
        "Economic activity (Aggregate): Trade, Transportation, Accommodation and Food, and Business and Administrative Services",
        "Economic activity (Aggregate): Public Administration, Community, Social and other Services and Activities"
    ],
    "ISIC Rev.4 Codes": [
        entry for entry in df['classification2'].dropna().unique()
        if entry.startswith("Economic activity (ISIC-Rev.4):")
    ]
}

# --- Sidebar Filters ---
st.sidebar.header("🔎 Filter Main Indicator View")

category = st.sidebar.selectbox("📁 Indicator Category:", list(indicator_groups.keys()))
indicator = st.sidebar.selectbox("🎯 Indicator:", indicator_groups[category])
year_range = st.sidebar.slider("📅 Year Range:", int(df['year'].min()), int(df['year'].max()), (2015, 2025))

# --- Dynamic Filtering Options ---
filtered_temp = df[(df['indicator'] == indicator) & (df['year'] >= year_range[0]) & (df['year'] <= year_range[1])]
sex_options = sorted(filtered_temp['sex'].dropna().unique())
sex = st.sidebar.selectbox("👥 Sex:", ["All"] + sex_options) if len(sex_options) > 1 else "All"

# --- Classification 1 Filter ---
st.sidebar.markdown("### Demographic Group (Grouped)")
selected_classifications = []
for group_name, group_values in classification_groups.items():
    valid_values = [val for val in group_values if val in filtered_temp['classification1'].unique()]
    if valid_values:
        selection = st.sidebar.multiselect(f"🔸 {group_name}:", options=valid_values)
        selected_classifications.extend(selection)
apply_classification1_filter = bool(selected_classifications)

# --- Classification 2 Filter ---
st.sidebar.markdown("### Economic Sector (Grouped)")
classif2 = []
for group, options in classification2_groups.items():
    valid_opts = [opt for opt in options if opt in filtered_temp['classification2'].unique()]
    if valid_opts:
        sel = st.sidebar.multiselect(f"📂 {group}:", options=valid_opts)
        classif2.extend(sel)
apply_classification2_filter = bool(classif2)

# --- Apply Final Filters ---
filtered = df[(df['indicator'] == indicator) & (df['year'] >= year_range[0]) & (df['year'] <= year_range[1])]
if sex != "All":
    filtered = filtered[filtered['sex'] == sex]
if apply_classification1_filter:
    filtered = filtered[filtered['classification1'].isin(selected_classifications)]
if apply_classification2_filter:
    filtered = filtered[filtered['classification2'].isin(classif2)]

# --- Main Display ---
title = beautify_label(indicator)
st.title("📊 Sri Lanka Labour & Poverty Dashboard")
st.markdown(f"### Indicator: **{title}**")

if filtered.empty:
    st.warning("⚠️ No data available for the selected filters.")
else:
    # --- Line Chart ---
    filtered['color_group'] = filtered['sex']
    if apply_classification1_filter:
        filtered['color_group'] += " | " + filtered['classification1']
    if apply_classification2_filter:
        filtered['color_group'] += " | " + filtered['classification2']
        
    fig = px.line(filtered, x="year", y="value", color="color_group", markers=True,
                  title=f"{title} Over Time",
                  labels={"value": title, "year": "Year", "color_group": "Group"},
                  color_discrete_sequence=px.colors.qualitative.Set3)

# --- Fix legend overlap ---
    # Determine whether legend should go below based on number of groups
too_many_groups = filtered['color_group'].nunique() > 6
fig.update_layout(
    legend=dict(
        orientation="h" if too_many_groups else "v",
        yanchor="bottom" if too_many_groups else "top",
        y=-0.8 if too_many_groups else 1,
        xanchor="center" if too_many_groups else "left",
        x=0.5 if too_many_groups else 1.02,
        bgcolor="rgba(255,255,255,0.7)",
        bordercolor="gray",
        borderwidth=0.5,
        font=dict(size=10),
    ),
    margin=dict(l=60, r=60, t=60, b=120 if too_many_groups else 60),
    height=650
)
st.plotly_chart(fig, use_container_width=True)

# --- Summary Cards ---
latest_year = filtered['year'].max()
latest = filtered[filtered['year'] == latest_year]

if sex == "All":
        latest_total = latest[latest['sex'] == "Total"]
        mean_val = round(latest_total['value'].mean(), 2)
        min_val = round(latest_total['value'].min(), 2)
        max_val = round(latest_total['value'].max(), 2)
else:
        mean_val = round(latest['value'].mean(), 2)
        min_val = round(latest['value'].min(), 2)
        max_val = round(latest['value'].max(), 2)

col1, col2, col3 = st.columns(3)
col1.metric("🔹 Average", f"{mean_val}")
col2.metric("📉 Minimum", f"{min_val}")
col3.metric("📈 Maximum", f"{max_val}")
style_metric_cards()

    # --- Classification Charts ---
grid1, grid2 = st.columns(2)
if filtered['classification1'].nunique() > 1:
    with grid1:
        fig1 = px.bar(filtered, x='classification1', y='value', color='sex',
                      title=f"{title} by Classification 1",
                      labels={"classification1": "Classification 1", "value": title},
                      color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig1, use_container_width=True)

if filtered['classification2'].nunique() > 1:
    with grid2:
        fig2 = px.bar(filtered, x='classification2', y='value', color='sex',
                      title=f"{title} by Classification 2",
                      labels={"classification2": "Classification 2", "value": title},
                      color_discrete_sequence=px.colors.qualitative.Prism)
        st.plotly_chart(fig2, use_container_width=True)

# --- Footer ---
st.markdown("---")
st.caption("Developed for University of Westminster – Data Science Project Lifecycle © 2025")
