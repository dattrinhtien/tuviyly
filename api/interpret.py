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
        
        # Thiết lập cấu hình cho độ dài và sự ổn định
        generation_config = {
            "temperature": 0.4, # Tăng một chút để AI có sự phóng tác thâm thúy
            "top_p": 0.95,
            "max_output_tokens": 12000, # Tăng tối đa độ dài đầu ra
        }

        prompt_text = f"""
Bạn là một Đại sư Tử Vi chuyên về Y Học và Hình Thể, với kiến thức uyên bác về sự tương tác giữa các vì tinh tú và sức khỏe con người. 
Nhiệm vụ của bạn là thực hiện một bài luận giải **CHUYÊN SÂU, CHI TIẾT VÀ DÀI** cho đương số dựa trên dữ liệu lá số được cung cấp.

**THÔNG TIN ĐƯƠNG SỐ:**
- Họ tên: {thien_ban.get('ten')}
- Năm sinh: {thien_ban.get('nam_am')} ({thien_ban.get('nam_duong')})
- Bản mệnh: {thien_ban.get('ban_menh')}, Cục: {thien_ban.get('cuc')}
- Chủ mệnh: {thien_ban.get('menh_chu')}, Chủ thân: {thien_ban.get('than_chu')}
- Tương quan: {thien_ban.get('sinh_khac')}

**DỮ LIỆU CÁC CUNG VÀ SAO:**
{cung_info}

---

**YÊU CẦU LUẬN GIẢI (BẮT BUỘC TUÂN THỦ):**

1. **Phong cách**: Ngôn từ thâm thúy, học thuật, có chiều sâu tâm linh và y học. Tránh trả lời ngắn gọn hay chung chung. Mỗi phần phân tích phải đi kèm **dẫn chứng cụ thể từ bộ sao và cung** (Ví dụ: "Do cung Tật Ách có Kình Dương ngộ Hình nên...").

2. **Cấu trúc bài viết**:

   **I. Tổng quan về Bản thể và Thọ mệnh**: 
   Nhận định về gốc rễ thể chất, sức sống bẩm sinh. Phân tích tương quan giữa Bản mệnh và Cục, Mệnh và Thân để thấy được khả năng chống chọi bệnh tật.

   **II. Phân tích chi tiết Thân thể và Bệnh lý bẩm sinh**:
   - Đi sâu vào cung Mệnh, Thân, Tật Ách, Phúc Đức.
   - Chỉ rõ các bộ sao chủ về bệnh tật hiện diện trong lá số. 
   - Phân tích từng hệ cơ quan (Tuần hoàn, Hô hấp, Tiêu hóa, Thần kinh, Xương khớp...) dựa trên các vì sao tọa thủ. Phải chỉ rõ sao nào gây ra nguy cơ gì.

   **III. Nguy cơ tai nạn, phẫu thuật và thương tật**:
   Phân tích các bộ sao mang tính sát phạt, huyết quang (Kình, Đà, Không, Kiếp, Hình, Hỏa, Linh...) và khả năng cứu giải từ các cát tinh (Quang, Quý, Giải Thần, Thiên Hỷ...).

   **IV. Luận giải Đại hạn 10 năm hiện tại**:
   Đương số đang ở đại hạn nào? Vận trình sức khỏe trong 10 năm này thăng trầm ra sao? Những năm nào trong đại hạn này đáng lo ngại nhất?

   **V. Chi tiết Tiểu hạn 3 năm liên tiếp (Trọng tâm)**:
   Hôm nay là năm 2026. Hãy phân tích chi tiết sức khỏe và rủi ro cho 3 năm:
   - **Năm ngoái (2025 - Ất Tỵ)**: Nhìn lại các vấn đề sức khỏe đã qua để kiểm chứng.
   - **Năm nay (2026 - Bính Ngọ)**: Phân tích cực kỳ chi tiết về nguy cơ bệnh tật, tai nạn trong năm hiện tại. Các tháng nào cần lưu tâm?
   - **Năm tới (2027 - Đinh Mùi)**: Dự báo sớm các rủi ro để đương số có sự chuẩn bị và phòng tránh.

   **VI. Các bộ sao Then chốt và Lời khuyên Y học**:
   Tổng hợp lại các "tội đồ" (hung tinh gây bệnh) và các "vị thần hộ mệnh" (cát tinh cứu giải) trong lá số này. Đưa ra lời khuyên về lối sống, dinh dưỡng hoặc tâm thế dựa trên lý thuyết Tử Vi Y Học.

3. **Lưu ý quan trọng**:
- Không được kết luận tuyệt đối như bác sĩ, chỉ dùng ngôn ngữ xu hướng và rủi ro.
- Bài viết phải **RẤT DÀI VÀ CHI TIẾT**. Hãy viết như một cuốn sách nhỏ dành riêng cho đương số.
- Trích dẫn rõ tên các vì sao khi phân tích.
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
