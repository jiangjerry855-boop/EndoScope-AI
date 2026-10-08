# EndoScope AI

EndoScope AI is a Python desktop research prototype that marks candidate polyp regions in endoscopic images with a compact U-Net model. It displays the original image alongside a segmentation overlay, lists candidate regions, and exports the results.

**Research and education only. It is not a diagnostic device.** Model scores are not disease probabilities, and an empty prediction does not establish a normal examination. Inflammation and ulcer detection are not implemented.

## Try the project

- [Demo video page with English and Chinese captions](https://endoscope-ai-demo.jiangjerry855.chatgpt.site/)
- [Browser demonstration](https://endoscope-ai-demo.jiangjerry855.chatgpt.site/try/)

This repository currently contains the **Python desktop application**. The separately hosted browser demonstration is not built from the files in this repository.

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

The **Load test example** button looks for JPG files inside an `examples/` folder. No example images are currently bundled in this repository; use **Open endoscopy image**, or add your own permitted JPG images to `examples/` locally.

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
| `docs/HACKATHON_STATUS.md` | Verified repository readiness and remaining submission work |

## Troubleshooting

- **A package is missing:** install requirements using the same `.venv` Python that launches the application.
- **Tkinter is missing:** install or repair Python with Tcl/Tk support. Tkinter is not installed by `pip install -r requirements.txt`.
- **The model is missing:** make sure the extracted repository contains `models/polyp_unet.pt`, or select the bundled checkpoint with **Choose trained checkpoint**.
- **The example button finds nothing:** use **Open endoscopy image**; the repository does not include example images.
- **Results disappear after changing settings:** rerun the analysis so the displayed results match the selected threshold and checkpoint.

## Development and hackathon status

The existing prototype was built before the Devpost Learn Skill Pack onboarding used in the current workflow. New documents will describe the actual subsequent planning and development; they will not be presented as plans that guided the earlier prototype.

The required Skill Pack planning and build stages are still in progress. See [the readiness record](docs/HACKATHON_STATUS.md) for the remaining work. A publicly hosted project website is separate from the required YouTube or Vimeo submission video.

## License

See the complete [MIT License](LICENSE). Dependencies and any separately obtained images or datasets retain their own licenses.
