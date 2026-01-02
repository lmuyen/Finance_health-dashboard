# ============================================================
# TRANG 2 – PHÂN TÍCH DOANH NGHIỆP | NHÀ ĐẦU TƯ
# ============================================================

# =======================
# LỚP 0 – CẤU HÌNH + CSS
# =======================
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(
    page_title="Phân tích doanh nghiệp – Nhà đầu tư mới",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
body { background-color:#0b1220; color:#e5e7eb; }
.block-container { padding-top:1.2rem; }

.title { font-size:32px; font-weight:800; color:#0f172a; background-color:#ffffff; padding:10px 15px; border-radius:8px; display:inline-block; }
.subtitle { color:#0f172a; margin-bottom:20px; font-size:14px; background-color:#ffffff; padding:8px 15px; border-radius:8px; display:inline-block; }

.section { font-size:20px; font-weight:700; margin-top:32px; margin-bottom:12px; color:#0f172a; background-color:#ffffff; padding:10px 15px; border-radius:8px; display:inline-block; }

.card {
    background:#1f2a3d;
    border:1px solid #2a3a52;
    border-radius:16px;
    padding:18px;
}

.card-health {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius:16px;
    padding:20px;
    color:#ffffff;
    box-shadow:0 4px 6px rgba(0,0,0,0.1);
}

.card-rating {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    border-radius:16px;
    padding:20px;
    color:#ffffff;
    box-shadow:0 4px 6px rgba(0,0,0,0.1);
}

.card-roa {
    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    border-radius:16px;
    padding:20px;
    color:#ffffff;
    box-shadow:0 4px 6px rgba(0,0,0,0.1);
}

.card-roe {
    background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
    border-radius:16px;
    padding:20px;
    color:#ffffff;
    box-shadow:0 4px 6px rgba(0,0,0,0.1);
}

.card-white {
    background:#ffffff;
    color:#0f172a;
    border-radius:16px;
    padding:22px;
    box-shadow:0 10px 24px rgba(0,0,0,.25);
    margin-bottom:20px;
}

.card-title { font-size:13px; color:rgba(255,255,255,0.8); margin-bottom:8px; }
.card-value { font-size:28px; font-weight:800; }

.info-label { font-weight:600; color:#374151; margin-top:12px; }
.info-value { color:#111827; margin-left:8px; }

.analysis-box {
    background:#ffffff;
    color:#0f172a;
    border-left:4px solid #667eea;
    border-radius:8px;
    padding:20px;
    margin:20px 0;
}

.warning-box {
    background:#fff3cd;
    color:#856404;
    border-left:4px solid #ffc107;
    border-radius:8px;
    padding:20px;
    margin:20px 0;
}

.suggestion-box {
    background:#d1ecf1;
    color:#0c5460;
    border-left:4px solid #17a2b8;
    border-radius:8px;
    padding:20px;
    margin:20px 0;
}
</style>
""", unsafe_allow_html=True)

# =======================
# LỚP 1 – TẢI DỮ LIỆU
# =======================
@st.cache_data
def load_data():
    df_health = pd.read_parquet("Data_health_score_dashboard.parquet")
    df_flow = pd.read_parquet("data_dau_tu.parquet")
    df_ft = pd.read_parquet("df_ft_sorted_2021_2024.parquet")
    return df_health, df_flow, df_ft

df_health, df_flow, df_ft = load_data()

# =======================
# LỚP 2 – CHUẨN HÓA & XỬ LÝ
# =======================
@st.cache_data
def process_data(df_health, df_flow, df_ft):
    """Process and clean data"""
    # Make copies
    df_health = df_health.copy()
    df_flow = df_flow.copy()
    df_ft = df_ft.copy()
    
    # Clean column names
    for df in [df_health, df_flow, df_ft]:
        df.columns = df.columns.str.strip()
    
    # Rename columns
    df_health = df_health.rename(columns={"Mã": "Ticker", "Năm": "Year"})
    df_flow = df_flow.rename(columns={"Mã": "Ticker", "Năm": "Year"})
    
    # Handle df_ft columns
    if "Mã" in df_ft.columns:
        df_ft = df_ft.rename(columns={"Mã": "Ticker"})
    if "Ngày" in df_ft.columns:
        df_ft = df_ft.rename(columns={"Ngày": "Date"})
    
    # Convert dates
    if "Date" in df_ft.columns:
        df_ft["Date"] = pd.to_datetime(df_ft["Date"], errors='coerce')
        df_ft["Year"] = df_ft["Date"].dt.year
    
    # Convert numeric columns in df_ft
    if "Net.F_Val" in df_ft.columns:
        df_ft["Net.F_Val"] = pd.to_numeric(df_ft["Net.F_Val"], errors='coerce')
    
    # Convert numeric columns in df_flow
    if "Total_Net_F_Val" in df_flow.columns:
        df_flow["Total_Net_F_Val"] = pd.to_numeric(df_flow["Total_Net_F_Val"], errors='coerce')
    
    return df_health, df_flow, df_ft

df_health, df_flow, df_ft = process_data(df_health, df_flow, df_ft)

# =======================
# LỚP 3 – TIÊU ĐỀ + LỰA CHỌN
# =======================
st.markdown("<h1 style='text-align: center; background-color: #ffffff; color: #0f172a; font-size: 48px; font-weight: 800; margin-bottom: 20px; margin-top: 10px; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>PHÂN TÍCH DOANH NGHIỆP</h1>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown(
        "<span style='font-weight:700; color:#0f172a; font-size:18px; margin-bottom:0; padding-bottom:0;'>Chọn mã cổ phiếu</span>",
        unsafe_allow_html=True
    )
    st.markdown("<style>.stSelectbox {margin-top: -18px !important;}</style>", unsafe_allow_html=True)
    ticker = st.selectbox(
        "",
        sorted(df_health["Ticker"].unique()) if "Ticker" in df_health.columns else [],
        key="ticker_select",
        label_visibility="collapsed"
    )
with col2:
    st.markdown(
        "<span style='font-weight:700; color:#0f172a; font-size:18px; margin-bottom:0; padding-bottom:0;'>Chọn năm</span>",
        unsafe_allow_html=True
    )
    st.markdown("<style>.stSelectbox {margin-top: -18px !important;}</style>", unsafe_allow_html=True)
    year = st.selectbox(
        "",
        sorted(df_health["Year"].dropna().unique()) if "Year" in df_health.columns else [],
        index=len(sorted(df_health["Year"].dropna().unique())) - 1 if "Year" in df_health.columns and len(sorted(df_health["Year"].dropna().unique())) > 0 else 0,
        key="year_select",
        label_visibility="collapsed"
    )

# Filter data for selected company and year
health_data = df_health[(df_health["Ticker"] == ticker) & (df_health["Year"] == year)]
flow_year_data = df_flow[(df_flow["Ticker"] == ticker)]
flow_daily_data = df_ft[(df_ft["Ticker"] == ticker) & (df_ft["Year"] == year)] if "Ticker" in df_ft.columns and "Year" in df_ft.columns else pd.DataFrame()

if len(health_data) == 0:
    st.warning(f"Không tìm thấy dữ liệu cho mã {ticker} năm {year}")
    st.stop()

info = health_data.iloc[0]


# =======================
# (0) BẢNG CHỈ TIÊU TÀI CHÍNH CHI TIẾT
# =======================
st.markdown("""
<div style="background: linear-gradient(90deg, #e0f2fe 0%, #bae6fd 100%);
            border-radius: 16px; padding: 18px 18px 6px 18px; margin-bottom: 18px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.07);">
<span style="font-size:20px; font-weight:700; color:#0f172a;">
Bảng chỉ tiêu tài chính chi tiết
</span>
</div>
""", unsafe_allow_html=True)

@st.cache_data
def load_bctc_data():
    years = [2021, 2022, 2023, 2024]
    dfs = []
    for y in years:
        try:
            df = pd.read_excel(f"{y}_BCTC.xlsx")
            df["NĂM"] = y  # Đổi thành in hoa cho đồng bộ với file
            dfs.append(df)
        except Exception as e:
            continue
    if dfs:
        df_bctc = pd.concat(dfs, ignore_index=True)
        # Chuẩn hóa tên cột về in hoa để đồng bộ với file gốc
        df_bctc.columns = [col.strip().upper() for col in df_bctc.columns]
        return df_bctc
    else:
        return pd.DataFrame()

df_bctc = load_bctc_data()

# Lọc theo mã cổ phiếu đã chọn (cột "MÃ")
if not df_bctc.empty and "MÃ" in df_bctc.columns:
    bctc_data = df_bctc[df_bctc["MÃ"] == ticker]
else:
    bctc_data = pd.DataFrame()

# Hiển thị bảng, đơn vị tỷ đồng
cols_show = [
    "NĂM", "CĐKT. TÀI SẢN NGẮN HẠN", "CĐKT. TỔNG CỘNG TÀI SẢN", "CĐKT. TIỀN VÀ TƯƠNG ĐƯƠNG TIỀN",
    "CĐKT. NỢ PHẢI TRẢ", "CĐKT. NỢ NGẮN HẠN", "CĐKT. VỐN CHỦ SỞ HỮU", "CĐKT. TỔNG CỘNG NGUỒN VỐN",
    "KQKD. DOANH THU THUẦN", "KQKD. LỢI NHUẬN SAU THUẾ THU NHẬP DOANH NGHIỆP",
    "KQKD. LÃI CƠ BẢN TRÊN CỔ PHIẾU", "LCTT. LƯU CHUYỂN TIỀN TỆ RÒNG TỪ CÁC HOẠT ĐỘNG SẢN XUẤT KINH DOANH (TT)",
    "LCTT. TIỀN VÀ TƯƠNG ĐƯƠNG TIỀN CUỐI KỲ (TT)"
]
cols_show = [col for col in cols_show if col in bctc_data.columns]

if not bctc_data.empty and cols_show:
    st.dataframe(
        bctc_data[cols_show].sort_values("NĂM", ascending=False),
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("Không có dữ liệu chỉ tiêu tài chính chi tiết cho mã cổ phiếu này.")
# =======================
# (1) BẢNG TÌNH HÌNH SỨC KHỎE TÀI CHÍNH
# =======================
st.markdown("""
<div style="background: linear-gradient(90deg, #d1fae5 0%, #a7f3d0 100%);
            border-radius: 16px; padding: 18px 18px 6px 18px; margin-bottom: 18px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.07);">
<span style="font-size:20px; font-weight:700; color:#0f172a;">
Tình hình sức khỏe tài chính
</span>
</div>
""", unsafe_allow_html=True)

# Ánh xạ tên cột sang tiếng Việt
col_map = {
    "Health_Score": "Điểm sức khỏe",
    "Health_Group": "Nhóm sức khỏe",
    "Credit_Rating_Z": "Xếp hạng tín nhiệm",
    "Current Ratio": "Tỷ lệ thanh khoản hiện tại",
    "Cash Ratio": "Tỷ lệ tiền mặt",
    "Interest Coverage": "Khả năng trả lãi",
    "Debt to Asset": "Nợ/Tài sản",
    "Equity Ratio": "Tỷ lệ vốn chủ sở hữu",
    "ROA": "ROA (%)",
    "ROE": "ROE (%)",
    "Net Profit Margin": "Biên LN ròng",
    "Operating Profit Margin": "Biên LN HĐKD",
    "Total Asset Turnover": "Vòng quay tài sản",
    "Revenue Growth": "Tăng trưởng doanh thu",
    "Net Income Growth": "Tăng trưởng LN ròng",
    "Asset Growth": "Tăng trưởng tài sản"
}

cols_show = [
    "Health_Score", "Health_Group", "Credit_Rating_Z", "Current Ratio", "Cash Ratio", "Interest Coverage",
    "Debt to Asset", "Equity Ratio", "ROA", "ROE", "Net Profit Margin", "Operating Profit Margin",
    "Total Asset Turnover", "Revenue Growth", "Net Income Growth", "Asset Growth"
]

df_vn = health_data[cols_show].rename(columns=col_map)

st.dataframe(
    df_vn,
    use_container_width=True,
    hide_index=True
)
# =======================
# (2) KẾT LUẬN NHANH – SỨC KHỎE DOANH NGHIỆP
# =======================
st.markdown("<div class='section'>Kết luận nhanh sức khỏe doanh nghiệp</div>", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

# Thẻ 1: Z-Score tổng hợp sức khỏe
health_z = info.get('Health_Z', None)
if pd.notna(health_z):
    if health_z > 1:
        z_label = "Tốt"
        z_color = "#10b981"
    elif health_z > 0:
        z_label = "Trung bình"
        z_color = "#f59e0b"
    else:
        z_label = "Cần cải thiện"
        z_color = "#ef4444"
    c1.markdown(f"""
    <div class="card-health">
    <div class="card-title">Z-Score tổng hợp sức khỏe</div>
    <div class="card-value" style="color:{z_color};">{health_z:.2f}</div>
    <div style="font-size:14px; margin-top:8px; opacity:0.9;">{z_label}</div>
    </div>
    """, unsafe_allow_html=True)
else:
    c1.markdown("""
    <div class="card-health">
    <div class="card-title">Z-Score tổng hợp sức khỏe</div>
    <div class="card-value">N/A</div>
    </div>
    """, unsafe_allow_html=True)

# Thẻ 2: Xếp hạng tín nhiệm
credit_rating = info.get('Credit_Rating_Z', 'N/A')
c2.markdown(f"""
<div class="card-rating">
<div class="card-title">Xếp hạng tín nhiệm</div>
<div class="card-value">{credit_rating}</div>
</div>
""", unsafe_allow_html=True)

# Thẻ 3: ROA
roa = info.get('ROA', 0)
c3.markdown(f"""
<div class="card-roa">
<div class="card-title">ROA (%)</div>
<div class="card-value">{roa:.2f}%</div>
</div>
""", unsafe_allow_html=True)

# Thẻ 4: ROE
roe = info.get('ROE', 0)
c4.markdown(f"""
<div class="card-roe">
<div class="card-title">ROE (%)</div>
<div class="card-value">{roe:.2f}%</div>
</div>
""", unsafe_allow_html=True)

# =======================
# (2) GIẢI THÍCH ĐIỂM SỨC KHỎE
# =======================
st.markdown("<div class='section'>Giải thích điểm sức khỏe</div>", unsafe_allow_html=True)

# Phân tích các khía cạnh khác nhau
current_ratio = info.get('Current Ratio', 0)
cash_ratio = info.get('Cash Ratio', 0)
interest_coverage = info.get('Interest Coverage', 0)

debt_to_asset = info.get('Debt to Asset', 0)
equity_ratio = info.get('Equity Ratio', 0)

roa_val = info.get('ROA', 0)
roe_val = info.get('ROE', 0)
net_profit_margin = info.get('Net Profit Margin', 0)
operating_profit_margin = info.get('Operating Profit Margin', 0)

revenue_growth = info.get('Revenue Growth', 0)
net_income_growth = info.get('Net Income Growth', 0)
asset_growth = info.get('Asset Growth', 0)

analysis_text = f"""
<div class="analysis-box">
<h3 style="color:#0f172a; margin-bottom:15px;">Phân tích chi tiết</h3>

<p><b>Thanh khoản:</b> """
if current_ratio >= 1.5 and cash_ratio >= 0.3:
    analysis_text += "Doanh nghiệp có khả năng thanh khoản tốt với tỷ lệ thanh khoản hiện tại {:.2f} và tỷ lệ tiền mặt {:.2f}.".format(current_ratio, cash_ratio)
elif current_ratio >= 1.0:
    analysis_text += "Khả năng thanh khoản ở mức chấp nhận được (tỷ lệ thanh khoản: {:.2f}).".format(current_ratio)
else:
    analysis_text += "Cần lưu ý về khả năng thanh khoản (tỷ lệ thanh khoản: {:.2f}).".format(current_ratio)

analysis_text += f"</p><p><b>Đòn bẩy tài chính:</b> "
if debt_to_asset < 0.4:
    analysis_text += f"Cơ cấu vốn an toàn với tỷ lệ nợ/vốn {debt_to_asset:.2%} và tỷ lệ vốn chủ sở hữu {equity_ratio:.2%}."
elif debt_to_asset < 0.6:
    analysis_text += f"Đòn bẩy tài chính ở mức trung bình (tỷ lệ nợ/vốn: {debt_to_asset:.2%})."
else:
    analysis_text += f"Cần thận trọng với đòn bẩy tài chính cao (tỷ lệ nợ/vốn: {debt_to_asset:.2%})."

analysis_text += f"</p><p><b>Sinh lời:</b> "
if roa_val > 5 and roe_val > 10:
    analysis_text += f"Khả năng sinh lời tốt với ROA {roa_val:.2f}% và ROE {roe_val:.2f}%."
elif roa_val > 0 and roe_val > 0:
    analysis_text += f"Khả năng sinh lời ở mức trung bình (ROA: {roa_val:.2f}%, ROE: {roe_val:.2f}%)."
else:
    analysis_text += f"Cần theo dõi khả năng sinh lời (ROA: {roa_val:.2f}%, ROE: {roe_val:.2f}%)."

analysis_text += f"</p><p><b>Tăng trưởng:</b> "
if revenue_growth > 0 and net_income_growth > 0:
    analysis_text += f"Doanh nghiệp đang tăng trưởng với tốc độ tăng doanh thu {revenue_growth:.2f}% và tăng lợi nhuận {net_income_growth:.2f}%."
elif revenue_growth > 0:
    analysis_text += f"Doanh thu tăng trưởng {revenue_growth:.2f}% nhưng lợi nhuận cần theo dõi."
else:
    analysis_text += f"Cần lưu ý về xu hướng tăng trưởng (tăng trưởng doanh thu: {revenue_growth:.2f}%)."

# Thêm các chỉ số Z-Score
analysis_text += "</p><h4 style='color:#0f172a; margin-top:20px; margin-bottom:10px;'>Đánh giá tổng quan (Z-Score)</h4>"

# Lấy các giá trị Z-Score nếu có
roa_z = info.get('ROA_z', None)
roe_z = info.get('ROE_z', None)
current_ratio_z = info.get('Current Ratio_z', None)
cash_ratio_z = info.get('Cash Ratio_z', None)
interest_coverage_z = info.get('Interest Coverage_z', None)
debt_to_asset_z = info.get('Debt to Asset_z', None)
equity_ratio_z = info.get('Equity Ratio_z', None)
net_income_growth_z = info.get('Net Income Growth_z', None)
asset_growth_z = info.get('Asset Growth_z', None)
health_z = info.get('Health_Z', None)

z_scores = []
if pd.notna(roa_z):
    z_scores.append(("ROA", roa_z))
if pd.notna(roe_z):
    z_scores.append(("ROE", roe_z))
if pd.notna(current_ratio_z):
    z_scores.append(("Current Ratio", current_ratio_z))
if pd.notna(cash_ratio_z):
    z_scores.append(("Cash Ratio", cash_ratio_z))
if pd.notna(interest_coverage_z):
    z_scores.append(("Interest Coverage", interest_coverage_z))
if pd.notna(debt_to_asset_z):
    z_scores.append(("Debt to Asset", debt_to_asset_z))
if pd.notna(equity_ratio_z):
    z_scores.append(("Equity Ratio", equity_ratio_z))
if pd.notna(net_income_growth_z):
    z_scores.append(("Net Income Growth", net_income_growth_z))
if pd.notna(asset_growth_z):
    z_scores.append(("Asset Growth", asset_growth_z))
if pd.notna(health_z):
    z_scores.append(("Health Score", health_z))

if len(z_scores) > 0:
    analysis_text += "<p><b>Z-Score các chỉ tiêu chính:</b></p><ul>"
    for indicator, z_val in z_scores[:6]:  # Show top 6
        if z_val > 1:
            status = "Tốt"
            color = "#10b981"
        elif z_val > 0:
            status = "Trung bình"
            color = "#f59e0b"
        else:
            status = "Cần cải thiện"
            color = "#ef4444"
        analysis_text += f'<li><b>{indicator}:</b> <span style="color:{color};">{z_val:.2f} ({status})</span></li>'
    analysis_text += "</ul>"
    
    if pd.notna(health_z):
        analysis_text += f"<p><b>Z-Score tổng hợp sức khỏe:</b> <span style='color:#667eea; font-weight:bold;'>{health_z:.2f}</span></p>"
        if health_z > 1:
            analysis_text += "<p>Doanh nghiệp có sức khỏe tài chính tốt so với trung bình ngành.</p>"
        elif health_z > 0:
            analysis_text += "<p>Sức khỏe tài chính ở mức trung bình so với ngành.</p>"
        else:
            analysis_text += "<p>Cần cải thiện sức khỏe tài chính so với trung bình ngành.</p>"
else:
    analysis_text += "<p>Z-Score không khả dụng cho doanh nghiệp này.</p>"

analysis_text += "</p></div>"

st.markdown(analysis_text, unsafe_allow_html=True)

# =======================
# (3) DÒNG TIỀN NHÀ ĐẦU TƯ
# =======================
st.markdown("<div class='section'>DÒNG TIỀN NHÀ ĐẦU TƯ NƯỚC NGOÀI</div>", unsafe_allow_html=True)

# (3A) Dòng tiền theo năm
st.markdown("<h4 style='color:#0f172a; background-color:#ffffff; padding:10px; border-radius:8px; display:inline-block; margin-top:20px;'> Dòng tiền theo năm</h4>", unsafe_allow_html=True)

if len(flow_year_data) > 0 and "Total_Net_F_Val" in flow_year_data.columns:
    flow_year_chart = flow_year_data.sort_values("Year")
    
    fig_year = px.bar(
        flow_year_chart,
        x="Year",
        y="Total_Net_F_Val",
        title=f"Dòng tiền nhà đầu tư nước ngoài theo năm - {ticker}",
        labels={"Total_Net_F_Val": "Giá trị mua/bán ròng (tỷ VND)", "Year": "Năm"},
        color="Total_Net_F_Val",
        color_continuous_scale="RdYlGn"
    )
    fig_year.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#e5e7eb',
        title_font_color='#0f172a'
    )
    fig_year.update_traces(marker_line_color='rgba(0,0,0,0.3)', marker_line_width=1)
    st.plotly_chart(fig_year, use_container_width=True)
    
    # Phân tích nhận xét
    avg_flow = flow_year_chart["Total_Net_F_Val"].mean()
    if avg_flow > 0:
        flow_trend = "tích lũy"
    else:
        flow_trend = "rút ròng"
    
    st.markdown(f"""
    <div class="analysis-box">
    <p><b>Nhận xét:</b> Dòng tiền nước ngoài có xu hướng <b>{flow_trend}</b> trong giai đoạn {flow_year_chart['Year'].min():.0f}–{flow_year_chart['Year'].max():.0f}, 
    với giá trị trung bình {avg_flow:,.0f} tỷ VND.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.info("Không có dữ liệu dòng tiền theo năm cho doanh nghiệp này.")

# (3B) Dòng tiền theo ngày (1 năm)
st.markdown("<h4 style='color:#0f172a; background-color:#ffffff; padding:10px; border-radius:8px; display:inline-block; margin-top:20px;'>Dòng tiền theo ngày trong một năm </h4>", unsafe_allow_html=True)

if len(flow_daily_data) > 0 and "Net.F_Val" in flow_daily_data.columns:
    flow_daily_chart = flow_daily_data.sort_values("Date")
    flow_daily_chart = flow_daily_chart[flow_daily_chart["Date"].notna()].copy()
    
    if len(flow_daily_chart) > 0:
        # Convert Net.F_Val to numeric, handling errors
        flow_daily_chart["Net.F_Val"] = pd.to_numeric(flow_daily_chart["Net.F_Val"], errors='coerce')
        # Remove rows with invalid values
        flow_daily_chart = flow_daily_chart[flow_daily_chart["Net.F_Val"].notna()]
        
        if len(flow_daily_chart) > 0:
            # Calculate MA(20) and MA(30)
            flow_daily_chart["MA20"] = flow_daily_chart["Net.F_Val"].rolling(window=20, min_periods=1).mean()
            flow_daily_chart["MA30"] = flow_daily_chart["Net.F_Val"].rolling(window=30, min_periods=1).mean()
            
            fig_daily = go.Figure()
            
            # Add daily line
            fig_daily.add_trace(go.Scatter(
                x=flow_daily_chart["Date"],
                y=flow_daily_chart["Net.F_Val"],
                mode='lines',
                name='Dòng tiền hàng ngày',
                line=dict(color='rgba(102, 126, 234, 0.6)', width=1)
            ))
            
            # Add MA20
            fig_daily.add_trace(go.Scatter(
                x=flow_daily_chart["Date"],
                y=flow_daily_chart["MA20"],
                mode='lines',
                name='Trung bình 20 ngày',
                line=dict(color='#f5576c', width=2)
            ))
            
            # Add MA30
            fig_daily.add_trace(go.Scatter(
                x=flow_daily_chart["Date"],
                y=flow_daily_chart["MA30"],
                mode='lines',
                name='Trung bình 30 ngày',
                line=dict(color='#43e97b', width=2)
            ))
            
            fig_daily.update_layout(
                title=f"Dòng tiền nhà đầu tư nước ngoài theo ngày - {ticker} ({year})",
                xaxis_title="Ngày",
                yaxis_title="Giá trị mua/bán ròng (tỷ VND)",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#e5e7eb',
                title_font_color='#0f172a',
                hovermode='x unified'
            )
            
            st.plotly_chart(fig_daily, use_container_width=True)
            
            # Phân tích nhận xét
            if len(flow_daily_chart) >= 30:
                recent_trend = "tích cực" if flow_daily_chart["Net.F_Val"].tail(30).mean() > 0 else "tiêu cực"
            else:
                recent_trend = "tích cực" if flow_daily_chart["Net.F_Val"].mean() > 0 else "tiêu cực"
            
            st.markdown(f"""
            <div class="analysis-box">
            <p><b>Nhận xét:</b> Xu hướng dòng tiền trong năm cho thấy <b>{recent_trend}</b>, 
            với biến động phản ánh hành vi giao dịch của nhà đầu tư nước ngoài.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Không có dữ liệu hợp lệ cho dòng tiền theo ngày.")
    else:
        st.info("Không có dữ liệu dòng tiền theo ngày cho năm này.")
else:
    st.info("Không có dữ liệu dòng tiền theo ngày cho doanh nghiệp này.")


# =======================
# (5) CẢNH BÁO & GỢI Ý ĐẦU TƯ
# =======================
st.markdown("<div class='section'>Cảnh báo & Gợi ý đầu tư</div>", unsafe_allow_html=True)

warnings = []
suggestions = []

# Kiểm tra rủi ro
if debt_to_asset > 0.6:
    warnings.append("Đòn bẩy tài chính cao (tỷ lệ nợ/vốn > 60%)")
if net_income_growth < 0:
    warnings.append("Lợi nhuận có xu hướng giảm")
if current_ratio < 1.0:
    warnings.append("Khả năng thanh khoản cần được theo dõi")
if roa_val < 0 or roe_val < 0:
    warnings.append("Doanh nghiệp đang thua lỗ")

# Sinh gợi ý dựa trên Z-Score tổng hợp sức khỏe (health_z)
if health_z is not None and pd.notna(health_z):
    if health_z > 1 and credit_rating in ['AAA', 'AA', 'A']:
        suggestions.append("Doanh nghiệp có sức khỏe tài chính tốt, phù hợp cho đầu tư dài hạn")
    elif health_z > 0:
        suggestions.append("Theo dõi các chỉ số tài chính và xu hướng dòng tiền")
    else:
        suggestions.append("Cần thận trọng, nên theo dõi kỹ các chỉ số trước khi quyết định đầu tư")
else:
    suggestions.append("Không đủ dữ liệu để đánh giá sức khỏe tài chính doanh nghiệp")

if len(warnings) > 0:
    warning_text = "<ul>" + "".join([f"<li>{w}</li>" for w in warnings]) + "</ul>"
    st.markdown(f"""
    <div class="warning-box">
    <h4 style="color:#856404; margin-bottom:10px;"> Rủi ro cần lưu ý</h4>
    {warning_text}
    </div>
    """, unsafe_allow_html=True)

if len(suggestions) > 0:
    suggestion_text = "<ul>" + "".join([f"<li>{s}</li>" for s in suggestions]) + "</ul>"
    st.markdown(f"""
    <div class="suggestion-box">
    <h4 style="color:#0c5460; margin-bottom:10px;"> Gợi ý đầu tư</h4>
    {suggestion_text}
    </div>
    """, unsafe_allow_html=True)

# Chân trang
st.markdown("---")

