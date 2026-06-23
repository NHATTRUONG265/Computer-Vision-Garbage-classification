import cv2
from ultralytics import YOLO
from tkinter import *
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import threading

# KHỞI TẠO MÔ HÌNH
model = YOLO("best1.pt")

# BIẾN TOÀN CỤC
camera_running = False
cap = None
current_mode = None  # 'image', 'video', 'camera'
video_running = False
confidence_threshold = 0.7  # Ngưỡng mặc định
iou_threshold = 0.3  # Ngưỡng NMS - giảm xuống để tách riêng các vật thể

# CỬA SỔ CHÍNH
root = Tk()
root.title("Hệ Thống Phân Loại Rác Tái Chế")
root.geometry("1400x800")
root.config(bg="#f0f4f8")

# FONT CHUNG
FONT_TITLE = ("Segoe UI", 16, "bold")
FONT_NORMAL = ("Segoe UI", 11)
FONT_BUTTON = ("Segoe UI", 10, "bold")

# MÀU SẮC
COLOR_PRIMARY = "#2563eb"
COLOR_SUCCESS = "#10b981"
COLOR_DANGER = "#ef4444"
COLOR_WARNING = "#f59e0b"
COLOR_BG = "#f0f4f8"
COLOR_CARD = "#ffffff"

# ================== HÀNG 1: HEADER ==================
header_frame = Frame(root, bg=COLOR_CARD, height=120, relief="flat", bd=0)
header_frame.pack(fill=X, padx=0, pady=0)
header_frame.pack_propagate(False)

# Tạo grid cho header
header_frame.grid_rowconfigure(0, weight=1)
header_frame.grid_columnconfigure(0, weight=1)
header_frame.grid_columnconfigure(1, weight=2)
header_frame.grid_columnconfigure(2, weight=1)

# LOGO 1 (Trái)
logo1_frame = Frame(header_frame, bg=COLOR_CARD)
logo1_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=15)

try:
    logo1_img = Image.open("VAA.png")
    logo1_img = logo1_img.resize((80, 80), Image.Resampling.LANCZOS)
    logo1_photo = ImageTk.PhotoImage(logo1_img)
    logo1_label = Label(logo1_frame, image=logo1_photo, bg=COLOR_CARD)
    logo1_label.image = logo1_photo
    logo1_label.pack()
except:
    Label(logo1_frame, text="🌱", font=("Arial", 50), bg=COLOR_CARD, fg=COLOR_SUCCESS).pack()

# THÔNG TIN NHÓM (Giữa)
info_frame = Frame(header_frame, bg=COLOR_CARD)
info_frame.grid(row=0, column=1, sticky="nsew")

Label(info_frame, text="HỆ THỐNG PHÂN LOẠI RÁC TÁI CHẾ", 
      font=("Segoe UI", 22, "bold"), fg="#1e293b", bg=COLOR_CARD).pack(pady=(15, 5))
Label(info_frame, text="Sử dụng AI & Computer Vision", 
      font=("Segoe UI", 12), fg="#64748b", bg=COLOR_CARD).pack(pady=(0, 5))
Label(info_frame, text="YOLO Object Detection", 
      font=("Segoe UI", 11, "italic"), fg="#94a3b8", bg=COLOR_CARD).pack()

# LOGO 2 (Phải)
logo2_frame = Frame(header_frame, bg=COLOR_CARD)
logo2_frame.grid(row=0, column=2, sticky="nsew", padx=20, pady=15)

try:
    logo2_img = Image.open("cntt.png")
    logo2_img = logo2_img.resize((80, 80), Image.Resampling.LANCZOS)
    logo2_photo = ImageTk.PhotoImage(logo2_img)
    logo2_label = Label(logo2_frame, image=logo2_photo, bg=COLOR_CARD)
    logo2_label.image = logo2_photo
    logo2_label.pack()
except:
    Label(logo2_frame, text="♻️", font=("Arial", 50), bg=COLOR_CARD).pack()

# ================== HÀNG 2: NỘI DUNG CHÍNH ==================
main_frame = Frame(root, bg=COLOR_BG)
main_frame.pack(fill=BOTH, expand=True, padx=15, pady=(0, 15))

main_frame.grid_rowconfigure(0, weight=1)
main_frame.grid_columnconfigure(0, weight=1, minsize=300)
main_frame.grid_columnconfigure(1, weight=2)
main_frame.grid_columnconfigure(2, weight=2)

# ========== CỘT 1: BẢNG ĐIỀU KHIỂN ==========
control_panel = Frame(main_frame, bg=COLOR_CARD, relief="flat", bd=0)
control_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=0)

# Tiêu đề bảng điều khiển
Label(control_panel, text="⚙️ BẢNG ĐIỀU KHIỂN", 
      font=FONT_TITLE, bg=COLOR_CARD, fg="#1e293b").pack(pady=(20, 15))

# Container cho các nút
buttons_container = Frame(control_panel, bg=COLOR_CARD)
buttons_container.pack(fill=BOTH, expand=True, padx=15, pady=10)

def create_button(parent, text, icon, command, color):
    btn_frame = Frame(parent, bg=COLOR_CARD)
    btn_frame.pack(fill=X, pady=8)
    
    btn = Button(btn_frame, text=f"{icon}  {text}", command=command,
                 bg=color, fg="white", font=FONT_BUTTON,
                 relief="flat", cursor="hand2", 
                 activebackground=color, activeforeground="white",
                 height=2, bd=0)
    btn.pack(fill=X, ipady=8)
    
    # Hiệu ứng hover
    def on_enter(e):
        btn['background'] = adjust_color(color, -20)
    def on_leave(e):
        btn['background'] = color
    
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    
    return btn

def adjust_color(color, amount):
    """Điều chỉnh độ sáng màu"""
    color = color.lstrip('#')
    rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
    rgb = tuple(max(0, min(255, c + amount)) for c in rgb)
    return '#{:02x}{:02x}{:02x}'.format(*rgb)

# CÁC NÚT CHỨC NĂNG
create_button(buttons_container, "Nhận Diện Từ Ảnh", "🖼️", lambda: open_image(), COLOR_PRIMARY)
create_button(buttons_container, "Nhận Diện Từ Video", "🎥", lambda: open_video(), COLOR_WARNING)

# Nút Camera đặc biệt
camera_btn_frame = Frame(buttons_container, bg=COLOR_CARD)
camera_btn_frame.pack(fill=X, pady=8)

camera_btn = Button(camera_btn_frame, text="📷  Bật Camera", command=lambda: toggle_camera(),
                    bg=COLOR_SUCCESS, fg="white", font=FONT_BUTTON,
                    relief="flat", cursor="hand2", height=2, bd=0)
camera_btn.pack(fill=X, ipady=8)

# Thông tin hướng dẫn
info_frame = Frame(control_panel, bg="#e0f2fe", relief="flat", bd=0)
info_frame.pack(fill=X, padx=15, pady=20, ipady=10)

Label(info_frame, text="💡 HƯỚNG DẪN", 
      font=("Segoe UI", 10, "bold"), bg="#e0f2fe", fg="#0369a1").pack(pady=(10, 5))
Label(info_frame, text="• Chọn chức năng bên trên\n• Xem ảnh/video gốc ở giữa\n• Kết quả hiển thị bên phải",
      font=("Segoe UI", 9), bg="#e0f2fe", fg="#075985", justify=LEFT).pack(padx=10, pady=(0, 10))

# Cài đặt ngưỡng nhận diện
threshold_frame = Frame(control_panel, bg="#fef3c7", relief="flat", bd=0)
threshold_frame.pack(fill=X, padx=15, pady=(0, 15), ipady=15)

Label(threshold_frame, text="⚙️ NGƯỠNG NHẬN DIỆN", 
      font=("Segoe UI", 10, "bold"), bg="#fef3c7", fg="#92400e").pack(pady=(10, 5))

# Slider
threshold_slider_frame = Frame(threshold_frame, bg="#fef3c7")
threshold_slider_frame.pack(fill=X, padx=15, pady=5)

threshold_value_label = Label(threshold_slider_frame, text=f"{int(confidence_threshold*100)}%", 
                             font=("Segoe UI", 11, "bold"), bg="#fef3c7", fg="#92400e")
threshold_value_label.pack()

def update_threshold(val):
    global confidence_threshold
    confidence_threshold = float(val) / 100
    threshold_value_label.config(text=f"{int(confidence_threshold*100)}%")

threshold_slider = Scale(threshold_slider_frame, from_=10, to=95, 
                        orient=HORIZONTAL, command=update_threshold,
                        bg="#fef3c7", fg="#92400e", troughcolor="#fde68a",
                        highlightthickness=0, relief="flat", 
                        sliderlength=25, width=15)
threshold_slider.set(70)
threshold_slider.pack(fill=X, pady=5)

Label(threshold_frame, text="Thấp: nhiều kết quả | Cao: chính xác hơn",
      font=("Segoe UI", 8), bg="#fef3c7", fg="#78350f", justify=CENTER).pack(pady=(0, 10))

# Cài đặt IOU threshold (NMS)
iou_frame = Frame(control_panel, bg="#e0f2fe", relief="flat", bd=0)
iou_frame.pack(fill=X, padx=15, pady=(0, 20), ipady=15)

Label(iou_frame, text="🎯 ĐỘ CHỒNG CHÉO (IOU)", 
      font=("Segoe UI", 10, "bold"), bg="#e0f2fe", fg="#0369a1").pack(pady=(10, 5))

# Slider IOU
iou_slider_frame = Frame(iou_frame, bg="#e0f2fe")
iou_slider_frame.pack(fill=X, padx=15, pady=5)

iou_value_label = Label(iou_slider_frame, text=f"{int(iou_threshold*100)}%", 
                        font=("Segoe UI", 11, "bold"), bg="#e0f2fe", fg="#0369a1")
iou_value_label.pack()

def update_iou(val):
    global iou_threshold
    iou_threshold = float(val) / 100
    iou_value_label.config(text=f"{int(iou_threshold*100)}%")

iou_slider = Scale(iou_slider_frame, from_=10, to=80, 
                   orient=HORIZONTAL, command=update_iou,
                   bg="#e0f2fe", fg="#0369a1", troughcolor="#bfdbfe",
                   highlightthickness=0, relief="flat", 
                   sliderlength=25, width=15)
iou_slider.set(30)
iou_slider.pack(fill=X, pady=5)

Label(iou_frame, text="Thấp: tách riêng vật | Cao: gộp vật gần nhau",
      font=("Segoe UI", 8), bg="#e0f2fe", fg="#075985", justify=CENTER).pack(pady=(0, 10))

# ========== CỘT 2: ẢNH/VIDEO GỐC ==========
original_panel = Frame(main_frame, bg=COLOR_CARD, relief="flat", bd=0)
original_panel.grid(row=0, column=1, sticky="nsew", padx=5, pady=0)

Label(original_panel, text="📥 NGUỒN GỐC", 
      font=FONT_TITLE, bg=COLOR_CARD, fg="#1e293b").pack(pady=(20, 10))

original_frame = Frame(original_panel, bg="#e2e8f0", relief="sunken", bd=2)
original_frame.pack(fill=BOTH, expand=True, padx=15, pady=(0, 20))

original_label = Label(original_frame, text="Chưa có dữ liệu\n\n📂 Chọn ảnh/video hoặc bật camera",
                      font=FONT_NORMAL, bg="#e2e8f0", fg="#64748b")
original_label.pack(expand=True)

# ========== CỘT 3: KẾT QUẢ PHÂN LOẠI ==========
result_panel = Frame(main_frame, bg=COLOR_CARD, relief="flat", bd=0)
result_panel.grid(row=0, column=2, sticky="nsew", padx=(10, 0), pady=0)

Label(result_panel, text="✅ KẾT QUẢ PHÂN LOẠI", 
      font=FONT_TITLE, bg=COLOR_CARD, fg="#1e293b").pack(pady=(20, 10))

result_frame = Frame(result_panel, bg="#e2e8f0", relief="sunken", bd=2)
result_frame.pack(fill=BOTH, expand=True, padx=15, pady=(0, 10))

result_label = Label(result_frame, text="Đang chờ phân tích...\n\n🤖 AI sẽ xử lý và hiển thị kết quả ở đây",
                    font=FONT_NORMAL, bg="#e2e8f0", fg="#64748b")
result_label.pack(expand=True)

# Thông tin trạng thái
status_frame = Frame(result_panel, bg="#dcfce7", relief="flat", bd=0)
status_frame.pack(fill=X, padx=15, pady=(0, 20), ipady=8)

status_label = Label(status_frame, text="⏳ Sẵn sàng", 
                    font=("Segoe UI", 10, "bold"), bg="#dcfce7", fg="#166534")
status_label.pack()

# ================== CÁC HÀM XỬ LÝ ==================

def resize_image(image, max_width=500, max_height=550):
    """Resize ảnh giữ tỷ lệ"""
    width, height = image.size
    ratio = min(max_width/width, max_height/height)
    new_size = (int(width*ratio), int(height*ratio))
    return image.resize(new_size, Image.Resampling.LANCZOS)

def open_image():
    """Xử lý ảnh từ file"""
    global current_mode
    stop_all()
    current_mode = 'image'
    
    file_path = filedialog.askopenfilename(
        title="Chọn ảnh",
        filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")]
    )
    
    if not file_path:
        return
    
    try:
        status_label.config(text="⏳ Đang xử lý ảnh...", bg="#fef3c7", fg="#92400e")
        root.update()
        
        # Hiển thị ảnh gốc
        img_original = Image.open(file_path)
        img_original_resized = resize_image(img_original)
        img_original_tk = ImageTk.PhotoImage(img_original_resized)
        
        original_label.config(image=img_original_tk, text="")
        original_label.image = img_original_tk
        
        # Nhận diện YOLO
        frame = cv2.imread(file_path)
        results = model(frame, conf=confidence_threshold, iou=iou_threshold, max_det=10)
        annotated_frame = results[0].plot()
        
        # Hiển thị kết quả
        img_result = Image.fromarray(cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB))
        img_result_resized = resize_image(img_result)
        img_result_tk = ImageTk.PhotoImage(img_result_resized)
        
        result_label.config(image=img_result_tk, text="")
        result_label.image = img_result_tk
        
        # Cập nhật trạng thái
        if len(results[0].boxes) > 0:
            names = results[0].names
            detected = [names[int(box.cls)] for box in results[0].boxes]
            status_label.config(text=f"✅ Phát hiện: {', '.join(set(detected))}", 
                              bg="#dcfce7", fg="#166534")
        else:
            status_label.config(text="⚠️ Không phát hiện vật thể", bg="#fee2e2", fg="#991b1b")
            
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể xử lý ảnh: {str(e)}")
        status_label.config(text="❌ Lỗi xử lý", bg="#fee2e2", fg="#991b1b")

def open_video():
    """Xử lý video từ file"""
    global current_mode, video_running, cap
    stop_all()
    current_mode = 'video'
    
    file_path = filedialog.askopenfilename(
        title="Chọn video",
        filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv")]
    )
    
    if not file_path:
        return
    
    cap = cv2.VideoCapture(file_path)
    video_running = True
    status_label.config(text="▶️ Đang phát video...", bg="#dbeafe", fg="#1e40af")
    
    threading.Thread(target=process_video, daemon=True).start()

def process_video():
    """Xử lý từng frame của video"""
    global video_running, cap
    
    while video_running and cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            video_running = False
            status_label.config(text="⏹️ Video kết thúc", bg="#e0e7ff", fg="#4338ca")
            break
        
        # Hiển thị frame gốc
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_original = Image.fromarray(frame_rgb)
        img_original_resized = resize_image(img_original)
        img_original_tk = ImageTk.PhotoImage(img_original_resized)
        
        original_label.config(image=img_original_tk, text="")
        original_label.image = img_original_tk
        
        # Nhận diện YOLO
        results = model(frame, conf=confidence_threshold, iou=iou_threshold, max_det=10)
        annotated_frame = results[0].plot()
        
        # Hiển thị kết quả
        img_result = Image.fromarray(cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB))
        img_result_resized = resize_image(img_result)
        img_result_tk = ImageTk.PhotoImage(img_result_resized)
        
        result_label.config(image=img_result_tk, text="")
        result_label.image = img_result_tk
        
        # Cập nhật trạng thái
        if len(results[0].boxes) > 0:
            names = results[0].names
            detected = [names[int(box.cls)] for box in results[0].boxes]
            status_label.config(text=f"✅ Phát hiện: {', '.join(set(detected))}", 
                              bg="#dcfce7", fg="#166534")
        
        cv2.waitKey(30)
    
    if cap:
        cap.release()

def toggle_camera():
    """Bật/tắt camera"""
    global camera_running, cap, current_mode
    
    if camera_running:
        stop_camera()
    else:
        stop_all()
        current_mode = 'camera'
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            messagebox.showerror("Lỗi", "Không thể mở camera!")
            return
        
        camera_running = True
        camera_btn.config(text="⏹️  Tắt Camera", bg=COLOR_DANGER)
        status_label.config(text="📹 Camera đang hoạt động", bg="#dbeafe", fg="#1e40af")
        
        threading.Thread(target=process_camera, daemon=True).start()

def process_camera():
    """Xử lý camera realtime"""
    global camera_running, cap
    
    while camera_running and cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Hiển thị frame gốc
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_original = Image.fromarray(frame_rgb)
        img_original_resized = resize_image(img_original)
        img_original_tk = ImageTk.PhotoImage(img_original_resized)
        
        original_label.config(image=img_original_tk, text="")
        original_label.image = img_original_tk
        
        # Nhận diện YOLO
        results = model(frame, conf=confidence_threshold, iou=iou_threshold, max_det=10)
        annotated_frame = results[0].plot()
        
        # Hiển thị kết quả
        img_result = Image.fromarray(cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB))
        img_result_resized = resize_image(img_result)
        img_result_tk = ImageTk.PhotoImage(img_result_resized)
        
        result_label.config(image=img_result_tk, text="")
        result_label.image = img_result_tk
        
        # Cập nhật trạng thái
        if len(results[0].boxes) > 0:
            names = results[0].names
            detected = [names[int(box.cls)] for box in results[0].boxes]
            status_label.config(text=f"✅ Phát hiện: {', '.join(set(detected))[:50]}", 
                              bg="#dcfce7", fg="#166534")
        else:
            status_label.config(text="⏳ Đang quét...", bg="#fef3c7", fg="#92400e")
    
    if cap:
        cap.release()

def stop_camera():
    """Dừng camera"""
    global camera_running, cap
    camera_running = False
    
    if cap:
        cap.release()
    
    camera_btn.config(text="📷  Bật Camera", bg=COLOR_SUCCESS)
    status_label.config(text="⏹️ Camera đã tắt", bg="#e0e7ff", fg="#4338ca")

def stop_all():
    """Dừng tất cả"""
    global camera_running, video_running, cap
    
    camera_running = False
    video_running = False
    
    if cap:
        cap.release()
        cap = None
    
    camera_btn.config(text="📷  Bật Camera", bg=COLOR_SUCCESS)
    
    # Reset hiển thị
    original_label.config(image="", text="Chưa có dữ liệu\n\n📂 Chọn ảnh/video hoặc bật camera")
    result_label.config(image="", text="Đang chờ phân tích...\n\n🤖 AI sẽ xử lý và hiển thị kết quả ở đây")
    status_label.config(text="⏳ Sẵn sàng", bg="#dcfce7", fg="#166534")

# Xử lý đóng cửa sổ
def on_closing():
    stop_all()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

# CHẠY ỨNG DỤNG
root.mainloop()