# Hệ Thống Phân Loại Rác Tái Chế

Phiên bản GUI và demo dùng YOLO 8 (ultralytics) để phát hiện và phân loại rác
tái chế từ ảnh, video và camera.

## Mô tả nhanh

- Ứng dụng dùng mô hình YOLO 8 đã huấn luyện (file weights) để nhận diện rác
  (Chai, lon, cốc, giấy).
- Có hai script GUI trong repository: giao diện đầy đủ (`final.py`) và phiên bản
  đơn giản (`basic.py`).

## Nội dung file

- File trọng số mô hình (Sử dụng GG Colab để train)
  - `best.pt` - model weights (dùng bởi `basic.py`)
  - `best1.pt` - model weights (dùng bởi `final.py`)

- Ứng dụng và giao diện:
  - Ứng dụng GUI chính (Tkinter). Hỗ trợ mở ảnh, mở video, stream camera, điều
    chỉnh ngưỡng confidence và IOU, hiển thị ảnh gốc và ảnh đã chú thích.
  - Phiên bản đơn giản hơn: nút START/STOP camera, hiển thị nhãn dự đoán trực
    tiếp.

## Yêu cầu

- Python 3.8+
- Thư viện chính:
  - `ultralytics` (API YOLO của Ultralytics)
  - `opencv-python`
  - `Pillow`
- PyTorch: `ultralytics` yêu cầu `torch` (PyTorch).

## Cài đặt nhanh (Windows)

1. Tạo và kích hoạt virtual environment:

```bash
python -m venv venv
venv\Scripts\activate
```

2. Cài các thư viện:

```bash
pip install ultralytics opencv-python pillow
```

## Chạy ứng dụng

- Chạy GUI đầy đủ:

```bash
python final.py
```

- Chạy phiên bản đơn giản:

```bash
python basic.py
```

Lưu ý: đường dẫn `best.pt` / `best1.pt` trong file phải chính xác.
