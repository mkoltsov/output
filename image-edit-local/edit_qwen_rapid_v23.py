#!/usr/bin/env python3
"""Local Qwen Image Edit Rapid AIO NSFW Q4_K runner.

Usage: edit_qwen_rapid_v23.py IMAGE PROMPT OUTPUT_FOLDER
"""

from __future__ import annotations

import atexit
from datetime import datetime
import os
from pathlib import Path
import re
import shutil
import signal
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


def boolean_env(name: str, default: bool) -> bool:
    value = os.environ.get(name, "1" if default else "0").strip().lower()
    if value in {"1", "true", "yes", "on"}:
        return True
    if value in {"0", "false", "no", "off"}:
        return False
    fail(f"{name} must be 1 or 0")


class TemporaryPerformanceProfile:
    """Temporarily select Tuned throughput-performance and restore safely."""

    target = "throughput-performance"

    def __init__(self) -> None:
        self.enabled = boolean_env("QWEN_PERFORMANCE_MODE", True)
        self.tuned_adm = shutil.which("tuned-adm")
        self.original: str | None = None
        self.original_platform: str | None = None
        self.switched = False
        self.previous_handlers: dict[int, object] = {}

    def active_profile(self) -> str | None:
        if not self.tuned_adm:
            return None
        result = subprocess.run(
            [self.tuned_adm, "active"], capture_output=True, text=True, check=False
        )
        prefix = "Current active profile:"
        for line in result.stdout.splitlines():
            if line.startswith(prefix):
                return line.removeprefix(prefix).strip()
        return None

    @staticmethod
    def platform_profile() -> str | None:
        path = Path("/sys/firmware/acpi/platform_profile")
        try:
            return path.read_text().strip()
        except OSError:
            return None

    def switch(self, profile: str) -> bool:
        if not self.tuned_adm:
            return False
        result = subprocess.run(
            [self.tuned_adm, "profile", profile],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            detail = (result.stderr or result.stdout).strip()
            print(f"warning: cannot select Tuned profile {profile}: {detail}", file=sys.stderr)
            return False
        return self.active_profile() == profile

    def __enter__(self) -> "TemporaryPerformanceProfile":
        if not self.enabled:
            print("Performance profile switching: disabled", flush=True)
            return self
        if not self.tuned_adm:
            print("warning: tuned-adm is unavailable; keeping the current profile", file=sys.stderr)
            return self
        self.original = self.active_profile()
        self.original_platform = self.platform_profile()
        if not self.original or self.original == self.target:
            print(f"Performance profile: {self.original or 'unknown'} (unchanged)", flush=True)
            return self
        self.switched = True
        atexit.register(self.restore)
        for signum in (signal.SIGTERM, signal.SIGHUP):
            self.previous_handlers[signum] = signal.getsignal(signum)
            signal.signal(signum, self.handle_signal)
        if not self.switch(self.target):
            self.switched = False
            atexit.unregister(self.restore)
            for signum, handler in self.previous_handlers.items():
                signal.signal(signum, handler)
            self.previous_handlers.clear()
            print("warning: performance profile switch was not applied", file=sys.stderr)
            return self
        print(
            f"Performance profile: {self.original} -> {self.target} "
            f"(platform {self.original_platform or 'unknown'} -> "
            f"{self.platform_profile() or 'unknown'})",
            flush=True,
        )
        return self

    def restore(self) -> None:
        if not self.switched or not self.original:
            return
        current = self.active_profile()
        if current != self.target:
            print(
                f"Performance profile changed externally to {current or 'unknown'}; "
                "leaving it unchanged",
                file=sys.stderr,
                flush=True,
            )
            self.switched = False
            return
        restored = self.switch(self.original)
        if restored:
            print(
                f"Performance profile restored: {self.original} "
                f"(platform {self.platform_profile() or 'unknown'})",
                flush=True,
            )
            self.switched = False
        else:
            print(
                f"error: failed to restore Tuned profile {self.original}",
                file=sys.stderr,
                flush=True,
            )

    def handle_signal(self, signum: int, _frame: object) -> None:
        self.restore()
        raise SystemExit(128 + signum)

    def __exit__(self, _exc_type: object, _exc: object, _traceback: object) -> None:
        self.restore()
        try:
            atexit.unregister(self.restore)
        except Exception:
            pass
        for signum, handler in self.previous_handlers.items():
            signal.signal(signum, handler)


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
    threads = integer_env("QWEN_THREADS", 8, 1, 16)
    seed = integer_env("QWEN_SEED", 23002, 0, 2_147_483_647)
    max_vram = float_env("QWEN_MAX_VRAM", 2.0, 0.5, 6.0)
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    output = output_dir / f"{source.stem}-qwen-rapid-{version}-q4-{stamp}.png"

    environment = os.environ.copy()
    environment.setdefault("OTEL_SERVICE_NAME", "image-edit-local-qwen")
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
            "--threads", str(threads),
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
            f"Steps: {steps}\nThreads: {threads}\nCFG: {cfg:g}\n"
            f"Image CFG: {image_cfg:g}\nSeed: {seed}",
            flush=True,
        )
        try:
            with TemporaryPerformanceProfile():
                subprocess.run(command, env=environment, check=True)
        except subprocess.CalledProcessError as exc:
            fail(f"inference failed with exit code {exc.returncode}")
    if not output.is_file() or output.stat().st_size == 0:
        fail("backend exited successfully but did not create an output image")
    print(output)


if __name__ == "__main__":
    main()
