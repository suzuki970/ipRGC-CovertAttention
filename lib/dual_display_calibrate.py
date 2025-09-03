import cv2
import numpy as np
import json
from psychopy import visual, event, core

# === 設定 ===
chessboard_image_path = "source/chessboard.png"
captured_photo_path = "source/captured_dual_display.jpg"
json_output_1 = "screen1_points.json"
json_output_2 = "screen2_points.json"
chessboard_size = (5,7)  # マス数 → (交点は3x3)

# === グリッドの理想座標生成 ===
def generate_reference_grid(spacing=200):
    grid = []
    for i in range(chessboard_size[1]):
        for j in range(chessboard_size[0]):
            grid.append([j * spacing, i * spacing])
    return np.array(grid, dtype=np.float32)

# === チェスボード検出処理 ===
def detect_chessboard_corners(gray_img, side="left"):
    
    found, corners = cv2.findChessboardCorners(gray_img, chessboard_size, None)
    if not found:
        raise RuntimeError(f"[{side}] チェスボードが検出できませんでした。")
    
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    corners = cv2.cornerSubPix(gray_img, corners, (11, 11), (-1, -1), criteria)
    return corners.reshape(-1, 2)

# === 補正点をJSONに保存 ===
def save_points_json(json_path, original, adjusted):
    data = {
        "original": original.tolist(),
        "adjusted": adjusted.tolist()
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"保存しました: {json_path}")

# === 2画面にチェスボード画像を表示 ===
def show_chessboard_on_two_displays():
    win1 = visual.Window(screen=1, fullscr=True, color=[1, 1, 1], units='pix')
    win2 = visual.Window(screen=2, fullscr=True, color=[1, 1, 1], units='pix')

    stim1 = visual.ImageStim(win=win1, image=chessboard_image_path, size=win1.size)
    stim2 = visual.ImageStim(win=win2, image=chessboard_image_path, size=win2.size)

    stim1.draw()
    stim2.draw()
    win1.flip()
    win2.flip()

    print("チェスボード画像を2画面に表示中。撮影したら任意のキーを押してください。")
    event.waitKeys()
    win1.close()
    win2.close()

# === 撮影画像からキャリブレーション実行 ===
def calibrate_from_photo(photo_path):
    img = cv2.imread(photo_path)
    if img is None:
        raise FileNotFoundError(f"画像が読み込めません: {photo_path}")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape

    # 左右に分割
    left_img = gray[:, :w//2]
    right_img = gray[:, w//2:]

    # 対応点検出
    corners1 = detect_chessboard_corners(left_img, "左")
    corners2 = detect_chessboard_corners(right_img, "右")

    # 理想グリッド
    ref_grid = generate_reference_grid()

    # JSONに保存
    save_points_json(json_output_1, ref_grid, corners1)
    save_points_json(json_output_2, ref_grid, corners2)

    # 結果を可視化して確認
    vis = img.copy()
    cv2.drawChessboardCorners(vis[:, :w//2], chessboard_size, corners1.reshape(-1, 1, 2), True)
    cv2.drawChessboardCorners(vis[:, w//2:], chessboard_size, corners2.reshape(-1, 1, 2), True)
    cv2.imshow("確認用 - 検出結果", vis)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# === メイン ===
def main():
    show_chessboard_on_two_displays()
    print(f"スマホで撮影後、画像を {captured_photo_path} に保存してください。")
    input("画像の準備ができたら Enter を押してください。")
    calibrate_from_photo(captured_photo_path)

if __name__ == "__main__":
    main()
