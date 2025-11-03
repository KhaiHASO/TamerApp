# TAMERApp — Streamlit Inference App

A self-contained Streamlit app to recognize handwritten mathematical expressions using the TAMER model.

## Folder Layout

- `TamerApp/app.py`: Streamlit UI and inference logic
- `TamerApp/tamer/`: Local vendored TAMER code (encoder/decoder/transformer/utils)
- Place your checkpoint (`.ckpt`) and `dictionary.txt` directly in `TamerApp/`

## Recommended: Create a clean conda environment (avoid conflicts)

Option A — CPU-only (simple and stable)
```bash
conda create -y -n tamerapp python=3.9
conda activate tamerapp

# Install PyTorch CPU
conda install -y -c pytorch pytorch torchvision cpuonly

# Install Python deps from requirements.txt
python -m pip install -r TamerApp/requirements.txt
# On Windows, install editdistance from conda-forge if pip build fails
conda install -y -c conda-forge editdistance
```

Option B — GPU (CUDA). Replace the PyTorch install line with the CUDA build you have installed. Example (CUDA 11.8):
```bash
conda create -y -n tamerapp python=3.9
conda activate tamerapp
conda install -y pytorch torchvision pytorch-cuda=11.8 -c pytorch -c nvidia
python -m pip install -r TamerApp/requirements.txt
# If editdistance fails to build wheel on Windows
conda install -y -c conda-forge editdistance
```

## Quick Start

1) Copy files into `TamerApp/`:
   - Checkpoint: e.g. `epoch=55-step=175503-val_ExpRate=0.6954.ckpt`
   - `dictionary.txt`

2) Run the app (using the new env):
   ```bash
   conda activate tamerapp
   cd C:\Users\admin\Desktop\github\TamerApp
   streamlit run TamerApp\app.py
   ```

3) In the app:
   - App will auto-detect `.ckpt` and `dictionary.txt` in `TamerApp/`
   - Upload a PNG/JPG image of a handwritten math expression
   - Click "Run Inference" to get predicted LaTeX and a rendered preview

## Options

- Device: `auto` (default), `cuda`, or `cpu`
- "Scale to training limits": applies the same resizing policy as training

## Notes

- The app is isolated: it imports the vendored `tamer` package in `TamerApp/tamer`.
- No need to install the repo as a package; running via Streamlit is enough.
- `dictionary.txt` must match the vocabulary used during training of your checkpoint.

## Troubleshooting

- Missing Streamlit: `python -m pip install streamlit` (inside `tamerapp` env) or `python -m pip install -r TamerApp/requirements.txt`
- ImportError: numpy.core.multiarray failed to import → mismatch NumPy/OpenCV. In `tamerapp` env run:
  ```bash
  python -m pip install --force-reinstall --no-deps numpy==1.26.4 opencv-python==4.8.1.78
  ```
- OpenCV read error: ensure PNG/JPG; try another image
- Preprocess assertion (ratio bounds): uncheck "Scale to training limits"
- CUDA not used: choose Device=CUDA and ensure `torch.cuda.is_available()` is True

## License / Reference

- Model and ideas from TAMER: Tree-Aware Transformer for Handwritten Mathematical Expression Recognition
- See the original paper and repository for research details


