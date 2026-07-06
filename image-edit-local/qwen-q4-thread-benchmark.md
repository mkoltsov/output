# Qwen Q4 8-thread versus 16-thread benchmark

Tested 6 July 2026 on a Lenovo ThinkPad T14s Gen 1 AMD with an 8-core,
16-thread Ryzen 7 PRO 4750U and 16 GB RAM. All runs were sequential and used
the runner's temporary performance profile while connected to AC power. The
original `powersave` and `low-power` profiles were independently verified after
the final run.

## Controlled settings

- Qwen Image Edit Rapid AIO NSFW Q4_K, v19 and v23
- CPU diffusion with disk-backed weights
- 336 × 640 output
- Four Euler Ancestral/Beta steps
- CFG 1 and image CFG 1
- Seed 23002
- Identical source, prompt, run order, and performance policy

## Results

| Model | 8-thread total | 16-thread total | 16-thread change | 8-thread sampling | 16-thread sampling | Sampling change |
|---|---:|---:|---:|---:|---:|---:|
| v19 Q4 | 13 min 26.72 s | 16 min 06.96 s | 19.9% slower | 652.85 s | 803.08 s | 23.0% slower |
| v23 Q4 | 15 min 23.25 s | 17 min 39.26 s | 14.7% slower | 757.08 s | 886.93 s | 17.2% slower |

| Model | Threads | Mean CPU use | Peak resident memory | Major page faults | Involuntary context switches | Swap |
|---|---:|---:|---:|---:|---:|---:|
| v19 Q4 | 8 | 686% | 9.34 GiB | 7,553,499 | 50,380 | 0 |
| v19 Q4 | 16 | 1,279% | 9.78 GiB | 7,522,121 | 2,023,120 | 0 |
| v23 Q4 | 8 | 701% | 10.07 GiB | 7,738,294 | 51,058 | 0 |
| v23 Q4 | 16 | 1,209% | 9.36 GiB | 8,016,288 | 2,347,615 | 0 |

The 16-thread runs consumed substantially more CPU time but finished later.
Their roughly 40–46-fold increase in involuntary context switches is consistent
with logical-thread contention on the eight physical cores, compounded by the
model's heavy disk-backed paging. This interpretation is supported by the
measurements; it is not a direct hardware-counter diagnosis.

## Output integrity

Changing the thread count did not change either generated image. The 8-thread
and 16-thread output hashes matched exactly for each model:

- v19 SHA-256: `bc54b9428864813bd82c89c7009573da61f8f14531761bb5506aef36d130bbe4`
- v23 SHA-256: `188ded9171eca625dba3b1d3ef91add39268dee806fb44eca97979de4522be86`

## Recommendation

Keep the runner's default at 8 threads on this laptop. Using all 16 logical
threads is reliably slower in this controlled v19/v23 comparison and provides
no image-quality or determinism benefit. `QWEN_THREADS=16` remains available as
an explicit override for testing.
