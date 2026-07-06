#!/usr/bin/env python3
"""Generate locally with CyberRealistic CyberIllustrious.

Usage: generate_cyberillustrious.py PROMPT OUTPUT_FOLDER SEED
Environment overrides: CYBERILLUSTRIOUS_WIDTH, CYBERILLUSTRIOUS_HEIGHT,
CYBERILLUSTRIOUS_STEPS, CYBERILLUSTRIOUS_CFG, CYBERILLUSTRIOUS_MAX_VRAM,
CYBERILLUSTRIOUS_PROFILE (fast or quality).
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
from time import strftime


ROOT = Path(__file__).resolve().parent
BACKEND_DIR = ROOT / "backend"
BACKEND = BACKEND_DIR / "sd-cli"
MODEL_DIR = ROOT / "models" / "cyberillustrious"
FAST_MODEL = MODEL_DIR / "cyberrealistic_v70DMD2.safetensors"
QUALITY_MODEL = MODEL_DIR / "cyberrealistic_v120.safetensors"
EXPECTED_MINIMUM_SIZE = 6_900_000_000


def integer_env(name: str, default: int, minimum: int, maximum: int) -> int:
    raw = os.environ.get(name, str(default))
    try:
        value = int(raw)
    except ValueError as exc:
        raise SystemExit(f"{name} must be an integer") from exc
    if not minimum <= value <= maximum:
        raise SystemExit(f"{name} must be between {minimum} and {maximum}")
    return value


def float_env(name: str, default: float, minimum: float, maximum: float) -> float:
    raw = os.environ.get(name, str(default))
    try:
        value = float(raw)
    except ValueError as exc:
        raise SystemExit(f"{name} must be a number") from exc
    if not minimum <= value <= maximum:
        raise SystemExit(f"{name} must be between {minimum} and {maximum}")
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("prompt", help="Description of the image to generate")
    parser.add_argument("output_folder", help="Folder in which to save the PNG")
    parser.add_argument("seed", type=int, help="Non-negative generation seed")
    args = parser.parse_args()

    prompt = args.prompt.strip()
    if not prompt:
        raise SystemExit("PROMPT must not be empty")
    if args.seed < 0:
        raise SystemExit("SEED must be non-negative")
    if not BACKEND.is_file():
        raise SystemExit(f"Inference backend is missing: {BACKEND}")
    profile = os.environ.get("CYBERILLUSTRIOUS_PROFILE", "fast").strip().lower()
    if profile == "fast":
        model = FAST_MODEL
        default_width, default_height = 384, 576
        default_steps, default_cfg = 8, 1.5
        sampler, scheduler = "lcm", "exponential"
        model_label = "CyberIllustrious v7 DMD2"
    elif profile == "quality":
        model = QUALITY_MODEL
        default_width, default_height = 512, 768
        default_steps, default_cfg = 30, 5.0
        sampler, scheduler = "dpm++2m", "karras"
        model_label = "CyberIllustrious v12"
    else:
        raise SystemExit("CYBERILLUSTRIOUS_PROFILE must be fast or quality")
    if not model.is_file() or model.stat().st_size < EXPECTED_MINIMUM_SIZE:
        raise SystemExit(f"Required model is missing or incomplete: {model}")

    width = integer_env("CYBERILLUSTRIOUS_WIDTH", default_width, 256, 1216)
    height = integer_env("CYBERILLUSTRIOUS_HEIGHT", default_height, 256, 1216)
    if width % 64 or height % 64:
        raise SystemExit("CYBERILLUSTRIOUS_WIDTH and HEIGHT must be multiples of 64")
    steps = integer_env("CYBERILLUSTRIOUS_STEPS", default_steps, 1, 60)
    cfg = float_env("CYBERILLUSTRIOUS_CFG", default_cfg, 1.0, 12.0)
    max_vram = float_env("CYBERILLUSTRIOUS_MAX_VRAM", 2.0, 0.5, 6.0)

    output_dir = Path(args.output_folder).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / (
        f"cyberillustrious-{profile}-{strftime('%Y%m%d-%H%M%S')}-seed{args.seed}.png"
    )

    positive = f"masterpiece, best quality, high quality, ultra-detailed, realistic, {prompt}"
    negative = (
        "child, teenager, young-looking, low quality, bad quality, worst quality, blurry, "
        "deformed face, deformed anatomy, bad proportions, extra limbs, extra fingers, "
        "fused fingers, malformed hands, malformed feet, duplicate, cropped, text, logo, "
        "watermark, cartoon, illustration, anime, comic, 3d, cgi"
    )

    command = [
        str(BACKEND),
        "--model", str(model),
        "--backend", "diffusion=vulkan0,te=cpu,vae=cpu",
        "--params-backend", "diffusion=disk,te=disk,vae=cpu",
        "--max-vram", f"vulkan0={max_vram:g}",
        "--mmap",
        "--rng", "cpu",
        "--vae-tiling",
        "--fa",
        "--cfg-scale", f"{cfg:g}",
        "--sampling-method", sampler,
        "--scheduler", scheduler,
        "--steps", str(steps),
        "--width", str(width),
        "--height", str(height),
        "--seed", str(args.seed),
        "--prompt", positive,
        "--negative-prompt", negative,
        "--output", str(output),
    ]

    environment = os.environ.copy()
    old_library_path = environment.get("LD_LIBRARY_PATH", "")
    environment["LD_LIBRARY_PATH"] = (
        str(BACKEND_DIR)
        if not old_library_path
        else f"{BACKEND_DIR}:{old_library_path}"
    )

    print(
        f"Model: {model_label}\n"
        f"Profile: {profile}\n"
        f"Output: {output}\n"
        f"Size: {width}x{height}\n"
        f"Steps: {steps}\n"
        f"CFG: {cfg:g}\n"
        f"Seed: {args.seed}",
        flush=True,
    )
    try:
        subprocess.run(command, env=environment, check=True)
    except subprocess.CalledProcessError as exc:
        raise SystemExit(f"Inference failed with exit code {exc.returncode}") from exc

    if not output.is_file() or output.stat().st_size == 0:
        raise SystemExit(f"Backend returned without a valid output: {output}")
    print(output)


if __name__ == "__main__":
    main()
