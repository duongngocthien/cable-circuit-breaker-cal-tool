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

# --- DỮ LIỆU BẢNG TRA ---
reduction_factors = {
    "31E: Multi-core on perforated tray": [1.00,0.88,0.82,0.77,0.75,0.73,0.73,0.72,0.72],
    "31F: Multi-core on ladder": [1.00,0.87,0.82,0.80,0.79,0.79,0.79,0.78,0.78],
    "31B: Single layer on wall": [1.00,0.85,0.79,0.75,0.73,0.72,0.72,0.71,0.70],
    "31C: Single layer under wooden ceiling": [0.95,0.81,0.72,0.68,0.66,0.64,0.63,0.62,0.61],
    "31A: Bunched in air": [1.00,0.80,0.70,0.65,0.60,0.57,0.54,0.52,0.50,0.45,0.41,0.38],
    "32: Buried in ground (Cáp đi ngầm)": [1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00] # dummy k4, k2 và k3 sẽ quyết định
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

# --- HÀM TRA CỨU ---
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
            col = "col5" if "Bunched" in k4_choice else "col6"
            return next(((a, v[col], col) for a, v in cable_table_al.items() if v[col] >= I_per_cable), (None, None, None))
        table = cable_table_cu if (k2_val == 1.0 and k3_val == 1.0) else cable_table_cu_armoured
        col = "C" if "Bunched" in k4_choice else "B"
        return next(((a, v[col], col) for a, v in table.items() if v[col] >= I_per_cable), (None, None, None))

def calculate_pe_size(phase_area):
    if phase_area <= 16:
        return phase_area
    elif phase_area <= 35:
        return 16
    else:
        std_sizes = [1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120, 150, 185, 240, 300, 400, 500, 630]
        half_size = phase_area / 2
        for s in std_sizes:
            if s >= half_size:
                return s
        return phase_area

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

# Khởi tạo trạng thái tính toán
if 'calculated' not in st.session_state:
    st.session_state.calculated = False

# --- THIẾT KẾ HAI CỘT FORM ---
left_col, right_col = st.columns([1, 1], gap="large")

with left_col:
    # --- PANEL 1: PROJECT PARAMETERS ---
    with st.container():
        st.markdown('<div class="panel-header">Project parameters</div>', unsafe_allow_html=True)
        freq = row_select("Frequency (Hz)", "freq", [50, 60], 0)
        voltage = row_number("Phase to phase voltage (V)", "voltage", 400.0, 10.0, 50.0)
        earthing = row_select("System Earthing Arrangement", "earthing", ["TN-S", "TN-C", "TT", "IT"], 0)
        max_csa = row_select("Max. permissible CSA (mm²)", "max_csa", [300, 400, 500, 630, 800, 1000], 0)
        max_vdrop = row_number("Max Δu (%)", "max_vdrop", 4.0, 0.5, 0.1)

    # --- PANEL 2: LOAD INPUT PARAMETERS ---
    with st.container():
        st.markdown('<div class="panel-header">Load input parameters</div>', unsafe_allow_html=True)
        load_cond = row_select("Number and type of load conductors", "load_cond", ["3Ph+N", "1Ph+N"], 0)
        
        # Dòng nhập tải đặc biệt (giá trị + đơn vị trên cùng dòng bằng cách dùng 3 cột ngang hàng không lồng nhau)
        col_lbl, col_val, col_unit = st.columns([3, 1.2, 0.8])
        with col_lbl:
            st.markdown('<div class="row-label">Sr (kVA) / Pr (kW) / Ir (A)</div>', unsafe_allow_html=True)
        with col_val:
            load_val = st.number_input("Load Value", value=15.0, min_value=0.0, label_visibility="collapsed", key="load_val")
        with col_unit:
            load_unit = st.selectbox("Load Unit", ["kW", "kVA", "A"], label_visibility="collapsed", key="load_unit")
                
        pf = row_number("Power factor", "pf", 0.85, 0.05, 0.1)

with right_col:
    # --- PANEL 3: CABLE INPUT PARAMETERS ---
    with st.container():
        st.markdown('<div class="panel-header">Cable input parameters</div>', unsafe_allow_html=True)
        
        # Standard installation (Chỉ hiển thị text)
        col_lbl, col_wgt = st.columns([3, 2])
        with col_lbl:
            st.markdown('<div class="row-label">Standard installation</div>', unsafe_allow_html=True)
        with col_wgt:
            st.markdown('<div style="padding-top: 6px; font-size: 0.85rem; font-weight: bold; color: #495057;">IEC 60364-5-52</div>', unsafe_allow_html=True)
            
        live_cond = row_select("Live conductors", "live_cond", ["Multi-core", "Single-core"], 0)
        arrangement = row_select("Method Of Installation", "arrangement", list(reduction_factors.keys()), 0)
        
        # Số sợi chạy song song (N)
        max_circuits = len(reduction_factors[arrangement])
        num_cables = row_number("Number of parallel cables (N)", "num_cables", 1.0, 1.0, 1.0)
        num_cables = int(num_cables)
        
        conductor_metal = row_select("Active conductor metal", "conductor_metal", ["Copper", "Aluminum"], 0)
        pe_metal = row_select("PE conductor metal", "pe_metal", ["Copper", "Aluminum"], 0)
        pe_type = row_select("Type of PE", "pe_type", ["PE included", "Separate PE"], 0)
        insulation = row_select("Insulation", "insulation", ["XLPE", "PVC"], 0)
        length = row_number("Length (m)", "length", 5.0, 5.0, 0.1)
        user_k = row_number("User Defined Correction Factor", "user_k", 1.0, 0.05, 0.01)
        
        # Hiển thị các trường ngầm nếu chọn phương thức đi ngầm 32
        is_buried = "32:" in arrangement
        if is_buried:
            insul_ground = row_select("k2 - Ground Insulation Class", "insul_ground", list(k2_factors.keys()), 0)
            ground_temps = sorted(list(k2_factors[insul_ground].keys()))
            temp_ground = row_select("Ground temperature (°C)", "temp_ground", ground_temps, ground_temps.index(20) if 20 in ground_temps else 0)
            soil = row_select("k3 - Soil Nature", "soil", [k for k in k3_factors.keys() if k != "N/A"], 2)
        else:
            insul_air = row_select("k1 - Air Insulation Class", "insul_air", list(k1_factors.keys()), 0)
            air_temps = sorted(list(k1_factors[insul_air].keys()))
            temp_air = row_select("Ambient temperature (°C)", "temp_air", air_temps, air_temps.index(30) if 30 in air_temps else 0)

        # Nút bấm Calculate cable giống Schneider
        st.markdown('<div style="margin-top: 25px; height: 40px;">', unsafe_allow_html=True)
        calculate_click = st.button("Calculate cable", key="calc_btn")
        st.markdown('</div>', unsafe_allow_html=True)
        
        if calculate_click:
            st.session_state.calculated = True

# --- PHẦN TÍNH TOÁN VÀ BÁO CÁO KẾT QUẢ ---
if st.session_state.calculated:
    # 1. Xác định Hệ số Hiệu chỉnh K
    num_cables_idx = min(num_cables - 1, len(reduction_factors[arrangement]) - 1)
    k4 = reduction_factors[arrangement][num_cables_idx]
    
    if not is_buried:
        k1 = k1_factors[insul_air].get(temp_air, 1.0)
        k2 = 1.0
        k3 = 1.0
        T_ambient = temp_air
    else:
        k1 = 1.0
        k2 = k2_factors[insul_ground].get(temp_ground, 1.0)
        k3 = k3_factors[soil]
        T_ambient = temp_ground
        
    K = k1 * k2 * k3 * k4 * user_k
    
    # 2. Tính toán dòng điện tải thiết kế (I_tt) dựa trên đơn vị nhập
    system_type = "3 pha" if load_cond == "3Ph+N" else "1 pha"
    
    # Thiết lập điện áp tính toán
    if system_type == "3 pha":
        voltage_calc = voltage
    else:
        voltage_calc = voltage / math.sqrt(3)  # Pha - Trung tính
        
    if load_unit == "kW":
        P_watt = load_val * 1000
        I_tt = P_watt / (math.sqrt(3) * voltage_calc * pf) if system_type == "3 pha" else P_watt / (voltage_calc * pf)
    elif load_unit == "kVA":
        S_va = load_val * 1000
        I_tt = S_va / (math.sqrt(3) * voltage_calc) if system_type == "3 pha" else S_va / voltage_calc
    else: # Đơn vị là Ampe (A)
        I_tt = load_val
        
    # Tính dòng điện sau hiệu chỉnh
    I_tt_k = I_tt / K
    I_chon = I_tt_k / 0.8  # Giữ hệ số dự trữ 0.8 từ code gốc
    I_per_cable = I_chon / num_cables
    I_tt_cb = I_tt / 0.8
    
    # 3. Chọn cáp và CB
    area, ampacity, col_used = select_cable(I_per_cable, arrangement, conductor_metal, k2, k3, system_type)
    cb_val = select_cb(I_tt_cb, system_type)
    
    # 4. Kiểm tra giới hạn tiết diện cáp lớn nhất (Max. permissible CSA)
    csa_warning = False
    if area and area > max_csa:
        csa_warning = True
        
    # 5. Tính toán sụt áp thực tế
    deltaU = 0.0
    deltaU_percent = 0.0
    vdrop_ok = True
    pe_size = 1.5
    
    if area:
        R0 = cable_table_cxv[area]["Rdc"] if conductor_metal == "Copper" else cable_table_axv[area]["Rdc"]
        Dia = cable_table_cxv[area]["Dia"] if conductor_metal == "Copper" else cable_table_axv[area]["Dia"]
        
        alpha = 0.00393 if conductor_metal == "Copper" else 0.00403
        R_T = (R0 * (1 + alpha * (T_ambient - 20))) / num_cables
        X = 0.08
        L_km = length / 1000
        
        if system_type == "3 pha":
            deltaU = math.sqrt(3) * I_tt * (R_T * pf + X * math.sin(math.acos(pf))) * L_km
        else:
            deltaU = 2 * I_tt * (R_T * pf + X * math.sin(math.acos(pf))) * L_km
            
        deltaU_percent = 100 * deltaU / voltage_calc
        
        if deltaU_percent > max_vdrop:
            vdrop_ok = False
            
        pe_size = calculate_pe_size(area)

    # --- HIỂN THỊ THẺ BÁO CÁO KẾT QUẢ ---
    st.markdown('<div class="report-card">', unsafe_allow_html=True)
    st.markdown('<div class="report-title">⚡ ELECTRICAL CALCULATION REPORT (IEC 60364-5-52)</div>', unsafe_allow_html=True)
    
    # Hộp trạng thái
    if area and vdrop_ok and not csa_warning:
        st.success("🟢 **THIẾT KẾ ĐẠT YÊU CẦU (PASS)** - Cáp chọn lựa đáp ứng đầy đủ điều kiện phát nhiệt và sụt áp giới hạn.")
    elif not area:
        st.error("🔴 **THIẾT KẾ THẤT BẠI (FAIL)** - Không tìm thấy tiết diện cáp phù hợp trong bảng tra của tiêu chuẩn.")
    else:
        st.warning("⚠️ **THIẾT KẾ CÓ CẢNH BÁO (WARNING)** - Kiểm tra kỹ các thông số sụt áp hoặc giới hạn tiết diện tối đa.")

    # 3 Cột chỉ số chính
    rep_col1, rep_col2, rep_col3 = st.columns(3)
    
    with rep_col1:
        if area:
            cable_text = f"**{num_cables} Sợi x {area} mm²**"
            pe_text = f"<br>PE: {pe_size} mm² ({pe_metal})"
            st.markdown(f"""
            <div style="background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 6px; padding: 15px; text-align: center;">
                <span style="font-size: 0.8rem; color: #6b7280; text-transform: uppercase;">Tiết diện cáp Phase đề xuất</span>
                <div style="font-size: 1.4rem; font-weight: 700; color: #3dcd58; margin-top: 5px;">{cable_text}</div>
                <div style="font-size: 0.85rem; color: #4b5563; margin-top: 5px;">Cáp {insulation} {conductor_metal} {pe_text}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 6px; padding: 15px; text-align: center;">
                <span style="font-size: 0.8rem; color: #6b7280; text-transform: uppercase;">Tiết diện cáp Phase</span>
                <div style="font-size: 1.4rem; font-weight: 700; color: #ef4444; margin-top: 5px;">N/A</div>
            </div>
            """, unsafe_allow_html=True)
            
    with rep_col2:
        cb_display = f"**{cb_val} A**" if cb_val else "N/A"
        st.markdown(f"""
        <div style="background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 6px; padding: 15px; text-align: center;">
            <span style="font-size: 0.8rem; color: #6b7280; text-transform: uppercase;">CB Bảo Vệ Đề Xuất</span>
            <div style="font-size: 1.4rem; font-weight: 700; color: #3284ff; margin-top: 5px;">{cb_display}</div>
            <div style="font-size: 0.85rem; color: #4b5563; margin-top: 5px;">Hệ thống {system_type}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with rep_col3:
        color_vdrop = "#3dcd58" if vdrop_ok else "#ef4444"
        st.markdown(f"""
        <div style="background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 6px; padding: 15px; text-align: center;">
            <span style="font-size: 0.8rem; color: #6b7280; text-transform: uppercase;">Sụt áp tính toán (Giới hạn {max_vdrop}%)</span>
            <div style="font-size: 1.4rem; font-weight: 700; color: {color_vdrop}; margin-top: 5px;">{deltaU_percent:.2f}%</div>
            <div style="font-size: 0.85rem; color: #4b5563; margin-top: 5px;">Gương sụt áp: {deltaU:.2f} V</div>
        </div>
        """, unsafe_allow_html=True)

    # Hiển thị các cảnh báo kỹ thuật nếu có
    if csa_warning:
        st.error(f"⚠️ **Cảnh báo giới hạn CSA**: Tiết diện cáp tính toán ({area} mm²) vượt quá mức tiết diện cho phép lớn nhất đặt trong dự án ({max_csa} mm²). Vui lòng chọn tăng số mạch song song (N) hoặc nới rộng giới hạn tối đa.")
    if not vdrop_ok:
        st.error(f"⚠️ **Cảnh báo sụt áp**: Độ sụt áp thực tế ({deltaU_percent:.2f}%) đã vượt mức giới hạn cho phép ({max_vdrop}%). Đề xuất tăng số mạch song song (N) hoặc chọn tăng tiết diện dây dẫn.")

    # Các tab phân tích kỹ thuật chi tiết
    st.markdown('<div style="margin-top: 25px;"></div>', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["📋 Hệ số hiệu chỉnh K", "📊 Phân tích dòng điện", "📐 Trở kháng & Sụt áp IEC"])
    
    with tab1:
        st.write("Bảng thống kê các hệ số hiệu chỉnh K theo **IEC 60364-5-52**:")
        k_df = {
            "Hệ số hiệu chỉnh": ["k1 (Nhiệt độ môi trường)", "k2 (Nhiệt độ đất)", "k3 (Tính chất đất)", "k4 (Mạch song song / đi chung)", "K_user (Hệ số người dùng định nghĩa)", "K_total (Hệ số hiệu chỉnh tổng)"],
            "Mô tả chi tiết": [
                f"Cách điện {insulation} ở {T_ambient}°C ngoài không khí" if not is_buried else "Không áp dụng (1.00)",
                f"Cách điện {insulation} ở {T_ambient}°C trong lòng đất" if is_buried else "Không áp dụng (1.00)",
                f"Loại đất: {soil}" if is_buried else "Không áp dụng (1.00)",
                f"Phương pháp: {arrangement} (N={num_cables} mạch)",
                f"Hệ số hiệu chỉnh bổ sung tự nhập",
                "K = k1 × k2 × k3 × k4 × K_user"
            ],
            "Giá trị tra được": [f"{k1:.2f}", f"{k2:.2f}", f"{k3:.2f}", f"{k4:.2f}", f"{user_k:.2f}", f"{K:.2f}"]
        }
        st.table(k_df)
        
    with tab2:
        st.write("Bảng chuyển đổi dòng điện phục vụ lựa chọn thiết bị và cáp:")
        curr_df = {
            "Thông số dòng điện": [
                "Dòng điện tải thiết kế ban đầu (I_tt)",
                "Dòng điện sau hiệu chỉnh suy giảm nhiệt độ & đi chung (I_tt_k = I_tt / K)",
                "Dòng điện dùng để chọn cáp (sau khi tính hệ số an toàn dự trữ 0.8)",
                "Dòng điện phân bổ trên mỗi sợi song song (I_per_cable)",
                "Dòng điện định mức yêu cầu tối thiểu của CB bảo vệ (I_tt / 0.8)"
            ],
            "Giá trị tính toán (A)": [
                f"{I_tt:.2f} A",
                f"{I_tt_k:.2f} A",
                f"{I_chon:.2f} A",
                f"{I_per_cable:.2f} A",
                f"{I_tt_cb:.2f} A"
            ]
        }
        st.table(curr_df)
        
    with tab3:
        if area:
            st.write("Các thông số vật lý và công thức tính sụt áp theo **IEC 60364-5-52**:")
            st.write(f"- **Đường kính cáp ngoài gần đúng (Dia)**: `{Dia} mm` (mỗi sợi)")
            st.write(f"- **Điện trở DC gốc của dây dẫn ở 20°C (R0)**: `{R0} \Omega/km`")
            st.write(f"- **Điện trở hoạt động thực tế ở {T_ambient}°C (RT)**: `{R_T:.5f} \Omega/km` (cho toàn hệ song song)")
            st.write(f"- **Điện kháng xoay chiều định mức (X)**: `0.08 \Omega/km` (theo tiêu chuẩn IEC)")
            
            st.write("---")
            st.write("**Công thức tính toán dòng sụt áp:**")
            if system_type == "3 pha":
                st.latex(r"\Delta U = \sqrt{3} \cdot I_{tt} \cdot \left( R_T \cdot \cos\phi + X \cdot \sin(\arccos(\cos\phi)) \right) \cdot \frac{L}{1000}")
            else:
                st.latex(r"\Delta U = 2 \cdot I_{tt} \cdot \left( R_T \cdot \cos\phi + X \cdot \sin(\arccos(\cos\phi)) \right) \cdot \frac{L}{1000}")
        else:
            st.warning("Không có dữ liệu cáp để phân tích thông số vật lý.")
            
    st.markdown('</div>', unsafe_allow_html=True)

# --- 3. FOOTER BRAND SCHNEIDER ELECTRIC ---
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