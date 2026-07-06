#!/usr/bin/env python3
"""Local Qwen Image Edit Rapid AIO NSFW Q4_K runner.

Usage: edit_qwen_rapid_v23.py IMAGE PROMPT OUTPUT_FOLDER
"""

from __future__ import annotations

from datetime import datetime
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parent
BACKEND_DIR = ROOT / "backend"
BACKEND = BACKEND_DIR / "sd-cli"
SHARED_MODEL_DIR = ROOT / "models" / "qwen-edit-v23"
TEXT_ENCODER = SHARED_MODEL_DIR / "Qwen2.5-VL-7B-Instruct-abliterated.Q4_K_M.gguf"
VISION = SHARED_MODEL_DIR / "Qwen2.5-VL-7B-Instruct-abliterated.mmproj-Q8_0.gguf"
VAE = SHARED_MODEL_DIR / "qwen_image_vae.safetensors"

# Do not turn an identifiable person's photograph into explicit sexual content.
DISALLOWED_EXPLICIT_TERMS = re.compile(
    r"\b(?:nude|nudity|naked|undress(?:ed|ing)?|topless|bottomless|porn(?:ographic)?|"
    r"explicit|genitals?|vulva|vagina|penis|nipples?|areolae?|sex(?:ual)?|intercourse)\b",
    re.IGNORECASE,
)


def fail(message: str) -> "NoReturn":
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(2)


def integer_env(name: str, default: int, minimum: int, maximum: int) -> int:
    raw = os.environ.get(name, str(default))
    try:
        value = int(raw)
    except ValueError:
        fail(f"{name} must be an integer")
    if not minimum <= value <= maximum:
        fail(f"{name} must be between {minimum} and {maximum}")
    return value


def float_env(name: str, default: float, minimum: float, maximum: float) -> float:
    raw = os.environ.get(name, str(default))
    try:
        value = float(raw)
    except ValueError:
        fail(f"{name} must be a number")
    if not minimum <= value <= maximum:
        fail(f"{name} must be between {minimum} and {maximum}")
    return value


def select_diffusion_model() -> tuple[str, Path]:
    version = os.environ.get("QWEN_VERSION", "v19").lower()
    choices = {
        "v19": ROOT / "models/qwen-edit-v19/Qwen-Rapid-AIO-NSFW-v19_Q4_K.gguf",
        "v23": ROOT / "models/qwen-edit-v23/Qwen-Rapid-NSFW-v23_Q4_K.gguf",
    }
    if version not in choices:
        fail("QWEN_VERSION must be v19 or v23")
    return version, choices[version]


def select_device() -> str:
    device = os.environ.get("QWEN_DEVICE", "cpu").lower()
    if device not in {"cpu", "vulkan"}:
        fail("QWEN_DEVICE must be cpu or vulkan")
    return device


def target_dimensions(image_path: Path) -> tuple[int, int]:
    max_side = integer_env("QWEN_MAX_SIDE", 640, 256, 1024)
    try:
        with Image.open(image_path) as image:
            source_width, source_height = image.size
    except Exception as exc:
        fail(f"cannot read input image {image_path}: {exc}")
    scale = min(1.0, max_side / max(source_width, source_height))
    width = max(256, round(source_width * scale / 16) * 16)
    height = max(256, round(source_height * scale / 16) * 16)
    return width, height


def prepare_reference(source: Path, destination: Path) -> tuple[int, int]:
    """Normalize a reference to Qwen2.5-VL's 28-pixel vision patch grid."""
    max_side = integer_env("QWEN_REF_MAX_SIDE", 672, 280, 1344)
    try:
        with Image.open(source) as opened:
            image = ImageOps.exif_transpose(opened).convert("RGB")
    except Exception as exc:
        fail(f"cannot read input image {source}: {exc}")

    scale = min(1.0, max_side / max(image.size))
    width = max(28, round(image.width * scale / 28) * 28)
    height = max(28, round(image.height * scale / 28) * 28)
    if image.size != (width, height):
        image = image.resize((width, height), Image.Resampling.LANCZOS)
    image.save(destination, format="PNG", optimize=True)
    return width, height


def main() -> None:
    if len(sys.argv) != 4:
        fail(f'usage: {Path(sys.argv[0]).name} "IMAGE" "PROMPT" "OUTPUT_FOLDER"')
    source = Path(sys.argv[1]).expanduser().resolve()
    prompt = sys.argv[2].strip()
    output_dir = Path(sys.argv[3]).expanduser().resolve()
    if not source.is_file():
        fail(f"input image does not exist: {source}")
    if not prompt:
        fail("prompt cannot be empty")
    if DISALLOWED_EXPLICIT_TERMS.search(prompt):
        fail("explicit sexual alteration of an identifiable person is not supported")
    if not BACKEND.is_file():
        fail(f"inference backend is missing: {BACKEND}")
    version, diffusion = select_diffusion_model()
    device = select_device()
    expected_minimum_sizes = {
        diffusion: 13_342_000_000,
        TEXT_ENCODER: 4_683_000_000,
        VISION: 853_000_000,
        VAE: 253_000_000,
    }
    for path, minimum in expected_minimum_sizes.items():
        if not path.is_file() or path.stat().st_size < minimum:
            fail(f"required model component is missing or incomplete: {path}")

    width, height = target_dimensions(source)
    steps = integer_env("QWEN_STEPS", 4, 1, 12)
    cfg = float_env("QWEN_CFG", 1.0, 1.0, 8.0)
    image_cfg = float_env("QWEN_IMG_CFG", 1.0, 0.5, 4.0)
    seed = integer_env("QWEN_SEED", 23002, 0, 2_147_483_647)
    max_vram = float_env("QWEN_MAX_VRAM", 2.0, 0.5, 6.0)
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    output = output_dir / f"{source.stem}-qwen-rapid-{version}-q4-{stamp}.png"

    environment = os.environ.copy()
    old_library_path = environment.get("LD_LIBRARY_PATH", "")
    environment["LD_LIBRARY_PATH"] = (
        str(BACKEND_DIR)
        if not old_library_path
        else f"{BACKEND_DIR}:{old_library_path}"
    )
    with tempfile.TemporaryDirectory(prefix="qwen-v23-reference-") as temporary:
        reference = Path(temporary) / "reference.png"
        reference_width, reference_height = prepare_reference(source, reference)
        backend = (
            "diffusion=cpu,te=cpu,vae=cpu"
            if device == "cpu"
            else "diffusion=vulkan0,te=cpu,vae=cpu"
        )
        command = [
            str(BACKEND),
            "--diffusion-model", str(diffusion),
            "--vae", str(VAE),
            "--llm", str(TEXT_ENCODER),
            "--llm_vision", str(VISION),
            "--ref-image", str(reference),
            "--qwen-image-zero-cond-t",
            "--prompt", prompt,
            "--negative-prompt",
            "low quality, blurry, distorted anatomy, watermark, text",
            "--output", str(output),
            "--width", str(width),
            "--height", str(height),
            "--steps", str(steps),
            "--cfg-scale", f"{cfg:g}",
            "--img-cfg-scale", f"{image_cfg:g}",
            "--sampling-method", "euler_a",
            "--scheduler", "beta",
            "--flow-shift", "3",
            "--seed", str(seed),
            "--backend", backend,
            "--params-backend", "diffusion=disk,te=disk,vae=cpu",
            "--mmap",
            "--rng", "cpu",
            "--vae-tiling",
            "--diffusion-fa",
        ]
        if device == "vulkan":
            command.extend(["--max-vram", f"vulkan0={max_vram:g}"])
        print(
            f"Model: Qwen Image Edit Rapid AIO NSFW {version} Q4_K\n"
            f"Device: {device}\n"
            f"Input: {source}\nReference grid: {reference_width}x{reference_height}\n"
            f"Output: {output}\nSize: {width}x{height}\n"
            f"Steps: {steps}\nCFG: {cfg:g}\nImage CFG: {image_cfg:g}\nSeed: {seed}",
            flush=True,
        )
        try:
            subprocess.run(command, env=environment, check=True)
        except subprocess.CalledProcessError as exc:
            fail(f"inference failed with exit code {exc.returncode}")
    if not output.is_file() or output.stat().st_size == 0:
        fail("backend exited successfully but did not create an output image")
    print(output)


if __name__ == "__main__":
    main()
