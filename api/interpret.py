import os
import sys
import json
import time
import google.generativeai as genai
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Thiết lập đường dẫn
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.append(CURRENT_DIR)

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Lấy API Key với fallback
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY_TUVI_Y_HOC")

class InterpretInput(BaseModel):
    data: dict

@app.post("/api/interpret")
async def interpret_tuvi(input_data: InterpretInput):
    try:
        if not GEMINI_API_KEY:
            return {"success": False, "error": "Thiếu Gemini API Key."}

        # Cấu hình AI
        api_key = GEMINI_API_KEY.strip()
        genai.configure(api_key=api_key)
        
        data = input_data.data
        thien_ban = data.get("thien_ban", {})
        cung_dict = data.get("cung", {})
        
        # Xây dựng thông tin các cung
        cung_info = "\n".join([f"Cung {v['chu_cung']} ({v['name']}): {', '.join(v['stars'])}" for k, v in cung_dict.items()])
        
        # Thiết lập cấu hình
        generation_config = {
            "temperature": 0.2, # Tăng nhẹ để tránh việc copy-paste lại prompt
            "top_p": 0.9,
            "max_output_tokens": 10000,
        }

        # SYSTEM_INSTRUCTIONS (Chỉ dẫn ngầm - AI không được in ra)
        system_instruction = """
        BẠN LÀ CHUYÊN GIA LUẬN GIẢI TỬ VI Y HỌC. 
        NHIỆM VỤ: PHÂN TÍCH SỨC KHỎE, BỆNH TẬT, TAI NẠN VÀ THỌ MỆNH.
        PHONG CÁCH: CHUYÊN LUẬN, CHẶT CHẼ, CÓ CĂN CỨ SAO/CUNG.
        
        QUY TẮC NGHIÊM NGẶT:
        1. TUYỆT ĐỐI KHÔNG in lại các quy tắc, chỉ dẫn hay tiêu đề hướng dẫn trong phản hồi.
        2. BẮT ĐẦU PHẢN HỒI trực tiếp bằng tiêu đề "PHÂN TÍCH LÁ SỐ TỬ VI - [TÊN ĐƯƠNG SỐ]".
        3. KHÔNG chào hỏi, không xã giao, không dùng lời khen mở đầu.
        4. Mọi kết luận phải dựa trên: Cung liên quan | Sao liên quan | Ý nghĩa suy ra | Mức độ.
        5. KHÔNG bịa thêm dữ liệu không có trong lá số.
        """

        prompt_text = f"""
{system_instruction}

---
DỮ LIỆU ĐƯƠNG SỐ:
- Họ tên: {thien_ban.get('ten')}
- Năm sinh: {thien_ban.get('nam_am')} ({thien_ban.get('nam_duong')})
- Bản mệnh: {thien_ban.get('ban_menh')} | Cục: {thien_ban.get('cuc')}
- Chủ mệnh: {thien_ban.get('menh_chu')} | Chủ thân: {thien_ban.get('than_chu')}
- Tương quan: {thien_ban.get('sinh_khac')}

DỮ LIỆU CUNG VÀ SAO:
{cung_info}

---
HÃY TRÌNH BÀY BÀI LUẬN GIẢI THEO CẤU TRÚC SAU (CHỈ IN RA PHẦN NÀY):

A. TỔNG QUAN NỀN THỂ CHẤT
(Phân tích Mệnh/Thân/Tật/Phúc. Đánh giá lực lượng bẩm sinh, sao chủ sống/suy).

B. CÁC DẤU HIỆU THÂN THỂ VÀ BỘ PHẬN DỄ TỔN THƯƠNG
(Chia theo nhóm: Đầu/Mặt, Tim/Tuần hoàn, Hô hấp, Tiêu hóa, Thận, Thần kinh, Xương khớp... Gắn cụ thể với sao/cung).

C. CÁC XU HƯỚNG BỆNH NỔI BẬT VÀ BỆNH MÃN TÍNH
(Xác định các bệnh trọng tâm nhất của lá số).

D. TAI NẠN, THƯƠNG TÍCH, PHẪU THUẬT, HUYẾT QUANG
(Phân tích các bộ sát tinh hội tụ và yếu tố cứu giải).

E. THỌ MỆNH VÀ YẾU TỐ TỔN THỌ
(Đánh giá xu hướng trường/tổn thọ, các giai đoạn khủng hoảng lớn).

F. PHÂN TÍCH TOÀN BỘ CÁC ĐẠI HẠN (VÒNG ĐỜI 1-90 TUỔI)
(Phân tích từng chặng 10 năm. Với đại hạn hung hiểm, bắt buộc chỉ ra NĂM NÀO và TUỔI NÀO nguy hiểm nhất).

G. PHÂN TÍCH CHI TIẾT 3 NĂM TRỌNG TÂM: 2025, 2026, 2027
(Đánh giá rủi ro, nguy cơ bệnh và căn cứ sao/cung cho từng năm).

H. BẢNG TỔNG HỢP SAO THEN CHỐT
(Chia 3 nhóm: Hung tinh bệnh | Sao mãn tính | Cát tinh cứu giải).

I. KẾT LUẬN 5 Ý NGẮN GỌN
(Tóm lược: Thể chất | Bệnh tật | Tai nạn | Hạn đáng chú ý | Cứu giải).
"""

        # Danh sách các model tiềm năng
        models_to_try = ['models/gemini-1.5-flash', 'models/gemini-1.5-pro']
        
        try:
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            if available_models:
                for am in reversed(available_models):
                    if am not in models_to_try:
                        models_to_try.insert(0, am)
        except:
            pass

        errors = []
        for model_name in models_to_try:
            try:
                model = genai.GenerativeModel(
                    model_name=model_name,
                    generation_config=generation_config
                )
                response = model.generate_content(prompt_text)
                
                if response and response.text:
                    return {"success": True, "interpretation": response.text}
                else:
                    errors.append(f"{model_name}: Không có phản hồi")
            except Exception as e:
                err_str = str(e)
                errors.append(f"{model_name}: {err_str}")
                if "429" in err_str:
                    time.sleep(3)
                else:
                    time.sleep(1)
                continue
        
        combined_errors = " | ".join(errors)
        return {"success": False, "error": f"AI đang bận. Chi tiết: {combined_errors}"}

    except Exception as e:
        return {"success": False, "error": f"Lỗi hệ thống: {str(e)}"}
