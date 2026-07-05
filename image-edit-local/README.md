# Local PhotoMaker outfit and pose editors

This archive contains the verified Python implementation for the existing
`image-edit-local` installation:

- `edit_photomaker_outfit.py`: waist-up outfit replacement
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

