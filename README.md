# Tử Vi Y Học (TuviYly-Web)

Ứng dụng luận giải lá số Tử Vi chuyên sâu về khía cạnh Y học, Sức khỏe và Thọ mệnh, tích hợp Trí tuệ nhân tạo Gemini.

## ✨ Tính năng nổi bật

- **Lập lá số Tử Vi**: Tự động an sao và lập lá số chính xác dựa trên thông tin ngày giờ sinh.
- **Phân tích Y học chuyên sâu**: Tập trung vào thể chất bẩm sinh, các nhóm bệnh tiềm tàng qua các cung Mệnh, Thân, Tật Ách.
- **Luận giải bằng AI**: Sử dụng mô hình Gemini (1.5 Flash/Pro, 2.0 Flash) để phân tích chi tiết từng đại hạn, tiểu hạn và các năm hung họa mạnh nhất.
- **Thiết kế phong cách Y học cổ điển**: Giao diện mang hơi hướng hàn lâm, chuyên nghiệp với tông màu đỏ trầm và giấy cổ.

## 🛠 Công nghệ sử dụng

- **Frontend**: Next.js 15 (App Router), React 19, Tailwind CSS 4.
- **Backend**: Python FastAPI (chạy dưới dạng Vercel Serverless Functions).
- **AI**: Google Gemini API.
- **Font**: Inter & Playfair Display.

## 🚀 Cài đặt và Chạy local

1. **Clone repository**:
   ```bash
   git clone <repository-url>
   cd tuviyly-web
   ```

2. **Cài đặt dependencies**:
   ```bash
   npm install
   pip install -r api/requirements.txt
   ```

3. **Cấu hình biến môi trường**:
   Tạo file `.env.local` ở thư mục gốc và thêm API Key:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

4. **Chạy server phát triển**:
   ```bash
   npm run dev
   ```

5. **Truy cập**: Mở [http://localhost:3000](http://localhost:3000) trên trình duyệt.

## 📋 Lưu ý quan trọng

Các kết quả luận giải từ AI chỉ mang tính chất tham khảo học thuật và giải trí theo triết lý Tử Vi cổ điển. Ứng dụng không thay thế các chẩn đoán, tư vấn hoặc điều trị y khoa chuyên nghiệp. Đương số luôn cần tham vấn ý kiến bác sĩ cho các vấn đề sức khỏe thực tế.

---
Phát triển bởi đội ngũ đam mê Tử Vi & Công nghệ.
