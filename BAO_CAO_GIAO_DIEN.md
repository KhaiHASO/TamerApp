# BÁO CÁO GIAO DIỆN PIX2TEXT

## 📋 TỔNG QUAN

Dự án **Pix2Text** là một công cụ chuyển đổi ký tự toán học viết tay thành LaTeX. Giao diện web được xây dựng bằng **Streamlit** - một framework Python cho phép tạo ứng dụng web một cách nhanh chóng và dễ dàng.

---

## 🎨 MÔ TẢ GIAO DIỆN

### 1. **Thông Tin Dự Án**

**Tiêu đề chính:**
- **Text:** "Công cụ chuyển đổi ký tự toán học viết tay thành LaTeX"
- **Vị trí:** Ở đầu trang, căn giữa, font size lớn (H1)
- **Style:** Center-aligned, bold

**Thông tin tác giả:**
- **Text:** "Tác giả: Phan Hoàng Khải - Lê Minh Nhật - Trần Thị Minh Ánh"
- **Link:** GitHub profile: https://github.com/KhaiHASO
- **Vị trí:** Bên dưới tiêu đề, căn giữa
- **Style:** Center-aligned, có hyperlink

### 2. **Phần Upload Ảnh**

**Tiêu đề phụ:**
- **Text:** "Chọn ảnh cần nhận diện"
- **Component:** `st.subheader()`
- **Vị trí:** Sau phần giới thiệu

**File Uploader:**
- **Component:** `st.file_uploader()`
- **Chức năng:** Cho phép người dùng upload ảnh
- **Định dạng hỗ trợ:** PNG, JPG, JPEG, WEBP
- **Validation:** Dừng chương trình nếu không có file được upload

### 3. **Phần Hiển Thị Kết Quả**

**Ảnh gốc:**
- **Tiêu đề:** "##### Ảnh gốc:"
- **Component:** `st.image()`
- **Layout:** 3 cột (1:3:1), ảnh ở giữa
- **Chức năng:** Hiển thị ảnh mà người dùng đã upload

**Kết quả nhận diện:**
- **Tiêu đề:** "Kết quả nhận diện:"
- **Component:** `st.subheader()`
- **Nội dung:** Hiển thị text đã được nhận diện từ ảnh

**Xử lý kết quả:**
- **Nếu kết quả là string:** Hiển thị trực tiếp text đã nhận diện
- **Nếu kết quả là dictionary:** Hiển thị loại ảnh và nội dung
- **Nếu kết quả là Page object:** Chuyển đổi sang markdown và hiển thị

---

## 🔧 CÔNG NGHỆ SỬ DỤNG

### Frontend Framework
- **Streamlit** - Python web framework
- **Version:** Latest stable
- **Layout:** Wide layout (`st.set_page_config(layout="wide")`)

### Backend Engine
- **Pix2Text** - OCR engine chính
- **Model:** Tự động tải model khi khởi động
- **Cache:** Model được cache để tăng tốc độ xử lý

### Image Processing
- **PIL (Pillow)** - Xử lý ảnh
- **Format:** RGB conversion
- **Temporary file:** Lưu ảnh tạm với tên 'ori.jpg'

---

## 📐 CẤU TRÚC LAYOUT

```
┌─────────────────────────────────────────┐
│  Công cụ chuyển đổi ký tự toán học...   │ ← H1, Center
│  Tác giả: [Link]                        │ ← Center
│                                         │
│  Chọn ảnh cần nhận diện                 │ ← Subheader
│  [File Uploader]                        │
│                                         │
│  ##### Ảnh gốc:                         │
│  [    ] [Ảnh Upload] [    ]             │ ← 1:3:1 Columns
│                                         │
│  Kết quả nhận diện:                     │ ← Subheader
│  [    ] [Nội dung...] [    ]            │ ← 1:3:1 Columns
└─────────────────────────────────────────┘
```

---

## ⚙️ TÍNH NĂNG

### ✅ Tính Năng Đã Implement

1. **Upload Ảnh**
   - Hỗ trợ nhiều định dạng: PNG, JPG, JPEG, WEBP
   - Validation: Kiểm tra file có tồn tại
   - Tự động convert sang RGB

2. **Nhận Diện Text/Formula**
   - Sử dụng model Pix2Text
   - Nhận diện công thức toán học
   - Nhận diện văn bản hỗn hợp
   - Xử lý nhiều kiểu trả về (string, dict, Page object)

3. **Hiển Thị Kết Quả**
   - Hiển thị ảnh gốc
   - Hiển thị text đã nhận diện
   - Format đẹp với layout cân đối

4. **Error Handling**
   - Try-catch để bắt lỗi
   - Hiển thị traceback khi có lỗi
   - User-friendly error messages

### 🔄 Cải Tiến So Với Phiên Bản Gốc

1. **Sửa lỗi 'Page' object is not subscriptable**
   - Thay đổi từ `p2t(img)` sang `p2t.recognize(img, file_type='text_formula', return_text=True)`
   - Xử lý đúng các kiểu trả về khác nhau

2. **Dịch toàn bộ sang tiếng Việt**
   - Tất cả text hiển thị đã được dịch sang tiếng Việt
   - Comments trong code cũng đã được dịch

3. **Cập nhật thông tin tác giả**
   - Thay đổi tác giả thành nhóm sinh viên
   - Cập nhật link GitHub

---

## 🚀 CÁCH SỬ DỤNG

### Cài Đặt Dependencies

```bash
pip install streamlit
pip install pix2text
```

### Chạy Giao Diện

```bash
streamlit run pix2text/app.py
```

### Truy Cập

- **URL:** http://localhost:8501
- **Tự động mở trình duyệt** khi chạy lệnh

### Quy Trình Sử Dụng

1. **Mở giao diện** trên trình duyệt
2. **Upload ảnh** bằng cách click vào file uploader
3. **Chọn file** từ máy tính (PNG, JPG, JPEG, WEBP)
4. **Chờ xử lý** - Model sẽ tự động nhận diện
5. **Xem kết quả** - Text đã nhận diện sẽ hiển thị bên dưới

---

## 📊 FLOW CHART

```
START
  │
  ├─> Hiển thị tiêu đề và thông tin tác giả
  │
  ├─> Hiển thị file uploader
  │
  ├─> Người dùng upload ảnh
  │   │
  │   ├─> Không có file? → STOP
  │   │
  │   └─> Có file? → Tiếp tục
  │
  ├─> Convert ảnh sang RGB
  │
  ├─> Lưu ảnh tạm (ori.jpg)
  │
  ├─> Gọi Pix2Text.recognize()
  │   │
  │   ├─> file_type='text_formula'
  │   └─> return_text=True
  │
  ├─> Xử lý kết quả
  │   │
  │   ├─> String? → Hiển thị trực tiếp
  │   ├─> Dict? → Parse và hiển thị
  │   └─> Page? → Convert sang markdown
  │
  ├─> Hiển thị ảnh gốc
  │
  ├─> Hiển thị kết quả nhận diện
  │
  └─> END
```

---

## 🐛 XỬ LÝ LỖI

### Các Lỗi Đã Được Xử Lý

1. **TypeError: 'Page' object is not subscriptable**
   - **Nguyên nhân:** Code cố truy cập Page object như dictionary
   - **Giải pháp:** Sử dụng `recognize()` với `return_text=True` thay vì `__call__()`

2. **File không tồn tại**
   - **Xử lý:** Kiểm tra `content_file is None` và dừng chương trình

3. **Exception trong quá trình xử lý**
   - **Xử lý:** Try-catch với traceback để debug dễ dàng

### Error Messages

```python
st.error(e)  # Hiển thị lỗi chính
st.error(traceback.format_exc())  # Hiển thị full traceback
```

---

## 📝 CODE STRUCTURE

### Main Components

```python
@st.cache(allow_output_mutation=True)
def get_model():
    """Cache model để tăng tốc"""
    return Pix2Text()

def main():
    """Hàm chính xử lý UI"""
    # 1. Setup model
    # 2. Display header
    # 3. File uploader
    # 4. Process image
    # 5. Display results
```

### Key Functions

1. **`get_model()`** - Cache model, chỉ load 1 lần
2. **`main()`** - Xử lý toàn bộ UI flow
3. **Image processing** - Convert và lưu ảnh
4. **Result handling** - Xử lý các kiểu trả về khác nhau

---

## 🎯 KẾT QUẢ ĐẠT ĐƯỢC

### ✅ Functional Requirements

- [x] Upload ảnh thành công
- [x] Nhận diện text/công thức từ ảnh
- [x] Hiển thị kết quả rõ ràng
- [x] Xử lý lỗi đầy đủ
- [x] UI thân thiện, dễ sử dụng

### ✅ Non-Functional Requirements

- [x] Giao diện tiếng Việt
- [x] Layout đẹp, cân đối
- [x] Performance tốt (model caching)
- [x] Error handling tốt
- [x] Code dễ maintain

---

## 📸 MÔ TẢ GIAO DIỆN (Text-based)

### Header Section
```
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║   Công cụ chuyển đổi ký tự toán học viết tay thành LaTeX ║
║                                                          ║
║   Tác giả: Phan Hoàng Khải - Lê Minh Nhật - Trần Thị    ║
║            Minh Ánh                                       ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
```

### Upload Section
```
┌─────────────────────────────────────────┐
│  Chọn ảnh cần nhận diện                 │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │  [Browse files] hoặc kéo thả ảnh   │ │
│  │  Hỗ trợ: PNG, JPG, JPEG, WEBP     │ │
│  └───────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

### Results Section
```
┌─────────────────────────────────────────┐
│  ##### Ảnh gốc:                         │
│                                         │
│     ┌─────────────────────────┐        │
│     │                         │        │
│     │    [Ảnh đã upload]       │        │
│     │                         │        │
│     └─────────────────────────┘        │
│                                         │
│  Kết quả nhận diện:                     │
│                                         │
│     ┌─────────────────────────┐        │
│     │  Text đã nhận diện:     │        │
│     │  [Kết quả hiển thị ở đây]│        │
│     └─────────────────────────┘        │
└─────────────────────────────────────────┘
```

---

## 🔮 HƯỚNG PHÁT TRIỂN TƯƠNG LAI

### Có Thể Thêm

1. **Download kết quả**
   - Export text ra file .txt
   - Export LaTeX ra file .tex
   - Export markdown

2. **Xử lý nhiều ảnh cùng lúc**
   - Batch upload
   - Progress bar
   - Download kết quả hàng loạt

3. **Cải thiện UI**
   - Dark mode
   - Responsive design
   - Animation khi xử lý

4. **Tính năng nâng cao**
   - So sánh ảnh trước/sau
   - Edit kết quả trực tiếp
   - Preview LaTeX render

---

## 📚 TÀI LIỆU THAM KHẢO

- **Streamlit Documentation:** https://docs.streamlit.io
- **Pix2Text GitHub:** https://github.com/breezedeus/pix2text
- **PIL Documentation:** https://pillow.readthedocs.io

---

## 👥 THÔNG TIN TÁC GIẢ

**Nhóm phát triển:**
- Phan Hoàng Khải
- Lê Minh Nhật  
- Trần Thị Minh Ánh

**GitHub:** https://github.com/KhaiHASO

**Ngày tạo báo cáo:** 2025

---

## ✅ KẾT LUẬN

Giao diện Pix2Text đã được hoàn thiện với các tính năng cơ bản:
- ✅ Upload và xử lý ảnh
- ✅ Nhận diện text/công thức toán học
- ✅ Hiển thị kết quả rõ ràng
- ✅ Xử lý lỗi đầy đủ
- ✅ Giao diện tiếng Việt, thân thiện

Giao diện sẵn sàng để sử dụng và có thể mở rộng thêm các tính năng trong tương lai.

---

**Ngày báo cáo:** 2025  
**Phiên bản:** 1.0  
**Trạng thái:** ✅ Hoàn thành

