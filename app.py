import pandas as pd 
import seaborn as sns 
import matplotlib.pyplot as plt
import streamlit as st
@st.cache_data
def load_data():
    raw_data = pd.read_csv('sales_data.csv')
    df =pd.DataFrame({
        "sales_id": pd.to_numeric(raw_data['SaleID'], errors='coerce'),
        "date": pd.to_datetime(raw_data['Date'], errors='coerce'),
        "product": raw_data['Product'].astype(str),
        "quantity": pd.to_numeric(raw_data['Quantity'], errors='coerce'),
        "price": pd.to_numeric(raw_data['Price'], errors='coerce'),
        "total": pd.to_numeric(raw_data['Total'], errors='coerce'),
        "region": raw_data['Region']
        })
    return df
df =load_data()

# check_empty_data  =df.isnull().sum()
# count_unknown =(df["region"] =="Unknown").sum()
df["region"] =df["region"].fillna(value="unknown").astype(str)

#=========

st.title("Sales Analysis Dashboard")
st.header("Sales Data Overview")
st.write("This dashboard provides insights into sales data, including total revenue by product, monthly sales trends, and average sales per product.")

#filter 
st.sidebar.header("filter bar")
select_region =st.sidebar.multiselect(
    "select region",
    options =df["region"].unique(),
    default =df["region"].unique())
filter_df = df[df["region"].notna() & df["region"].isin(select_region)]
product_revenue =filter_df.groupby('product')['total'].sum().reset_index().sort_values(by='total', ascending=False)
regional_sales = filter_df.groupby('region')['total'].sum().reset_index().sort_values(by='total', ascending=False)
filter_df["month"]  =filter_df["date"].dt.to_period('M').astype(str)
monthly_sales = filter_df.groupby('month')['total'].sum().reset_index()
monthly_sales["month"] = pd.to_datetime(
    monthly_sales["month"],
    format="%Y-%m"
)

monthly_sales = monthly_sales.sort_values("month")

st.subheader("Key Metrics")
col1, col2 = st.columns(2)
with col1:
    st.metric(label="Total Sales", value=f"${filter_df['total'].sum():,.2f}")
with col2:
    average_sales =filter_df.groupby("product")["total"].sum().mean()
    st.metric(label="Average Sales per Product", value=f"${average_sales:,.2f}")

#chart description 
def chart_description(df, value_col, category_col):
    total = df[value_col].sum()
    top = df.loc[df[value_col].idxmax()]
    bottom = df.loc[df[value_col].idxmin()]
    mean_v = df[value_col].mean()
    max_v = df[value_col].max()
    min_v = df[value_col].min()

    description = f"""
📊 Chart Description

- Total: {total:,.2f}
- Top {category_col}: {top[category_col]} ({top[value_col]:,.2f})
- Bottom {category_col}: {bottom[category_col]} ({bottom[value_col]:,.2f})
- Mean: {mean_v:,.2f}
- Max: {max_v:,.2f}
- Min: {min_v:,.2f}
"""

    return description




st.header("Total Revenue by Product")
fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(
    x='total', 
    y='product', 
    data= product_revenue)
ax.set_title("Total Revenue by Product")
st.pyplot(fig)
st.write(chart_description(product_revenue, "total", "product"))

st.divider()

st.subheader("Sales by region")
fig1, ax1 = plt.subplots(figsize=(8, 8))
ax1.pie(
regional_sales['total'], 
    labels=regional_sales['region'], 
        autopct='%1.1f%%', 
        startangle=90)
ax1.set_title("Sales Distribution by Region")
st.pyplot(fig1)

st.divider()

st.subheader("Monthly Sales Trends")

fig2, ax2 = plt.subplots(figsize=(10, 6))
sns.lineplot(
    data=monthly_sales,
    x="month", 
    y ="total", 
    marker='o')
ax2.set_title("Monthly Sales Trends")
ax2.set_xlabel("Month")
ax2.set_ylabel("Total Sales")
st.pyplot(fig2)

st.subheader("raw data table")

st.write("This table displays the raw sales data used for analysis. You can explore the individual sales records, including product details, quantities, prices, and regions.")

st.dataframe(df)
