import streamlit as st
import pandas as pd
import plotly.express as px

# Load data

df = pd.read_pickle("Models/Sales_project/Clustered_data.pkl")  # your df_sort saved as csv

st.set_page_config(page_title="Sales Cluster Dashboard", layout="wide")

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.title("Filters")

cluster_selected = st.sidebar.multiselect(
    "Select Cluster(s)",
    sorted(df['Clusters'].unique()),
    default=sorted(df['Clusters'].unique())
)

item_selected = st.sidebar.multiselect(
    "Select Item Type(s)",
    df['ITEM TYPE'].unique(),
    default=df['ITEM TYPE'].unique()
)

df_f = df[
    df['Clusters'].isin(cluster_selected) &
    df['ITEM TYPE'].isin(item_selected)
]

# -----------------------------
# Title
# -----------------------------
st.title("📊 Sales Segmentation Dashboard")

st.markdown("""
This dashboard explains **product sales behavior** using clustering.
Each cluster represents a **distinct sales pattern**.
""")

# -----------------------------
# KPI Row
# -----------------------------
col1, col2, col3 = st.columns(3)

col1.metric("Total SKUs", df_f['ITEM CODE'].nunique())
col2.metric("Avg Retail Sales", round(df_f['RETAIL SALES'].mean(), 2))
col3.metric("Avg Warehouse Sales", round(df_f['WAREHOUSE SALES'].mean(), 2))

# -----------------------------
# Cluster info
# -----------------------------

cluster_text = {
    "Low Volume – Stable Retail": [
        "These items sell slowly and in small quantities.",
        "Orders are infrequent and low value.",
        "Mainly kept to complete the product range."
    ],

    "Low Volume – Warehouse Lean": [
        "These items sell in slightly bigger batches, but still not often.",
        "Orders come less frequently.",
        "When they come, they are more warehouse-driven.",
        "Often used by specific customers."
    ],

    "Low Volume – Mixed Channel": [
        "These items sell regularly, but in small amounts.",
        "Sales are balanced between retail and warehouse.",
        "Demand is predictable but limited."
    ],

    "Bulk / Institutional High Volume": [
        "These are bulk products sold in very large quantities.",
        "Sales are mainly warehouse-based.",
        "A knowing few items generate extremely high volume.",
        "Commonly purchased by institutional or bulk buyers."
    ],

    "High Performing Core Products": [
        "These items sell frequently and in high volume.",
        "They generate a large share of total revenue.",
        "Critical products that should never go out of stock."
    ]
}

# -----------------------------
# Item Lookup
# -----------------------------
st.subheader("🔎 Item Lookup")

item_code_input = st.text_input(
    "Enter Item Code",
    placeholder="e.g. 100009"
)

if item_code_input:
    item_row = df[df['ITEM CODE'].astype(str) == item_code_input]

    if item_row.empty:
        st.error("Item code not found.")
    else:
        item = item_row.iloc[0]

        st.success("Item found")

        st.markdown(f"""
        **Item Code:** {item['ITEM CODE']}  
        **Description:** {item['ITEM DESCRIPTION']}  
        **Item Type:** {item['ITEM TYPE']}  
        **Cluster:** {item['Clusters']}
        """)

        # Cluster explanation
        st.markdown("### What this means")
        for point in cluster_text.get(item['Clusters'], []):
            st.markdown(f"- {point}")


# -----------------------------
# Cluster Sales Profile
# -----------------------------
st.subheader("Cluster Sales Profile")

cluster_profile = (
    df_f.groupby('Clusters')[['RETAIL SALES', 'WAREHOUSE SALES']]
    .mean()
    .reset_index()
)

fig1 = px.bar(
    cluster_profile,
    x='Clusters',
    y=['RETAIL SALES', 'WAREHOUSE SALES'],
    barmode='group'
)

st.plotly_chart(fig1, use_container_width=True)

# -----------------------------
# Cluster Explanation
# -----------------------------
st.subheader("📌 Cluster Interpretation")


for c in cluster_selected:
    st.markdown(f"### {c}")
    for point in cluster_text.get(c, []):
        st.markdown(f"- {point}")

# -----------------------------
# Item Type Contribution
# -----------------------------
st.subheader("Item Type Contribution per Cluster")

item_mix = (
    df_f.groupby('Clusters')['ITEM TYPE']
    .value_counts(normalize=True)
    .rename('share')
    .reset_index()
)

fig2 = px.bar(
    item_mix,
    x='Clusters',
    y='share',
    color='ITEM TYPE',
    title="Item Type Share",
)

st.plotly_chart(fig2, use_container_width=True)

# -----------------------------
# Monthly Trend
# -----------------------------
st.subheader("Monthly Sales Trend")

monthly = (
    df_f.groupby(['Clusters', 'MONTH'])[['RETAIL SALES', 'WAREHOUSE SALES']]
    .mean()
    .reset_index()
)

# ⬇️ PLACE OPTION 2 HERE
sales_type = st.selectbox(
    "Select Sales Type",
    ['RETAIL SALES', 'WAREHOUSE SALES']
)

fig3 = px.line(
    monthly,
    x='MONTH',
    y=sales_type,
    color='Clusters',
    markers=True
)

st.plotly_chart(fig3, use_container_width=True)
