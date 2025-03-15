import cv2
import numpy as np
import pandas as pd
import os
import winsound  # For sound in Windows
from sklearn.cluster import KMeans
from collections import Counter
from datetime import datetime
import time


def action():
    user_permission = False
    scanned_color_name = ""
    show_message_duration = 5  # Duration to show scanned color message (in seconds)
    last_scan_time = 0

    '''
    color_categories = {
        "Red": (255, 0, 0),
        "Green": (0, 255, 0),
        "Blue": (0, 0, 255),
        "Yellow": (255, 255, 0),
        "Cyan": (0, 255, 255),
        "Magenta": (255, 0, 255),
        "Black": (0, 0, 0),
        "White": (255, 255, 255),
        "Gray": (128, 128, 128),
        "Orange": (255, 165, 0),
        "Purple": (128, 0, 128),
        
    }
    '''
     # Load color categories from CSV file
    color_df = pd.read_csv('rgb.csv')
    color_categories = {
        row['name']: (row['red'], row['green'], row['blue']) for _, row in color_df.iterrows()
    }

    for color in  color_categories.keys():
        os.makedirs(f"sorted_products/{color}", exist_ok=True)

    csv_filename = "sorted_products.csv"
    if not os.path.exists(csv_filename):
        pd.DataFrame(columns=["Timestamp", "Color", "Filename"]).to_csv(csv_filename, index=False)

    def get_nearest_color_category(R, G, B):
        min_dist = float('inf')
        closest_color = "Unknown"
        for color_name, (r, g, b) in color_categories.items():
            dist = np.sqrt((R - r) ** 2 + (G - g) ** 2 + (B - b) ** 2)
            if dist < min_dist:
                min_dist = dist
                closest_color = color_name
        return closest_color

    def get_dominant_color(image, k=3):
        image = cv2.resize(image, (100, 100))
        image = image.reshape(-1, 3)
        kmeans = KMeans(n_clusters=k, n_init=10)
        kmeans.fit(image)
        counts = Counter(kmeans.labels_)
        dominant_color = kmeans.cluster_centers_[max(counts, key=counts.get)]
        return dominant_color

    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        height, width, _ = frame.shape
        x1, y1, x2, y2 = width // 3, height // 3, 2 * width // 3, 2 * height // 3
        scan_box = frame[y1:y2, x1:x2]

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, "Press 'S' to Scan Color", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        if time.time() - last_scan_time < show_message_duration and scanned_color_name:
            cv2.putText(frame, f"Scanned Color: {scanned_color_name}", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)

        cv2.imshow("Color-Based Product Sorting", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('s'):  # User gives permission to scan
            user_permission = True
            winsound.Beep(1000, 200)

        if user_permission:
            dominant_color = get_dominant_color(scan_box)
            R, G, B = int(dominant_color[2]), int(dominant_color[1]), int(dominant_color[0])
            product_color = get_nearest_color_category(R, G, B)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"sorted_products/{product_color}/product_{timestamp}.jpg"
            cv2.imwrite(filename, frame)

            df = pd.read_csv(csv_filename)
            new_entry = pd.DataFrame([{"Timestamp": timestamp, "Color": product_color, "Filename": filename}])
            df = pd.concat([df, new_entry], ignore_index=True)
            df.to_csv(csv_filename, index=False)

            scanned_color_name = product_color  # Store the scanned color name for display
            last_scan_time = time.time()  # Record the scan time

            user_permission = False  # Reset user permission

        if key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    print(f"✅ Sorted products saved in 'sorted_products/' directory.")
    print(f"📂 Log file: {csv_filename}")


action()
