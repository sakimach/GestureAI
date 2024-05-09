from flask import Flask, render_template, Response
import cv2
from flask_cors import CORS
import mediapipe
import pyautogui


app = Flask(__name__)
CORS(app)
camera = cv2.VideoCapture(0)
capture_hands = mediapipe.solutions.hands.Hands()
drawing_utils = mediapipe.solutions.drawing_utils
screen_width, screen_height = pyautogui.size()
drawing_option = mediapipe.solutions.drawing_utils

def frames():
    while True:
        s,frame = camera.read()
        imh, imw, _ = frame.shape
        frame = cv2.flip(frame,1)
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        output_hands = capture_hands.process(rgb_image)
        all_hands = output_hands.multi_hand_landmarks

        if all_hands:
            for hand in all_hands:
                drawing_option.draw_landmarks(frame, hand)
                one_hand_landmarks = hand.landmark
                #landmark_list = pre_process_landmark(calc_landmark_list(copy.deepcopy(frame), hand))
                for id, lm in enumerate(one_hand_landmarks):
                    x = int(lm.x * imw)
                    y = int(lm.y * imh)                
                    if id == 8:
                        mouse_x = int(screen_width / imw * x)
                        mouse_y = int(screen_height / imh * y)
                        cv2.circle(frame, (x, y), 10, (0, 255, 255))
                        pyautogui.moveTo(mouse_x, mouse_y)
                        x1 = x
                        y1 = y
                    if id == 4:
                        x2 = x
                        y2 = y
                        cv2.circle(frame, (x, y), 10, (0, 255, 255))
            print(pyautogui.position())
            dist = y2 - y1
            if dist < 30:
                pyautogui.click()
                print("click")
        key = cv2.waitKey(100)
        if not s or key == 27:
            break
        else:
            ret, buffer = cv2.imencode(".jpg", frame)
            frame = buffer.tobytes()
        yield(b'--frame\r\n'
        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')




@app.route("/")
def index():
    return render_template("frontend.html")


@app.route("/video")
def video():
    return Response(frames(), mimetype="multipart/x-mixed-replace; boundary=frame")


if __name__ == "__main__":
    app.run(debug=True, port = "8001")

