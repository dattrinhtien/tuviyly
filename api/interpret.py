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
        
        prompt_text = f"""
Bạn là chuyên gia luận giải lá số Tử Vi theo hướng chuyên sâu về:
- thân thể
- thể chất bẩm sinh
- bệnh tật
- tai nạn thương tích
- thọ yểu
- các giai đoạn dễ phát bệnh nặng hoặc gặp hung họa

Nhiệm vụ của bạn là phân tích lá số Tử Vi tôi cung cấp theo đúng trọng tâm trên, với phong cách học thuật, chặt chẽ, có dẫn giải rõ căn cứ từng bước. Không trả lời chung chung.

**THÔNG TIN ĐƯƠNG SỐ:**
- Họ tên: {thien_ban.get('ten')}
- Năm sinh: {thien_ban.get('nam_am')} ({thien_ban.get('nam_duong')})
- Bản mệnh: {thien_ban.get('ban_menh')}, Cục: {thien_ban.get('cuc')}
- Chủ mệnh: {thien_ban.get('menh_chu')}, Chủ thân: {thien_ban.get('than_chu')}
- Tương quan: {thien_ban.get('sinh_khac')}

**DỮ LIỆU CÁC CUNG VÀ SAO:**
{cung_info}

**YÊU CẦU PHÂN TÍCH:**

1. Nguyên tắc chung
- Chỉ tập trung vào khía cạnh sức khỏe, bệnh tật, thọ yểu, thương tật, tai nạn, hung họa liên quan thân thể.
- Không sa đà sang công danh, tài lộc, tình cảm, trừ khi có liên hệ trực tiếp đến bệnh tật hoặc sinh tử.
- Không dùng ngôn ngữ mê tín hù dọa; phải phân tích như một hệ thống luận đoán cổ điển có logic nội bộ.
- Không được kết luận tuyệt đối như bác sĩ. Chỉ được nói theo mức độ khả năng, xu hướng mạnh/yếu, nguy cơ cao/thấp.

2. Quy trình phân tích bắt buộc (Hãy đi theo đúng thứ tự sau):

A. Phân tích nền tảng thân thể bẩm sinh
- Xem Mệnh, Thân, Tật Ách, Phúc Đức, Điền Trạch, Phụ Mẫu nếu liên quan.
- Đánh giá thể chất gốc: khỏe/yếu, âm hư/dương hư, dễ hàn/nhiệt, khí huyết mạnh hay suy nếu có thể quy chiếu theo logic Tử Vi.
- Xác định bộ sao chủ về thân thể, sức sống, bệnh tật, thương tích, giải ách, thọ yểu.
- Chỉ rõ sao nào là cát tinh cứu giải, sao nào là hung tinh gây bệnh hao tổn.

B. Phân tích bệnh tật tiềm tàng
- Liệt kê các nhóm bệnh hoặc khuynh hướng bệnh có khả năng nổi bật nhất.
- Ưu tiên phân tích theo từng hệ:
  1) đầu mặt mắt tai mũi họng
  2) tim mạch huyết áp tuần hoàn
  3) hô hấp
  4) tiêu hóa gan mật tỳ vị
  5) thận tiết niệu sinh dục
  6) thần kinh tâm thần mất ngủ
  7) xương khớp cột sống gân cơ
  8) da liễu dị ứng
  9) tai nạn, phẫu thuật, dao kéo, huyết quang
- Với mỗi nhóm, nêu rõ:
  - dấu hiệu sao/cung nào gợi ra
  - mức độ mạnh/yếu
  - là bệnh mãn tính, cấp tính, tái phát hay tai họa đột ngột

C. Phân tích thọ yểu
- Đánh giá xu hướng trường thọ hay tổn thọ.
- Không được phán chết chính xác.
- Chỉ phân tích:
  - nền tảng thọ mệnh mạnh hay yếu
  - yếu tố làm giảm thọ
  - yếu tố cứu giải, kéo dài thọ
  - giai đoạn nào dễ có khủng hoảng sức khỏe nặng

D. Phân tích đại hạn
- Xét toàn bộ các đại hạn và chỉ ra:
  - đại hạn nào tốt cho phục hồi sức khỏe
  - đại hạn nào xấu nhất về bệnh tật, tai nạn, phẫu thuật, huyết quang
  - đại hạn nào có nguy cơ suy kiệt hoặc hung họa mạnh
- Với mỗi đại hạn quan trọng, nêu:
  - tuổi
  - cung đại hạn
  - sao chính, sao phụ, sát tinh, hóa tinh liên quan
  - lý do vì sao đại hạn đó đáng lo hay đáng mừng

E. Phân tích tiểu hạn và lưu niên hung họa mạnh nhất
- Chỉ ra các năm nổi bật nhất về:
  - bệnh nặng
  - tai nạn thương tích
  - mổ xẻ, huyết quang
  - suy kiệt tinh thần thể xác
- Hãy chọn:
  - 3 năm đáng lo nhất trong tiền vận
  - 3 năm đáng lo nhất trong trung vận
  - 3 năm đáng lo nhất trong hậu vận
- Với từng năm, nêu:
  - căn cứ sao/cung/hạn
  - dạng rủi ro thiên về bệnh gì hay tai họa gì
  - mức độ nguy cơ: nhẹ / vừa / cao / rất cao

F. Phân tích sao then chốt
- Hãy dành riêng một mục tổng hợp các sao có ý nghĩa mạnh nhất đối với:
  - bệnh tật
  - thương tích
  - huyết quang
  - yểu mệnh
  - giải ách
  - trường thọ
- Nêu vai trò của từng sao trong lá số cụ thể này, không chỉ định nghĩa lý thuyết chung.

3. Phương pháp lập luận
- Luôn trích rõ:
  - cung nào
  - sao nào
  - bộ sao nào
  - hóa khí nào
  - tương tác nào
- Nếu có mâu thuẫn giữa cát và hung, phải cân đo lực lượng và giải thích bên nào lấn át.
- Nếu chưa đủ dữ liệu để chắc chắn, phải nói rõ mức độ bất định.

4. Định dạng đầu ra bắt buộc
Hãy trả lời theo cấu trúc (Markdown):

I. Tổng quan sức khỏe và thọ mệnh
II. Các dấu hiệu bệnh tật bẩm sinh
III. Các nhóm bệnh nổi bật nhất
IV. Các yếu tố tổn thọ và yếu tố cứu giải
V. Đại hạn quan trọng về bệnh tật và hung họa
VI. Các năm nguy cơ mạnh nhất
VII. Bảng tổng hợp các sao/chỉ dấu quan trọng
VIII. Kết luận ngắn gọn, xếp hạng mức độ rủi ro toàn lá số

5. Thang đánh giá cuối cùng
Cuối bài, cho điểm 10 về các mục:
- nền tảng thể chất
- nguy cơ bệnh mãn tính
- nguy cơ tai nạn thương tích
- nguy cơ huyết quang/phẫu thuật
- mức độ tổn thọ
- khả năng có sao cứu giải

6. Lưu ý quan trọng
- Đây là bài luận đoán Tử Vi mang tính tham khảo học thuật, không thay thế chẩn đoán y khoa.
- Khi nói về bệnh, chỉ dùng ngôn ngữ “xu hướng”, “nguy cơ”, “khả năng”, không khẳng định tuyệt đối.
- Mốc thời gian hiện tại là tháng 4/2026. Hãy dùng mốc này để tính toán các hạn.
"""

        # Danh sách các model tiềm năng (sử dụng tên đầy đủ models/...)
        models_to_try = ['models/gemini-1.5-flash', 'models/gemini-1.5-pro']
        
        # Thử lấy danh sách model thực tế từ tài khoản (Auto-discovery)
        try:
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            if available_models:
                # Đưa các model khả dụng lên đầu danh sách thử nghiệm
                for am in reversed(available_models):
                    if am not in models_to_try:
                        models_to_try.insert(0, am)
        except Exception as e:
            # Nếu không liệt kê được cũng không sao, sẽ dùng danh sách mặc định
            pass

        errors = []
        for model_name in models_to_try:
            try:
                # Sử dụng thư viện SDK chính thức với tên model đầy đủ
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt_text)
                
                if response and response.text:
                    return {"success": True, "interpretation": response.text}
                else:
                    errors.append(f"{model_name}: Không có phản hồi văn bản")
            except Exception as e:
                err_str = str(e)
                errors.append(f"{model_name}: {err_str}")
                
                # Nếu là lỗi hết hạn mức (429), đợi lâu hơn một chút
                if "429" in err_str:
                    time.sleep(3)
                else:
                    time.sleep(1)
                continue
        
        combined_errors = " | ".join(errors)
        return {"success": False, "error": f"AI đang bận hoặc hết hạn mức. Chi tiết: {combined_errors}"}

    except Exception as e:
        return {"success": False, "error": f"Lỗi hệ thống: {str(e)}"}
