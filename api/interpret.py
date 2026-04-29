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
        
        # Thiết lập cấu hình chuyên biệt theo yêu cầu
        generation_config = {
            "temperature": 0.15,
            "top_p": 0.85,
            "max_output_tokens": 10000,
        }

        prompt_text = f"""
Bạn là chuyên gia luận giải Tử Vi theo hướng chuyên sâu về:
- sức khỏe
- thân thể
- bệnh tật
- tai nạn thương tích
- phẫu thuật, huyết quang
- xu hướng thọ yểu
- đại hạn và tiểu hạn liên quan đến bệnh tật

Nhiệm vụ của bạn là phân tích lá số được cung cấp theo phong cách CHUYÊN LUẬN, CHẶT CHẼ, CÓ CĂN CỨ, KHÔNG VĂN CHƯƠNG KHOE MẼ.

========================
I. QUY TẮC BẮT BUỘC
========================

1. Chỉ được phép sử dụng dữ liệu lá số đã cung cấp trong đề bài.
2. Không được bịa thêm sao, cung, bộ sao, hạn, tháng hoặc kết luận không có căn cứ.
3. Nếu dữ liệu không đủ để kết luận, phải ghi rõ: "Không đủ dữ liệu để kết luận chắc hơn".
4. Không được mở đầu bằng các câu xã giao như:
   - "Tuyệt vời"
   - "Dưới đây là"
   - "Hy vọng"
   - "Rất vui"
   - "Một cuốn sách nhỏ"
5. Không dùng giọng văn tâng bốc, huyền bí hóa hoặc kể chuyện lan man.
6. Không kết luận như bác sĩ. Chỉ dùng các từ:
   - xu hướng
   - nguy cơ
   - khả năng
   - mức độ gợi ý
7. Khi nói đến bệnh tật, phải phân loại rõ:
   - bệnh bẩm sinh / nền tảng thể chất
   - bệnh mãn tính / kéo dài
   - bệnh cấp tính / bộc phát
   - tai nạn / thương tích / huyết quang / phẫu thuật
8. Mỗi nhận định bắt buộc phải theo mẫu:
   - Cung liên quan:
   - Sao liên quan:
   - Bộ sao/tổ hợp:
   - Ý nghĩa suy ra:
   - Mức độ mạnh/yếu:
9. Không được chỉ giải nghĩa sao chung chung như sách giáo khoa. Phải gắn vào lá số cụ thể này.
10. Nếu có cát tinh cứu giải, phải nêu rõ yếu tố cứu giải và mức độ giảm hung.
11. Nếu có xung đột giữa hung tinh và cát tinh, phải cân lực hai bên rồi mới kết luận.
12. Không được lặp lại cùng một ý dưới nhiều cách diễn đạt khác nhau.

========================
II. DỮ LIỆU ĐƯƠNG SỐ
========================

- Họ tên: {thien_ban.get('ten')}
- Năm sinh âm: {thien_ban.get('nam_am')}
- Năm sinh dương: {thien_ban.get('nam_duong')}
- Bản mệnh: {thien_ban.get('ban_menh')}
- Cục: {thien_ban.get('cuc')}
- Chủ mệnh: {thien_ban.get('menh_chu')}
- Chủ thân: {thien_ban.get('than_chu')}
- Tương quan sinh khắc: {thien_ban.get('sinh_khac')}

========================
III. DỮ LIỆU CUNG VÀ SAO
========================

{cung_info}

========================
IV. TRÌNH TỰ PHÂN TÍCH BẮT BUỘC
========================

Hãy trả lời đúng theo thứ tự sau:

1. TỔNG QUAN BẢN THỂ VÀ NỀN TẢNG THỂ CHẤT
- Phân tích Mệnh, Thân, Tật Ách, Phúc Đức và các cung liên đới.
- Đánh giá nền tảng thể lực bẩm sinh: khỏe / yếu / hao tổn / dễ bệnh / dễ phục hồi.
- Nêu rõ sao nào chủ sức sống, sao nào chủ suy tổn.

2. THÂN THỂ VÀ NHÓM CƠ QUAN DỄ BỊ ẢNH HƯỞNG
Chia theo nhóm:
- đầu, mặt, mắt, tai, mũi, họng
- tim mạch, huyết áp, tuần hoàn
- hô hấp
- tiêu hóa, gan mật, tỳ vị
- thận, tiết niệu, sinh dục
- thần kinh, tâm thần, mất ngủ
- xương khớp, cột sống, gân cơ
- da liễu, dị ứng
- nội tiết, suy nhược, khí huyết
Với mỗi nhóm:
- chỉ nói khi có căn cứ từ sao/cung
- nêu mức độ: thấp / vừa / cao / rất cao

3. BỆNH TẬT BẨM SINH VÀ XU HƯỚNG BỆNH LÂU DÀI
- Chỉ ra những xu hướng bệnh nổi bật nhất
- Phân biệt cái nào là nền thể chất yếu, cái nào là bệnh dễ tái phát lâu dài

4. NGUY CƠ TAI NẠN, THƯƠNG TÍCH, PHẪU THUẬT, HUYẾT QUANG
- Tập trung vào các bộ sao sát tinh
- Chỉ rõ nguy cơ thiên về:
  - té ngã
  - xe cộ
  - dao kéo, mổ xẻ
  - va chạm, thương tích
  - huyết quang
- Nếu có sao giải cứu thì nói rõ

5. THỌ MỆNH VÀ YẾU TỐ TỔN THỌ
- Không được phán năm chết hoặc tuổi chết cụ thể
- Chỉ được đánh giá:
  - nền tảng trường thọ hay tổn thọ
  - yếu tố làm giảm tuổi thọ
  - yếu tố cứu giải, kéo dài, phục hồi
  - giai đoạn nào dễ khủng hoảng sức khỏe lớn

6. ĐẠI HẠN (VÒNG ĐỜI TỪ 1 ĐẾN 90 TUỔI)
- Phân tích toàn bộ các đại hạn 10 năm trong vòng đời (từ khi sinh ra đến tối đa 90 tuổi).
- Đánh giá chi tiết vận trình sức khỏe, bệnh tật và thọ yểu cho từng chặng 10 năm.
- Xác định rõ các đại hạn hung hiểm nhất về: sinh tử, bệnh nan y, tai nạn thảm khốc.
- ĐẶC BIỆT: Với mỗi đại hạn được xác định là có rủi ro cao (bệnh nặng, tai nạn, hoặc sinh tử), bắt buộc phải truy tìm và chỉ đích danh NĂM NÀO là năm nguy hiểm nhất trong chặng đó (nêu rõ số tuổi và năm cụ thể).
- Với mỗi đại hạn quan trọng, nêu:
  - Khoảng tuổi (ví dụ: 24-33)
  - Cung hạn
  - Các bộ sao chủ chốt (hung/cát)
  - Loại rủi ro chính và mức độ nguy hại

7. TIỂU HẠN / LƯU NIÊN TRỌNG TÂM
Hôm nay là năm 2026.
Phân tích 3 năm:
- 2025
- 2026
- 2027

Với từng năm, bắt buộc nêu:
- mức độ rủi ro tổng quát: thấp / vừa / cao / rất cao
- nguy cơ chính về bệnh gì hoặc tai họa gì
- cung và sao làm căn cứ
- nếu dữ liệu tháng không đủ thì ghi rõ không đủ dữ liệu để chốt tháng

8. TỔNG HỢP SAO THEN CHỐT
Tạo 3 nhóm:
- Hung tinh gây bệnh / tổn thọ / tai nạn
- Sao báo bệnh mãn tính hoặc suy yếu cơ thể
- Cát tinh cứu giải / giảm hung

9. KẾT LUẬN CUỐI
Tóm tắt đúng 5 ý:
- 1 ý về nền thể chất
- 1 ý về bệnh tật nổi bật
- 1 ý về tai nạn / huyết quang
- 1 ý về đại hạn / tiểu hạn đáng chú ý
- 1 ý về yếu tố cứu giải

========================
V. ĐỊNH DẠNG ĐẦU RA
========================

Bắt buộc trả ra theo cấu trúc sau:

A. Tổng quan nền thể chất
B. Các dấu hiệu thân thể và bộ phận dễ tổn thương
C. Các xu hướng bệnh nổi bật
D. Tai nạn, thương tích, phẫu thuật, huyết quang
E. Thọ mệnh và yếu tố tổn thọ
F. Đại hạn quan trọng
G. Phân tích 2025, 2026, 2027
H. Bảng tổng hợp sao then chốt
I. Kết luận 5 ý ngắn gọn

========================
VI. RÀNG BUỘC CUỐI
========================

- Không được dùng lời khen mở đầu.
- Không viết theo phong cách huyền bí sáo rỗng.
- Không nói chung chung.
- Không lặp ý.
- Mỗi kết luận phải gắn với sao và cung.
- Nếu không đủ dữ liệu thì phải thừa nhận không đủ dữ liệu.
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
