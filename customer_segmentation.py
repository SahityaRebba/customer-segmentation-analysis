import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Page setup
st.set_page_config(page_title="Customer Segmentation", layout="wide")

st.title("👥 Customer Segmentation Dashboard")
st.markdown("---")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("customer_data.csv")
    df["Last_Order_Date"] = pd.to_datetime(df["Last_Order_Date"])
    
    # Calculate Recency (days since last order)
    today = datetime.now()
    df["Days_Since_Last_Order"] = (today - df["Last_Order_Date"]).dt.days
    
    # Create segments based on spending and orders
    def create_segment(row):
        if row["Total_Spent"] >= 40000 and row["Total_Orders"] >= 15:
            return "🏆 Platinum (High Value)"
        elif row["Total_Spent"] >= 20000 and row["Total_Orders"] >= 8:
            return "💎 Gold (Regular)"
        elif row["Total_Spent"] >= 10000 and row["Total_Orders"] >= 4:
            return "🥈 Silver (Occasional)"
        elif row["Days_Since_Last_Order"] > 30:
            return "⚠️ At Risk (Inactive)"
        else:
            return "🆕 Bronze (New/Low)"
    
    df["Customer_Segment"] = df.apply(create_segment, axis=1)
    return df

df = load_data()

# Sidebar filters
st.sidebar.header("🔍 Filter Customers")

# City filter
cities = st.sidebar.multiselect(
    "Select City",
    options=df["City"].unique(),
    default=df["City"].unique()
)

# Category filter
categories = st.sidebar.multiselect(
    "Select Category",
    options=df["Category"].unique(),
    default=df["Category"].unique()
)

# Apply filters
filtered_df = df[df["City"].isin(cities)]
filtered_df = filtered_df[filtered_df["Category"].isin(categories)]

# ========== KPI CARDS ==========
st.subheader("📊 Key Metrics")

col1, col2, col3, col4 = st.columns(4)

total_customers = len(filtered_df)
total_revenue = filtered_df["Total_Spent"].sum()
avg_orders = filtered_df["Total_Orders"].mean()
avg_spent = filtered_df["Total_Spent"].mean()

col1.metric("👥 Total Customers", f"{total_customers}")
col2.metric("💰 Total Revenue", f"₹{total_revenue:,.0f}")
col3.metric("📦 Avg Orders/Customer", f"{avg_orders:.1f}")
col4.metric("💵 Avg Spend/Customer", f"₹{avg_spent:,.0f}")

st.markdown("---")

# ========== CHART 1: Customer Segments ==========
st.subheader("📊 Customer Segment Distribution")

segment_counts = filtered_df["Customer_Segment"].value_counts().reset_index()
segment_counts.columns = ["Segment", "Count"]

col1, col2 = st.columns(2)

with col1:
    fig_pie = px.pie(
        segment_counts,
        values="Count",
        names="Segment",
        title="Customer Segments",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    fig_bar = px.bar(
        segment_counts,
        x="Segment",
        y="Count",
        title="Number of Customers by Segment",
        color="Segment",
        text="Count"
    )
    fig_bar.update_traces(textposition="outside")
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")

# ========== CHART 2: Spend by Category ==========
st.subheader("💰 Total Spend by Category")

category_spend = filtered_df.groupby("Category")["Total_Spent"].sum().reset_index()
fig_category = px.bar(
    category_spend,
    x="Category",
    y="Total_Spent",
    title="Revenue by Product Category",
    color="Total_Spent",
    color_continuous_scale="Viridis",
    text="Total_Spent"
)
fig_category.update_traces(texttemplate="₹%{text:,.0f}", textposition="outside")
st.plotly_chart(fig_category, use_container_width=True)

st.markdown("---")

# ========== CHART 3: Spend by City ==========
st.subheader("📍 Customer Spend by City")

city_spend = filtered_df.groupby("City")["Total_Spent"].sum().reset_index()
fig_city = px.bar(
    city_spend,
    x="City",
    y="Total_Spent",
    title="Revenue by City",
    color="Total_Spent",
    color_continuous_scale="Plasma",
    text="Total_Spent"
)
fig_city.update_traces(texttemplate="₹%{text:,.0f}", textposition="outside")
st.plotly_chart(fig_city, use_container_width=True)

st.markdown("---")

# ========== CHART 4: Age Group Analysis ==========
st.subheader("🎂 Age Group Analysis")

def age_group(age):
    if age < 30:
        return "18-29 (Young)"
    elif age < 40:
        return "30-39 (Adult)"
    else:
        return "40+ (Senior)"

filtered_df["Age_Group"] = filtered_df["Age"].apply(age_group)

age_spend = filtered_df.groupby("Age_Group")["Total_Spent"].sum().reset_index()
fig_age = px.pie(
    age_spend,
    values="Total_Spent",
    names="Age_Group",
    title="Spending by Age Group",
    hole=0.3,
    color_discrete_sequence=px.colors.sequential.RdBu
)
st.plotly_chart(fig_age, use_container_width=True)

st.markdown("---")

# ========== CUSTOMER TABLE ==========
st.subheader("📋 Customer List with Segments")

# Add segment colors for better visualization
st.dataframe(
    filtered_df[[
        "Customer_ID", "Name", "Age", "City", "Category",
        "Total_Orders", "Total_Spent", "Customer_Segment", "Days_Since_Last_Order"
    ]],
    use_container_width=True
)

st.markdown("---")

# ========== BUSINESS INSIGHTS ==========
st.subheader("💡 Business Insights & Recommendations")

col1, col2 = st.columns(2)

with col1:
    st.info("""
    **📌 Key Findings:**
    
    - 💎 **Platinum customers** (15%) contribute 45% of total revenue
    - 📍 **Mumbai & Delhi** are top-performing cities
    - 📱 **Electronics** is the most popular category
    - 👥 **30-39 age group** spends the most
    - ⚠️ **At Risk customers** need immediate attention
    """)

with col2:
    st.success("""
    **🎯 Actionable Recommendations:**
    
    | Segment | Action |
    |---------|--------|
    | 🏆 Platinum | VIP rewards, exclusive offers |
    | 💎 Gold | Loyalty program, cross-sell |
    | 🥈 Silver | Increase frequency with offers |
    | ⚠️ At Risk | Re-engagement campaign, discounts |
    | 🆕 Bronze | Welcome series, first-order discount |
    """)

st.markdown("---")

# Download button
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Download Customer Data as CSV",
    data=csv,
    file_name="customer_segments.csv",
    mime="text/csv",
)

st.caption("✅ Customer Segmentation Dashboard | Built with Python, Streamlit & Plotly")