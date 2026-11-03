# Cosine mapping validation (exploratory)

Model Qwen/Qwen3-Embedding-0.6B; instruction 'Instruct: Embed aroma/flavor descriptors.\nText:'. Truth = current wheel + alias mapping. Units = words or phrases as matched (longest match first); token accuracy weights each unit by its occurrences in the data.

## Accuracy

| Units | Representation | Level | Units (n) | Type accuracy | Token accuracy |
|---|---|---|---:|---:|---:|
| wheel terms (leave-one-out) | prototype | category | 53 | 0.74 | 0.78 |
| wheel terms (leave-one-out) | prototype | family | 53 | 0.81 | 0.86 |
| wheel terms (leave-one-out) | label only | category | 53 | 0.51 | 0.68 |
| wheel terms (leave-one-out) | label only | family | 53 | 0.72 | 0.84 |
| aliases | prototype | category | 56 | 0.71 | 0.93 |
| aliases | prototype | family | 58 | 0.83 | 0.96 |
| aliases | label only | category | 56 | 0.61 | 0.85 |
| aliases | label only | family | 58 | 0.76 | 0.94 |
| all mapped | prototype | category | 109 | 0.72 | 0.84 |
| all mapped | prototype | family | 111 | 0.82 | 0.91 |
| all mapped | label only | category | 109 | 0.56 | 0.75 |
| all mapped | label only | family | 111 | 0.74 | 0.89 |

## Cosine of the best category (prototype)

| Units | n | Median | 10th pct | 90th pct |
|---|---:|---:|---:|---:|
| mapped, category correct | 79 | 0.866 | 0.817 | 0.929 |
| mapped, category wrong | 30 | 0.825 | 0.750 | 0.873 |
| no wheel home (5_other) | 10 | 0.797 | 0.767 | 0.837 |

## Threshold on the best cosine (prototype): mapped units kept and correct, no-home units rejected

| Threshold | Mapped units kept | Of those, category correct | No-home units rejected (n = 10) |
|---:|---:|---:|---:|
| 0.50 | 109/109 | 0.72 | 0/10 |
| 0.55 | 109/109 | 0.72 | 0/10 |
| 0.60 | 109/109 | 0.72 | 0/10 |
| 0.65 | 109/109 | 0.72 | 0/10 |
| 0.70 | 108/109 | 0.73 | 0/10 |
| 0.75 | 105/109 | 0.74 | 0/10 |
| 0.80 | 92/109 | 0.80 | 6/10 |
| 0.85 | 61/109 | 0.85 | 9/10 |

## Units without a wheel home: what the rule would pick

| Unit | Count | Best category | Cosine | Margin |
|---|---:|---|---:|---:|
| butter | 10 | 5_other|5b_papery/musty | 0.794 | 0.003 |
| cream | 8 | 2_fruity|2c_other fruit | 0.784 | 0.000 |
| ripe | 7 | 2_fruity|2c_other fruit | 0.898 | 0.037 |
| plane | 2 | 4_green/vegetative|4c_green/vegetative | 0.796 | 0.007 |
| milk | 2 | 6_roasted|6a_cereal | 0.757 | 0.001 |
| rusty | 1 | 6_roasted|6b_burnt | 0.830 | 0.034 |
| peppermint | 1 | 7_spices|7a_brown spice | 0.804 | 0.003 |
| cookie | 1 | 9_sweet|9a_brown sugar | 0.768 | 0.001 |
| iron | 1 | 6_roasted|6b_burnt | 0.817 | 0.041 |
| fat | 1 | 5_other|5b_papery/musty | 0.797 | 0.005 |

## Most frequent mapped units the prototype rule gets wrong

| Unit | Count | Truth | Predicted | Cosine |
|---|---:|---|---|---:|
| smoky | 45 | 6_roasted|6b_burnt | 6_roasted|6c_tobacco | 0.859 |
| caramel | 37 | 9_sweet|9a_brown sugar | 8_nutty/cocoa|8a_cocoa | 0.853 |
| nutmeg | 21 | 7_spices|7a_brown spice | 8_nutty/cocoa|8b_nutty | 0.872 |
| bitter | 17 | 5_other|5a_chemical | 6_roasted|6b_burnt | 0.828 |
| prune | 13 | 2_fruity|2b_dried fruit | 2_fruity|2c_other fruit | 0.838 |
| malt | 12 | 6_roasted|6a_cereal | 9_sweet|9a_brown sugar | 0.841 |
| ashy | 10 | 6_roasted|6b_burnt | 4_green/vegetative|4c_green/vegetative | 0.757 |
| citric | 9 | 3_sour/fermented|3a_sour | 2_fruity|2d_citrus fruit | 0.913 |
| cherry | 8 | 2_fruity|2c_other fruit | 2_fruity|2a_berry | 0.884 |
| tomato | 8 | 4_green/vegetative|4c_green/vegetative | 2_fruity|2c_other fruit | 0.750 |
| coconut | 7 | 2_fruity|2c_other fruit | 7_spices|7a_brown spice | 0.749 |
| fresh | 6 | 4_green/vegetative|4c_green/vegetative | 2_fruity|2d_citrus fruit | 0.840 |
| grape | 6 | 2_fruity|2c_other fruit | 2_fruity|2a_berry | 0.827 |
| sugar | 5 | 9_sweet|9a_brown sugar | 9_sweet|9d_overall sweet | 0.850 |
| toast | 4 | 6_roasted|6b_burnt | 6_roasted|6a_cereal | 0.769 |
