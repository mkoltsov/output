#!/usr/bin/env python3
"""Image-to-image editing with CyberRealistic CyberIllustrious.

Usage: edit_cyberillustrious.py IMAGE PROMPT OUTPUT_FOLDER
"""

from __future__ import annotations

from datetime import datetime
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

from PIL import Image

from align_source_head import align_head


ROOT = Path(__file__).resolve().parent
BACKEND_DIR = ROOT / "backend"
BACKEND = BACKEND_DIR / "sd-cli"
MODEL_DIR = ROOT / "models" / "cyberillustrious"
FAST_MODEL = MODEL_DIR / "cyberrealistic_v70DMD2.safetensors"
QUALITY_MODEL = MODEL_DIR / "cyberrealistic_v120.safetensors"
EXPECTED_MINIMUM_SIZE = 6_900_000_000
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


def boolean_env(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    normalized = raw.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    fail(f"{name} must be 1/0, true/false, yes/no, or on/off")


def target_dimensions(image_path: Path, default_max_side: int) -> tuple[int, int]:
    max_side = integer_env("EDIT_MAX_SIDE", default_max_side, 256, 1216)
    try:
        with Image.open(image_path) as image:
            source_width, source_height = image.size
    except Exception as exc:
        fail(f"cannot read input image {image_path}: {exc}")
    scale = min(1.0, max_side / max(source_width, source_height))
    width = max(256, round(source_width * scale / 64) * 64)
    height = max(256, round(source_height * scale / 64) * 64)
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

    profile = os.environ.get("CYBERILLUSTRIOUS_PROFILE", "quality").strip().lower()
    if profile == "fast":
        model = FAST_MODEL
        default_max_side = 576
        default_steps, default_cfg = 12, 1.5
        sampler, scheduler = "lcm", "exponential"
        model_label = "CyberIllustrious v7 DMD2"
    elif profile == "quality":
        model = QUALITY_MODEL
        default_max_side = 576
        default_steps, default_cfg = 30, 5.0
        sampler, scheduler = "dpm++2m", "karras"
        model_label = "CyberIllustrious v12"
    else:
        fail("CYBERILLUSTRIOUS_PROFILE must be fast or quality")
    if not model.is_file() or model.stat().st_size < EXPECTED_MINIMUM_SIZE:
        fail(f"required model is missing or incomplete: {model}")

    width, height = target_dimensions(source, default_max_side)
    steps = integer_env("EDIT_STEPS", default_steps, 1, 60)
    cfg = float_env("EDIT_CFG", default_cfg, 1.0, 12.0)
    strength = float_env("EDIT_STRENGTH", 0.85, 0.05, 1.0)
    seed = integer_env("EDIT_SEED", 13001, 0, 2_147_483_647)
    max_vram = float_env("EDIT_MAX_VRAM", 2.0, 0.5, 6.0)
    preserve_head = boolean_env("EDIT_PRESERVE_HEAD", True)

    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    output = output_dir / f"{source.stem}-cyberillustrious-{profile}-{stamp}.png"
    positive = (
        "masterpiece, best quality, high quality, ultra-detailed, realistic, "
        "preserve the same person, facial features, hairstyle, framing and background, "
        f"{prompt}"
    )
    negative = (
        "low quality, bad quality, worst quality, blurry, changed identity, different person, "
        "deformed face, deformed anatomy, bad proportions, extra limbs, extra fingers, "
        "fused fingers, malformed hands, malformed feet, duplicate, cropped, text, logo, "
        "watermark, cartoon, illustration, anime, comic, 3d, cgi"
    )

    environment = os.environ.copy()
    old_library_path = environment.get("LD_LIBRARY_PATH", "")
    environment["LD_LIBRARY_PATH"] = (
        str(BACKEND_DIR)
        if not old_library_path
        else f"{BACKEND_DIR}:{old_library_path}"
    )
    print(
        f"Model: {model_label}\nProfile: {profile}\nInput: {source}\nOutput: {output}\n"
        f"Size: {width}x{height}\nSteps: {steps}\nCFG: {cfg:g}\n"
        f"Strength: {strength:g}\nSeed: {seed}\nPreserve head: {preserve_head}",
        flush=True,
    )
    with tempfile.TemporaryDirectory(prefix="cyberillustrious-i2i-") as temp_dir:
        generated = Path(temp_dir) / "generated.png"
        command = [
            str(BACKEND),
            "--model", str(model),
            "--init-img", str(source),
            "--strength", f"{strength:g}",
            "--prompt", positive,
            "--negative-prompt", negative,
            "--output", str(generated),
            "--width", str(width),
            "--height", str(height),
            "--steps", str(steps),
            "--cfg-scale", f"{cfg:g}",
            "--sampling-method", sampler,
            "--scheduler", scheduler,
            "--seed", str(seed),
            "--backend", "diffusion=vulkan0,te=cpu,vae=cpu",
            "--params-backend", "diffusion=disk,te=disk,vae=cpu",
            "--max-vram", f"vulkan0={max_vram:g}",
            "--mmap",
            "--rng", "cpu",
            "--vae-tiling",
            "--fa",
        ]
        try:
            subprocess.run(command, env=environment, check=True)
        except subprocess.CalledProcessError as exc:
            fail(f"inference failed with exit code {exc.returncode}")
        if not generated.is_file() or generated.stat().st_size == 0:
            fail("backend exited successfully but did not create an output image")
        if preserve_head:
            align_head(source, generated, output)
        else:
            generated.replace(output)
    if not output.is_file() or output.stat().st_size == 0:
        fail("final output image was not created")
    print(output)


if __name__ == "__main__":
    main()
