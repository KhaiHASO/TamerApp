import io
import os
import sys
from functools import lru_cache

import streamlit as st
import torch
import numpy as np
import cv2

# Ensure repo root is on sys.path to import the local package without pip install -e .
REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from tamer.lit_tamer import LitTAMER
from tamer.datamodule import vocab
from tamer.datamodule.transforms import ScaleToLimitRange


@st.cache_resource
def load_model(checkpoint_path: str, device: str = "auto") -> LitTAMER:
    if device == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"
    model = LitTAMER.load_from_checkpoint(checkpoint_path, map_location=device)
    model.eval()
    model.to(device)
    return model


def find_default_dictionary() -> str:
    # Try common locations for dictionary.txt
    candidates = [
        os.path.join(REPO_ROOT, "lightning_logs", "version_1", "dictionary.txt"),
        os.path.join(REPO_ROOT, "lightning_logs", "version_0", "dictionary.txt"),
        os.path.join(REPO_ROOT, "data", "hme100k", "dictionary.txt"),
        os.path.join(REPO_ROOT, "data", "crohme", "dictionary.txt"),
    ]
    for p in candidates:
        if os.path.isfile(p):
            return p
    # Fallback: search under lightning_logs
    logs_dir = os.path.join(REPO_ROOT, "lightning_logs")
    for root, _dirs, files in os.walk(logs_dir):
        if "dictionary.txt" in files:
            return os.path.join(root, "dictionary.txt")
    return ""


@lru_cache(maxsize=1)
def init_vocab(dictionary_path: str) -> int:
    vocab.init(dictionary_path)
    return len(vocab)


def preprocess_image(image_bytes: bytes, scale_to_limit: bool = True):
    # Decode to numpy (grayscale)
    data = np.frombuffer(image_bytes, dtype=np.uint8)
    img = cv2.imdecode(data, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError("Unsupported image format or corrupted file.")

    # Ensure 2D uint8
    if img.ndim == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Match dataset transform: ScaleToLimitRange + ToTensor
    if scale_to_limit:
        scaler = ScaleToLimitRange(w_lo=16, w_hi=1024, h_lo=16, h_hi=256)
        img = scaler(img)

    # Normalize to [0,1] and to tensor shape [1, 1, H, W]
    tensor = torch.from_numpy(img).float() / 255.0
    tensor = tensor.unsqueeze(0).unsqueeze(0)  # [1,1,H,W]

    # Build mask: False for valid pixels, True for padding. No padding here → zeros.
    mask = torch.zeros((1, tensor.shape[2], tensor.shape[3]), dtype=torch.bool)
    return tensor, mask


def predict(model: LitTAMER, img_tensor: torch.Tensor, mask_tensor: torch.Tensor):
    device = next(model.parameters()).device
    with torch.no_grad():
        hyps = model.approximate_joint_search(img_tensor.to(device), mask_tensor.to(device))
    # Take first hypothesis (batch size = 1)
    if len(hyps) == 0:
        return ""
    tokens = hyps[0].seq
    words = vocab.indices2words(tokens)
    return " ".join(words)


def main():
    st.set_page_config(page_title="TAMER Inference", layout="centered")
    st.title("TAMER: Tree-Aware Transformer — Inference (Streamlit)")
    st.caption("Load your v3 checkpoint and get LaTeX predictions from handwritten math images.")

    default_ckpt = os.path.join(
        REPO_ROOT,
        "lightning_logs",
        "version_3",
        "checkpoints",
        "epoch=55-step=175503-val_ExpRate=0.6954.ckpt",
    )
    checkpoint_path = st.text_input("Checkpoint path", value=default_ckpt)

    default_dict = find_default_dictionary()
    dictionary_path = st.text_input("Dictionary path (dictionary.txt)", value=default_dict)

    col1, col2 = st.columns(2)
    with col1:
        device_choice = st.selectbox("Device", ["auto", "cuda", "cpu"], index=0)
    with col2:
        scale_to_limit = st.checkbox("Scale to limit (match training)", value=True)

    uploaded = st.file_uploader("Upload an image (png/jpg/jpeg)", type=["png", "jpg", "jpeg"])

    ready = os.path.isfile(checkpoint_path) and os.path.isfile(dictionary_path)
    if not ready:
        st.info("Please provide valid checkpoint and dictionary.txt paths.")

    run_btn = st.button("Run Inference", type="primary", disabled=not (uploaded and ready))

    if run_btn and uploaded is not None:
        try:
            # Init vocab (cached)
            _ = init_vocab(dictionary_path)

            # Load model (cached)
            model = load_model(checkpoint_path, device_choice)

            # Preprocess
            img_bytes = uploaded.read()
            img_tensor, mask_tensor = preprocess_image(img_bytes, scale_to_limit=scale_to_limit)

            # Predict
            latex_str = predict(model, img_tensor, mask_tensor)

            # Show
            st.subheader("Prediction (LaTeX tokens)")
            st.code(latex_str, language="text")
            st.subheader("Render")
            try:
                st.latex(latex_str)
            except Exception:
                st.warning("Could not render LaTeX. Tokens still shown above.")

        except AssertionError as e:
            # Likely ratio assertion in ScaleToLimitRange
            st.error(f"Preprocess assertion failed: {e}")
        except Exception as e:
            st.exception(e)


if __name__ == "__main__":
    main()


