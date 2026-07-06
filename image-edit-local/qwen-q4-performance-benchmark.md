# Qwen Q4 performance-profile benchmark

Tested 6 July 2026 on a Lenovo ThinkPad T14s Gen 1 AMD with a Ryzen 7 PRO
4750U and 16 GB RAM. Both performance runs were executed sequentially while
connected to AC power. The runner temporarily selected Tuned
`throughput-performance` and firmware `performance`, then restored
`powersave` and `low-power` after each run.

## Controlled settings

- Qwen Image Edit Rapid AIO NSFW Q4_K
- CPU diffusion with disk-backed weights
- 336 × 640 output
- Four Euler Ancestral/Beta steps
- CFG 1 and image CFG 1
- Seed 23002
- Identical source and prompt for all runs

## Results

| Model | Low-power total | Performance total | Time saved | Reduction | Throughput |
|---|---:|---:|---:|---:|---:|
| v19 Q4 | 19 min 51.41 s | 13 min 26.72 s | 6 min 24.69 s | 32.3% | 1.48× |
| v23 Q4 | 17 min 17.21 s | 15 min 23.25 s | 1 min 53.96 s | 11.0% | 1.12× |

| Model | Low-power sampling | Performance sampling | Sampling reduction | Performance peak RSS | Swap |
|---|---:|---:|---:|---:|---:|
| v19 Q4 | 1,024.39 s | 652.85 s | 36.3% | 9.34 GiB | 0 |
| v23 Q4 | 881.33 s | 757.08 s | 14.1% | 10.07 GiB | 0 |

During the v19 run, all 16 logical CPUs reported an average of approximately
3.71 GHz after the profile switch. The performance-mode outputs were
byte-for-byte identical to their corresponding low-power outputs:

- v19 SHA-256: `bc54b9428864813bd82c89c7009573da61f8f14531761bb5506aef36d130bbe4`
- v23 SHA-256: `188ded9171eca625dba3b1d3ef91add39268dee806fb44eca97979de4522be86`

## Interpretation

The performance switch gives v19 a large and repeatable benefit without
changing the image. The v23 result is conservative: it ran immediately after
the 13-minute v19 performance run, and its last denoising step slowed sharply,
consistent with sustained thermal or power saturation. Therefore these numbers
measure realistic back-to-back use, not an isolated cold-start best case.

After both tests the active profiles were verified as `powersave` and
`low-power`.
