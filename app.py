from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(page_title="Commerce | EDA", page_icon="◈", layout="wide")

COLORS = ["#56D6B2", "#7C83FD", "#FFB86B", "#FF718B", "#72B7F2", "#B991F7"]
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
REQUIRED = {"Year", "Month", "Category", "Region", "Units_Sold", "Revenue", "Profit", "Customer_Rating", "Ad_Spend"}

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;600;700&display=swap');
.stApp { background:#0b0e14; color:#edf1f7; font-family:'DM Sans',sans-serif; }
[data-testid="stSidebar"] { background:#10141c; border-right:1px solid #222936; }
[data-testid="stMetric"] { background:#121822; border:1px solid #242d3b; border-radius:12px; padding:16px 18px; }
[data-testid="stMetricLabel"] { color:#929daf; font-size:12px; }
[data-testid="stMetricValue"] { color:#f2f5fa; font-family:'DM Mono',monospace; font-size:25px; }
.hero { padding:8px 0 16px; }
.eyebrow { color:#56d6b2; letter-spacing:2px; font:500 11px 'DM Mono',monospace; text-transform:uppercase; }
.hero h1 { font-size:34px; letter-spacing:-1.4px; margin:5px 0 2px; color:#f3f5f8; }
.hero p { margin:0; color:#929daf; font-size:14px; }
.section-title { color:#ecf0f6; font-size:17px; font-weight:600; margin:12px 0 0; }
.section-note { color:#8490a2; font-size:12px; margin:2px 0 9px; }
div[data-testid="stPlotlyChart"] { border:1px solid #202938; border-radius:12px; background:#10151e; padding:7px 7px 0; }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def read_csv(data: bytes) -> pd.DataFrame:
    return pd.read_csv(pd.io.common.BytesIO(data))


def money(value, compact=False):
    if compact and abs(value) >= 1_000_000:
        return f"${value / 1_000_000:,.2f}M"
    if compact and abs(value) >= 1_000:
        return f"${value / 1_000:,.1f}K"
    return f"${value:,.0f}"


def card_title(title, note):
    st.markdown(f'<div class="section-title">{title}</div><div class="section-note">{note}</div>', unsafe_allow_html=True)


def style(fig, height=340):
    fig.update_layout(
        height=height, paper_bgcolor="#10151e", plot_bgcolor="#10151e",
        font=dict(family="DM Sans, sans-serif", color="#d9e0ea", size=11),
        margin=dict(l=18, r=18, t=28, b=18),
        legend=dict(bgcolor="rgba(0,0,0,0)", orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hoverlabel=dict(bgcolor="#1a2230", bordercolor="#344052", font_color="#f4f6fa"),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor="#293241", tickfont_color="#9da8b8")
    fig.update_yaxes(showgrid=True, gridcolor="#202936", zeroline=False, linecolor="#293241", tickfont_color="#9da8b8")
    return fig


st.sidebar.markdown("### ◈  COMMERCE / EDA")
st.sidebar.caption("Explore the sales dataset")
upload = st.sidebar.file_uploader("Upload ecommerce_sales_data.csv", type=["csv"])
default_file = Path(__file__).parent / "ecommerce_sales_data.csv"

try:
    if upload:
        original = read_csv(upload.getvalue())
        data_label = upload.name
    elif default_file.exists():
        original = read_csv(default_file.read_bytes())
        data_label = default_file.name
    else:
        st.markdown('<div class="hero"><div class="eyebrow">SALES INTELLIGENCE · 2020—2024</div><h1>Commerce overview</h1><p>Interactive exploration of revenue, profit, customer ratings, and ad spend.</p></div>', unsafe_allow_html=True)
        st.info("Upload the `ecommerce_sales_data.csv` file from the notebook to open the dashboard. The notebook itself contains EDA results, but not the source CSV.")
        st.stop()
except Exception as exc:
    st.error(f"Could not read the CSV: {exc}")
    st.stop()

missing = REQUIRED - set(original.columns)
if missing:
    st.error("This file is missing required columns: " + ", ".join(sorted(missing)))
    st.stop()

df = original.copy()
for col in ["Year", "Units_Sold", "Revenue", "Profit", "Customer_Rating", "Ad_Spend"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")
df["Month"] = df["Month"].astype(str).str.strip().str.title()
df["Category"] = df["Category"].astype(str).str.strip()
df["Region"] = df["Region"].astype(str).str.strip()
df = df.dropna(subset=list(REQUIRED)).copy()
df["Year"] = df["Year"].astype(int)
df["Date"] = pd.to_datetime(df["Year"].astype(str) + "-" + df["Month"], format="%Y-%B", errors="coerce")
df = df.dropna(subset=["Date"])
df["Profit_Margin"] = df["Profit"].div(df["Revenue"].where(df["Revenue"].ne(0))).mul(100)

st.markdown(f'<div class="hero"><div class="eyebrow">SALES INTELLIGENCE · {df.Year.min()}—{df.Year.max()}</div><h1>Commerce overview</h1><p>Revenue, profit, customer experience, and marketing performance <span style="color:#56d6b2">/</span> {data_label}</p></div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("---")
    years = sorted(df.Year.unique())
    selected_years = st.multiselect("Year", years, default=years)
    categories = sorted(df.Category.unique())
    selected_categories = st.multiselect("Category", categories, default=categories)
    regions = sorted(df.Region.unique())
    selected_regions = st.multiselect("Region", regions, default=regions)
    st.markdown("---")
    st.caption(f"{len(df):,} valid records · {df.Date.min():%b %Y} – {df.Date.max():%b %Y}")

view = df[df.Year.isin(selected_years) & df.Category.isin(selected_categories) & df.Region.isin(selected_regions)].copy()
if view.empty:
    st.warning("No records match these filters. Select at least one year, category, and region.")
    st.stop()

revenue = view.Revenue.sum()
profit = view.Profit.sum()
margin = profit / revenue * 100 if revenue else 0
ad_return = profit / view.Ad_Spend.sum() if view.Ad_Spend.sum() else 0

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("TOTAL REVENUE", money(revenue, True), f"{len(view):,} records")
k2.metric("TOTAL PROFIT", money(profit, True), f"{margin:.1f}% margin")
k3.metric("UNITS SOLD", f"{view.Units_Sold.sum():,.0f}", f"{view.Units_Sold.mean():.0f} / record")
k4.metric("AVG. RATING", f"{view.Customer_Rating.mean():.2f} / 5", f"{(view.Customer_Rating >= 4).mean():.0%} rated 4+")
k5.metric("PROFIT / AD $", f"${ad_return:.2f}", "descriptive ratio")

st.markdown("")
left, right = st.columns([1.65, 1])
with left:
    card_title("Revenue over time", "Monthly totals · hover for exact values · click legend to isolate a year")
    monthly = view.groupby(["Date", "Year"], as_index=False).agg(Revenue=("Revenue", "sum"), Profit=("Profit", "sum"))
    fig = px.line(monthly, x="Date", y="Revenue", color="Year", markers=True, color_discrete_sequence=COLORS,
                  hover_data={"Revenue": ":$,.0f", "Profit": ":$,.0f", "Date": "%b %Y"})
    fig.update_traces(line=dict(width=2.5), marker=dict(size=5))
    fig.update_layout(yaxis_title="Revenue ($)", xaxis_title=None, hovermode="x unified")
    st.plotly_chart(style(fig), use_container_width=True, config={"displayModeBar": False})
with right:
    card_title("Revenue by category", "Ranked total revenue · filtered selection")
    cat = view.groupby("Category", as_index=False).agg(Revenue=("Revenue", "sum"), Profit=("Profit", "sum"), Units=("Units_Sold", "sum"))
    cat = cat.sort_values("Revenue")
    fig = px.bar(cat, x="Revenue", y="Category", orientation="h", color="Revenue", color_continuous_scale=["#284a56", "#56d6b2"],
                 hover_data={"Revenue": ":$,.0f", "Profit": ":$,.0f", "Units": ":,.0f"})
    fig.update_layout(xaxis_title="Revenue ($)", yaxis_title=None, coloraxis_showscale=False)
    st.plotly_chart(style(fig), use_container_width=True, config={"displayModeBar": False})

left, right = st.columns(2)
with left:
    card_title("Regional performance", "Compare revenue across categories and regions")
    region_cat = view.groupby(["Category", "Region"], as_index=False).agg(Revenue=("Revenue", "sum"), Profit=("Profit", "sum"))
    fig = px.bar(region_cat, x="Category", y="Revenue", color="Region", barmode="group", color_discrete_sequence=COLORS,
                 hover_data={"Revenue": ":$,.0f", "Profit": ":$,.0f"})
    fig.update_layout(xaxis_title=None, yaxis_title="Revenue ($)")
    fig.update_xaxes(tickangle=-25)
    st.plotly_chart(style(fig), use_container_width=True, config={"displayModeBar": False})
with right:
    card_title("Profitability by category", "Revenue-weighted margin alongside profit contribution")
    cat_margin = view.groupby("Category", as_index=False).agg(Revenue=("Revenue", "sum"), Profit=("Profit", "sum"))
    cat_margin["Margin"] = cat_margin.Profit.div(cat_margin.Revenue.where(cat_margin.Revenue.ne(0))).mul(100)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=cat_margin.Category, y=cat_margin.Profit, name="Profit ($)", marker_color="#7c83fd", yaxis="y",
                         hovertemplate="%{x}<br>Profit: $%{y:,.0f}<extra></extra>"))
    fig.add_trace(go.Scatter(x=cat_margin.Category, y=cat_margin.Margin, name="Margin (%)", mode="lines+markers", line=dict(color="#56d6b2", width=3), yaxis="y2",
                             hovertemplate="%{x}<br>Margin: %{y:.1f}%<extra></extra>"))
    fig.update_layout(xaxis_title=None, yaxis=dict(title="Profit ($)", showgrid=True, gridcolor="#202936"),
                      yaxis2=dict(title="Margin (%)", overlaying="y", side="right", showgrid=False), legend=dict(orientation="h", y=1.12))
    fig.update_xaxes(tickangle=-25)
    st.plotly_chart(style(fig), use_container_width=True, config={"displayModeBar": False})

left, right = st.columns(2)
with left:
    card_title("Ad spend & profit", "Each point is a record · color = category · size = revenue")
    fig = px.scatter(view, x="Ad_Spend", y="Profit", color="Category", size="Revenue", size_max=22,
                     color_discrete_sequence=COLORS, opacity=0.76,
                     hover_data={"Year": True, "Region": True, "Revenue": ":$,.0f", "Ad_Spend": ":$,.0f", "Profit": ":$,.0f", "Customer_Rating": ":.1f"})
    fig.update_layout(xaxis_title="Ad spend ($)", yaxis_title="Profit ($)")
    st.plotly_chart(style(fig), use_container_width=True, config={"displayModeBar": False})
with right:
    card_title("Customer ratings", "Rating distribution by category · box shows median and middle 50%")
    fig = px.box(view, x="Category", y="Customer_Rating", color="Category", points="outliers", color_discrete_sequence=COLORS,
                 hover_data=["Region", "Year"])
    fig.update_layout(xaxis_title=None, yaxis_title="Rating (1–5)", showlegend=False)
    fig.update_xaxes(tickangle=-25)
    st.plotly_chart(style(fig), use_container_width=True, config={"displayModeBar": False})

top = view.groupby("Category").agg(Revenue=("Revenue", "sum"), Profit=("Profit", "sum"), Rating=("Customer_Rating", "mean"), Ad_Spend=("Ad_Spend", "sum"))
if len(top):
    best_revenue = top.Revenue.idxmax()
    best_margin = (top.Profit / top.Revenue.replace(0, float("nan"))).idxmax()
    best_rating = top.Rating.idxmax()
    st.markdown(f"**In this selection:** {best_revenue} leads revenue at {money(top.loc[best_revenue, 'Revenue'], True)}. {best_margin} has the highest revenue-weighted margin ({top.loc[best_margin, 'Profit'] / top.loc[best_margin, 'Revenue']:.1%}), while {best_rating} has the highest average rating ({top.loc[best_rating, 'Rating']:.2f}/5).")

with st.expander("Explore records and data quality", expanded=False):
    m1, m2, m3 = st.columns(3)
    m1.metric("Rows shown", f"{len(view):,}")
    m2.metric("Missing cells in source", f"{int(original.isna().sum().sum()):,}")
    m3.metric("Duplicate rows in source", f"{int(original.duplicated().sum()):,}")
    st.dataframe(view.drop(columns=["Date"]), use_container_width=True, hide_index=True)
    st.download_button("Download filtered data", view.drop(columns=["Date"]).to_csv(index=False).encode("utf-8"), "filtered_sales.csv", "text/csv")

st.caption("Profit per ad dollar is total profit divided by total ad spend; it is a descriptive ratio, not an attribution estimate. Profit margin uses total profit ÷ total revenue.")
