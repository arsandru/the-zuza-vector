# Cleaning and model sensitivity of the stimulation vs sham comparison (exploratory)

Paired participant bootstrap (1000) and condition-swap permutation (1000); seed 42.

| Model | Cleaning | Field | Unique descriptors | Stimulation | Sham | Delta [95% CI] | p |
|---|---|---|---:|---:|---:|---|---:|
| Qwen3-Embedding-0.6B | raw | notesaroma | 600 | 0.062 | 0.068 | -0.007 [-0.038, +0.031] | 0.70 |
| Qwen3-Embedding-0.6B | raw | flavor_notes | 600 | 0.051 | 0.053 | -0.002 [-0.035, +0.031] | 0.87 |
| Qwen3-Embedding-0.6B | spelling only | notesaroma | 597 | 0.063 | 0.069 | -0.006 [-0.038, +0.031] | 0.73 |
| Qwen3-Embedding-0.6B | spelling only | flavor_notes | 597 | 0.052 | 0.055 | -0.003 [-0.035, +0.031] | 0.84 |
| Qwen3-Embedding-0.6B | lemma only | notesaroma | 592 | 0.059 | 0.067 | -0.008 [-0.040, +0.029] | 0.66 |
| Qwen3-Embedding-0.6B | lemma only | flavor_notes | 592 | 0.049 | 0.057 | -0.009 [-0.041, +0.023] | 0.56 |
| Qwen3-Embedding-0.6B | stop words only | notesaroma | 584 | 0.060 | 0.068 | -0.008 [-0.039, +0.028] | 0.64 |
| Qwen3-Embedding-0.6B | stop words only | flavor_notes | 584 | 0.051 | 0.055 | -0.004 [-0.037, +0.029] | 0.80 |
| Qwen3-Embedding-0.6B | synonym variants only | notesaroma | 586 | 0.057 | 0.065 | -0.007 [-0.038, +0.028] | 0.64 |
| Qwen3-Embedding-0.6B | synonym variants only | flavor_notes | 586 | 0.049 | 0.053 | -0.003 [-0.035, +0.029] | 0.82 |
| Qwen3-Embedding-0.6B | lemma + stop words | notesaroma | 578 | 0.061 | 0.067 | -0.006 [-0.039, +0.031] | 0.73 |
| Qwen3-Embedding-0.6B | lemma + stop words | flavor_notes | 578 | 0.050 | 0.059 | -0.009 [-0.042, +0.024] | 0.57 |
| Qwen3-Embedding-0.6B | all steps, no descriptors-only filter | notesaroma | 559 | 0.062 | 0.065 | -0.003 [-0.035, +0.034] | 0.84 |
| Qwen3-Embedding-0.6B | all steps, no descriptors-only filter | flavor_notes | 559 | 0.052 | 0.060 | -0.008 [-0.040, +0.025] | 0.58 |
| Qwen3-Embedding-0.6B | main (all steps + descriptors only) | notesaroma | 524 | 0.068 | 0.068 | +0.000 [-0.034, +0.040] | 0.99 |
| Qwen3-Embedding-0.6B | main (all steps + descriptors only) | flavor_notes | 524 | 0.057 | 0.063 | -0.006 [-0.040, +0.028] | 0.70 |
| bge-small-en-v1.5 | raw | notesaroma | 600 | 0.028 | 0.029 | -0.001 [-0.020, +0.021] | 0.94 |
| bge-small-en-v1.5 | raw | flavor_notes | 600 | 0.022 | 0.018 | +0.005 [-0.010, +0.021] | 0.48 |
| bge-small-en-v1.5 | all steps, no descriptors-only filter | notesaroma | 559 | 0.032 | 0.035 | -0.003 [-0.023, +0.020] | 0.79 |
| bge-small-en-v1.5 | all steps, no descriptors-only filter | flavor_notes | 559 | 0.029 | 0.025 | +0.004 [-0.015, +0.022] | 0.59 |
| bge-small-en-v1.5 | main (all steps + descriptors only) | notesaroma | 524 | 0.035 | 0.037 | -0.002 [-0.023, +0.021] | 0.88 |
| bge-small-en-v1.5 | main (all steps + descriptors only) | flavor_notes | 524 | 0.031 | 0.027 | +0.004 [-0.015, +0.023] | 0.60 |
| all-mpnet-base-v2 | raw | notesaroma | 600 | 0.038 | 0.035 | +0.002 [-0.016, +0.025] | 0.84 |
| all-mpnet-base-v2 | raw | flavor_notes | 600 | 0.028 | 0.029 | -0.001 [-0.023, +0.019] | 0.95 |
| all-mpnet-base-v2 | all steps, no descriptors-only filter | notesaroma | 559 | 0.039 | 0.038 | +0.001 [-0.020, +0.025] | 0.92 |
| all-mpnet-base-v2 | all steps, no descriptors-only filter | flavor_notes | 559 | 0.029 | 0.034 | -0.005 [-0.027, +0.015] | 0.61 |
| all-mpnet-base-v2 | main (all steps + descriptors only) | notesaroma | 524 | 0.042 | 0.041 | +0.001 [-0.021, +0.026] | 0.94 |
| all-mpnet-base-v2 | main (all steps + descriptors only) | flavor_notes | 524 | 0.032 | 0.034 | -0.002 [-0.026, +0.020] | 0.81 |
