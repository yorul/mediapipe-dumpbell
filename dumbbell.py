#参考にしたサイト：https://qiita.com/Kentea/items/98459705cfcbc4fb16e1

import math
import cv2
import sys
import mediapipe as mp
import os

HOME = os.getcwd()

def calculate_distance(landmark1, landmark2):
    return math.sqrt((landmark1.x - landmark2.x)**2 + (landmark1.y - landmark2.y)**2)

def dumbbell_lift_counter(video_path, output_path):
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    mp_pose = mp.solutions.pose

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    max_inference = fps * 3

    lift_count = 0
    frame = 0
    prev_distance = None
    motion = "down"  # 初期状態は下げ動作と仮定
    cooldown = 0  # デバウンス用のクールダウンタイマー

    # VideoWriterオブジェクトの設定
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # MP4フォーマット
    out = cv2.VideoWriter(output_path, fourcc, 30, (frame_width, frame_height))

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                break

            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = pose.process(image)

            # 判定する基準の設定
            if results.pose_landmarks:
                left_shoulder = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]
                left_wrist = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST]
                right_shoulder = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER]
                right_wrist = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST]

                current_distance = min(calculate_distance(left_shoulder, left_wrist), calculate_distance(right_shoulder, right_wrist))

                if prev_distance is not None and cooldown == 0:
                    if motion == "down" and current_distance < prev_distance and current_distance < 0.22:
                        motion = "up"
                    elif motion == "up" and current_distance > prev_distance:
                        motion = "down"
                        lift_count += 1  # 完全な上げ動作が完了したとみなす
                        cooldown = 30  # 30フレームの間、カウントを増やさない

                prev_distance = current_distance

            # クールダウンタイマーの更新
            if cooldown > 0:
                cooldown -= 1

            # Draw the pose annotation on the image.
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            mp_drawing.draw_landmarks(
                image,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
            
            cv2.putText(image,
                        text='Lift count : ' + str(lift_count),
                        org=(10, 40),
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=1.0,
                        color=(0, 255, 0),
                        thickness=3,
                        lineType=cv2.LINE_4)

            out.write(image)  # フレームを動画ファイルに書き込む
            #cv2.imshow('Dumbbell Lift Counter', image)

            #if cv2.waitKey(1) & 0xFF == ord('q'):
            #    break

        cap.release()
        out.release()  # VideoWriterを閉じる
        cv2.destroyAllWindows()

if __name__ == "__main__":
    input_video_path = sys.argv[1]
    output_video_path = sys.argv[2]
    dumbbell_lift_counter(input_video_path, output_video_path)
