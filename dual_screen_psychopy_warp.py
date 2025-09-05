#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 21 11:56:09 2025

@author: yutasuzuki
"""

import json
import numpy as np
import cv2
from psychopy import visual, event, core
import config

def generate_grid_points(width, height, margin=100):
    
    points = []
    grid_w = width - 2 * margin
    grid_h = height - 2 * margin

    for i in range(2):
        for j in range(2):
            x = margin + j * grid_w / 1 - width/2
            y = margin + i * grid_h / 1 - height/2
            points.append([x, y])
    print(points)
    return np.array(points, dtype=np.float32)

def load_points(json_path, default_shape):
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return (np.array(data["original"], dtype=np.float32),
                    np.array(data["adjusted"], dtype=np.float32))
    except:
        print(f"{json_path} 読み込み失敗 → 初期点を生成")
        return generate_grid_points(*default_shape), generate_grid_points(*default_shape)

def save_points(json_path, original, adjusted):
    data = {
        "original": original.tolist(),
        "adjusted": adjusted.tolist()
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Saved: {json_path}")

def apply_homography(img, original_pts, adjusted_pts):
    H, _ = cv2.findHomography(original_pts, adjusted_pts, method=0)
    warped = cv2.warpPerspective(img, H, (img.shape[1], img.shape[0]))
    return warped

def create_image_stim(win, img_cv):
    from PIL import Image
    img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
    pil = Image.fromarray(img_rgb)
    stim = visual.ImageStim(win=win, image=pil, size=win.size)
    return stim

# --- 初期設定 ---
image1_path = "source/colored_whale_image1.png"
image2_path = "source/colored_whale_image2.png"
json1_path = "screen1_points.json"
json2_path = "screen2_points.json"

img1 = cv2.imread(image1_path)
img2 = cv2.imread(image2_path)
img_shape = (img1.shape[1], img1.shape[0])  # width, height

# PsychoPyウィンドウ（別ディスプレイに表示するには screen=0,1 を調整）
win1 = visual.Window(size=img_shape, screen=config.SCREEN_NUM_BLUE, fullscr=True, units='pix')
win2 = visual.Window(size=img_shape, screen=config.SCREEN_NUM_YELLOW, fullscr=True, units='pix')

# キャリブレーション点を読み込み or 初期化
orig1, adj1 = load_points(json1_path, (win1.size[0], win1.size[1]))
orig2, adj2 = load_points(json2_path, (win2.size[0], win2.size[1]))

dragging = None  # (win_idx, point_idx)
threshold = 20

clock = core.Clock()

# --- メインループ ---
while True:
    for iwin, (win, img, orig, adj, json_path) in enumerate([
        (win1, img1, orig1, adj1, json1_path),
        (win2, img2, orig2, adj2, json2_path)
    ]):
        # warp画像生成
        warped = apply_homography(img, orig, adj)
        stim = create_image_stim(win, warped)

        # 描画
        stim.draw()
        for i, pt in enumerate(adj):
            marker = visual.Circle(win, radius=8, pos=pt, fillColor='red')
            label = visual.TextStim(win, text=str(i+1), pos=(pt[0]+10, pt[1]+10), height=14, color='white')
            marker.draw()
            label.draw()

        win.flip()

    # --- 入力処理 ---
    mouse1 = event.Mouse(win=win1)
    mouse2 = event.Mouse(win=win2)

    for win_idx, (mouse, adj) in enumerate([(mouse1, adj1), (mouse2, adj2)]):
        if dragging is None and mouse.getPressed()[0]:
            pos = np.array(mouse.getPos())
            for i, pt in enumerate(adj):
                if np.linalg.norm(pt - pos) < threshold:
                    dragging = (win_idx, i)
                    break

        elif dragging and not mouse.getPressed()[0]:
            dragging = None

        elif dragging:
            win_drag, pt_idx = dragging
            if win_idx == win_drag:
                adj[pt_idx] = mouse.getPos()

    keys = event.getKeys()
    if 'escape' in keys:
        break
    if 's' in keys:
        save_points(json1_path, orig1, adj1)
        save_points(json2_path, orig2, adj2)

# --- 終了処理 ---
win1.close()
win2.close()
core.quit()
