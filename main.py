from tkinter import *
from tkinter.filedialog import askopenfilename, askopenfilenames, askdirectory
import tkinter.font as tkFont
from tkinter import messagebox
from PIL import ImageTk
import os
from img_processing import *

WTM_PREVIEW_SIZE = (400, 400)
IMG_PREVIEW_SIZE = (800, 800)
DEFAULT_RESIZE_FACTOR = 1/6
# NAME_EXTENSION = "_modified"
window = Tk()


watermark_path = ""
watermark_pil_img = Image.Image()
watermark_pil_prev = Image.Image()
watermark_tk_img = PhotoImage()
wtm_canvas_id = 0
wtm_options = {
    'resize_factor': DEFAULT_RESIZE_FACTOR,
    'opacity': 1.0,
    'rotation': 0,
    'position': 'Bottom Right'
}

# ----- Variables for images
list_img_paths = []
img_path = ""
selec_img_pil = Image.Image()
selec_img_pil_prev = Image.Image()
selec_img_tk = PhotoImage()
img_canvas_id = 0
modif_img_pil = Image.Image()


def select_watermark():
    global watermark_path
    global watermark_pil_img
    global watermark_pil_prev
    global watermark_tk_img
    global img_canvas_id
    watermark_path = askopenfilename()
    watermark_pil_img = Image.open(watermark_path)
    watermark_pil_prev = watermark_pil_img.copy()
    # Using .thumbnail rather than .resize, because it keeps the aspect ratio
    watermark_pil_prev.thumbnail(WTM_PREVIEW_SIZE)
    width, height = watermark_pil_prev.size
    watermark_tk_img = ImageTk.PhotoImage(watermark_pil_prev)
    canvas.delete("all")
    canvas.config(width=width, height=height)
    img_canvas_id = canvas.create_image(int(width / 2), int(height / 2), image=watermark_tk_img)


def select_images():
    if not watermark_path:
        messagebox.showinfo(message="Please select a watermark first, before selecting images.",
                            title="Select Images")
    else:
        global list_img_paths
        new_img_paths = askopenfilenames()
        for path in new_img_paths:
            if path not in list_img_paths:
                list_img_paths.append(path)
                # Getting the file names for the listbox
                img_name = os.path.basename(path)
                files_listbox.insert(END, img_name)


def preview_img(event):
    global img_path
    global selec_img_pil
    img_name = files_listbox.get(files_listbox.curselection())
    for path in list_img_paths:
        if img_name in path:
            img_path = path
    selec_img_pil = Image.open(img_path)
    update_img()


def update_img():
    global img_path
    global selec_img_pil_prev
    global selec_img_tk
    global img_canvas_id
    global modif_img_pil
    # Adding the watermark, with the custom options
    modif_img_pil = add_wtm(watermark_pil_img, selec_img_pil, wtm_options)
    # Creating preview for GUI display
    selec_img_pil_prev = modif_img_pil.copy()
    selec_img_pil_prev.thumbnail(IMG_PREVIEW_SIZE)
    selec_img_tk = ImageTk.PhotoImage(selec_img_pil_prev)
    width, height = selec_img_pil_prev.size
    canvas.delete("all")
    canvas.config(width=width, height=height)
    img_canvas_id = canvas.create_image(int(width / 2), int(height / 2), image=selec_img_tk)


def change_position():
    wtm_options['position'] = position_state.get()
    if watermark_path and img_path:
        update_img()


def change_size(expand_coef):
    wtm_options['resize_factor'] = DEFAULT_RESIZE_FACTOR * float(expand_coef)
    if watermark_path and img_path:
        update_img()


def change_opacity(opac_value):
    wtm_options['opacity'] = float(opac_value)
    if watermark_path and img_path:
        update_img()


def save_all():
    if watermark_path and list_img_paths:
        save_dir = askdirectory(title="Select the Save Folder")
        for path in list_img_paths:
            img_pil = Image.open(path)
            new_img_pil = add_wtm(watermark_pil_img, img_pil, wtm_options)
            save_path = save_dir + '/' + os.path.basename(path)
            new_img_pil.save(save_path)
        messagebox.showinfo(message="Your images have been saved!\nThank you for using this tool.",
                            title="Saving Successful")
    else:
        messagebox.showinfo(message="You haven't uploaded a watermark and/or an image.",
                            title="Can Not Save")


# ---------------------------- UI SETUP ------------------------------- #
window.title("Watermark Image tool")
window.config(padx=15, pady=15)

# ----- 1. SETTING UP FONTS
default_font = tkFont.nametofont("TkDefaultFont")  # Get default font value into Font object
lg_font = default_font.copy()
lg_font.config(size=12)
std_font = default_font.copy()
std_font.config(size=10)
underline_font = lg_font.copy()
underline_font.config(underline=True)
bold_font = std_font.copy()
bold_font.config(weight='bold')

# ----- 2. CREATING ALL THE WIDGETS
intro_label = Label(window, text="Add a watermark to your photos:")
intro_label.config(font=underline_font)

instruc_label = Label(window, text="1. Please select a watermark in the form of a PNG file "
                                   "(ideally with a transparent background).\n"
                                   "2. Then select the images you want to add the watermark to.\n"
                                   "3. You can see a preview by clicking on an image in the list.\n"
                                   "4. Finally you can change the position and settings of the "
                                   "watermark with the options below.\n"
                                   "5. When you're satisfied, click 'Save' to save your work.")
instruc_label.config(justify=LEFT, height=8, font=std_font)

select_water_btn = Button(window, text="Select Watermark", font=std_font, width=20, command=select_watermark)

select_imgs_btn = Button(window, text="Select Images", font=std_font, width=20, command=select_images)

files_scroll = Scrollbar(window)
files_listbox = Listbox(window, height=6, yscrollcommand=files_scroll.set, font=std_font)
files_listbox.bind("<<ListboxSelect>>", preview_img)

files_scroll.config(command=files_listbox.yview)

size_label = Label(text="Size", font=bold_font)
size_bar = Scale(from_=1, to=5, orient=HORIZONTAL, command=change_size, resolution=0.5)
opacity_label = Label(text="Opacity", font=bold_font)
opacity_bar = Scale(from_=0, to=1, orient=HORIZONTAL, resolution=0.1, command=change_opacity)
opacity_bar.set(1)
# SEE COMMENT IN "img_processing.py" ABOUT ROTATION
# rotation_label = Label(text="Rotation", font=bold_font)
# rotation_bar = Scale(from_=0, to=360, orient=HORIZONTAL, resolution=5, command=rotate)

position_label = Label(text="Position", font=bold_font)
position_state = StringVar(value="Bottom Right")
center_btn = Radiobutton(text="Center", value="Center", variable=position_state, font=std_font,
                         command=change_position)
top_l_btn = Radiobutton(text="Top Left", value="Top Left", variable=position_state, font=std_font,
                        command=change_position)
top_r_btn = Radiobutton(text="Top Right", value="Top Right", variable=position_state, font=std_font,
                        command=change_position)
bottom_l_btn = Radiobutton(text="Bottom Left", value="Bottom Left", variable=position_state, font=std_font,
                           command=change_position)
bottom_r_btn = Radiobutton(text="Bottom Right", value="Bottom Right", variable=position_state, font=std_font,
                           command=change_position)

save_btn = Button(text="Save Your Work", font=std_font, width=40, command=save_all)
version_label = Label(text="Version 1.0", font=std_font)
canvas = Canvas(width=0, height=0)

# ----- 3. PLACING ALL THE WIDGETS
intro_label.grid(row=0, column=1, columnspan=3, sticky=W)
instruc_label.grid(row=1, column=1, columnspan=3)
select_water_btn.grid(row=2, column=1, columnspan=2)
select_imgs_btn.grid(row=2, column=3)
files_scroll.grid(row=3, column=0, sticky=N+S, pady=10)
files_listbox.grid(row=3, column=1, columnspan=3, sticky=E+W, pady=10)
size_label.grid(row=4, column=1)
size_bar.grid(row=4, column=2, columnspan=2, sticky=E+W)
opacity_label.grid(row=5, column=1)
opacity_bar.grid(row=5, column=2, columnspan=2, sticky=E+W)

position_label.grid(row=7, column=1)
center_btn.grid(row=7, column=2, sticky=W)
top_l_btn.grid(row=8, column=2, sticky=W)
top_r_btn.grid(row=9, column=2, sticky=W)
bottom_l_btn.grid(row=7, column=3, sticky=W)
bottom_r_btn.grid(row=8, column=3, sticky=W)
save_btn.grid(row=10, column=1, columnspan=3, pady=20)
version_label.grid(row=11, column=1, sticky=S+W)
canvas.grid(row=0, column=4, rowspan=12)

window.mainloop()
