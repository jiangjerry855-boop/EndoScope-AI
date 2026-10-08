"""Local desktop app. Images stay on this machine; no network calls are made."""
import datetime
import json
from pathlib import Path
import queue
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
from endo.data import load_rgb
from endo.inference import Predictor, export_prediction

ROOT = Path(__file__).resolve().parent
BG, PANEL, CARD, TEXT, MUTED, ACCENT = "#0c1520", "#142131", "#192a3c", "#edf5fa", "#95abba", "#38dfb1"


class EndoApp:
    def __init__(self, window):
        self.window = window
        window.title("EndoScope AI - Endoscopic Polyp Research Demo")
        window.geometry("1400x900"); window.minsize(1200, 800); window.configure(bg=BG)
        self.events = queue.Queue(); self.predictor = None; self.busy = False
        self.source = None; self.image = None; self.prediction = None; self.photo_refs = []
        self.threshold = tk.DoubleVar(value=0.5)
        self.model_path = ROOT / "models" / "polyp_unet.pt"
        self.status = tk.StringVar(value="Loading trained model...")
        self.filename = tk.StringVar(value="No image selected")
        self.result_summary = tk.StringVar(value="Ready for analysis")
        self.metric_text = tk.StringVar(value="Model: Compact U-Net\nScope: polyp candidate regions")
        self.make_style(); self.build()
        self.set_busy(True)
        threading.Thread(target=self.load_model_worker, daemon=True).start()
        window.after(80, self.poll)
        window.bind("<Configure>", self.on_resize)

    def make_style(self):
        s = ttk.Style(); s.theme_use("clam")
        s.configure("TButton", background=CARD, foreground=TEXT, borderwidth=0, padding=(12, 11), font=("Segoe UI", 10))
        s.map("TButton", background=[("active", "#254059"), ("disabled", PANEL)], foreground=[("disabled", "#536b7e")])
        s.configure("Accent.TButton", background=ACCENT, foreground="#06392e", font=("Segoe UI", 11, "bold"))
        s.map("Accent.TButton", background=[("active", "#66ecc7"), ("disabled", "#285349")])
        s.configure("Treeview", background=PANEL, fieldbackground=PANEL, foreground=TEXT, borderwidth=0,
                    rowheight=30, font=("Segoe UI", 9))
        s.configure("Treeview.Heading", background=CARD, foreground=MUTED, padding=8)
        s.map("Treeview", background=[("selected", "#264d61")])

    def label(self, parent, text=None, variable=None, size=10, color=TEXT, bold=False, bg=None, **kwargs):
        return tk.Label(parent, text=text, textvariable=variable, bg=bg or parent.cget("bg"), fg=color,
                        font=("Segoe UI", size, "bold" if bold else "normal"), **kwargs)

    def build(self):
        header = tk.Frame(self.window, bg=BG, padx=26, pady=20); header.pack(fill="x")
        self.label(header, "ENDO / SCOPE", size=21, bold=True).pack(side="left")
        self.label(header, "Endoscopic Image Analysis", color=MUTED, size=11).pack(side="left", padx=25)
        self.label(header, "  RESEARCH ONLY  ", color=ACCENT, bg="#183d34", size=9).pack(side="right")
        body = tk.Frame(self.window, bg=BG); body.pack(fill="both", expand=True, padx=22)
        sidebar = tk.Frame(body, bg=PANEL, width=285, padx=20, pady=20); sidebar.pack(side="left", fill="y", padx=(0, 18)); sidebar.pack_propagate(False)
        self.label(sidebar, "01  Import and settings", size=13, bold=True).pack(anchor="w", pady=(0, 18))
        self.browse = ttk.Button(sidebar, text="+  Open endoscopy image", command=self.open_image); self.browse.pack(fill="x")
        self.sample = ttk.Button(sidebar, text="Load test example", command=self.open_example); self.sample.pack(fill="x", pady=10)
        self.label(sidebar, variable=self.filename, size=9, color=MUTED, wraplength=240, justify="left").pack(anchor="w", pady=(0, 24))
        self.label(sidebar, "Pixel segmentation threshold", size=10, bold=True).pack(anchor="w")
        self.scale = tk.Scale(sidebar, from_=0.10, to=0.90, resolution=0.05, orient="horizontal", variable=self.threshold,
                              bg=PANEL, fg=TEXT, troughcolor=CARD, highlightthickness=0, activebackground=ACCENT,
                              command=self.threshold_changed)
        self.scale.pack(fill="x", pady=(2, 8))
        self.label(sidebar, "A higher threshold selects fewer pixels. Run analysis again after changing it.", color=MUTED, size=9,
                   wraplength=240, justify="left").pack(anchor="w", pady=(0, 18))
        self.run_button = ttk.Button(sidebar, text="Run analysis", style="Accent.TButton", command=self.run); self.run_button.pack(fill="x")
        self.export_button = ttk.Button(sidebar, text="Export images and JSON", command=self.export); self.export_button.pack(fill="x", pady=10)
        self.label(sidebar, "Model information", size=11, bold=True).pack(anchor="w", pady=(20, 10))
        self.label(sidebar, variable=self.metric_text, color=MUTED, size=9, wraplength=240, justify="left").pack(anchor="w")
        self.model_button = ttk.Button(sidebar, text="Choose trained checkpoint", command=self.choose_model); self.model_button.pack(fill="x", pady=14)
        self.label(sidebar, "Polyp candidates only.\nInflammation and ulcers are unsupported.\nScores are not disease probabilities.", color="#e0bd88", size=9,
                   wraplength=240, justify="left").pack(side="bottom", anchor="w")
        content = tk.Frame(body, bg=BG); content.pack(side="left", fill="both", expand=True)
        row = tk.Frame(content, bg=BG); row.pack(fill="x", pady=(0, 12))
        self.label(row, "02  Images and segmentation", size=14, bold=True).pack(side="left")
        self.label(row, variable=self.result_summary, color=ACCENT, size=10).pack(side="right")
        images = tk.Frame(content, bg=BG); images.pack(fill="both", expand=True)
        images.columnconfigure(0, weight=1, uniform="image"); images.columnconfigure(1, weight=1, uniform="image"); images.rowconfigure(0, weight=1)
        self.canvases = []
        for col, title in enumerate(["ORIGINAL IMAGE  /  INPUT", "CANDIDATE REGIONS  /  PREDICTION"]):
            card = tk.Frame(images, bg=PANEL); card.grid(row=0, column=col, sticky="nsew", padx=(0, 7) if col == 0 else (7, 0))
            self.label(card, title, size=9, color=MUTED).pack(anchor="w", padx=14, pady=12)
            canvas = tk.Canvas(card, bg="#0a111b", highlightthickness=0, width=320, height=320)
            canvas.pack(fill="both", expand=True, padx=10, pady=(0, 10)); self.canvases.append(canvas)
        self.label(content, "03  Candidate regions", size=12, bold=True).pack(anchor="w", pady=(18, 10))
        self.table = ttk.Treeview(content, columns=("index", "label", "score", "box", "area"), show="headings", height=4)
        for name, title, width in [("index", "ID", 48), ("label", "Class", 130), ("score", "Mean model score", 130),
                                    ("box", "Box [x1, y1, x2, y2)", 200), ("area", "Area / px", 85)]:
            self.table.heading(name, text=title); self.table.column(name, width=width, anchor="center", stretch=True)
        self.table.pack(fill="x")
        footer = tk.Frame(self.window, bg=BG, padx=24, pady=13); footer.pack(fill="x")
        self.label(footer, variable=self.status, color=MUTED, size=9, wraplength=700, justify="left").pack(side="left")
        self.label(footer, "Research only - not for diagnosis or ruling out disease", color="#e0bd88", size=9).pack(side="right")
        self.render()

    def set_busy(self, busy):
        self.busy = busy
        state = "disabled" if busy else "normal"
        for button in (self.browse, self.sample, self.model_button):
            button.configure(state=state)
        self.scale.configure(state=state)
        self.run_button.configure(state="normal" if not busy and self.image is not None and self.predictor else "disabled")
        self.export_button.configure(state="normal" if not busy and self.prediction is not None else "disabled")

    def load_model_worker(self):
        try:
            self.events.put(("model", Predictor(self.model_path)))
        except Exception as exc:
            self.events.put(("error", str(exc)))

    def clear_prediction(self):
        self.prediction = None
        for item in self.table.get_children(): self.table.delete(item)
        self.result_summary.set("Ready for analysis"); self.render(); self.set_busy(self.busy)

    def threshold_changed(self, _):
        if self.prediction is not None:
            self.clear_prediction(); self.status.set("Threshold changed. Run analysis again.")

    def choose_model(self):
        path = filedialog.askopenfilename(title="Select a trusted checkpoint trained with this project", filetypes=[("PyTorch weights", "*.pt")])
        if path:
            self.predictor = None; self.model_path = Path(path); self.clear_prediction(); self.set_busy(True)
            self.status.set("Loading model..."); threading.Thread(target=self.load_model_worker, daemon=True).start()

    def open_image(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.jpeg *.png *.bmp"), ("All", "*.*")])
        if path: self.load_image(path)

    def open_example(self):
        files = sorted((ROOT / "examples").glob("*.jpg"))
        if files:
            idx = (getattr(self, "example_index", -1) + 1) % len(files)
            self.example_index = idx; self.load_image(files[idx])
        else: messagebox.showinfo("Examples", "No images were found in the examples folder.")

    def load_image(self, path):
        try:
            image = load_rgb(path)
            if image.width * image.height > 20_000_000: raise ValueError("Image exceeds 20 megapixels. Resize it first.")
            self.source, self.image = Path(path), image
            self.filename.set(f"{self.source.name}\n{image.width} × {image.height} px")
            self.clear_prediction(); self.status.set("Image loaded. Ready to analyze.")
        except Exception as exc: messagebox.showerror("Unable to open image", str(exc))

    def run(self):
        if self.busy or self.image is None or self.predictor is None: return
        self.set_busy(True); self.status.set("Analyzing image...")
        image, threshold = self.image.copy(), self.threshold.get()
        def worker():
            try: self.events.put(("prediction", self.predictor.predict(image, threshold)))
            except Exception as exc: self.events.put(("error", str(exc)))
        threading.Thread(target=worker, daemon=True).start()

    def poll(self):
        try:
            while True:
                kind, value = self.events.get_nowait()
                if kind == "model":
                    self.predictor = value
                    self.metric_text.set(f"Model: Compact U-Net\nClass: polyp\nInput: {value.size} x {value.size}\nBest epoch: {value.metadata['epoch']}\nDevice: CPU / offline")
                    self.status.set("Model ready. Open an image or load a test example.")
                elif kind == "prediction":
                    self.prediction = value; result, _, _ = value
                    result["source_filename"] = self.source.name
                    for item in self.table.get_children(): self.table.delete(item)
                    for idx, r in enumerate(result["regions"], 1):
                        self.table.insert("", "end", values=(idx, "Polyp candidate", f"{r['mean_model_score']:.3f}", str(r["bbox_xyxy"]), r["area_pixels"]))
                    n = len(result["regions"]); elapsed = result["inference_ms_including_pre_and_postprocessing"]
                    self.result_summary.set(f"{n} candidate regions  |  {elapsed:.0f} ms")
                    self.status.set("Analysis complete. Scores are not calibrated probabilities." if n else "No candidates found. This does not establish a normal examination.")
                    self.render()
                else:
                    self.status.set("Operation failed. Check the image and model files.")
                    messagebox.showerror("Operation failed", value)
                self.set_busy(False)
        except queue.Empty: pass
        self.window.after(80, self.poll)

    def render(self):
        self.photo_refs = []
        images = [self.image, self.prediction[2] if self.prediction else None]
        for canvas, image in zip(self.canvases, images):
            canvas.delete("all")
            w, h = max(100, canvas.winfo_width()), max(100, canvas.winfo_height())
            if image is None:
                canvas.create_text(w/2, h/2, text="Open an image to start" if canvas == self.canvases[0] else "Segmentation and boxes will appear here",
                                   fill="#718b9e", font=("Segoe UI", 10), width=w-25)
            else:
                shown = image.copy(); shown.thumbnail((max(1, w-16), max(1, h-16)), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(shown); self.photo_refs.append(photo)
                canvas.create_image(w/2, h/2, image=photo)

    def on_resize(self, event):
        if event.widget == self.window:
            if hasattr(self, "resize_job"): self.window.after_cancel(self.resize_job)
            self.resize_job = self.window.after(100, self.render)

    def export(self):
        if not self.prediction: return
        parent = filedialog.askdirectory(title="Select an export folder")
        if not parent: return
        try:
            name = datetime.datetime.now().strftime("endo_result_%Y%m%d_%H%M%S_%f")
            dest = Path(parent) / name
            export_prediction(dest, *self.prediction)
            self.status.set(f"Results exported to: {dest}")
        except Exception as exc: messagebox.showerror("Export failed", str(exc))


if __name__ == "__main__":
    window = tk.Tk()
    app = EndoApp(window)
    window.mainloop()
