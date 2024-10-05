import cv2
import os
import numpy as np
from ultralytics import YOLO
import paho.mqtt.client as mqtt
import torch
import base64
from datetime import datetime

from mail import sendEmail

def runElephantDetection():
    # MQTT connection functions (unchanged)
    def on_connect(client, userdata, flags, reason_code, properties):
        print(f"Connected with result code {reason_code}")
        client.subscribe("topic/topic1")

    def on_message(client, userdata, msg):
        print(str(msg.payload))

    def send_message(client, topic, message):
        result = client.publish(topic, message)
        status = result[0]
        if status == 0:
            print(f"Message '{message}' sent to topic '{topic}'")
        else:
            print(f"Failed to send message to topic '{topic}'")

    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message
    mqttc.connect("broker.hivemq.com", 1883, 60)

    # Video input/output settings
    video_path = 'input4.mp4'
    video_path_out = '{}_out.mp4'.format(video_path)

    # Open video and get frame size
    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()
    H, W, _ = np.shape(frame)
    frame = cv2.resize(frame, (640, 480))
    savedFrame=frame

    # Detection-related variables
    recodedElephants = 0
    elephantsRecordedThreshold = 30
    elephantDetected = False
    elephantExitCount = 0

    recodedDangerEvents = 0
    dangerRecordedThreshold = 3

    # Reference bounding box width and distance for distance estimation
    REFERENCE_BBOX_WIDTH = 300
    REFERENCE_DISTANCE = 10

    def calculate_distance(bbox_width, reference_width, reference_distance):
        """Estimate the distance of the elephant based on the bounding box width."""
        if bbox_width == 0:
            return float('inf')
        return reference_distance * (reference_width / bbox_width)

    # New variables to store bounding boxes
    elephants = []
    humans = []

    try:
        out = cv2.VideoWriter(video_path_out, cv2.VideoWriter_fourcc(*'MP4V'), int(cap.get(cv2.CAP_PROP_FPS)), (W, H))

        if torch.cuda.is_available():
            device = torch.device('cuda')
            print("GPU detected")
        else:
            device = torch.device('cpu')
            print("GPU not detected, using CPU")

        model_path = "best3.pt"
        model = YOLO(model_path).to(device)

        threshold = 0.5
        allowed_class_idsDic = {0: 'Human', 20: "Elephant"}
        allowed_class_ids = list(allowed_class_idsDic.keys())

        proximity_threshold = 250  # Set a pixel threshold for proximity

        while ret:
            frame = cv2.resize(frame, (640, 480))
            # savedFrame=frame

            current_time = cv2.getTickCount()
            results = model.predict(source=frame, device=device, classes=allowed_class_ids)[0]
            
            elephants = []
            humans = []

            for result in results.boxes.data.tolist():
                x1, y1, x2, y2, score, class_id = result

                if score > threshold and class_id in allowed_class_ids:

                    # Increment elephant detection counter
                    if recodedElephants == elephantsRecordedThreshold:
                        print('true message⏭')
                        elephantDetected = True
                        recodedElephants = 1  # Reset count after detection
                        send_message(mqttc, "sliitelp/detect", "true")
                    else:
                        recodedElephants += 1


                    bbox_width = x2 - x1
                    distance = calculate_distance(bbox_width, REFERENCE_BBOX_WIDTH, REFERENCE_DISTANCE)

                    center_x = (x1 + x2) / 2
                    center_y = (y1 + y2) / 2

                    # Store elephants and humans bounding boxes and centers
                    if class_id == 20:  # Elephant class
                        elephants.append((x1, y1, x2, y2, center_x, center_y))
                    elif class_id == 0:  # Human class
                        humans.append((x1, y1, x2, y2, center_x, center_y))

                    # Default label color: green
                    label_color = (0, 255, 0)

                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), label_color, 4)

                    if (class_id == 0):  # Human
                        cv2.putText(frame, f"{allowed_class_idsDic[class_id]}", 
                                    (int(x1), int(y1 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 1.3, label_color, 3)
                    else:  # Elephant
                        cv2.putText(frame, f"{allowed_class_idsDic[class_id]} {distance:.2f}m", 
                                    (int(x1), int(y1 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 1.3, label_color, 3)

            # Check proximity between elephants and humans
            danger_detected = False
            for (ex1, ey1, ex2, ey2, ecx, ecy) in elephants:
                for (hx1, hy1, hx2, hy2, hcx, hcy) in humans:
                    distance_between_centers = np.sqrt((ecx - hcx)**2 + (ecy - hcy)**2)
                    if distance_between_centers < proximity_threshold:
                        # Set bounding boxes to red when danger is detected
                        cv2.rectangle(frame, (int(ex1), int(ey1)), (int(ex2), int(ey2)), (0, 0, 255), 4)
                        cv2.rectangle(frame, (int(hx1), int(hy1)), (int(hx2), int(hy2)), (0, 0, 255), 4)

                        # Change label text color to red
                        label_color = (0, 0, 255)

                        # Update the text to red for danger labels
                        cv2.putText(frame, f"{allowed_class_idsDic[20]} {calculate_distance(ex2-ex1, REFERENCE_BBOX_WIDTH, REFERENCE_DISTANCE):.2f}m", 
                                    (int(ex1), int(ey1 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 1.3, label_color, 3)
                        cv2.putText(frame, f"{allowed_class_idsDic[0]}", 
                                    (int(hx1), int(hy1 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 1.3, label_color, 3)

                        # Display danger message
                        cv2.putText(frame, "DANGER!", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                      
                        # Increment elephant detection counter
                        if recodedDangerEvents == dangerRecordedThreshold:
                            recodedDangerEvents = 1 

                            

                            # Convert the encoded image to a Base64 string
                            img_base64 = base64.b64encode(buffer).decode('utf-8')

                            # Create the data URL format for embedding in HTML
                            data_url = f"data:image/jpeg;base64,{img_base64}"
                            sendEmail(data_url)

                        else:
                            recodedDangerEvents += 1
                      
                      
                        # Save the frame as a Data URL
                        _, buffer = cv2.imencode('.png', savedFrame)
                        img_str = base64.b64encode(buffer).decode('utf-8')
                        data_url = f"data:image/png;base64,{img_str}"

                        # Generate timestamp for filename
                        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
                        filename = f"danger_frame-{timestamp}.txt"

                        # Write the Data URL to a text file
                        # with open(filename, "a") as f:
                        #     f.write(data_url + "\n")

                        danger_detected = True

            if len(results.boxes.data.tolist()) == 0 and elephantDetected and elephantExitCount == 15:
                elephantExitCount = 0
                elephantDetected = False
                send_message(mqttc, "sliitelp/detect", "false")
            elephantExitCount += 1

            time_diff = (cv2.getTickCount() - current_time) / cv2.getTickFrequency()
            fps = 1 / time_diff
            cv2.putText(frame, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            cv2.imshow('Frame', frame)
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break

            out.write(frame)
            ret, frame = cap.read()

        cap.release()
        out.release()
        cv2.destroyAllWindows()

    except Exception as e:
        print(f"An error occurred: {e}")

# Call the function to run the detection
# runElephantDetection()
