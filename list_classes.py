from ultralytics import YOLO

model = YOLO("yolov8n.pt")

for class_id, name in model.names.items():
    print(class_id, name)

print("Total classes:", len(model.names))