# Hướng Dẫn Chạy Giao Diện TamerApp

Dự án TamerApp hỗ trợ 2 cách chạy giao diện:

**Giao diện Web Streamlit** (GUI đơn giản, dễ sử dụng)

---

## 1. Cài Đặt Dependencies
```
conda create -n pix2text python=3.9 -y
conda activate pix2text
```
Trước tiên, đảm bảo bạn đã cài đặt các package cần thiết:

```bash
# Cài đặt pix2text

# Nếu cần nhận diện ngôn ngữ khác ngoài tiếng Anh và tiếng Trung

# Cài đặt Streamlit (cho giao diện web)

# Cài đặt FastAPI và uvicorn (cho HTTP service - thường đã có trong pix2text)
pip install pix2text
pip install pix2text[multilingual]
pip install streamlit
pip install fastapi uvicorn
```

---

## 2. Cách 1: Chạy Giao Diện Web Streamlit (GUI)

Đây là giao diện web đơn giản, cho phép upload ảnh và xem kết quả trực tiếp trên trình duyệt.

### Bước 1: Chạy lệnh

```bash
streamlit run TamerApp/app.py
```

Hoặc nếu bạn đang ở thư mục gốc của project:

```bash
streamlit run TamerApp/app.py
```

### Bước 2: Mở trình duyệt

Lệnh trên sẽ tự động mở trình duyệt tại địa chỉ: `http://localhost:8501`

Nếu không tự động mở, bạn có thể truy cập thủ công:
- URL: `http://localhost:8501`
- Hoặc: `http://127.0.0.1:8501`

### Bước 3: Sử dụng

1. Upload ảnh (hỗ trợ: PNG, JPG, JPEG, WEBP)
2. Hệ thống sẽ tự động nhận diện
3. Xem kết quả ngay trên trang web

### Tùy chỉnh Port (nếu cần)

```bash
streamlit run pix2text/app.py --server.port 8502
```

---

