import os
import sys
from functools import lru_cache

import cv2
import numpy as np
import streamlit as st
import torch


# Make sure local package is importable
REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from tamer.lit_tamer import LitTAMER
from tamer.datamodule import vocab
from tamer.datamodule.transforms import ScaleToLimitRange


def _guess_default_ckpt() -> str:
    candidates = [
        os.path.join(REPO_ROOT, "lightning_logs", "version_3", "checkpoints", "epoch=55-step=175503-val_ExpRate=0.6954.ckpt"),
        os.path.join(REPO_ROOT, "TamerTrainning", "lightning_logs", "version_3", "checkpoints", "epoch=55-step=175503-val_ExpRate=0.6954.ckpt"),
        os.path.join(REPO_ROOT, "TamerApp", "epoch=55-step=175503-val_ExpRate=0.6954.ckpt"),
    ]
    for p in candidates:
        if os.path.isfile(p):
            return p
    # Search under repo
    for root, _dirs, files in os.walk(REPO_ROOT):
        for f in files:
            if f.endswith(".ckpt") and "val_ExpRate=0.6954" in f:
                return os.path.join(root, f)
    return ""


def _guess_default_dictionary() -> str:
    candidates = [
        os.path.join(REPO_ROOT, "lightning_logs", "version_3", "dictionary.txt"),
        os.path.join(REPO_ROOT, "lightning_logs", "version_1", "dictionary.txt"),
        os.path.join(REPO_ROOT, "lightning_logs", "version_0", "dictionary.txt"),
        os.path.join(REPO_ROOT, "data", "hme100k", "dictionary.txt"),
        os.path.join(REPO_ROOT, "data", "crohme", "dictionary.txt"),
    ]
    for p in candidates:
        if os.path.isfile(p):
            return p
    for root, _dirs, files in os.walk(REPO_ROOT):
        if "dictionary.txt" in files:
            return os.path.join(root, "dictionary.txt")
    return ""


@st.cache_resource
def load_model(checkpoint_path: str, device_preference: str = "auto") -> LitTAMER:
    device = (
        "cuda" if device_preference == "cuda" or (device_preference == "auto" and torch.cuda.is_available()) else "cpu"
    )
    model = LitTAMER.load_from_checkpoint(checkpoint_path, map_location=device)
    model.eval().to(device)
    return model


@lru_cache(maxsize=1)
def init_vocab(dictionary_path: str) -> int:
    vocab.init(dictionary_path)
    return len(vocab)


def preprocess_image(image_bytes: bytes, apply_scale_limit: bool = True):
    data = np.frombuffer(image_bytes, dtype=np.uint8)
    img = cv2.imdecode(data, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError("Unsupported image format or corrupted file.")

    if apply_scale_limit:
        scaler = ScaleToLimitRange(w_lo=16, w_hi=1024, h_lo=16, h_hi=256)
        img = scaler(img)

    x = torch.from_numpy(img).float() / 255.0
    x = x.unsqueeze(0).unsqueeze(0)  # [1,1,H,W]
    mask = torch.zeros((1, x.shape[2], x.shape[3]), dtype=torch.bool)
    return x, mask


def predict(model: LitTAMER, x: torch.Tensor, mask: torch.Tensor) -> str:
    device = next(model.parameters()).device
    with torch.no_grad():
        hyps = model.approximate_joint_search(x.to(device), mask.to(device))
    if not hyps:
        return ""
    tokens = hyps[0].seq
    return " ".join(vocab.indices2words(tokens))


def main():
    st.set_page_config(page_title="TAMER Streamlit App", layout="centered")
    st.title("TAMER — Math Expression Recognition (Streamlit)")

    with st.sidebar:
        st.header("Settings")
        ckpt = st.text_input("Checkpoint .ckpt path", value=_guess_default_ckpt())
        dictionary = st.text_input("dictionary.txt path", value=_guess_default_dictionary())
        device = st.selectbox("Device", ["auto", "cuda", "cpu"], index=0)
        scale_limit = st.checkbox("Scale to training limits", value=True)

    st.write("Upload a handwritten math image (png/jpg)")
    file = st.file_uploader("Image", type=["png", "jpg", "jpeg"])

    ready = os.path.isfile(ckpt) and os.path.isfile(dictionary)
    if not ready:
        st.info("Provide valid paths for checkpoint and dictionary.txt in the sidebar.")

    if st.button("Run Inference", type="primary", disabled=not (file and ready)):
        try:
            init_vocab(dictionary)
            model = load_model(ckpt, device)
            x, mask = preprocess_image(file.read(), apply_scale_limit=scale_limit)
            latex = predict(model, x, mask)
            st.subheader("Predicted LaTeX")
            st.code(latex, language="text")
            st.subheader("Render")
            try:
                st.latex(latex)
            except Exception:
                st.warning("Could not render LaTeX; tokens shown above.")
        except AssertionError as e:
            st.error(f"Preprocess assertion failed: {e}")
        except Exception as e:
            st.exception(e)


if __name__ == "__main__":
    main()

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



