import streamlit as st
import math

# --- CẤU HÌNH TRANG WEB ---
st.set_page_config(
    page_title="Schneider Electric - Cable Sizing Tool",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- THIẾT KẾ GIAO DIỆN SCHNEIDER ELECTRIC VỚI CUSTOM CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Segoe+UI:wght@300;400;600;700&display=swap');
    
    /* Ẩn header và footer mặc định của Streamlit */
    header {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    #MainMenu {visibility: hidden !important;}
    
    /* Thiết lập giao diện tổng thể màu sáng chuyên nghiệp */
    .stApp {
        background-color: #ffffff !important;
        color: #333333 !important;
        font-family: 'Segoe UI', Arial, sans-serif !important;
    }
    
    /* Container panel viền xám nhẹ giống hình vẽ */
    div[data-testid="stContainer"] {
        background-color: #fcfcfc !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 6px !important;
        padding: 20px !important;
        margin-bottom: 20px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02) !important;
    }
    
    /* Tiêu đề xám của các nhóm thông số giống hình ảnh */
    .panel-header {
        background-color: #f1f3f5;
        border-radius: 4px;
        padding: 5px 12px;
        font-weight: 700;
        font-size: 0.9rem;
        color: #495057;
        margin-bottom: 18px;
        border-left: 5px solid #3dcd58;
    }
    
    /* Label căn lề trái */
    .row-label {
        font-size: 0.85rem;
        color: #495057;
        font-weight: 600;
        padding-top: 6px;
    }
    
    /* Thẻ kết quả thiết kế sang trọng */
    .report-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 20px;
        margin-top: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    .report-title {
        font-size: 1.2rem;
        font-weight: 700;
        color: #111827;
        border-bottom: 2px solid #3dcd58;
        padding-bottom: 8px;
        margin-bottom: 15px;
    }
    
    /* Nút bấm Calculate màu xanh Schneider */
    div.stButton > button:first-child {
        background-color: #3dcd58 !important;
        border-color: #3dcd58 !important;
        color: white !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        border-radius: 4px !important;
        padding: 10px 24px !important;
        float: right !important;
        transition: background-color 0.2s ease !important;
    }
    div.stButton > button:first-child:hover {
        background-color: #2b993f !important;
        border-color: #2b993f !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 1. HEADER BRAND SCHNEIDER ELECTRIC ---
st.markdown("""
<div style="background-color: #3dcd58; padding: 12px 24px; color: white; display: flex; justify-content: space-between; align-items: center; font-family: sans-serif; box-shadow: 0 2px 4px rgba(0,0,0,0.08);">
    <div style="display: flex; align-items: center; gap: 15px;">
        <span style="font-weight: 300; font-size: 0.95rem; opacity: 0.9; letter-spacing: 0.5px;">Life Is On</span>
        <span style="font-weight: 800; font-size: 1.35rem; letter-spacing: 0.5px; border-left: 1px solid rgba(255,255,255,0.4); padding-left: 15px;">Schneider</span>
        <span style="font-weight: 400; font-size: 1.35rem; opacity: 0.95; margin-left: -5px;">Electric</span>
    </div>
    <div style="display: flex; gap: 25px; font-size: 0.9rem; font-weight: 600;">
        <a href="#" style="color: white; text-decoration: none; opacity: 0.85; hover: opacity: 1;">Home</a>
        <a href="#" style="color: white; text-decoration: none; opacity: 0.85; hover: opacity: 1;">Protections</a>
        <a href="#" style="color: white; text-decoration: none; border-bottom: 2px solid white; padding-bottom: 2px;">Cables</a>
        <a href="#" style="color: white; text-decoration: none; opacity: 0.85; hover: opacity: 1;">Contact</a>
        <a href="#" style="color: white; text-decoration: none; opacity: 0.85; hover: opacity: 1;">Forum</a>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 2. BREADCRUMB / SUB-HEADER ---
st.markdown("""
<div style="background-color: #f8f9fa; border-bottom: 1px solid #dee2e6; padding: 10px 24px; display: flex; justify-content: space-between; align-items: center; font-size: 0.85rem; color: #495057; font-family: sans-serif;">
    <div style="font-weight: 500;">Cables &gt; Calculate Cross Section Area</div>
    <div style="font-weight: 500;">0 items in Cable Schedule | <a href="#" style="color: #3dcd58; text-decoration: none; font-weight: 600;">View Cable Schedule</a></div>
</div>
<div style="margin-top: 15px;"></div>
""", unsafe_allow_html=True)

# --- DỮ LIỆU BẢNG TRA (Từ file cũ) ---
reduction_factors = {
    "Bunched in air": [1.00,0.80,0.70,0.65,0.60,0.57,0.54,0.52,0.50,0.45,0.41,0.38],
    "Single layer on wall": [1.00,0.85,0.79,0.75,0.73,0.72,0.72,0.71,0.70],
    "Single layer under wooden ceiling": [0.95,0.81,0.72,0.68,0.66,0.64,0.63,0.62,0.61],
    "Single layer on perforated tray": [1.00,0.88,0.82,0.77,0.75,0.73,0.73,0.72,0.72],
    "Single layer on ladder": [1.00,0.87,0.82,0.80,0.79,0.79,0.79,0.78,0.78]
}

k1_factors = {
    "PVC": {10:1.22,15:1.17,20:1.12,25:1.06,30:1.00,35:0.94,40:0.87,45:0.79,50:0.71,55:0.61,60:0.50},
    "XLPE/EPR": {10:1.15,15:1.12,20:1.08,25:1.04,30:1.00,35:0.96,40:0.91,45:0.87,50:0.82,55:0.76,60:0.71,65:0.65,70:0.58,75:0.50,80:0.41}
}

k2_factors = {
    "PVC": {10:1.10,15:1.05,20:1.00,25:0.95,30:0.89,35:0.84,40:0.77,45:0.71,50:0.63,55:0.55,60:0.45},
    "XLPE/EPR": {10:1.07,15:1.04,20:1.00,25:0.96,30:0.93,35:0.89,40:0.85,45:0.80,50:0.76,55:0.71,60:0.65,65:0.60,70:0.53,75:0.46,80:0.38}
}

k3_factors = {
    "Very wet soil": 1.21, "Wet soil": 1.13, "Damp soil": 1.05, "Dry soil": 1.00, "Very dry soil": 0.86, "N/A": 1.00
}

cable_table_al = {
    25: {"col4":121, "col5":103, "col6":107, "col7":138, "col8":122},
    35: {"col4":150, "col5":129, "col6":135, "col7":172, "col8":153},
    50: {"col4":184, "col5":159, "col6":165, "col7":210, "col8":188},
    70: {"col4":237, "col5":206, "col6":215, "col7":271, "col8":244},
    95: {"col4":289, "col5":253, "col6":264, "col7":332, "col8":300},
    120: {"col4":337, "col5":296, "col6":308, "col7":387, "col8":351},
    150: {"col4":389, "col5":343, "col6":358, "col7":448, "col8":407},
    185: {"col4":447, "col5":395, "col6":413, "col7":515, "col8":470},
    240: {"col4":530, "col5":471, "col6":492, "col7":608, "col8":561},
    300: {"col4":613, "col5":547, "col6":571, "col7":708, "col8":652},
    400: {"col4":740, "col5":663, "col6":694, "col7":856, "col8":792},
    500: {"col4":856, "col5":770, "col6":806, "col7":991, "col8":921},
    630: {"col4":996, "col5":899, "col6":942, "col7":1154, "col8":1077}
}

cable_table_cu = {
    1.5: {"A":28, "B":25, "C":24}, 2.5: {"A":37, "B":34, "C":33}, 4: {"A":52, "B":44, "C":43},
    6: {"A":66, "B":55, "C":52}, 10: {"A":91, "B":79, "C":75}, 16: {"A":118, "B":110, "C":107},
    25: {"A":161, "B":141, "C":135}, 35: {"A":200, "B":176, "C":169}, 50: {"A":242, "B":215, "C":207},
    70: {"A":310, "B":279, "C":268}, 95: {"A":377, "B":341, "C":328}, 120: {"A":437, "B":399, "C":382},
    150: {"A":504, "B":462, "C":443}, 185: {"A":575, "B":531, "C":509}, 240: {"A":679, "B":631, "C":604},
    300: {"A":783, "B":731, "C":699}, 400: {"A":940, "B":880, "C":839}, 500: {"A":1083, "B":1006, "C":958},
    630: {"A":1254, "B":1117, "C":1077}, 800: {"A":1460, "B":1262, "C":1152}, 1000: {"A":1683, "B":1432, "C":1240}
}

cable_table_cu_armoured = {
    16: {"A":142, "B":142, "C":135}, 25: {"A":185, "B":185, "C":172}, 35: {"A":226, "B":226, "C":208},
    50: {"A":275, "B":275, "C":235}, 70: {"A":340, "B":340, "C":290}, 95: {"A":405, "B":405, "C":345},
    120: {"A":460, "B":460, "C":390}, 150: {"A":510, "B":510, "C":435}, 185: {"A":580, "B":580, "C":490},
    240: {"A":670, "B":670, "C":560}, 300: {"A":750, "B":750, "C":630}, 400: {"A":830, "B":830, "C":700},
    500: {"A":910, "B":910, "C":770}, 630: {"A":1000, "B":1000, "C":840}, 800: {"A":1117, "B":1117, "C":931},
    1000: {"A":1254, "B":1254, "C":1038}
}

cable_table_cxv = {
    1.5: {"Rdc": 12.1, "Dia": 5.8}, 2.5: {"Rdc": 7.41, "Dia": 6.2}, 4: {"Rdc": 4.61, "Dia": 6.8},
    6: {"Rdc": 3.08, "Dia": 7.3}, 10: {"Rdc": 1.83, "Dia": 7.5}, 16: {"Rdc": 1.15, "Dia": 8.4},
    25: {"Rdc": 0.727, "Dia": 9.9}, 35: {"Rdc": 0.524, "Dia": 11.0}, 50: {"Rdc": 0.387, "Dia": 12.3},
    70: {"Rdc": 0.268, "Dia": 14.2}, 95: {"Rdc": 0.193, "Dia": 16.0}, 120: {"Rdc": 0.153, "Dia": 17.6},
    150: {"Rdc": 0.124, "Dia": 19.6}, 185: {"Rdc": 0.0991,"Dia": 21.6}, 240: {"Rdc": 0.0754,"Dia": 24.3},
    300: {"Rdc": 0.0601,"Dia": 27.0}, 400: {"Rdc": 0.0470,"Dia": 30.4}, 500: {"Rdc": 0.0366,"Dia": 34.0},
    630: {"Rdc": 0.0283,"Dia": 38.8}, 800: {"Rdc": 0.0221, "Dia": 45.0}, 1000: {"Rdc": 0.0176, "Dia": 50.0}
}

cable_table_axv = {
    10: {"Rdc": 3.08, "Dia": 7.5}, 16: {"Rdc": 1.91, "Dia": 8.4}, 25: {"Rdc": 1.20, "Dia": 9.9},
    35: {"Rdc": 0.868, "Dia": 11.0}, 50: {"Rdc": 0.641, "Dia": 12.3}, 70: {"Rdc": 0.443, "Dia": 14.3},
    95: {"Rdc": 0.320, "Dia": 16.0}, 120: {"Rdc": 0.253, "Dia": 17.6}, 150: {"Rdc": 0.206, "Dia": 19.6},
    185: {"Rdc": 0.164,"Dia": 21.6}, 240: {"Rdc": 0.125,"Dia": 24.3}, 300: {"Rdc": 0.100,"Dia": 27.0},
    400: {"Rdc": 0.0778,"Dia": 30.4}, 500: {"Rdc": 0.0605,"Dia": 34.0}, 630: {"Rdc": 0.0469,"Dia": 38.8}
}

cb_table_1p = [6,10,16,20,25,32,40,50,63,80,100,125]
cb_table_3p = [6,10,16,20,25,32,40,50,63,75,80,100,125,160,175,200,225,250,315,400,500,630,800,1000,1250,1600,2000,3200]

# --- HÀM HỖ TRỢ ---
def select_cb(I_tt_cb, system_type):
    table = cb_table_1p if system_type == "1 pha" else cb_table_3p
    for cb in table:
        if cb >= I_tt_cb: return cb
    return None

def select_cable(I_per_cable, k4_choice, conductor_type, k2_val, k3_val, system_type):
    if system_type == "1 pha":
        if conductor_type == "Aluminum":
            return next(((a, v["col4"], "col4") for a, v in cable_table_al.items() if v["col4"] >= I_per_cable), (None, None, None))
        table = cable_table_cu if (k2_val == 1.0 and k3_val == 1.0) else cable_table_cu_armoured
        return next(((a, v["A"], "A") for a, v in table.items() if v["A"] >= I_per_cable), (None, None, None))
    else:
        if conductor_type == "Aluminum":
            col = "col5" if k4_choice == "Bunched in air" else "col6"
            return next(((a, v[col], col) for a, v in cable_table_al.items() if v[col] >= I_per_cable), (None, None, None))
        table = cable_table_cu if (k2_val == 1.0 and k3_val == 1.0) else cable_table_cu_armoured
        col = "C" if k4_choice == "Bunched in air" else "B"
        return next(((a, v[col], col) for a, v in table.items() if v[col] >= I_per_cable), (None, None, None))

# --- HÀM TẠO HÀNG PANEL ---
def row_select(label, key, options, default_idx=0):
    col_lbl, col_wgt = st.columns([3, 2])
    with col_lbl:
        st.markdown(f'<div class="row-label">{label}</div>', unsafe_allow_html=True)
    with col_wgt:
        return st.selectbox(label, options, index=default_idx, label_visibility="collapsed", key=key)

def row_number(label, key, default_val, step=1.0, min_val=0.0):
    col_lbl, col_wgt = st.columns([3, 2])
    with col_lbl:
        st.markdown(f'<div class="row-label">{label}</div>', unsafe_allow_html=True)
    with col_wgt:
        return st.number_input(label, value=default_val, step=step, min_value=min_val, label_visibility="collapsed", key=key)

# Khởi tạo trạng thái tính toán để giữ lại kết quả
if 'calculated' not in st.session_state:
    st.session_state.calculated = False

# --- THIẾT KẾ HAI CỘT FORM ---
left_col, right_col = st.columns([1, 1], gap="large")

with left_col:
    # --- PANEL 1: THÔNG SỐ NGUỒN & TẢI ---
    with st.container():
        st.markdown('<div class="panel-header">Thông số nguồn & Tải</div>', unsafe_allow_html=True)
        
        system_type = row_select("Kiểu hệ thống điện", "system_type", ["3 pha", "1 pha"], 0)
        power = row_number("P – Công suất (kW)", "power", 15.0, 1.0, 0.1)
        
        # U - Điện áp (động dựa theo hệ thống điện)
        default_voltage = 380.0 if system_type == "3 pha" else 220.0
        voltage = row_number("U – Điện áp (V)", "voltage", default_voltage, 10.0, 110.0)
        
        cos_phi = row_number("cosφ – Hệ số công suất", "cos_phi", 0.85, 0.05, 0.1)
        k_du_tru = row_number("k_dự trữ (0–1)", "k_du_tru", 0.8, 0.05, 0.1)
        conductor_type = row_select("Loại dây dẫn", "conductor_type", ["Aluminum", "Copper"], 0)
        length = row_number("Chiều dài dây dẫn (m)", "length", 50.0, 10.0, 0.0)
        deltaV_allow = row_number("ΔV% cho phép", "deltaV_allow", 5.0, 0.5, 0.1)

with right_col:
    # --- PANEL 2: ĐIỀU KIỆN LẮP ĐẶT (HỆ SỐ K) ---
    with st.container():
        st.markdown('<div class="panel-header">Điều kiện lắp đặt (Hệ số K)</div>', unsafe_allow_html=True)
        
        arrangement = row_select("k4 – Arrangement", "arrangement", list(reduction_factors.keys()), 0)
        
        max_circuits = len(reduction_factors[arrangement])
        num_cables = row_number("Number of circuits", "num_cables", 1.0, 1.0, 1.0)
        num_cables = int(num_cables)
        
        insul_air = row_select("k1 – insul", "insul_air", list(k1_factors.keys()), 0)
        
        air_temps = sorted(list(k1_factors[insul_air].keys()))
        temp_air = row_select("AmbT (°C)", "temp_air", air_temps, air_temps.index(30) if 30 in air_temps else 0)
        
        ground_mode = row_select("Vị trí đi cáp", "ground_mode", ["Không đi ngầm", "Có đi ngầm dưới đất"], 0)
        
        if ground_mode == "Không đi ngầm":
            k2 = 1.0
            soil = "N/A"
            k3 = 1.0
        else:
            insul_ground = row_select("k2 – insul", "insul_ground", list(k2_factors.keys()), 0)
            
            ground_temps = sorted(list(k2_factors[insul_ground].keys()))
            temp_ground = row_select("Temp (°C)", "temp_ground", ground_temps, ground_temps.index(20) if 20 in ground_temps else 0)
            k2 = k2_factors[insul_ground].get(temp_ground, 1.0)
            
            soil = row_select("k3 – Soil nature", "soil", [k for k in k3_factors.keys() if k != "N/A"], 0)
            k3 = k3_factors[soil]

        # Nút bấm Calculate cable giống Schneider
        st.markdown('<div style="margin-top: 25px; height: 40px;">', unsafe_allow_html=True)
        calculate_click = st.button("TÍNH TOÁN KẾT QUẢ", key="calc_btn")
        st.markdown('</div>', unsafe_allow_html=True)
        
        if calculate_click:
            st.session_state.calculated = True

# --- THÌNH TOÁN VÀ HIỂN THỊ BÁO CÁO KẾT QUẢ ---
if st.session_state.calculated:
    # Đảm bảo số circuits không bị vượt giới hạn khi chọn lại arrangement
    num_cables_idx = min(num_cables - 1, len(reduction_factors[arrangement]) - 1)
    k4 = reduction_factors[arrangement][num_cables_idx]
    
    k1 = k1_factors[insul_air].get(temp_air, 1.0)
    K = k1 * k2 * k3 * k4
    
    P_watt = power * 1000
    if system_type == "3 pha":
        I_tt = P_watt / (math.sqrt(3) * voltage * cos_phi)
    else:
        I_tt = P_watt / (voltage * cos_phi)
        
    I_tt_k = I_tt / K
    I_chon = I_tt_k / k_du_tru
    I_per_cable = I_chon / num_cables
    I_tt_cb = I_tt / k_du_tru
    
    area, ampacity, col = select_cable(I_per_cable, arrangement, conductor_type, k2, k3, system_type)

    st.markdown('<div class="report-card">', unsafe_allow_html=True)
    st.markdown('<div class="report-title">⚡ KẾT QUẢ TÍNH TOÁN (IEC 60364-5-52)</div>', unsafe_allow_html=True)
    
    # 1. Các hệ số hiệu chỉnh (IEC)
    st.markdown("##### 📊 1. Các hệ số hiệu chỉnh (IEC)")
    st.info(f"k1 : {k1:.2f} | k2 : {k2:.2f} | k3 : {k3:.2f} | k4 : {k4:.2f}  \n**Hệ số tổng hợp K = {K:.2f}**")
    
    # 2. Dòng điện tính toán
    st.markdown("##### 📈 2. Dòng điện tính toán")
    st.warning(f"- Dòng điện tải ban đầu $I_{{tt}}$: **{I_tt:.2f} A** \n- Dòng điện sau suy giảm $I_{{tt\_k}}$: **{I_tt_k:.2f} A** \n- Dòng tính toán chọn dây (gồm dự trữ): **{I_chon:.2f} A** \n- Dòng phân bổ trên mỗi sợi: **{I_per_cable:.2f} A**")
    
    # 3. Kết quả chọn dây và sụt áp
    st.markdown("##### 🔌 3. Chọn Tiết diện Cáp & Thiết bị Bảo vệ")
    if area:
        res_text = f"✅ **Tiết diện đề xuất ({conductor_type}): {area} mm²** (Dòng định mức cáp gốc: {ampacity} A)  \n"
        res_text += f"- Cấu hình: 1 pha {num_cables} sợi.  \n"
        
        # Sụt áp
        R0 = cable_table_cxv[area]["Rdc"] if conductor_type == "Copper" else cable_table_axv[area]["Rdc"]
        alpha = 0.00393 if conductor_type=="Copper" else 0.00403
        R_T = (R0 * (1 + alpha * (temp_air - 20))) / num_cables
        X = 0.08
        L_km = length / 1000
        
        if system_type == "3 pha":
            deltaU = math.sqrt(3) * I_tt * (R_T * cos_phi + X * math.sin(math.acos(cos_phi))) * L_km
        else:
            deltaU = 2 * I_tt * (R_T * cos_phi + X * math.sin(math.acos(cos_phi))) * L_km
            
        deltaU_percent = 100 * deltaU / voltage
        
        res_text += f"- Điện trở dây dẫn tại {temp_air}°C: {R_T:.4f} $\Omega$/km  \n"
        if deltaU_percent <= deltaV_allow:
            res_text += f"- **Sụt áp ước tính: {deltaU:.2f} V ({deltaU_percent:.2f}%)** 🟢 *Nằm trong giới hạn cho phép (≤{deltaV_allow}%)*"
        else:
            res_text += f"- **Sụt áp ước tính: {deltaU:.2f} V ({deltaU_percent:.2f}%)** 🔴 *VƯỢT QUÁ giới hạn cho phép (>{deltaV_allow}%)*"
    else:
        res_text = "❌ Không tìm thấy tiết diện cáp nào phù hợp trong bảng tra dữ liệu có sẵn.  \n"
        
    cb_value = select_cb(I_tt_cb, system_type)
    if cb_value:
        res_text += f"  \n⚡ **Aptomat (CB) khuyến nghị: {cb_value} A** (Hệ thống {system_type})"
    else:
        res_text += f"  \n❌ Không tìm thấy CB phù hợp trong bảng tra."
        
    st.success(res_text)
    st.markdown('</div>', unsafe_allow_html=True)

# --- 4. FOOTER BRAND SCHNEIDER ELECTRIC ---
st.markdown("""
<div style="margin-top: 40px; border-top: 1px solid #dee2e6; background-color: #f1f3f5; padding: 20px 24px; font-family: sans-serif; display: flex; justify-content: space-between; align-items: center; font-size: 0.8rem; color: #495057;">
    <div style="display: flex; align-items: center; gap: 10px;">
        <span style="font-weight: 300; font-size: 0.8rem;">Life Is On</span>
        <span style="font-weight: 800; font-size: 1rem; color: #3dcd58;">Schneider Electric</span>
    </div>
    <div style="display: flex; gap: 20px; font-weight: 600;">
        <a href="#" style="color: #495057; text-decoration: none;">OUR SITE</a>
        <a href="#" style="color: #495057; text-decoration: none;">SUPPORT</a>
        <a href="#" style="color: #495057; text-decoration: none;">PARTNER</a>
    </div>
</div>
<div style="background-color: #3dcd58; padding: 15px 24px; color: white; display: flex; justify-content: flex-start; gap: 25px; font-size: 0.8rem; font-family: sans-serif;">
    <a href="#" style="color: white; text-decoration: none;">Legal</a>
    <a href="#" style="color: white; text-decoration: none;">Privacy Policy</a>
    <a href="#" style="color: white; text-decoration: none;">Terms of use</a>
    <a href="#" style="color: white; text-decoration: none;">Cookie Preferences</a>
</div>
""", unsafe_allow_html=True)