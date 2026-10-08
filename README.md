# EndoScope AI

EndoScope AI is a browser and Python desktop research prototype that marks candidate polyp regions in endoscopic images with a compact U-Net model. It displays the original image alongside a segmentation overlay, lists candidate regions, and exports the results.

**Research and education only. It is not a diagnostic device.** Model scores are not disease probabilities, and an empty prediction does not establish a normal examination. Inflammation and ulcer detection are not implemented.

## Try the project

- [Demo video page with English and Chinese captions](https://endoscope-ai-demo.jiangjerry855.chatgpt.site/)
- [Browser demonstration](https://endoscope-ai-demo.jiangjerry855.chatgpt.site/try/)

This repository includes both the **Python desktop application** and the complete **browser demonstration** in `web/`, including the model, local runtime, samples, and captions.

## Run the browser application

From the project folder, run:

```sh
python scripts/serve_browser.py
```

Open **http://localhost:8000/try/**. On Windows, use `py` instead of `python` if needed. This path uses Python’s built-in server; it needs no Python ML packages, Node, build step, API key, or account. Keep the server running while using the app; opening HTML directly with `file:` will not work. The model and inference engine are included in the download. The launcher reassembles two bundled runtime parts and verifies their SHA-256 hashes; it downloads nothing. User images are processed locally.

Choose an example, click **Run analysis**, change the threshold, and download **Overlay PNG**, **Mask PNG**, or **Results JSON**. The browser automatically updates thresholds after the first analysis. Large permitted images are resized locally; exported coordinates refer to the working image, and JSON includes the original dimensions.

## Run the desktop application

You need Python with Tkinter, the packages in `requirements.txt`, and a desktop display. Inference runs on the CPU; a GPU, API key, and model download are not required. The trained checkpoint is included in `models/polyp_unet.pt`.

### Windows

Download this repository using **Code → Download ZIP** and extract it, or clone it:

```cmd
git clone https://github.com/jiangjerry855-boop/EndoScope-AI.git
```

Open the extracted or cloned project folder, where `app.py` and `requirements.txt` are located. Enter `cmd` in File Explorer's address bar and press Enter. Run each command separately:

```cmd
py -m venv .venv
```

```cmd
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

```cmd
.venv\Scripts\python.exe app.py
```

If the `py` command is unavailable but `python` works, use `python -m venv .venv` for the first command. A fresh dependency installation requires internet access; the desktop application itself makes no network calls.

### macOS or Linux

From the project folder:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python app.py
```

The Python installation must include Tkinter. On Linux, install the Tkinter package appropriate for your Python version using your operating system's package manager. A headless server cannot display the desktop interface.

## Use the application

1. Wait until the status says **Model ready**.
2. Select **Open endoscopy image** and choose a JPG, JPEG, PNG, or BMP image you have permission to use. Images above 20 megapixels are rejected.
3. Select **Run analysis**. The right panel shows candidate regions and the table shows their bounding boxes, areas, and mean model scores.
4. Adjust **Pixel segmentation threshold** and run the analysis again to see how the selected pixels change. A higher threshold can split connected regions, so the number of boxes need not decrease monotonically.
5. Select **Export images and JSON** and choose a destination folder.

Each export creates a timestamped subfolder containing:

- `overlay.png`: the image with candidate masks and bounding boxes.
- `mask.png`: a binary mask, with selected pixels shown in white.
- `result.json`: settings, model hash, timing, and candidate-region measurements.

The **Load test example** button loads the bundled public-domain photograph in `examples/`. Its source and attribution are in [examples/README.md](examples/README.md). Five credited browser examples are included; they have no ground-truth masks and cannot measure accuracy.

## Model and processing

- Architecture: compact U-Net, 274,849 parameters.
- Model input: 160 × 160 RGB pixels, preserving aspect ratio with padding.
- Output: pixel scores, resized to the original image dimensions, followed by thresholding and connected-component filtering.
- Minimum retained component size: 16 pixels by default.
- Bounding boxes: `[x1, y1, x2, y2)`, with exclusive right and bottom coordinates.
- Supported class: polyp candidates only.

Training metadata records 800 training, 100 validation, and 100 test images, 40 training epochs, and a best validation Dice score of approximately 0.6663 at model resolution. This is a validation result from the recorded experiment, not a clinical-performance claim or a reproduced test-set result.

The checkpoint SHA-256 is:

```text
dcac0ac697b8fe0a69474d650bd5529bdc0df30fa73c3cb51b97ea4f80ed093e
```

This repository supports running the bundled model. It does not yet contain the training dataset, training script, or full evaluation pipeline needed to reproduce training and reported experiments.

## Repository files

| Path | Purpose |
| --- | --- |
| `app.py` | Tkinter desktop interface |
| `endo/model.py` | Compact U-Net architecture |
| `endo/data.py` | Image loading and preprocessing |
| `endo/inference.py` | Checkpoint loading, segmentation, overlays, and export |
| `models/polyp_unet.pt` | Trained checkpoint |
| `models/training_metadata.json` | Recorded model and training information |
| `models/history.csv` | Training history |
| `requirements.txt` | Python dependencies |
| `web/` | Complete static browser demo, model, runtime, samples, and video |
| `examples/` | Credited desktop demonstration input |
| `scripts/` | Reproducible inference, export, state checks, and captioned-video preparation |
| `devpost/` | Planning documents, factual progress checklist, and offline code map |
| `docs/VALIDATION.md` | Executed checks and remaining verification limits |
| `docs/HACKATHON_STATUS.md` | Verified repository readiness and remaining submission work |

## Troubleshooting

- **A package is missing:** install requirements using the same `.venv` Python that launches the application.
- **Tkinter is missing:** install or repair Python with Tcl/Tk support. Tkinter is not installed by `pip install -r requirements.txt`.
- **The model is missing:** make sure the extracted repository contains `models/polyp_unet.pt`, or select the bundled checkpoint with **Choose trained checkpoint**.
- **The example button finds nothing:** use **Open endoscopy image**; confirm `examples/01_polyp.jpg` was extracted.
- **Results disappear after changing settings:** rerun the analysis so the displayed results match the selected threshold and checkpoint.

## Development and hackathon status

The existing prototype was built before the Devpost Learn Skill Pack onboarding used in the current workflow. New documents will describe the actual subsequent planning and development; they will not be presented as plans that guided the earlier prototype.

Scope was approved; the PRD/specification were written before this increment under the entrant’s explicit delegation. Browser packaging, teaching guidance, result-state fixes, and reproducible checks are now implemented. Detailed learner review, final hands-on exploration, and submission remain open. See [the readiness record](docs/HACKATHON_STATUS.md) and [verification record](docs/VALIDATION.md).

The 33-second recording and an English-captioned MP4 are in `web/assets/`. [Download the English-captioned video](https://endoscope-ai-demo.jiangjerry855.chatgpt.site/assets/endoscope-demo-en.mp4). It shows actual desktop inference and threshold changes; it starts with a loaded image and does not show completed export. A project-hosted video does not replace the required public YouTube/Vimeo URL.

## Reproduce the checks

With the Python ML requirements installed, run:

```sh
python scripts/verify_project.py
node scripts/check_browser.mjs
node scripts/check_ui_state.mjs
```

Node is needed only for developer checks, not for using the browser app. The WASM check uses the bundled runtime and generated reference files; no npm install is needed. Generated evidence and sample exports go to ignored `validation/`. These checks do not open a real browser or desktop GUI. Open `devpost/app-map.html` for an offline guide to the code.

## License

See the complete [MIT License](LICENSE). Dependencies and any separately obtained images or datasets retain their own licenses.
