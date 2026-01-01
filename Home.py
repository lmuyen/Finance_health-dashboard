# ============================================================
# PAGE 1 – TỔNG QUAN THỊ TRƯỜNG | NHÀ ĐẦU TƯ MỚI
# Full Layer 0 → 7 | Academic Dark Finance Dashboard
# ============================================================

# =======================
# LAYER 0 – CONFIG + CSS
# =======================
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(
    page_title="Tổng quan thị trường – Nhà đầu tư mới",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.markdown("""
<style>
body { background-color:#0b1220; color:#ffffff; }
.block-container { padding-top:1.2rem; }

.title { font-size:32px; font-weight:800; color:#ffffff; }
.subtitle { color:#ffffff; margin-bottom:20px; font-size:14px; }

.section { font-size:20px; font-weight:700; margin-top:32px; margin-bottom:12px; color:#ffffff; }

.card {
    background:#1f2a3d;
    border:1px solid #2a3a52;
    border-radius:16px;
    padding:18px;
    color:#ffffff;
}

.card-white {
    background:#1f2a3d;
    color:#ffffff;
    border-radius:16px;
    padding:22px;
    box-shadow:0 10px 24px rgba(0,0,0,.25);
    margin-bottom:20px;
}

.card-title { font-size:13px; color:#ffffff; margin-bottom:8px; }
.card-value { font-size:26px; font-weight:800; color:#ffffff; }

.green { color:#10b981; }
.yellow { color:#f59e0b; }
.red { color:#ef4444; }

.info-label { font-weight:600; color:#ffffff; margin-top:12px; }
.info-value { color:#ffffff; margin-left:8px; }
</style>
""", unsafe_allow_html=True)

# =======================
# LAYER 1 – LOAD DATA
# =======================
@st.cache_data
def load_data():
    """Load all required data files"""
    try:
        # Try loading from root directory first
        df_health = pd.read_excel("Data_health_score_dashboard.xlsx")
        df_flow = pd.read_excel("data_dau_tu.xlsx")
        df_price = pd.read_excel("Price_2124.xlsx")
        df_mcap = pd.read_excel("Marketcap_2124.xlsx")
        df_volume = pd.read_excel("Volume_2124.xlsx")
    except FileNotFoundError:
        # Try loading from Data dash folder
        try:
            data_dir = Path("Data dash")
            df_health = pd.read_excel(data_dir / "Data_health_score_dashboard.xlsx")
            df_flow = pd.read_excel(data_dir / "data_dau_tu.xlsx")
            df_price = pd.read_excel("Price_2124.xlsx")
            df_mcap = pd.read_excel("Marketcap_2124.xlsx")
            df_volume = pd.read_excel(data_dir / "Volume_2124.xlsx")
        except FileNotFoundError:
            # Try from DATA folder
            data_dir = Path("DATA")
            df_health = pd.read_excel(data_dir / "Data_health_score_dashboard.xlsx")
            df_flow = pd.read_excel(data_dir / "data_dau_tu.xlsx")
            df_price = pd.read_excel(data_dir / "Price_2124.xlsx")
            df_mcap = pd.read_excel(data_dir / "Marketcap_2124.xlsx")
            df_volume = pd.read_excel(data_dir / "Volume_2124.xlsx")
    
    return df_health, df_flow, df_price, df_mcap, df_volume

try:
    df_health, df_flow, df_price, df_mcap, df_volume = load_data()
except Exception as e:
    st.error(f"Lỗi khi tải dữ liệu: {str(e)}")
    st.stop()

# =======================
# LAYER 2 – CHUẨN HÓA & XỬ LÝ
# =======================
@st.cache_data
def process_data(df_health, df_flow, df_price, df_mcap, df_volume):
    """Process and merge all data"""
    # Make copies to avoid modifying cached data
    df_health = df_health.copy()
    df_flow = df_flow.copy()
    df_price = df_price.copy()
    df_mcap = df_mcap.copy()
    df_volume = df_volume.copy()
    
    # Clean column names
    for df in [df_health, df_flow, df_price, df_mcap, df_volume]:
        df.columns = df.columns.str.strip()

    # Rename columns to standard format
    df_health = df_health.rename(columns={"Mã":"Ticker", "Năm":"Year"})
    df_flow = df_flow.rename(columns={"Mã":"Ticker", "Năm":"Year"})
    df_price = df_price.rename(columns={"Mã":"Ticker", "Ngày":"Date", "Giá":"Price"})
    df_mcap = df_mcap.rename(columns={"Mã":"Ticker", "Ngày":"Date"})
    df_volume = df_volume.rename(columns={"Mã":"Ticker", "Ngày":"Date", "Khối lượng":"Volume"})

    # Convert dates
    df_price["Date"] = pd.to_datetime(df_price["Date"], errors='coerce')
    df_mcap["Date"] = pd.to_datetime(df_mcap["Date"], errors='coerce')
    df_volume["Date"] = pd.to_datetime(df_volume["Date"], errors='coerce')

    df_price["Year"] = df_price["Date"].dt.year
    df_mcap["Year"] = df_mcap["Date"].dt.year
    df_volume["Year"] = df_volume["Date"].dt.year

    # Aggregate to year level for market KPIs
    price_year = (
        df_price.groupby(["Ticker", "Year"])
        .agg(
            Avg_Price=("Price", "mean"),
            Max_Price=("Price", "max"),
            Min_Price=("Price", "min")
        ).reset_index()
    )

    mcap_year = (
        df_mcap.groupby(["Ticker", "Year"])["MarketCap"]
        .mean().reset_index(name="Avg_MarketCap")
    )

    # Master table
    df = (
        df_health
        .merge(df_flow, on=["Ticker", "Year"], how="left")
        .merge(price_year, on=["Ticker", "Year"], how="left")
        .merge(mcap_year, on=["Ticker", "Year"], how="left")
    )

    # Clean industry column
    df["Ngành"] = df["Ngành"].astype(str)
    df.loc[df["Ngành"].isin(["nan", "None", "None"]), "Ngành"] = np.nan
    
    return df, df_price, df_mcap, df_volume

# Process data
df, df_price, df_mcap, df_volume = process_data(df_health, df_flow, df_price, df_mcap, df_volume)

# =======================
# LAYER 3 – SIDEBAR FILTER
# =======================
st.sidebar.header("Bộ lọc thị trường")

year = st.sidebar.selectbox(
    "Năm",
    sorted(df["Year"].dropna().unique()),
    index=len(sorted(df["Year"].dropna().unique())) - 1 if len(sorted(df["Year"].dropna().unique())) > 0 else 0
)

industry_options = sorted(df["Ngành"].dropna().unique())
industry = st.sidebar.multiselect(
    "Ngành",
    industry_options,
    default=industry_options[:min(10, len(industry_options))] if len(industry_options) > 0 else []
)

rating_options = sorted(df["Credit_Rating_Z"].dropna().unique())
rating = st.sidebar.multiselect(
    "Xếp hạng tín nhiệm",
    rating_options,
    default=rating_options
)

flow_map = {"Mua ròng": 1, "Bán ròng": 0}
flow_choice = st.sidebar.multiselect(
    "Trạng thái dòng tiền",
    ["Mua ròng", "Bán ròng"],
    default=["Mua ròng", "Bán ròng"]
)
flow_flag = [flow_map[x] for x in flow_choice]

top_n = st.sidebar.slider(
    "Top N doanh nghiệp theo Health Score",
    min_value=0,
    max_value=30,
    value=0
)

# Apply filters
dff = df[
    (df["Year"] == year) &
    (df["Ngành"].isin(industry) if len(industry) > 0 else True) &
    (df["Credit_Rating_Z"].isin(rating) if len(rating) > 0 else True) &
    (df["Buy_Net_Flag"].isin(flow_flag) if "Buy_Net_Flag" in df.columns else True)
]

# =======================
# LAYER 4 – HEADER
# =======================
st.markdown("<h1 style='text-align: center; background-color: #ffffff; color: #0f172a; font-size: 48px; font-weight: 800; margin-bottom: 20px; margin-top: 10px; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>TỔNG QUAN THỊ TRƯỜNG</h1>", unsafe_allow_html=True)
st.markdown("<div class='subtitle' style='text-align: center;'>Dashboard hỗ trợ nhà đầu tư mới | Dữ liệu 2021–2024</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# =======================
# LAYER 5 – KPI MARKET LEVEL
# =======================
st.markdown("<div class='section' style='color:#000;'>Tổng quan thị trường</div>", unsafe_allow_html=True)


# Row 1: Health KPIs
k1, k2, k3, k4 = st.columns(4)

num_companies = dff['Ticker'].nunique()
k1.markdown(
    f"<div class='card'><div class='card-title'>Số doanh nghiệp</div><div class='card-value'>{num_companies:,}</div></div>",
    unsafe_allow_html=True
)

avg_health = dff['Health_Score'].mean() if 'Health_Score' in dff.columns else 0
k2.markdown(
    f"<div class='card'><div class='card-title'>Điểm sức khỏe TB</div><div class='card-value green'>{avg_health:.1f} / 100</div></div>",
    unsafe_allow_html=True
)

safe_pct = (dff["Credit_Rating_Z"].isin(["AAA", "AA", "A"]).mean() * 100) if "Credit_Rating_Z" in dff.columns else 0
k3.markdown(
    f"<div class='card'><div class='card-title'>DN an toàn (%)</div><div class='card-value green'>{safe_pct:.1f}%</div></div>",
    unsafe_allow_html=True
)

buy_pct = (dff["Buy_Net_Flag"].mean() * 100) if "Buy_Net_Flag" in dff.columns else 0
k4.markdown(
    f"<div class='card'><div class='card-title'>DN mua ròng (%)</div><div class='card-value yellow'>{buy_pct:.1f}%</div></div>",
    unsafe_allow_html=True
)

# Thêm khoảng cách giữa 2 hàng KPI
st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

# Row 2: Price & Market Cap KPIs
k5, k6, k7, k8 = st.columns(4)

total_mcap = dff['Avg_MarketCap'].sum() / 1e9 if 'Avg_MarketCap' in dff.columns else 0
k5.markdown(
    f"<div class='card'><div class='card-title'>Tổng vốn hóa TB</div><div class='card-value green'>{total_mcap:,.0f} Tỷ</div></div>",
    unsafe_allow_html=True
)

avg_price = dff['Avg_Price'].mean() if 'Avg_Price' in dff.columns else 0
k6.markdown(
    f"<div class='card'><div class='card-title'>Giá CP TB</div><div class='card-value'>{avg_price:,.0f} VND</div></div>",
    unsafe_allow_html=True
)

max_price = dff['Max_Price'].max() if 'Max_Price' in dff.columns else 0
k7.markdown(
    f"<div class='card'><div class='card-title'>Giá cao nhất</div><div class='card-value green'>{max_price:,.0f} VND</div></div>",
    unsafe_allow_html=True
)

min_price = dff['Min_Price'].min() if 'Min_Price' in dff.columns else 0
k8.markdown(
    f"<div class='card'><div class='card-title'>Giá thấp nhất</div><div class='card-value red'>{min_price:,.0f} VND</div></div>",
    unsafe_allow_html=True
)

# =======================
# LAYER 6 – MARKET INSIGHT
# =======================
st.markdown("<div class='section'>Market Insight</div>", unsafe_allow_html=True)

c1, c2 = st.columns(2)

# Chart 1: Số DN theo mức tín nhiệm
if "Credit_Rating_Z" in dff.columns:
    rating_count = (
        dff["Credit_Rating_Z"]
        .value_counts()
        .reset_index()
    )
    # Fix column names - after reset_index, first col is the rating, second is count
    rating_count.columns = ["Xếp hạng tín nhiệm", "Số doanh nghiệp"]
    
    fig_rating = px.bar(
        rating_count,
        x="Xếp hạng tín nhiệm",
        y="Số doanh nghiệp",
        title="Số doanh nghiệp theo mức tín nhiệm",
        color="Xếp hạng tín nhiệm",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig_rating.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#e5e7eb'
    )
    c1.plotly_chart(fig_rating, use_container_width=True)

# Chart 2: Sức khỏe tài chính theo ngành
if "Health_Score" in dff.columns and "Ngành" in dff.columns:
    health_by_industry = (
        dff.groupby("Ngành")["Health_Score"]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
    )
    
    fig_ind = px.bar(
        health_by_industry,
        x="Health_Score",
        y="Ngành",
        orientation="h",
        title="Sức khỏe tài chính trung bình theo ngành",
        color="Health_Score",
        color_continuous_scale="Viridis"
    )
    fig_ind.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#e5e7eb'
    )
    c2.plotly_chart(fig_ind, use_container_width=True)

# Chart 3: Boxplot phân bố điểm sức khỏe theo ngành
if "Health_Score" in dff.columns and "Ngành" in dff.columns:
    fig_box = px.box(
        dff,
        x="Ngành",
        y="Health_Score",
        title="Phân bố điểm sức khỏe theo ngành"
    )
    fig_box.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#e5e7eb',
        xaxis_tickangle=-45
    )
    st.plotly_chart(fig_box, use_container_width=True)

# Chart 4: Heatmap Ngành × Xếp hạng tín nhiệm
if "Ngành" in dff.columns and "Credit_Rating_Z" in dff.columns:
    heat = (
        dff.groupby(["Ngành", "Credit_Rating_Z"])
        .size()
        .reset_index(name="Count")
    )
    
    if len(heat) > 0:
        fig_heat = px.density_heatmap(
            heat,
            x="Credit_Rating_Z",
            y="Ngành",
            z="Count",
            title="Heatmap: Ngành × Xếp hạng tín nhiệm",
            color_continuous_scale="Viridis"
        )
        fig_heat.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#e5e7eb'
        )
        st.plotly_chart(fig_heat, use_container_width=True)

# =======================
# LAYER 7 – PHÂN TÍCH NGÀNH (MẶC ĐỊNH HIỂN THỊ)
# =======================
st.markdown("<div class='section'>Sức khỏe tài chính theo ngành (Toàn thị trường)</div>", unsafe_allow_html=True)

if "Health_Score" in dff.columns and "Ngành" in dff.columns:
    industry_health = (
        dff.groupby("Ngành")["Health_Score"]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
        .rename(columns={"Health_Score": "Điểm sức khỏe TB"})
    )
    
    fig_industry = px.bar(
        industry_health,
        x="Ngành",
        y="Điểm sức khỏe TB",
        title="Sức khỏe tài chính theo ngành (Tất cả ngành)",
        color="Điểm sức khỏe TB",
        color_continuous_scale="RdYlGn"
    )
    fig_industry.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#e5e7eb',
        xaxis_tickangle=-45
    )
    st.plotly_chart(fig_industry, use_container_width=True)

# =======================
# LAYER 8 – TOP DOANH NGHIỆP (CÓ ĐIỀU KIỆN)
# =======================
if top_n > 0:
    st.markdown("<div class='section'>Top doanh nghiệp theo điểm sức khỏe</div>", unsafe_allow_html=True)
    
    top_df = (
        dff.sort_values("Health_Score", ascending=False)
        .head(top_n)
    )
    
    display_cols = ["Ticker", "Tên công ty", "Ngành", "Health_Score", "Credit_Rating_Z"]
    available_cols = [col for col in display_cols if col in top_df.columns]
    
    if len(available_cols) > 0:
        st.dataframe(
            top_df[available_cols],
            use_container_width=True,
            hide_index=True
        )

# =======================
# (4) DÒNG TIỀN THEO HEALTH_GROUP
# =======================
st.markdown("<div class='section'>Dòng tiền theo nhóm sức khỏe</div>", unsafe_allow_html=True)

if "Health_Group" in df_flow.columns and "Total_Net_F_Val" in df_flow.columns:
    flow_by_group = (
        df_flow.groupby("Health_Group")["Total_Net_F_Val"]
        .sum()
        .reset_index()
    )
    
    # Map Health_Group to labels
    def map_health_group(x):
        if pd.isna(x):
            return "Không xác định"
        elif x == 0:
            return "Yếu"
        elif x == 1:
            return "Trung bình"
        elif x == 2:
            return "Tốt"
        else:
            return f"Nhóm {x}"
    
    flow_by_group["Nhóm sức khỏe"] = flow_by_group["Health_Group"].apply(map_health_group)
    
    fig_group = px.bar(
        flow_by_group,
        x="Nhóm sức khỏe",
        y="Total_Net_F_Val",
        title="Dòng tiền nhà đầu tư nước ngoài theo nhóm sức khỏe",
        labels={"Total_Net_F_Val": "Tổng giá trị mua/bán ròng (tỷ VND)", "Nhóm sức khỏe": "Nhóm sức khỏe"},
        color="Total_Net_F_Val",
        color_continuous_scale="RdYlGn"
    )
    fig_group.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#e5e7eb',
        title_font_color='#0f172a'
    )
    st.plotly_chart(fig_group, use_container_width=True)
    
    # Find dominant group
    dominant_group = flow_by_group.loc[flow_by_group["Total_Net_F_Val"].abs().idxmax(), "Nhóm sức khỏe"]
    st.markdown(f"""
    <div class="analysis-box">
    <p><b>Nhận xét:</b> Dòng tiền có xu hướng tập trung nhiều hơn vào nhóm doanh nghiệp <b>{dominant_group}</b>, 
    phản ánh sự ưu tiên của nhà đầu tư nước ngoài đối với các doanh nghiệp có sức khỏe tài chính tốt.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.info("Không có dữ liệu để phân tích dòng tiền theo nhóm sức khỏe.")
# =======================
# LAYER 9 – BẢNG GỢI Ý ĐẦU TƯ (Moved Up)
# =======================
st.markdown("<div class='section' style='color:#000000;'>Gợi ý doanh nghiệp nên theo dõi</div>", unsafe_allow_html=True)

# Create investment suggestions based on health score and rating
if "Health_Score" in dff.columns:
    suggestions = (
        dff.sort_values("Health_Score", ascending=False)
        .head(20)
        .copy()
    )
    
    # Add investment assessment
    def get_assessment(row):
        health = row.get('Health_Score', 0)
        rating = row.get('Credit_Rating_Z', '')
        buy_flag = row.get('Buy_Net_Flag', 0)
        
        if health >= 75 and rating in ['AAA', 'AA', 'A']:
            return "Rất tốt - Nên theo dõi"
        elif health >= 65 and buy_flag == 1:
            return "Tốt - Có tiềm năng"
        elif health >= 60:
            return "Trung bình - Cần theo dõi"
        else:
            return "Cần thận trọng"
    
    suggestions['Nhận định'] = suggestions.apply(get_assessment, axis=1)
    
    display_cols_sug = ["Ticker", "Tên công ty", "Ngành", "Health_Score", "Credit_Rating_Z", "Nhận định"]
    available_cols_sug = [col for col in display_cols_sug if col in suggestions.columns]
    
    if len(available_cols_sug) > 0:
        st.dataframe(
            suggestions[available_cols_sug],
            use_container_width=True,
            hide_index=True
        )


# =======================
# LAYER 10 – TRA CỨU DOANH NGHIỆP
# =======================
st.markdown("<div class='section' style='color:#000000;'>Thông tin doanh nghiệp</div>", unsafe_allow_html=True)

ticker_search = st.selectbox(
    "**Chọn mã cổ phiếu để xem chi tiết**",
    sorted(df["Ticker"].unique()),
    help="Chọn doanh nghiệp sau khi đã quan sát bức tranh toàn thị trường"
)

col_date1, col_date2, col_date3 = st.columns([2, 2, 2])
with col_date1:
    start_date = st.date_input(
        "**Từ ngày**",
        value=df_price["Date"].min().date() if len(df_price) > 0 else pd.Timestamp('2021-01-01').date(),
        key="start_date"
    )
with col_date2:
    end_date = st.date_input(
        "**Đến ngày**",
        value=df_price["Date"].max().date() if len(df_price) > 0 else pd.Timestamp('2024-12-31').date(),
        key="end_date"
    )
with col_date3:
    st.write("")  # Spacing

# Get company info
company_info = df[(df["Ticker"] == ticker_search) & (df["Year"] == year)]
if len(company_info) > 0:
    info = company_info.iloc[0]

    # Card thông tin doanh nghiệp dạng bảng 3x3 màu xanh đen
    st.markdown("""
    <style>
    .dark-info-card {
        background: #1f2a3d;
        border-radius: 24px;
        box-shadow: 0 6px 32px rgba(0,0,0,0.15);
        padding: 36px 32px 28px 32px;
        margin-bottom: 32px;
        max-width: 900px;
        margin-left: auto;
        margin-right: auto;
    }
    .dark-info-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 22px 28px;
    }
    .dark-info-cell {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 70px;
        padding: 8px 0;
    }
    .dark-info-title {
        font-size: 15px;
        font-weight: 700;
        color: #a3e3ff;
        margin-bottom: 6px;
    }
    .dark-info-value {
        font-size: 22px;
        font-weight: 800;
        color: #fff;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="dark-info-card">
    <div class="dark-info-grid">
        <div class="dark-info-cell">
        <div class="dark-info-title">Tên công ty</div>
        <div class="dark-info-value">{info.get('Tên công ty','N/A')}</div>
        </div>
        <div class="dark-info-cell">
        <div class="dark-info-title">Ngành</div>
        <div class="dark-info-value">{info.get('Ngành','N/A')}</div>
        </div>
        <div class="dark-info-cell">
        <div class="dark-info-title">Điểm sức khỏe</div>
        <div class="dark-info-value">{info.get('Health_Score',0):.1f}</div>
        </div>
        <div class="dark-info-cell">
        <div class="dark-info-title">Nhóm sức khỏe</div>
        <div class="dark-info-value">{info.get('Health_Label','N/A')}</div>
        </div>
        <div class="dark-info-cell">
        <div class="dark-info-title">Xếp hạng tín nhiệm</div>
        <div class="dark-info-value">{info.get('Credit_Rating_Z','N/A')}</div>
        </div>
        <div class="dark-info-cell">
        <div class="dark-info-title">Vốn hóa TB năm</div>
        <div class="dark-info-value">{info.get('Avg_MarketCap',0)/1e9:,.1f} Tỷ</div>
        </div>
        <div class="dark-info-cell">
        <div class="dark-info-title">Giá cổ phiếu TB năm</div>
        <div class="dark-info-value">{info.get('Avg_Price',0):,.0f} VND</div>
        </div>
        <div class="dark-info-cell">
        <div class="dark-info-title">Giá cao nhất năm</div>
        <div class="dark-info-value">{info.get('Max_Price',0):,.0f} VND</div>
        </div>
        <div class="dark-info-cell">
        <div class="dark-info-title">Giá thấp nhất năm</div>
        <div class="dark-info-value">{info.get('Min_Price',0):,.0f} VND</div>
        </div>
        <div class="dark-info-cell" style="grid-column: 1 / span 3;">
        <div class="dark-info-title">Trạng thái dòng tiền</div>
        <div class="dark-info-value" style="color:{'#10b981' if info.get('Buy_Net_Flag',0)==1 else '#ef4444'};">
            {"Mua ròng" if info.get('Buy_Net_Flag',0)==1 else "Bán ròng"}
        </div>
        </div>
    </div>
    </div>
    """, unsafe_allow_html=True)
    # Time series charts
    chart_col1, chart_col2 = st.columns(2)

    # Filter time series data
    price_ts = df_price[
        (df_price["Ticker"] == ticker_search) &
        (df_price["Date"] >= pd.to_datetime(start_date)) &
        (df_price["Date"] <= pd.to_datetime(end_date))
    ].sort_values("Date")

    volume_ts = df_volume[
        (df_volume["Ticker"] == ticker_search) &
        (df_volume["Date"] >= pd.to_datetime(start_date)) &
        (df_volume["Date"] <= pd.to_datetime(end_date))
    ].sort_values("Date")

    mcap_ts = df_mcap[
        (df_mcap["Ticker"] == ticker_search) &
        (df_mcap["Date"] >= pd.to_datetime(start_date)) &
        (df_mcap["Date"] <= pd.to_datetime(end_date))
    ].sort_values("Date")

    # Chart: Volume
    with chart_col1:
        if len(volume_ts) > 0:
            fig_vol = px.area(
                volume_ts,
                x="Date",
                y="Volume",
                title=f"Khối lượng giao dịch của {ticker_search}",
                labels={"Volume": "Khối lượng", "Date": "Ngày"}
            )
            fig_vol.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#e5e7eb'
            )
            st.plotly_chart(fig_vol, use_container_width=True)
        else:
            st.info(f"Không có dữ liệu khối lượng giao dịch cho {ticker_search}")

    # Chart: Market Cap
    with chart_col2:
        if len(mcap_ts) > 0:
            fig_mcap = px.area(
                mcap_ts,
                x="Date",
                y="MarketCap",
                title=f"Vốn hóa thị trường của {ticker_search}",
                labels={"MarketCap": "Vốn hóa", "Date": "Ngày"}
            )
            fig_mcap.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#e5e7eb'
            )
            st.plotly_chart(fig_mcap, use_container_width=True)
        else:
            st.info(f"Không có dữ liệu vốn hóa cho {ticker_search}")

    # Optional: Price chart
    if len(price_ts) > 0:
        fig_price = px.line(
            price_ts,
            x="Date",
            y="Price",
            title=f"Giá cổ phiếu {ticker_search}",
            labels={"Price": "Giá (VND)", "Date": "Ngày"}
        )
        fig_price.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#e5e7eb'
        )
        st.plotly_chart(fig_price, use_container_width=True)
else:
    st.warning(f"Không tìm thấy thông tin cho mã {ticker_search} năm {year}")

# Footer
st.markdown("---")