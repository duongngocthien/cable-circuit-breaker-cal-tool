import streamlit as st
import math

# --- CẤU HÌNH TRANG WEB ---
st.set_page_config(
    page_title="IEC Cable & CB Calculator",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- THIẾT KẾ GIAO DIỆN PREMIUM VỚI CUSTOM CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Font mặc định cho toàn bộ trang */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Card kết quả */
    .kpi-card {
        padding: 20px;
        border-radius: 12px;
        color: white;
        margin-bottom: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.1);
    }
    
    /* Tiêu đề phần */
    .section-title {
        font-size: 1.15rem;
        font-weight: 600;
        margin-bottom: 12px;
        color: #1e293b;
        border-left: 4px solid #3b82f6;
        padding-left: 8px;
    }
    .dark .section-title {
        color: #f1f5f9;
        border-left: 4px solid #60a5fa;
    }
</style>
""", unsafe_allow_html=True)

# --- BANNER ĐẦU TRANG ---
st.markdown("""
<div style="
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
    padding: 30px;
    border-radius: 16px;
    color: white;
    text-align: center;
    margin-bottom: 25px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    border: 1px solid rgba(255,255,255,0.1);
">
    <h1 style="color: white; margin: 0; font-size: 2.2rem; font-weight: 700; letter-spacing: -0.5px;">⚡ IEC CABLE & CB SELECTOR</h1>
    <p style="margin: 10px 0 0 0; font-size: 1rem; opacity: 0.9; font-weight: 300;">Tính toán hệ số hiệu chỉnh, chọn tiết diện cáp hạ thế và CB theo tiêu chuẩn IEC 60364-5-52</p>
</div>
""", unsafe_allow_html=True)

# --- DỮ LIỆU BẢNG TRA ---
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

# --- Bảng dây nhôm (Aluminum, single core) ---
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

# --- Bảng dây đồng (Copper, single core, không đi đất) ---
cable_table_cu = {
    1.5: {"A":28, "B":25, "C":24}, 2.5: {"A":37, "B":34, "C":33}, 4: {"A":52, "B":44, "C":43},
    6: {"A":66, "B":55, "C":52}, 10: {"A":91, "B":79, "C":75}, 16: {"A":118, "B":110, "C":107},
    25: {"A":161, "B":141, "C":135}, 35: {"A":200, "B":176, "C":169}, 50: {"A":242, "B":215, "C":207},
    70: {"A":310, "B":279, "C":268}, 95: {"A":377, "B":341, "C":328}, 120: {"A":437, "B":399, "C":382},
    150: {"A":504, "B":462, "C":443}, 185: {"A":575, "B":531, "C":509}, 240: {"A":679, "B":631, "C":604},
    300: {"A":783, "B":731, "C":699}, 400: {"A":940, "B":880, "C":839}, 500: {"A":1083, "B":1006, "C":958},
    630: {"A":1254, "B":1117, "C":1077}, 800: {"A":1460, "B":1262, "C":1152}, 1000: {"A":1683, "B":1432, "C":1240}
}

# --- Bảng dây đồng có giáp nhôm (Copper armoured, buried) ---
cable_table_cu_armoured = {
    16: {"A":142, "B":142, "C":135}, 25: {"A":185, "B":185, "C":172}, 35: {"A":226, "B":226, "C":208},
    50: {"A":275, "B":275, "C":235}, 70: {"A":340, "B":340, "C":290}, 95: {"A":405, "B":405, "C":345},
    120: {"A":460, "B":460, "C":390}, 150: {"A":510, "B":510, "C":435}, 185: {"A":580, "B":580, "C":490},
    240: {"A":670, "B":670, "C":560}, 300: {"A":750, "B":750, "C":630}, 400: {"A":830, "B":830, "C":700},
    500: {"A":910, "B":910, "C":770}, 630: {"A":1000, "B":1000, "C":840}, 800: {"A":1117, "B":1117, "C":931},
    1000: {"A":1254, "B":1254, "C":1038}
}

# --- Bảng thông số kỹ thuật CXV (Đồng XLPE/PVC) ---
# Đã sửa lỗi thiếu thông số cho 800 mm² và 1000 mm² tránh crash KeyError
cable_table_cxv = {
    1.5: {"Rdc": 12.1, "Dia": 5.8}, 2.5: {"Rdc": 7.41, "Dia": 6.2}, 4: {"Rdc": 4.61, "Dia": 6.8},
    6: {"Rdc": 3.08, "Dia": 7.3}, 10: {"Rdc": 1.83, "Dia": 7.5}, 16: {"Rdc": 1.15, "Dia": 8.4},
    25: {"Rdc": 0.727, "Dia": 9.9}, 35: {"Rdc": 0.524, "Dia": 11.0}, 50: {"Rdc": 0.387, "Dia": 12.3},
    70: {"Rdc": 0.268, "Dia": 14.2}, 95: {"Rdc": 0.193, "Dia": 16.0}, 120: {"Rdc": 0.153, "Dia": 17.6},
    150: {"Rdc": 0.124, "Dia": 19.6}, 185: {"Rdc": 0.0991,"Dia": 21.6}, 240: {"Rdc": 0.0754,"Dia": 24.3},
    300: {"Rdc": 0.0601,"Dia": 27.0}, 400: {"Rdc": 0.0470,"Dia": 30.4}, 500: {"Rdc": 0.0366,"Dia": 34.0},
    630: {"Rdc": 0.0283,"Dia": 38.8}, 800: {"Rdc": 0.0221, "Dia": 45.0}, 1000: {"Rdc": 0.0176, "Dia": 50.0}
}

# --- Bảng thông số kỹ thuật AXV (Nhôm XLPE/PVC) ---
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
def select_cb(I_tt_k, system_type):
    table = cb_table_1p if system_type == "1 pha" else cb_table_3p
    for cb in table:
        if cb >= I_tt_k: return cb
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

def make_kpi_card(title, value, color_gradient, icon):
    return f"""
    <div class="kpi-card" style="background: {color_gradient};">
        <div style="font-size: 0.85rem; opacity: 0.85; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px;">{icon} {title}</div>
        <div style="font-size: 1.6rem; font-weight: 700; margin-top: 5px; line-height: 1.2;">{value}</div>
    </div>
    """

# --- GIAO DIỆN CHÍNH (2 cột: Trái nhập liệu, Phải tính toán thời gian thực) ---
left_col, right_col = st.columns([1, 1.25], gap="large")

with left_col:
    st.markdown('<div class="section-title">⚡ 1. Thông số Nguồn & Tải</div>', unsafe_allow_html=True)
    
    sub_col1, sub_col2 = st.columns(2)
    with sub_col1:
        system_type = st.selectbox("Kiểu hệ thống", ["3 pha", "1 pha"])
    with sub_col2:
        conductor_type = st.selectbox("Loại lõi dẫn", ["Copper", "Aluminum"])
        
    sub_col3, sub_col4 = st.columns(2)
    with sub_col3:
        power = st.number_input("P – Công suất (kW)", min_value=0.01, value=15.0, step=1.0)
    with sub_col4:
        default_voltage = 380 if system_type == "3 pha" else 220
        voltage = st.number_input("U – Điện áp (V)", min_value=50, value=default_voltage, step=10)
        
    sub_col5, sub_col6 = st.columns(2)
    with sub_col5:
        cos_phi = st.slider("cosφ – Hệ số công suất", min_value=0.1, max_value=1.0, value=0.85, step=0.01)
    with sub_col6:
        k_du_tru = st.slider("k_dự trữ (Hệ số an toàn)", min_value=0.1, max_value=1.0, value=0.80, step=0.05)
        
    sub_col7, sub_col8 = st.columns(2)
    with sub_col7:
        length = st.number_input("L – Chiều dài dây (m)", min_value=0.0, value=50.0, step=10.0)
    with sub_col8:
        deltaV_allow = st.number_input("ΔV% giới hạn (%)", min_value=0.1, max_value=20.0, value=5.0, step=0.5)

    st.markdown('<div class="section-title">🌍 2. Điều kiện Lắp đặt & Môi trường</div>', unsafe_allow_html=True)
    
    arrangement = st.selectbox("k4 – Phương thức đi dây", list(reduction_factors.keys()))
    
    # Giới hạn số mạch đi chung động theo k4
    max_circuits = len(reduction_factors[arrangement])
    num_cables = st.number_input("N – Số sợi chạy song song", min_value=1, max_value=max_circuits, value=1, step=1)
    
    sub_col9, sub_col10 = st.columns(2)
    with sub_col9:
        insul_air = st.selectbox("k1 – Loại cách điện (Khí)", list(k1_factors.keys()))
    with sub_col10:
        air_temps = sorted(list(k1_factors[insul_air].keys()))
        temp_air = st.selectbox("Nhiệt độ khí (°C)", air_temps, index=air_temps.index(30) if 30 in air_temps else 0)
        
    ground_mode = st.radio("Môi trường lắp đặt", ["Đi trên không / Máng cáp", "Đi ngầm dưới đất"], horizontal=True)
    
    if ground_mode == "Đi trên không / Máng cáp":
        k2 = 1.0
        soil = "N/A"
        k3 = 1.0
    else:
        sub_col11, sub_col12 = st.columns(2)
        with sub_col11:
            insul_ground = st.selectbox("k2 – Loại cách điện (Đất)", list(k2_factors.keys()))
            ground_temps = sorted(list(k2_factors[insul_ground].keys()))
            temp_ground = st.selectbox("Nhiệt độ đất (°C)", ground_temps, index=ground_temps.index(20) if 20 in ground_temps else 0)
            k2 = k2_factors[insul_ground].get(temp_ground, 1.0)
        with sub_col12:
            soil = st.selectbox("k3 – Tính chất đất", [k for k in k3_factors.keys() if k != "N/A"])
            k3 = k3_factors[soil]

# --- PHẦN TÍNH TOÁN (Real-time, không cần bấm nút) ---
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

# Tra bảng chọn cáp
area, ampacity, col_used = select_cable(I_per_cable, arrangement, conductor_type, k2, k3, system_type)

with right_col:
    st.markdown('<div class="section-title">📊 Kết Quả Tính Toán & Khuyến Nghị</div>', unsafe_allow_html=True)
    
    # KPI 1: Đề xuất tiết diện cáp
    if area:
        cable_title = f"{num_cables} Sợi x {area} mm² ({conductor_type})"
        cable_gradient = "linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)"
    else:
        cable_title = "Không tìm thấy cỡ cáp phù hợp!"
        cable_gradient = "linear-gradient(135deg, #ef4444 0%, #dc2626 100%)"
        
    # KPI 2: CB bảo vệ
    cb_val = select_cb(I_tt_cb, system_type)
    if cb_val:
        cb_title = f"{cb_val} A"
        cb_gradient = "linear-gradient(135deg, #0284c7 0%, #0369a1 100%)"
    else:
        cb_title = "Không tìm thấy CB phù hợp"
        cb_gradient = "linear-gradient(135deg, #f59e0b 0%, #d97706 100%)"
        
    # Sụt áp
    deltaU = 0.0
    deltaU_percent = 0.0
    status_msg = ""
    status_ok = True
    
    if area:
        # Lấy thông số kỹ thuật (Rdc & Dia)
        R0 = cable_table_cxv[area]["Rdc"] if conductor_type == "Copper" else cable_table_axv[area]["Rdc"]
        Dia = cable_table_cxv[area]["Dia"] if conductor_type == "Copper" else cable_table_axv[area]["Dia"]
        
        # Hiệu chỉnh điện trở theo nhiệt độ
        T_ambient = temp_air if ground_mode == "Đi trên không / Máng cáp" else temp_ground
        alpha = 0.00393 if conductor_type == "Copper" else 0.00403
        R_T = (R0 * (1 + alpha * (T_ambient - 20))) / num_cables
        X = 0.08
        L_km = length / 1000
        
        # Công thức sụt áp IEC
        if system_type == "3 pha":
            deltaU = math.sqrt(3) * I_tt * (R_T * cos_phi + X * math.sin(math.acos(cos_phi))) * L_km
        else:
            deltaU = 2 * I_tt * (R_T * cos_phi + X * math.sin(math.acos(cos_phi))) * L_km
            
        deltaU_percent = 100 * deltaU / voltage
        
        if deltaU_percent <= deltaV_allow:
            vd_gradient = "linear-gradient(135deg, #10b981 0%, #047857 100%)"
            status_msg = f"🟢 Đạt yêu cầu sụt áp (≤ {deltaV_allow}%)"
        else:
            vd_gradient = "linear-gradient(135deg, #f43f5e 0%, #be123c 100%)"
            status_msg = f"🔴 Cảnh báo: Sụt áp vượt giới hạn ({deltaU_percent:.2f}% > {deltaV_allow}%)"
            status_ok = False
    else:
        vd_gradient = "linear-gradient(135deg, #6b7280 0%, #4b5563 100%)"
        status_msg = "Không xác định"
        status_ok = False

    # Hiển thị các KPI chính dưới dạng thẻ thiết kế đẹp
    kpi_col1, kpi_col2 = st.columns(2)
    with kpi_col1:
        st.markdown(make_kpi_card("Tiết diện cáp & Sắp xếp", cable_title, cable_gradient, "🔌"), unsafe_allow_height=False, unsafe_allow_html=True)
    with kpi_col2:
        st.markdown(make_kpi_card("CB Bảo Vệ Đề Xuất", cb_title, cb_gradient, "⚡"), unsafe_allow_height=False, unsafe_allow_html=True)
        
    st.markdown(make_kpi_card("Độ sụt áp ước tính", f"{deltaU_percent:.2f}% ({deltaU:.2f} V)", vd_gradient, "📉"), unsafe_allow_height=False, unsafe_allow_html=True)

    if area:
        if status_ok:
            st.success(status_msg)
        else:
            st.error(status_msg)
            st.warning("👉 Khuyên dùng: Tăng số sợi song song (N), chọn kiểu đặt sát hoặc tăng cỡ cáp thủ công bằng cách tăng hệ số dự trữ.")
            
    # Tạo các tab phân tích chi tiết cho kỹ sư
    tab1, tab2, tab3 = st.tabs(["🔍 Chi Tiết Hệ Số K", "📊 Phân Tích Dòng Điện", "📐 Thông Số Vật Lý & Tổn Hao"])
    
    with tab1:
        st.write("Các hệ số hiệu chỉnh theo tiêu chuẩn **IEC 60364-5-52**:")
        k_df = {
            "Hệ số": ["k1 (Nhiệt độ khí)", "k2 (Nhiệt độ đất)", "k3 (Đất)", "k4 (Sắp xếp)", "Tổng hệ số K"],
            "Mô tả": [
                f"Cách điện {insul_air} ở {temp_air}°C",
                f"Cách điện {insul_ground} ở {temp_ground}°C" if ground_mode != "Đi trên không / Máng cáp" else "Không đi ngầm dưới đất (1.00)",
                f"Tính chất: {soil}" if ground_mode != "Đi trên không / Máng cáp" else "Không đi ngầm dưới đất (1.00)",
                f"Cách đi dây '{arrangement}' với {num_cables} sợi",
                "K = k1 × k2 × k3 × k4"
            ],
            "Giá trị": [f"{k1:.2f}", f"{k2:.2f}", f"{k3:.2f}", f"{k4:.2f}", f"{K:.2f}"]
        }
        st.table(k_df)
        st.write("---")
        st.markdown(r"**Công thức liên hệ dòng cho phép gốc và dòng hiệu chỉnh:**")
        st.latex(r"I_{per\_cable} \ge \frac{I_{tt}}{K \cdot k_{dự\_trữ} \cdot N}")

    with tab2:
        st.write("Quá trình biến đổi dòng điện thiết kế:")
        curr_data = {
            "Dòng điện tải ban đầu ($I_{tt}$)": f"{I_tt:.2f} A",
            "Dòng điện sau hiệu chỉnh suy giảm ($I_{tt\_k} = I_{tt} / K$)": f"{I_tt_k:.2f} A",
            "Dòng điện chọn cáp tổng (gồm dự trữ $I_{tt\_k} / k_{dự\_trữ}$)": f"{I_chon:.2f} A",
            "Dòng điện phân bổ trên mỗi dây dẫn ($I_{per\_cable}$)": f"{I_per_cable:.2f} A",
            "Dòng điện tính toán cho CB ($I_{tt} / k_{dự\_trữ}$)": f"{I_tt_cb:.2f} A"
        }
        for k, v in curr_data.items():
            st.markdown(f"- **{k}**: `{v}`")
            
        st.write("---")
        st.write("**Công thức dòng tải thiết kế:**")
        if system_type == "3 pha":
            st.latex(r"I_{tt} = \frac{P}{\sqrt{3} \cdot U \cdot \cos\phi}")
        else:
            st.latex(r"I_{tt} = \frac{P}{U \cdot \cos\phi}")

    with tab3:
        if area:
            st.write("Thông số chi tiết cáp lựa chọn:")
            st.write(f"- **Đường kính tổng ngoài gần đúng**: `{Dia} mm` (mỗi sợi)")
            st.write(f"- **Điện trở một chiều (DC) gốc ở 20°C (R0)**: `{R0} \Omega/km`")
            st.write(f"- **Điện trở hiệu chỉnh nhiệt độ hoạt động (RT)**: `{R_T:.5f} \Omega/km` (cho hệ song song `{num_cables}` sợi)")
            st.write(f"- **Điện kháng ước lượng (X)**: `0.08 \Omega/km` (tiêu chuẩn IEC)")
            
            st.write("---")
            st.write("**Công thức tính sụt áp theo IEC 60364:**")
            if system_type == "3 pha":
                st.latex(r"\Delta U = \sqrt{3} \cdot I_{tt} \cdot (R_T \cdot \cos\phi + X \cdot \sin(\theta)) \cdot \frac{L}{1000}")
            else:
                st.latex(r"\Delta U = 2 \cdot I_{tt} \cdot (R_T \cdot \cos\phi + X \cdot \sin(\theta)) \cdot \frac{L}{1000}")
            st.caption("Trong đó: sin(θ) được tính từ cos(φ) qua công thức lượng giác.")
        else:
            st.warning("Không có dữ liệu cáp phù hợp để tính thông số vật lý.")