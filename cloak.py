import cv2
import numpy as np
import time

def create_background(cap, frames = 30):
    print("Capturing Background, please move out of the frame")
    backgrnds = []
    for i in range(frames):
        ret, frame = cap.read()
        if ret:
            backgrnds.append(frame)
        else:
            print(f"Unable to read frame {i+1}/{frames}")
        time.sleep(0.1)
    if backgrnds:
        return np.median(backgrnds, axis=0).astype(np.uint8)
    else:
        raise ValueError("Unable to capture any frames")
    
def create_mask(frame, lower_col1, upper_col1):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_col1, upper_col1)
    # mask2 = cv2.inRange(hsv, lower_col2, upper_col2)
    # mask = cv2.bitwise_or(mask1, mask2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3,3), np.uint8), iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, np.ones((3,3), np.uint8), iterations=1)
    return mask

def apply_cloak(frame, mask, background):
    mask_inv = cv2.bitwise_not(mask)
    fg = cv2.bitwise_and(frame, frame, mask=mask_inv)
    bg = cv2.bitwise_and(background, background, mask=mask)
    return cv2.add(fg, bg)

def main():
    print("OpenCV version:", cv2.__version__)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error, Unable to open Camera")
        return
    
    try:
        background = create_background(cap)
    except ValueError as ex:
        print(f"Error: {ex}")
        cap.release()
        return

    lower_green = np.array([35, 50, 50])
    upper_green = np.array([85, 255, 255])



    print("Starting Main loop, Press e to exit")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error, Could not read frame.")
            time.sleep(1)
            continue
        mask = create_mask(frame, lower_green, upper_green)
        res = apply_cloak(frame, mask, background)

        cv2.namedWindow("resized", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("resized", 700, 700)
        
        cv2.imshow('resized', res)
        if cv2.waitKey(1) & 0xFF == ord('e'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()