# Local PhotoMaker outfit and pose editors

This archive contains the verified Python implementation for the existing
`image-edit-local` installation:

- `edit_photomaker_outfit.py`: 384 × 576 waist-up outfit replacement
- `edit_photomaker_pose.py`: full-body pose and outfit generation
- `align_source_head.py`: landmark-aligned face and hairstyle restoration
- `zimage_i2i_common.py`: face detection and source-hair mask helpers

Both editors accept exactly three arguments:

```bash
python3 edit_photomaker_outfit.py INPUT_IMAGE "OUTFIT PROMPT" OUTPUT_FOLDER
python3 edit_photomaker_pose.py INPUT_IMAGE "POSE AND OUTFIT PROMPT" OUTPUT_FOLDER
```

They require the local RealVisXL, PhotoMaker v1, YuNet face detector, and
stable-diffusion.cpp Vulkan installation described in the main project README.
Model weights and test photographs are intentionally not included.

The scripts reject prompts requesting explicit nudification of an identifiable
person. They are intended for ordinary outfit and pose changes.

## CyberIllustrious generator

`generate_cyberillustrious.py` is the verified three-argument local generator.
The default `fast` profile uses CyberIllustrious v7 DMD2 at 384 × 576, eight
LCM/Exponential steps and CFG 1.5. On the tested ThinkPad it completed in 234
seconds with about 3.5 GB peak resident memory.

```bash
python3 generate_cyberillustrious.py "PROMPT" OUTPUT_FOLDER SEED
```

Set `CYBERILLUSTRIOUS_PROFILE=quality` for the latest v12 checkpoint with 30
DPM++ 2M Karras steps and CFG 5. Model weights and the inference backend are
not included in this public repository.

### CyberIllustrious I2I

`edit_cyberillustrious.py` is the verified conventional SDXL I2I wrapper:

```bash
python3 edit_cyberillustrious.py INPUT_IMAGE "TARGET IMAGE PROMPT" OUTPUT_FOLDER
```

The default v12 profile uses a maximum side of 576 pixels, 30 steps, CFG 5 and
strength 0.85, then restores the source face and hair. The verified test
completed in 211 seconds with about 5.4 GB peak resident memory. This is not
Qwen-style semantic editing: high strength can change pose, shoes and details
outside the restored head region.
