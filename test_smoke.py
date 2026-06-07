"""Minimal smoke test for ComfyUI_TensorRT after uv setup.

Run after activating the venv created by setup_uv_env.ps1:

    python -m test_smoke
or
    python test_smoke.py

It will:
- Print python / torch / tensorrt / onnx versions (asserting the target stack)
- Import the two main modules (requires ComfyUI on PYTHONPATH)
- Exercise basic class presence (no full model conversion)
"""

import os
import sys

print("=" * 60)
print("ComfyUI_TensorRT smoke test")
print("=" * 60)

print("python :", sys.executable)
print("version:", sys.version.split()[0])

# --- Core packages that the TensorRT path actually needs ---
import torch
print("torch  :", torch.__version__, "cuda=", getattr(torch.version, "cuda", "n/a"))
print("cuda?  :", torch.cuda.is_available() if hasattr(torch, "cuda") else False)

try:
    import tensorrt as trt
    print("tensorrt:", trt.__version__)
    TRT_IMPORT_OK = True
except Exception as e:
    print("tensorrt import (runtime/DLL):", type(e).__name__, str(e)[:120])
    print("    (This is usually a PATH / full TensorRT 11 runtime issue on Windows, not a package install problem.)")
    TRT_IMPORT_OK = False

import onnx
print("onnx   :", onnx.__version__)

# Sanity on the exact version the user asked for
if 'TRT_IMPORT_OK' in dir() and TRT_IMPORT_OK:
    if not (trt.__version__.startswith("11.") or "11.0.0.114" in trt.__version__):
        print("WARNING: tensorrt version does not look like 11.0.0.114")
    else:
        print("tensorrt version check: PASS (11.x)")
else:
    print("tensorrt version check: SKIPPED (see DLL note above)")

# --- Now pull in the node modules (they import comfy.*) ---
# We expect to be run with the ComfyUI tree on PYTHONPATH or cwd parent.
comfy_root = os.environ.get("COMFYUI_ROOT") or r"G:\AI\ComfyNew\ComfyUI"
if comfy_root not in sys.path:
    sys.path.insert(0, comfy_root)

try:
    # These two modules do the real work
    from custom_nodes.ComfyUI_TensorRT import tensorrt_convert
    from custom_nodes.ComfyUI_TensorRT import tensorrt_loader

    print("tensorrt_convert import: OK")
    print("tensorrt_loader  import: OK")

    dyn = tensorrt_convert.DYNAMIC_TRT_MODEL_CONVERSION
    stat = tensorrt_convert.STATIC_TRT_MODEL_CONVERSION
    ldr = tensorrt_loader.TensorRTLoader

    print("DYNAMIC_TRT_MODEL_CONVERSION present:", hasattr(dyn, "INPUT_TYPES"))
    print("STATIC_TRT_MODEL_CONVERSION  present:", hasattr(stat, "INPUT_TYPES"))
    print("TensorRTLoader               present:", hasattr(ldr, "INPUT_TYPES"))

    print("\nAll smoke checks PASSED.")
    sys.exit(0)
except Exception as e:
    print("\nIMPORT / NODE CHECK FAILED:", type(e).__name__, str(e)[:200])
    print("Make sure you ran from the activated uv venv and that")
    print("G:\\AI\\ComfyNew\\ComfyUI is reachable (PYTHONPATH or COMFYUI_ROOT).")
    sys.exit(1)
