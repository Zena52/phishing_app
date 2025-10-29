import cv2
import torch

# Load YOLOv5s model (local from ultralytics repo if installed)
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
model.conf = 0.45  # minimum confidence threshold

# Class index for "fish" in COCO (using a generic fallback)
FISH_CLASSES = ["fish", "shark", "sea_lion"]

# Window text styling
FONT = cv2.FONT_HERSHEY_SIMPLEX
COLOR = (0, 255, 255)  # single consistent yellow-ish tone
THICKNESS = 2

# Access webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ Unable to access camera.")
    exit()

print("✅ Camera detected. Press 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Run inference
    results = model(frame)
    df = results.pandas().xyxy[0]

    fish_count = 0

    # Loop detections
    for _, row in df.iterrows():
        class_name = row['name'].lower()

        # Generic match
        if any(c in class_name for c in FISH_CLASSES):
            fish_count += 1

            # Draw bounding box
            x1, y1, x2, y2 = map(int, [row['xmin'], row['ymin'], row['xmax'], row['ymax']])
            conf = row['confidence']

            cv2.rectangle(frame, (x1, y1), (x2, y2), COLOR, THICKNESS)
            label = f"{class_name} {conf:.2f}"
            cv2.putText(frame, label, (x1, y1 - 6), FONT, 0.6, COLOR, 2)

    # Header info UI
    cv2.putText(frame, f"Fish detected: {fish_count}",
                (10, 30), FONT, 0.9, COLOR, 2)

    cv2.imshow("Fish Detector (Press Q to exit)", frame)

    # Quit logic
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
