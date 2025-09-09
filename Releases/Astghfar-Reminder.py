import tkinter as tk
from tkinter import messagebox, simpledialog, font, ttk
import random
import json
import os

# --- الإعدادات الأولية ---

SETTINGS_FILE = "adhkar_settings.json"

# قائمة الأذكار الافتراضية (تُستخدم فقط إذا لم يتم العثور على ملف إعدادات)
default_adhkar_list = [
    "أَسْتَغْفِرُ اللَّهَ الْعَظِيمَ وَأَتُوبُ إِلَيْهِ",
    "سُبْحَانَ اللَّهِ وَبِحَمْدِهِ",
    "سُبْحَانَ اللَّهِ الْعَظِيمِ",
    "الْحَمْدُ لِلَّهِ",
    "لا إِلَهَ إِلا اللَّهُ",
    "اللَّهُ أَكْبَرُ",
    "لا حَوْلَ وَلا قُوَّةَ إِلا بِاللَّهِ",
    "اللَّهُمَّ صَلِّ وَسَلِّمْ عَلَى نَبِيِّنَا مُحَمَدٍ",
    "لا إِلَهَ إِلا أَنْتَ سُبْحَانَكَ إِنِّي كُنْتُ مِنَ الظَّالِمِينَ"
]
adhkar_list = list(default_adhkar_list) # ابدأ بنسخة من القائمة الافتراضية

# مدة بقاء النافذة على الشاشة بالمللي ثانية (8 ثوانٍ)
NOTIFICATION_DURATION_MS = 8000

# متغير لتتبع حالة التذكير (يعمل أو متوقف)
reminder_job = None
is_running = False

# --- حفظ وتحميل والإعدادات ---

def save_settings():
    """
    تحفظ الإعدادات الحالية في ملف JSON
    """
    settings = {
        "adhkar": adhkar_list,
        "minutes": time_minutes_var.get(),
        "seconds": time_seconds_var.get(),
        "position": position_var.get()
    }
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=4)
    except IOError as e:
        print(f"Error saving settings: {e}")

def load_settings():
    """
    تحمل الإعدادات من ملف JSON عند بدء التشغيل
    """
    global adhkar_list
    if not os.path.exists(SETTINGS_FILE):
        return # لا تفعل شيئًا إذا كان الملف غير موجود
    
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            settings = json.load(f)
            adhkar_list = settings.get("adhkar", default_adhkar_list)
            time_minutes_var.set(settings.get("minutes", "1"))
            time_seconds_var.set(settings.get("seconds", "0"))
            position_var.set(settings.get("position", "أسفل اليمين"))
    except (json.JSONDecodeError, IOError, KeyError) as e:
        print(f"Error loading settings: {e}. Using defaults.")
        adhkar_list = list(default_adhkar_list)

def exit_app():
    """
    تحفظ الإعدادات وتغلق البرنامج بشكل كامل
    """
    save_settings()
    root.destroy()

# --- وظائف إخفاء وإظهار النافذة ---
def hide_window():
    """
    تخفي النافذة الرئيسية ليعمل البرنامج في الخلفية
    """
    root.withdraw()

def show_main_window():
    """
    تستعيد إظهار النافذة الرئيسية من الخلفية
    """
    root.deiconify()
    root.lift()
    root.focus_force()

# --- وظائف التنبيه المحسّنة ---

def fade_in(window, step=0.05):
    alpha = window.attributes("-alpha")
    if alpha < 1:
        alpha += step
        window.attributes("-alpha", alpha)
        window.after(20, fade_in, window, step)

def fade_out(window, step=0.05):
    alpha = window.attributes("-alpha")
    if alpha > 0:
        alpha -= step
        window.attributes("-alpha", alpha)
        window.after(20, fade_out, window, step)
    else:
        window.destroy()

def show_reminder():
    if not adhkar_list:
        return

    reminder_window = tk.Toplevel(root)
    reminder_window.overrideredirect(True)
    reminder_window.wm_attributes("-topmost", 1)
    reminder_window.attributes("-alpha", 0)
    
    random_dhikr = random.choice(adhkar_list)
    frame = tk.Frame(reminder_window, bg="#34495e", bd=1, relief="solid")
    frame.pack()
    label = tk.Label(frame, text=random_dhikr, font=("Arial", 16, "bold"), fg="#ffffff", bg="#34495e", padx=30, pady=20)
    label.pack()

    # إضافة زر الإعدادات إذا كانت النافذة الرئيسية مخفية
    if not root.winfo_viewable():
        settings_button = tk.Button(
            frame, text="⚙️ الإعدادات", font=("Arial", 10), command=show_main_window,
            bg="#5e7d9b", fg="white", relief="flat", height=1
        )
        settings_button.pack(pady=(0, 5), fill="x", padx=5)

    root.update_idletasks()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = reminder_window.winfo_width()
    window_height = reminder_window.winfo_height()
    position = position_var.get()
    margin_x = 20
    margin_y = 50

    if position == "أسفل اليمين":
        x_pos, y_pos = screen_width - window_width - margin_x, screen_height - window_height - margin_y
    elif position == "أعلى اليمين":
        x_pos, y_pos = screen_width - window_width - margin_x, margin_x
    elif position == "أسفل اليسار":
        x_pos, y_pos = margin_x, screen_height - window_height - margin_y
    elif position == "أعلى اليسار":
        x_pos, y_pos = margin_x, margin_x
    elif position == "أعلى المنتصف":
        x_pos, y_pos = (screen_width // 2) - (window_width // 2), margin_x
    elif position == "أسفل المنتصف":
        x_pos, y_pos = (screen_width // 2) - (window_width // 2), screen_height - window_height - margin_y
    
    reminder_window.geometry(f"+{x_pos}+{y_pos}")
    fade_in(reminder_window)
    reminder_window.after(NOTIFICATION_DURATION_MS - 1000, lambda: fade_out(reminder_window))
    
    global reminder_job
    if is_running:
        try:
            interval_minutes = int(time_minutes_var.get())
            interval_seconds = int(time_seconds_var.get())
            interval_ms = (interval_minutes * 60 + interval_seconds) * 1000
            if interval_ms < 1000:
                interval_ms = 1000
            reminder_job = root.after(interval_ms, show_reminder)
        except ValueError:
            toggle_reminder()

# --- وظائف الواجهة الرسومية ---

def update_listbox():
    adhkar_listbox.delete(0, tk.END)
    for dhikr in adhkar_list:
        adhkar_listbox.insert(tk.END, dhikr)

def add_dhikr():
    new_dhikr = simpledialog.askstring("إضافة ذكر جديد", "اكتب الذكر الذي تريد إضافته:", parent=root)
    if new_dhikr and new_dhikr.strip():
        adhkar_list.append(new_dhikr.strip())
        update_listbox()
    elif new_dhikr is not None:
        messagebox.showwarning("خطأ", "لا يمكن إضافة نص فارغ!")

def delete_dhikr():
    selected_indices = adhkar_listbox.curselection()
    if not selected_indices:
        messagebox.showwarning("تنبيه", "الرجاء تحديد ذكر لحذفه أولاً.")
        return
    for i in sorted(selected_indices, reverse=True):
        adhkar_list.pop(i)
    update_listbox()

def toggle_reminder():
    global is_running, reminder_job
    if is_running:
        if reminder_job:
            root.after_cancel(reminder_job)
            reminder_job = None
        is_running = False
        status_label.config(text="الحالة: متوقف", fg="red")
        toggle_button.config(text="ابدأ التذكير", bg="#27ae60")
    else:
        try:
            total_seconds = int(time_minutes_var.get()) * 60 + int(time_seconds_var.get())
            if total_seconds < 1:
                messagebox.showwarning("خطأ", "يجب أن يكون الوقت ثانية واحدة على الأقل.")
                return
        except ValueError:
            messagebox.showwarning("خطأ", "الرجاء إدخال أرقام صحيحة للوقت.")
            return
        is_running = True
        show_reminder()
        status_label.config(text="الحالة: يعمل", fg="green")
        toggle_button.config(text="أوقف التذكير", bg="#c0392b")

# --- إعداد الواجهة الرسومية الرئيسية ---
root = tk.Tk()
root.title("تذكير بالاستغفار")
root.geometry("500x620") # زيادة الارتفاع قليلاً
root.configure(bg="#f0f0f0")
root.resizable(False, False)

# --- تعريف متغيرات الإعدادات قبل تحميلها ---
time_minutes_var = tk.StringVar(value="1")
time_seconds_var = tk.StringVar(value="0")
position_var = tk.StringVar(value="أسفل اليمين")

# --- تحميل الإعدادات عند بدء التشغيل ---
load_settings()

# --- الخطوط ---
title_font = font.Font(family="Arial", size=16, weight="bold")
button_font = font.Font(family="Arial", size=11, weight="bold")
status_font = font.Font(family="Arial", size=12)
label_font = font.Font(family="Arial", size=10)

# --- إطار العنوان ---
title_frame = tk.Frame(root, bg="#f0f0f0")
title_frame.pack(pady=10)
tk.Label(title_frame, text="قائمة الأذكار", font=title_font, bg="#f0f0f0").pack()

# --- إطار قائمة الأذكار ---
list_frame = tk.Frame(root)
list_frame.pack(pady=5, padx=20, fill="both", expand=True)
adhkar_listbox = tk.Listbox(list_frame, font=("Arial", 12), selectmode=tk.MULTIPLE, justify="right")
scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=adhkar_listbox.yview)
adhkar_listbox.config(yscrollcommand=scrollbar.set)
scrollbar.pack(side="left", fill="y")
adhkar_listbox.pack(side="right", fill="both", expand=True)

# --- إطار الأزرار ---
button_frame = tk.Frame(root, bg="#f0f0f0")
button_frame.pack(pady=10)
add_button = tk.Button(button_frame, text="إضافة ذكر", font=button_font, command=add_dhikr, bg="#3498db", fg="white", width=12)
add_button.grid(row=0, column=0, padx=5)
delete_button = tk.Button(button_frame, text="حذف المحدد", font=button_font, command=delete_dhikr, bg="#e74c3c", fg="white", width=12)
delete_button.grid(row=0, column=1, padx=5)

# --- إطار الإعدادات ---
settings_frame = ttk.LabelFrame(root, text=" الإعدادات ", padding=(10, 10))
settings_frame.pack(padx=20, pady=5, fill="x")
settings_frame.columnconfigure(1, weight=1)
settings_frame.columnconfigure(3, weight=1)

# --- Time settings row ---
tk.Label(settings_frame, text="كرر الإشعار كل:", font=label_font).grid(row=0, column=0, sticky="w", pady=5)
minutes_spinbox = tk.Spinbox(settings_frame, from_=0, to=120, textvariable=time_minutes_var, width=5, font=label_font, justify='center')
minutes_spinbox.grid(row=0, column=1, sticky='ew', padx=5)
tk.Label(settings_frame, text="دقيقة و", font=label_font).grid(row=0, column=2)
seconds_spinbox = tk.Spinbox(settings_frame, from_=0, to=59, textvariable=time_seconds_var, width=5, font=label_font, justify='center')
seconds_spinbox.grid(row=0, column=3, sticky='ew', padx=5)
tk.Label(settings_frame, text="ثانية", font=label_font).grid(row=0, column=4)

# --- Position settings row ---
tk.Label(settings_frame, text="مكان ظهور الإشعار:", font=label_font).grid(row=1, column=0, sticky="w", pady=5)
positions = ["أسفل اليمين", "أعلى اليمين", "أسفل اليسار", "أعلى اليسار", "أعلى المنتصف", "أسفل المنتصف"]
position_menu = ttk.OptionMenu(settings_frame, position_var, position_var.get(), *positions)
position_menu.grid(row=1, column=1, columnspan=4, sticky="ew", pady=5)

# --- إطار التحكم والتشغيل ---
control_frame = tk.Frame(root, bg="#f0f0f0")
control_frame.pack(pady=15)
toggle_button = tk.Button(control_frame, text="ابدأ التذكير", font=button_font, command=toggle_reminder, bg="#27ae60", fg="white", width=15, height=2)
toggle_button.pack()
status_label = tk.Label(control_frame, text="الحالة: متوقف", font=status_font, fg="red", bg="#f0f0f0")
status_label.pack(pady=5)
exit_button = tk.Button(control_frame, text="إغلاق البرنامج نهائياً", font=label_font, command=exit_app, bg="#a9a9a9", fg="white")
exit_button.pack(pady=(10,0))

# --- التشغيل ---
update_listbox()
root.protocol("WM_DELETE_WINDOW", hide_window) # عند الضغط على X، قم بإخفاء النافذة
root.mainloop()

