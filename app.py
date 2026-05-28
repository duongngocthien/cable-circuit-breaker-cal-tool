import streamlit as st
import math

# --- CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="IEC Cable Calculator", layout="centered")
st.title("IEC Cable Correction Factors & Current Calculation")
st.write("Ứng dụng tính toán hệ số hiệu chỉnh, chọn tiết diện cáp hạ thế và CB theo tiêu chuẩn IEC.")

# --- Bảng k4: Arrangement ---
reduction_factors = {
    "Bunched in air": [1.00,0.80,0.70,0.65,0.60,0.57,0.54,0.52,0.50,0.45,0.41,0.38],
    "Single layer on wall": [1.00,0.85,0.79,0.75,0.73,0.72,0.72,0.71,0.70],
    "Single layer under wooden ceiling": [0.95,0.81,0.72,0.68,0.66,0.64,0.63,0.62,0.61],
    "Single layer on perforated tray": [1.00,0.88,0.82,0.77,0.75,0.73,0.73,0.72,0.72],
    "Single layer on ladder": [1.00,0.87,0.82,0.80,0.79,0.79,0.79,0.78,0.78]
}

# --- Bảng k1: Ambient air temperature ---
k1_factors = {
    "PVC": {10:1.22,15:1.17,20:1.12,25:1.06,30:1.00,35:0.94,40:0.87,45:0.79,50:0.71,55:0.61,60:0.50},
    "XLPE/EPR": {10:1.15,15:1.12,20:1.08,25:1.04,30:1.00,35:0.96,40:0.91,45:0.87,50:0.82,55:0.76,60:0.71,65:0.65,70:0.58,75:0.50,80:0.41}
}

# --- Bảng k2: Ground temperature ---
k2_factors = {
    "PVC": {10:1.10,15:1.05,20:1.00,25:0.95,30:0.89,35:0.84,40:0.77,45:0.71,50:0.63,55:0.55,60:0.45},
    "XLPE/EPR": {10:1.07,15:1.04,20:1.00,25:0.96,30:0.93,35:0.89,40:0.85,45:0.80,50:0.76,55:0.71,60:0.65,65:0.60,70:0.53,75:0.46,80:0.38}
}

# --- Bảng k3: Soil nature ---
k3_factors = {
    "Very wet soil": 1.21,
    "Wet soil": 1.13,
    "Damp soil": 1.05,
    "Dry soil": 1.00,
    "Very dry soil": 0.86,
    "N/A": 1.00
}

# --- Bảng dây nhôm (Aluminum, single core) ---col4-1pha; col5-tam giác; col6-Đặt sát nhau 1 lớp
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

# --- Bảng dây đồng (Copper, single core, không đi đất) ---B-1 lớp đặt sát;C- tam giác; A-1pha
cable_table_cu = {
    1.5: {"A":28, "B":25, "C":24},
    2.5: {"A":37, "B":34, "C":33},
    4: {"A":52, "B":44, "C":43},
    6: {"A":66, "B":55, "C":52},
    10: {"A":91, "B":79, "C":75},
    16: {"A":118, "B":110, "C":107},
    25: {"A":161, "B":141, "C":135},
    35: {"A":200, "B":176, "C":169},
    50: {"A":242, "B":215, "C":207},
    70: {"A":310, "B":279, "C":268},
    95: {"A":377, "B":341, "C":328},
    120: {"A":437, "B":399, "C":382},
    150: {"A":504, "B":462, "C":443},
    185: {"A":575, "B":531, "C":509},
    240: {"A":679, "B":631, "C":604},
    300: {"A":783, "B":731, "C":699},
    400: {"A":940, "B":880, "C":839},
    500: {"A":1083, "B":1006, "C":958},
    630: {"A":1254, "B":1117, "C":1077},
    800: {"A":1460, "B":1262, "C":1152},
    1000: {"A":1683, "B":1432, "C":1240}
}

# --- Bảng dây đồng có giáp nhôm (Copper armoured, buried) ---B-1 lớp đặt sát;C- tam giác; A-1pha
cable_table_cu_armoured = {
    16: {"A":142, "B":142, "C":135},
    25: {"A":185, "B":185, "C":172},
    35: {"A":226, "B":226, "C":208},
    50: {"A":275, "B":275, "C":235},
    70: {"A":340, "B":340, "C":290},
    95: {"A":405, "B":405, "C":345},
    120: {"A":460, "B":460, "C":390},
    150: {"A":510, "B":510, "C":435},
    185: {"A":580, "B":580, "C":490},
    240: {"A":670, "B":670, "C":560},
    300: {"A":750, "B":750, "C":630},
    400: {"A":830, "B":830, "C":700},
    500: {"A":910, "B":910, "C":770},
    630: {"A":1000, "B":1000, "C":840},
    800: {"A":1117, "B":1117, "C":931},
    1000: {"A":1254, "B":1254, "C":1038}
}

# --- Bảng CXV 1 core---
cable_table_cxv = {
    1.5: {"Rdc": 12.1, "Dia": 5.8},
    2.5: {"Rdc": 7.41, "Dia": 6.2},
    4:   {"Rdc": 4.61, "Dia": 6.8},
    6:   {"Rdc": 3.08, "Dia": 7.3},
    10:  {"Rdc": 1.83, "Dia": 7.5},
    16:  {"Rdc": 1.15, "Dia": 8.4},
    25:  {"Rdc": 0.727, "Dia": 9.9},
    35:  {"Rdc": 0.524, "Dia": 11.0},
    50:  {"Rdc": 0.387, "Dia": 12.3},
    70:  {"Rdc": 0.268, "Dia": 14.2},
    95:  {"Rdc": 0.193, "Dia": 16.0},
    120: {"Rdc": 0.153, "Dia": 17.6},
    150: {"Rdc": 0.124, "Dia": 19.6},
    185: {"Rdc": 0.0991,"Dia": 21.6},
    240: {"Rdc": 0.0754,"Dia": 24.3},
    300: {"Rdc": 0.0601,"Dia": 27.0},
    400: {"Rdc": 0.0470,"Dia": 30.4},
    500: {"Rdc": 0.0366,"Dia": 34.0},
    630: {"Rdc": 0.0283,"Dia": 38.8}
}

# --- Bảng AXV 1 core---
cable_table_axv = {
    10:  {"Rdc": 3.08,  "Dia": 7.5},
    16:  {"Rdc": 1.91,  "Dia": 8.4},
    25:  {"Rdc": 1.20, "Dia": 9.9},
    35:  {"Rdc": 0.868, "Dia": 11.0},
    50:  {"Rdc": 0.641, "Dia": 12.3},
    70:  {"Rdc": 0.443, "Dia": 14.3},
    95:  {"Rdc": 0.320, "Dia": 16.0},
    120: {"Rdc": 0.253, "Dia": 17.6},
    150: {"Rdc": 0.206, "Dia": 19.6},
    185: {"Rdc": 0.164,"Dia": 21.6},
    240: {"Rdc": 0.125,"Dia": 24.3},
    300: {"Rdc": 0.100,"Dia": 27.0},
    400: {"Rdc": 0.0778,"Dia": 30.4},
    500: {"Rdc": 0.0605,"Dia": 34.0},
    630: {"Rdc": 0.0469,"Dia": 38.8}
}

# --- Bảng CB 1 pha ---
cb_table_1p = [6,10,16,20,25,32,40,50,63,80,100,125]

# --- Bảng CB 3 pha ---
cb_table_3p = [6,10,16,20,25,32,40,50,63,75,80,100,125,
               160,175,200,225,250,315,400,500,630,
               800,1000,1250,1600,2000,3200]

# --- HÀM LOGIC (Giữ nguyên) ---
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

# --- GIAO DIỆN WEB (STREAMLIT) ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Thông số nguồn & Tải")
    system_type = st.selectbox("Kiểu hệ thống điện", ["3 pha", "1 pha"])
    power = st.number_input("P – Công suất (kW)", min_value=0.1, value=15.0, step=1.0)
    voltage = st.number_input("U – Điện áp (V)", min_value=110, value=380 if system_type=="3 pha" else 220)
    cos_phi = st.number_input("cosφ – Hệ số công suất", min_value=0.1, max_value=1.0, value=0.85, step=0.05)
    k_du_tru = st.number_input("k_dự trữ (0–1)", min_value=0.1, max_value=1.0, value=0.8, step=0.05)
    conductor_type = st.selectbox("Loại dây dẫn", ["Aluminum", "Copper"])
    length = st.number_input("Chiều dài dây dẫn (m)", min_value=0.0, value=50.0, step=10.0)
    deltaV_allow = st.number_input("ΔV% cho phép", min_value=0.1, value=5.0, step=0.5)

with col2:
    st.subheader("Điều kiện lắp đặt (Hệ số K)")
    arrangement = st.selectbox("k4 – Arrangement", list(reduction_factors.keys()))
    
    # Số sợi song song (Động dựa vào k4 chọn)
    max_circuits = len(reduction_factors[arrangement])
    num_cables = st.number_input("Number of circuits", min_value=1, max_value=max_circuits, value=1)
    
    insul_air = st.selectbox("k1 – insul", list(k1_factors.keys()))
    air_temps = sorted(list(k1_factors[insul_air].keys()))
    temp_air = st.selectbox("AmbT (°C)", air_temps, index=air_temps.index(30) if 30 in air_temps else 0)
    ground_mode = st.selectbox("Vị trí đi cáp", ["Không đi ngầm", "Có đi ngầm dưới đất"])
    if ground_mode == "Không đi ngầm":
        k2 = 1.0
        soil = "N/A"
        k3 = 1.0
    else:
        insul_ground = st.selectbox("k2 – insul", list(k2_factors.keys()))
        
        ground_temps = sorted(list(k2_factors[insul_ground].keys()))
        temp_ground = st.selectbox("Temp (°C)", ground_temps, index=ground_temps.index(20) if 20 in ground_temps else 0)
        k2 = k2_factors[insul_ground].get(temp_ground, 1.0)
        soil = st.selectbox("k3 – Soil nature", [k for k in k3_factors.keys() if k != "N/A"])
        k3 = k3_factors[soil]

# --- TÍNH TOÁN & HIỂN THỊ KẾT QUẢ ---
st.write("---")
if st.button("TÍNH TOÁN KẾT QUẢ", type="primary"):
    k4 = reduction_factors[arrangement][num_cables - 1]
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
    
    # Hiển thị các hệ số K
    st.subheader("1. Các hệ số hiệu chỉnh (IEC)")
    st.info(f"k1 : {k1:.2f} | k2 : {k2:.2f} | k3 : {k3:.2f} | k4 : {k4:.2f}  \n Hệ số tổng hợp K = {K:.2f}")
    
    # Hiển thị dòng điện
    st.subheader("2. Dòng điện tính toán")
    st.warning(f"- Dòng điện tải ban đầu $I_{{tt}}$: {I_tt:.2f} A \n- Dòng điện sau suy giảm $I_{{tt\_k}}$: {I_tt_k:.2f} A \n- Dòng tính toán chọn dây (gồm dự trữ): {I_chon:.2f} A \n- Dòng phân bổ trên mỗi sợi: {I_per_cable:.2f} A")
    
    # Kết quả chọn dây và sụt áp
    st.subheader("3. Chọn Tiết diện Cáp & Thiết bị Bảo vệ")
    
    if area:
        res_text = f"Tiết diện đề xuất ({conductor_type}): {area} mm² (Dòng định mức cáp gốc: {ampacity} A)  \n"
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
            res_text += f"- Sụt áp ước tính: {deltaU:.2f} V ({deltaU_percent:.2f}%)  Nằm trong giới hạn cho phép (≤{deltaV_allow}%)"
        else:
            res_text += f"- Sụt áp ước tính: {deltaU:.2f} V ({deltaU_percent:.2f}%)  VƯỢT QUÁ giới hạn cho phép (>{deltaV_allow}%)"
    else:
        res_text = "Không tìm thấy tiết diện cáp nào phù hợp trong bảng tra dữ liệu có sẵn.  \n"
        
    cb_value = select_cb(I_tt_cb, system_type)
    if cb_value:
        res_text += f"  \n Aptomat (CB) khuyến nghị: {cb_value} A (Hệ thống {system_type})"
    else:
        res_text += f"  \n Không tìm thấy CB phù hợp trong bảng tra."
        
    st.success(res_text)