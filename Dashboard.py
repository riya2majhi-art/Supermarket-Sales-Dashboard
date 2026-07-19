import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Supermarket Insights", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    /* Glowing metric cards */
    div[data-testid="stMetricValue"] { font-size: 32px; color: #00FFCC; font-weight: bold; text-shadow: 0 0 10px rgba(0,255,204,0.3); }
    div[data-testid="stMetricLabel"] { font-size: 14px; color: #8F9CAE; letter-spacing: 1px; }
    div[data-testid="stMetric"] { background-color: #131A2C; border-radius: 12px; padding: 20px; border: 1px solid #1E293B; }

    /* Ensure native scrolling works flawlessly */
    .main .block-container { padding-top: 1.5rem; }
    </style>
""", unsafe_allow_html=True)



@st.cache_data
def load_data():
    try:
        df = pd.read_csv(".venv/surobhi.csv", header=3)
    except FileNotFoundError:
        df = pd.read_csv("surobhi.csv", header=3)
    df.columns = df.columns.str.strip()
    df["Total"] = pd.to_numeric(df["Total"], errors="coerce").fillna(0)
    df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce").fillna(0)
    df["gross income"] = pd.to_numeric(df["gross income"], errors="coerce").fillna(0)
    df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce").fillna(0)
    return df


df = load_data()


if "current_page" not in st.session_state:
    st.session_state.current_page = "📋 Summary"

menu_col1, menu_col2, menu_col3, _ = st.columns([1, 1.2, 1.2, 4])

with menu_col1:
    if st.button("📋 Summary", use_container_width=True,
                 type="primary" if st.session_state.current_page == "📋 Summary" else "secondary"):
        st.session_state.current_page = "📋 Summary"
        st.rerun()

with menu_col2:
    if st.button("🏆 Product Performance", use_container_width=True,
                 type="primary" if st.session_state.current_page == "🏆 Product Performance" else "secondary"):
        st.session_state.current_page = "🏆 Product Performance"
        st.rerun()

with menu_col3:
    if st.button("📍 Regional Analysis", use_container_width=True,
                 type="primary" if st.session_state.current_page == "📍 Regional Analysis" else "secondary"):
        st.session_state.current_page = "📍 Regional Analysis"
        st.rerun()

st.markdown("---")

st.sidebar.header("🎛️ Dashboard Filters")

available_cities = [x for x in df["City"].dropna().unique() if str(x).strip().lower() != 'nan']
available_branches = [x for x in df["Branch"].dropna().unique() if str(x).strip().lower() != 'nan']
available_customers = [x for x in df["Customer_type"].dropna().unique() if str(x).strip().lower() != 'nan']

city_filter = st.sidebar.multiselect("Select Cities", options=available_cities, default=available_cities)
branch_filter = st.sidebar.multiselect("Select Branches", options=available_branches, default=available_branches)
customer_filter = st.sidebar.multiselect("Customer Type", options=available_customers, default=available_customers)

df_filtered = df[
    df["City"].isin(city_filter) &
    df["Branch"].isin(branch_filter) &
    df["Customer_type"].isin(customer_filter)
    ]

if st.session_state.current_page == "📋 Summary":
    st.title("📊 Supermarket Financial Summary")

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.metric(label="TOTAL GROSS REVENUE", value=f"${int(df_filtered['Total'].sum()):,}")
    with kpi2:
        st.metric(label="GROSS INCOME MARGIN", value=f"${int(df_filtered['gross income'].sum()):,}")
    with kpi3:
        st.metric(label="CUSTOMER EXPERIENCE", value=f"{round(df_filtered['Rating'].mean(), 1)} ⭐")
    with kpi4:
        st.metric(label="TRANSACTIONS LOGGED", value=f"{len(df_filtered):,}")

    st.markdown("---")

    col_left, col_right = st.columns(2)
    with col_left:
        product_sales = df_filtered.groupby("Product line")["Total"].sum().reset_index().sort_values(by="Total")
        fig_sales = px.bar(
            product_sales, x="Total", y="Product line", orientation="h",
            title="<b>Revenue by Department</b>", color="Total", color_continuous_scale="Mint", template="plotly_dark"
        )
        fig_sales.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", showlegend=False)
        st.plotly_chart(fig_sales, use_container_width=True)

    with col_right:
        payment_data = df_filtered.groupby("Payment")["Total"].sum().reset_index()
        fig_pie = px.pie(
            payment_data, names="Payment", values="Total", hole=0.4,
            title="<b>Payment Method Share</b>", color_discrete_sequence=["#00FFCC", "#3B82F6", "#EC4899"],
            template="plotly_dark"
        )
        fig_pie.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_pie, use_container_width=True)

elif st.session_state.current_page == "🏆 Product Performance":
    st.title("🏆 Department Rankings & Deep Dive")

    if not df_filtered.empty:
        selected_dept = st.selectbox("Select Department to inspect:", options=df_filtered["Product line"].unique())
        dept_df = df_filtered[df_filtered["Product line"] == selected_dept]

        col1, col2 = st.columns(2)
        with col1:
            fig_qty = px.box(
                dept_df, x="Branch", y="Quantity", title=f"Purchase Volume Distribution ({selected_dept})",
                color="Branch", color_discrete_sequence=["#00FFCC", "#3B82F6", "#EC4899"], template="plotly_dark"
            )
            fig_qty.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_qty, use_container_width=True)

        with col2:
            fig_scatter = px.scatter(
                dept_df, x="Total", y="Rating", color="Customer_type", title="Transaction Value vs. Customer Rating",
                color_discrete_sequence=["#00FFCC", "#EC4899"], template="plotly_dark"
            )
            fig_scatter.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.warning("No data matches the selected filters.")

elif st.session_state.current_page == "📍 Regional Analysis":
    st.title("📍 Branch & Location Matrix")

    # Clean data structure specifically for the sunburst chart to remove blanks/None
    sunburst_cols = ["Branch", "City", "Customer_type", "Total"]
    df_sunburst = df_filtered[sunburst_cols].dropna()

    # FIXED: Added correct .str accessor syntax for Pandas Series string manipulation
    for col in ["Branch", "City", "Customer_type"]:
        df_sunburst[col] = df_sunburst[col].astype(str).str.strip()
        df_sunburst = df_sunburst[(df_sunburst[col] != "") & (df_sunburst[col].str.lower() != "none") & (
                    df_sunburst[col].str.lower() != "nan")]

    if not df_sunburst.empty:
        fig_sunburst = px.sunburst(
            df_sunburst, path=["Branch", "City", "Customer_type"], values="Total",
            title="Multi-Level Sales Contribution Matrix", color="Total", color_continuous_scale="Tealgrn",
            template="plotly_dark"
        )
        fig_sunburst.update_layout(paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_sunburst, use_container_width=True)
    else:
        st.warning("No valid data available to build the regional hierarchy tree.")

    st.markdown("---")
    st.markdown("### Raw Regional Performance View Data")
    st.dataframe(df_filtered[["Invoice ID", "Branch", "City", "Customer_type", "Gender", "Total"]],
                 use_container_width=True)