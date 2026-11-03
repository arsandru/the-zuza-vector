# Cleaning and model sensitivity of the stimulation vs sham comparison (exploratory)

Paired participant bootstrap (1000) and condition-swap permutation (1000); seed 42.

| Model | Cleaning | Field | Unique descriptors | Stimulation | Sham | Delta [95% CI] | p |
|---|---|---|---:|---:|---:|---|---:|
| Qwen3-Embedding-0.6B | raw | notesaroma | 601 | 0.051 | 0.052 | -0.001 [-0.030, +0.031] | 0.91 |
| Qwen3-Embedding-0.6B | raw | flavor_notes | 601 | 0.044 | 0.045 | -0.000 [-0.033, +0.030] | 0.96 |
| Qwen3-Embedding-0.6B | spelling only | notesaroma | 598 | 0.052 | 0.053 | -0.001 [-0.029, +0.031] | 0.93 |
| Qwen3-Embedding-0.6B | spelling only | flavor_notes | 598 | 0.046 | 0.046 | -0.001 [-0.033, +0.030] | 0.96 |
| Qwen3-Embedding-0.6B | lemma only | notesaroma | 593 | 0.050 | 0.052 | -0.002 [-0.031, +0.031] | 0.90 |
| Qwen3-Embedding-0.6B | lemma only | flavor_notes | 593 | 0.043 | 0.049 | -0.005 [-0.037, +0.025] | 0.69 |
| Qwen3-Embedding-0.6B | stop words only | notesaroma | 585 | 0.050 | 0.052 | -0.002 [-0.030, +0.027] | 0.89 |
| Qwen3-Embedding-0.6B | stop words only | flavor_notes | 585 | 0.045 | 0.047 | -0.002 [-0.032, +0.029] | 0.91 |
| Qwen3-Embedding-0.6B | synonym variants only | notesaroma | 587 | 0.048 | 0.050 | -0.002 [-0.029, +0.027] | 0.88 |
| Qwen3-Embedding-0.6B | synonym variants only | flavor_notes | 587 | 0.044 | 0.045 | -0.001 [-0.032, +0.027] | 0.91 |
| Qwen3-Embedding-0.6B | lemma + stop words | notesaroma | 579 | 0.051 | 0.051 | -0.000 [-0.030, +0.032] | 0.98 |
| Qwen3-Embedding-0.6B | lemma + stop words | flavor_notes | 579 | 0.045 | 0.050 | -0.006 [-0.037, +0.026] | 0.69 |
| Qwen3-Embedding-0.6B | full | notesaroma | 560 | 0.052 | 0.050 | +0.002 [-0.026, +0.033] | 0.88 |
| Qwen3-Embedding-0.6B | full | flavor_notes | 560 | 0.046 | 0.051 | -0.005 [-0.037, +0.025] | 0.70 |
| bge-small-en-v1.5 | raw | notesaroma | 601 | 0.023 | 0.023 | -0.000 [-0.016, +0.018] | 1.00 |
| bge-small-en-v1.5 | raw | flavor_notes | 601 | 0.020 | 0.014 | +0.006 [-0.008, +0.021] | 0.33 |
| bge-small-en-v1.5 | full | notesaroma | 560 | 0.027 | 0.029 | -0.001 [-0.019, +0.017] | 0.89 |
| bge-small-en-v1.5 | full | flavor_notes | 560 | 0.026 | 0.021 | +0.006 [-0.011, +0.023] | 0.41 |
| all-mpnet-base-v2 | raw | notesaroma | 601 | 0.031 | 0.027 | +0.004 [-0.013, +0.023] | 0.64 |
| all-mpnet-base-v2 | raw | flavor_notes | 601 | 0.024 | 0.023 | +0.001 [-0.017, +0.020] | 0.87 |
| all-mpnet-base-v2 | full | notesaroma | 560 | 0.032 | 0.029 | +0.003 [-0.015, +0.021] | 0.74 |
| all-mpnet-base-v2 | full | flavor_notes | 560 | 0.026 | 0.028 | -0.002 [-0.022, +0.017] | 0.82 |
