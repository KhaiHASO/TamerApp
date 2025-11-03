import os
from functools import lru_cache

import cv2
import numpy as np
import streamlit as st
import torch


CUR_DIR = os.path.dirname(os.path.abspath(__file__))

from tamer.lit_tamer import LitTAMER
from tamer.datamodule import vocab
from tamer.datamodule.transforms import ScaleToLimitRange


def _guess_default_ckpt() -> str:
    # Prefer a checkpoint placed directly in this TamerApp folder
    local_candidates = [
        os.path.join(CUR_DIR, "epoch=55-step=175503-val_ExpRate=0.6954.ckpt"),
    ]
    for p in local_candidates:
        if os.path.isfile(p):
            return p
    # Fallback: first .ckpt found in this folder
    for f in os.listdir(CUR_DIR):
        if f.endswith(".ckpt"):
            return os.path.join(CUR_DIR, f)
    return ""


def _guess_default_dictionary() -> str:
    # Hard-coded to local dictionary.txt in TamerApp
    p = os.path.join(CUR_DIR, "dictionary.txt")
    return p if os.path.isfile(p) else ""


@st.cache_resource
def load_model(checkpoint_path: str, device_preference: str = "auto") -> LitTAMER:
    device = (
        "cuda" if device_preference == "cuda" or (device_preference == "auto" and torch.cuda.is_available()) else "cpu"
    )
    # Allow non-strict load to support checkpoints with fusion modules or different heads
    model = LitTAMER.load_from_checkpoint(checkpoint_path, map_location=device, strict=False)
    model.eval().to(device)
    return model


@lru_cache(maxsize=1)
def init_vocab(dictionary_path: str) -> int:
    vocab.init(dictionary_path)
    return len(vocab)


def preprocess_image(image_bytes: bytes, apply_scale_limit: bool = True, safe_memory: bool = False):
    data = np.frombuffer(image_bytes, dtype=np.uint8)
    img = cv2.imdecode(data, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError("Unsupported image format or corrupted file.")

    if apply_scale_limit:
        scaler = ScaleToLimitRange(w_lo=16, w_hi=1024, h_lo=16, h_hi=256)
        img = scaler(img)

    if safe_memory:
        h, w = img.shape[:2]
        max_w, max_h = 768, 192
        scale_r = min(max_h / h, max_w / w)
        if scale_r < 1.0:
            img = cv2.resize(img, None, fx=scale_r, fy=scale_r, interpolation=cv2.INTER_LINEAR)

    x = torch.from_numpy(img).float() / 255.0
    x = x.unsqueeze(0).unsqueeze(0)  # [1,1,H,W]
    mask = torch.zeros((1, x.shape[2], x.shape[3]), dtype=torch.bool)
    return x, mask


def predict(model: LitTAMER, x: torch.Tensor, mask: torch.Tensor) -> str:
    device = next(model.parameters()).device
    with torch.no_grad(), torch.autocast(device_type=("cuda" if device.type == "cuda" else "cpu"), enabled=(device.type == "cuda")):
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
        detected_ckpt = _guess_default_ckpt()
        if os.path.isfile(detected_ckpt):
            st.caption("Using checkpoint in TamerApp folder:")
            st.code(detected_ckpt, language="text")
            ckpt = detected_ckpt
        else:
            ckpt = st.text_input("Checkpoint .ckpt path", value="")

        # Dictionary: hard-coded to TamerApp/dictionary.txt (no input required)
        dictionary = _guess_default_dictionary()
        if os.path.isfile(dictionary):
            st.caption("Using dictionary.txt in TamerApp folder:")
            st.code(dictionary, language="text")
        else:
            st.error("dictionary.txt is missing in TamerApp folder.")

        device = st.selectbox("Device", ["auto", "cuda", "cpu"], index=0)
        scale_limit = st.checkbox("Scale to training limits", value=True)
        safe_mem = st.checkbox("Safe memory mode (extra downscale, slower)", value=False)

        with st.expander("Advanced (beam search)"):
            beam_size = st.slider("beam_size", min_value=1, max_value=10, value=5)
            max_len = st.slider("max_len", min_value=32, max_value=256, value=128, step=16)
            alpha = st.slider("alpha (length penalty)", min_value=0.0, max_value=2.0, value=1.0, step=0.1)
            temperature = st.slider("temperature", min_value=0.5, max_value=2.0, value=1.0, step=0.1)
            early_stopping = st.checkbox("early_stopping", value=True)

    st.write("Upload a handwritten math image (png/jpg)")
    file = st.file_uploader("Image", type=["png", "jpg", "jpeg"])

    ready = os.path.isfile(ckpt) and os.path.isfile(dictionary)
    if not ready:
        st.info("Provide valid paths for checkpoint and dictionary.txt in the sidebar.")

    if st.button("Run Inference", type="primary", disabled=not (file and ready)):
        try:
            init_vocab(dictionary)
            model = load_model(ckpt, device)
            img_bytes = file.read()
            x, mask = preprocess_image(img_bytes, apply_scale_limit=scale_limit, safe_memory=safe_mem)

            # override beam search params if possible
            try:
                model.hparams.beam_size = beam_size
                model.hparams.max_len = max_len
                model.hparams.alpha = alpha
                model.hparams.temperature = temperature
                model.hparams.early_stopping = early_stopping
            except Exception:
                pass

            try:
                latex = predict(model, x, mask)
            except RuntimeError as e:
                if "out of memory" in str(e).lower():
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()
                    model = load_model(ckpt, device_preference="cpu")
                    try:
                        model.hparams.beam_size = min(beam_size, 3)
                        model.hparams.max_len = min(max_len, 96)
                        model.hparams.alpha = alpha
                        model.hparams.temperature = temperature
                        model.hparams.early_stopping = True
                    except Exception:
                        pass
                    x, mask = preprocess_image(img_bytes, apply_scale_limit=True, safe_memory=True)
                    latex = predict(model, x, mask)
                else:
                    raise
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


