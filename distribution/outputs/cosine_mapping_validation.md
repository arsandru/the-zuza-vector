# Cosine mapping validation (exploratory)

Model Qwen/Qwen3-Embedding-0.6B; instruction 'Instruct: Embed aroma/flavor descriptors.\nText:'. Truth = current wheel + alias mapping (units sent to `5_other` or IGNORE by the alias file are manual decisions and not classified). Token accuracy weights each unit by its occurrences in the data.

## Accuracy

| Units | Prototype | Level | Units (n) | Type accuracy | Token accuracy |
|---|---|---|---:|---:|---:|
| wheel terms (leave-one-out) | L2+L3 | category | 53 | 0.74 | 0.78 |
| wheel terms (leave-one-out) | L2+L3 | family (parent of category) | 53 | 0.81 | 0.86 |
| wheel terms (leave-one-out) | L2+L3 | family (own prototype) | 53 | 0.79 | 0.88 |
| wheel terms (leave-one-out) | L1+L2+L3 | category | 53 | 0.68 | 0.81 |
| wheel terms (leave-one-out) | L1+L2+L3 | family (parent of category) | 53 | 0.81 | 0.90 |
| wheel terms (leave-one-out) | L1+L2+L3 | family (own prototype) | 53 | 0.79 | 0.88 |
| aliases | L2+L3 | category | 56 | 0.71 | 0.93 |
| aliases | L2+L3 | family (parent of category) | 58 | 0.83 | 0.96 |
| aliases | L2+L3 | family (own prototype) | 58 | 0.79 | 0.96 |
| aliases | L1+L2+L3 | category | 56 | 0.73 | 0.93 |
| aliases | L1+L2+L3 | family (parent of category) | 58 | 0.83 | 0.96 |
| aliases | L1+L2+L3 | family (own prototype) | 58 | 0.79 | 0.96 |
| all | L2+L3 | category | 109 | 0.72 | 0.84 |
| all | L2+L3 | family (parent of category) | 111 | 0.82 | 0.91 |
| all | L2+L3 | family (own prototype) | 111 | 0.79 | 0.92 |
| all | L1+L2+L3 | category | 109 | 0.71 | 0.86 |
| all | L1+L2+L3 | family (parent of category) | 111 | 0.82 | 0.93 |
| all | L1+L2+L3 | family (own prototype) | 111 | 0.79 | 0.92 |

## Most frequent units the L1+L2+L3 prototype rule assigns to a different category than the current mapping

| Unit | Count | Current mapping | Cosine mapping | Cosine |
|---|---:|---|---|---:|
| smoky | 45 | 6_roasted|6b_burnt | 6_roasted|6c_tobacco | 0.888 |
| nutmeg | 21 | 7_spices|7a_brown spice | 8_nutty/cocoa|8b_nutty | 0.879 |
| bitter | 17 | 5_other|5a_chemical | 6_roasted|6b_burnt | 0.818 |
| prune | 13 | 2_fruity|2b_dried fruit | 2_fruity|2c_other fruit | 0.835 |
| malt | 12 | 6_roasted|6a_cereal | 9_sweet|9a_brown sugar | 0.843 |
| ashy | 10 | 6_roasted|6b_burnt | 5_other|5a_chemical | 0.753 |
| citric | 9 | 3_sour/fermented|3a_sour | 2_fruity|2d_citrus fruit | 0.909 |
| cherry | 8 | 2_fruity|2c_other fruit | 2_fruity|2a_berry | 0.891 |
| tomato | 8 | 4_green/vegetative|4c_green/vegetative | 2_fruity|2c_other fruit | 0.750 |
| coconut | 7 | 2_fruity|2c_other fruit | 8_nutty/cocoa|8a_cocoa | 0.761 |
| fresh | 6 | 4_green/vegetative|4c_green/vegetative | 2_fruity|2d_citrus fruit | 0.845 |
| grape | 6 | 2_fruity|2c_other fruit | 2_fruity|2a_berry | 0.835 |
| chamomile | 4 | 1_floral|1b_floral | 1_floral|1a_black tea | 0.847 |
| bean | 4 | 4_green/vegetative|4d_beany | 6_roasted|6a_cereal | 0.809 |
| raisin | 4 | 2_fruity|2b_dried fruit | 6_roasted|6a_cereal | 0.876 |
