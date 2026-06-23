import cv2
from ultralytics import YOLO
from tkinter import *
from PIL import Image, ImageTk
import threading

# KHỞI TẠO MÔ HÌNH
model = YOLO("best.pt")

# Dự đoán với ngưỡng confidence cao hơn
results = model.predict(
    conf=0.7,   # 🔹 Ngưỡng nhận diện
    iou=0.5,    # (tuỳ chỉnh) ngưỡng NMS
    save=True
)

# BIẾN TOÀN CỤC 
camera_running = False
cap = None

#  CỬA SỔ CHÍNH
root = Tk()
root.title("ỨNG DỤNG THỊ GIÁC MÁY TÍNH TRONG PHÂN LOẠI RÁC TÁI CHẾ")
root.geometry("1000x700")
root.config(bg="#F6D39F")

#  HÀM MỞ / DỪNG CAMERA 
def start_camera():
    global camera_running, cap
    if camera_running:
        return
    cap = cv2.VideoCapture(0)
    camera_running = True
    threading.Thread(target=show_camera).start()

def stop_camera():
    global camera_running, cap
    camera_running = False
    if cap:
        cap.release()
    camera_label.config(image="")
    status_label.config(text="Camera đã tắt", fg="black")

def show_camera():
    global camera_running, cap
    while camera_running and cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Nhận dạng bằng YOLO
        results = model(frame)
        annotated_frame = results[0].plot()

        # Chuyển ảnh sang RGB để hiển thị
        cv2image = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)

        camera_label.imgtk = imgtk
        camera_label.config(image=imgtk)

        # Hiển thị nhãn dự đoán (nếu có)
        if len(results[0].boxes) > 0:
            names = results[0].names
            cls_id = int(results[0].boxes.cls[0])
            pred_name = names[cls_id]
            status_label.config(text=f"Nhận dạng: {pred_name}", fg="black")
        else:
            status_label.config(text="Không phát hiện vật thể", fg="red")

    if cap:
        cap.release()

# GIAO DIỆN TIÊU ĐỀ 
title_frame = Frame(root, bg="#FFFFFF")
title_frame.pack(pady=20)

Label(title_frame, text="ỨNG DỤNG THỊ GIÁC MÁY TÍNH TRONG PHÂN LOẠI RÁC TÁI CHẾ", 
      font=("Arial", 20, "bold"), fg="#000000", bg="#FFFFFF").pack()
Label(title_frame, text="Nhóm 03", 
      font=("Arial", 15), bg="#FFFFFF").pack()

#  KHUNG CAMERA 
camera_frame = Frame(root, bg="white", bd=3, relief="sunken")
camera_frame.pack(pady=25)

camera_label = Label(camera_frame)
camera_label.pack()

#  TRẠNG THÁI NHẬN DẠNG 
status_label = Label(root, text="Camera chưa bật", font=("Arial", 15), fg="black", bg="#FFFFFF")
status_label.pack(pady=10)

# 
# NÚT BẤM START / STOP 
button_frame = Frame(root, bg="#FEFEFE")
button_frame.pack(pady=10)

start_btn = Button(button_frame, text="START CAMERA", command=start_camera, 
                   bg="#98A903", fg="white", font=("Arial", 12, "bold"), width=15, height=2)
start_btn.grid(row=0, column=0, padx=10)

stop_btn = Button(button_frame, text="STOP CAMERA", command=stop_camera,
                  bg="#A43F04", fg="white", font=("Arial", 12, "bold"), width=15, height=2)
stop_btn.grid(row=0, column=1, padx=10)

#  CHẠY ỨNG DỤNG 
root.mainloop()
