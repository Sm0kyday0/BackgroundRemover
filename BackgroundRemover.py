import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw
import copy

def open_image():
    global img, img_path, tk_img, tk_img_preview, history
    img_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
    if img_path:
        img = Image.open(img_path).convert("RGBA")
        tk_img = ImageTk.PhotoImage(img.resize((300, 300)))
        history = [img.copy()]
        update_canvas()

def make_transparent_at(x, y):
    global img, history
    if not img:
        messagebox.showerror("Error", "画像を開いてください")
        return

    orig_width, orig_height = img.size
    scale_x = orig_width / 300
    scale_y = orig_height / 300
    orig_x = int(x * scale_x)
    orig_y = int(y * scale_y)

    target_color = img.getpixel((orig_x, orig_y))[:3]

    datas = img.getdata()
    new_data = []
    for item in datas:
        if item[:3] == target_color:
            new_data.append((item[0], item[1], item[2], 0))
        else:
            new_data.append(item)
    img.putdata(new_data)

    history.append(img.copy())
    update_canvas()

def undo():
    global img, history
    if len(history) <= 1:
        messagebox.showinfo("Undo", "これ以上戻せません")
        return
    history.pop()
    img = history[-1].copy()
    update_canvas()

def create_checkerboard(size=10, width=300, height=300):
    board = Image.new("RGBA", (width, height), "white")
    draw = ImageDraw.Draw(board)
    for y in range(0, height, size):
        for x in range(0, width, size):
            if (x//size + y//size) % 2 == 0:
                draw.rectangle([x, y, x+size, y+size], fill=(200,200,200,255))
    return board

def get_preview_image():
    if img is None:
        return None
    preview = img.resize((300,300)).copy()
    checker = create_checkerboard(width=300, height=300)
    preview = Image.alpha_composite(checker, preview)
    return ImageTk.PhotoImage(preview)

def update_canvas():
    global tk_img, tk_img_preview
    canvas.delete("all")
    if img is None:
        return
    tk_img_preview = get_preview_image()
    canvas.create_image(0, 0, anchor="nw", image=tk_img)
    canvas.create_image(310, 0, anchor="nw", image=tk_img_preview)
    canvas.image = tk_img_preview

def on_canvas_click(event):
    if event.x < 300:
        make_transparent_at(event.x, event.y)

def save_image():
    if not img:
        messagebox.showerror("Error", "画像を開いてください")
        return
    save_path = filedialog.asksaveasfilename(defaultextension=".png")
    if save_path:
        img.save(save_path, "PNG")
        messagebox.showinfo("保存完了", f"{save_path} に保存しました")
root = tk.Tk()
root.title("透過ツール")
root.resizable(False, False)
canvas = tk.Canvas(root, width=620, height=300)
canvas.pack()
canvas.bind("<Button-1>", on_canvas_click)
btn_frame = tk.Frame(root)
btn_frame.pack(pady=5)
open_btn = tk.Button(btn_frame, text="画像を開く", command=open_image)
open_btn.pack(side="left", padx=5)
undo_btn = tk.Button(btn_frame, text="戻す", command=undo)
undo_btn.pack(side="left", padx=5)
save_btn = tk.Button(btn_frame, text="保存", command=save_image)
save_btn.pack(side="left", padx=5)

img = None
img_path = None
tk_img = None
tk_img_preview = None
history = []
root.mainloop()
