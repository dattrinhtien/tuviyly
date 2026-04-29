import os
import sys
import json
import requests
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# Thiết lập đường dẫn
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.append(CURRENT_DIR)

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class InterpretInput(BaseModel):
    data: dict

@app.post("/api/interpret")
async def interpret_tuvi(input_data: InterpretInput):
    try:
        data = input_data.data
        thien_ban = data.get("thien_ban", {})
        cung_dict = data.get("cung", {})
        
        # Xây dựng thông tin các cung để gửi cho AI
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

        if not GEMINI_API_KEY:
            return {"success": False, "error": "Thiếu Gemini API Key."}

        # Danh sách các model ổn định
        models = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-2.0-flash']
        
        last_error = ""
        for model in models:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
                payload = {"contents": [{"parts": [{"text": prompt_text}]}]}
                response = requests.post(url, json=payload, timeout=90)
                
                if response.status_code == 200:
                    result = response.json()
                    interpretation = result['candidates'][0]['content']['parts'][0]['text']
                    return {"success": True, "interpretation": interpretation}
                else:
                    error_msg = response.json().get('error', {}).get('message', 'Unknown error')
                    last_error = error_msg
                    continue
            except Exception as e:
                last_error = str(e)
                continue
        
        return {"success": False, "error": f"AI đang bận: {last_error}"}
    except Exception as e:
        return {"success": False, "error": str(e)}
