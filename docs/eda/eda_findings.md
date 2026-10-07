## EDA Findings

**Missingness is informative.** The missing indicators are not missing completely at random; several carry default-rate signal. Relative to the overall default rate of 8.07%, applications with missing `EXT_SOURCE_1` (56.4%) or `EXT_SOURCE_3` (19.8%) default at higher rates (8.52% and 9.31% vs 7.50% and 7.77%), while those with missing `OCCUPATION_TYPE` (31.4%) default at a lower rate (6.51% vs 8.79%), consistent with the `DAYS_EMPLOYED = 365,243` low-risk group. Applications lacking the building-region block default at a higher rate (8.23% vs 6.32%).

**No leakage, weak linear signal.** No feature is identical to or the complement of `TARGET`, and the largest absolute correlation with `TARGET` is 0.179. The strongest linear correlates are `EXT_SOURCE_3` (0.179), `EXT_SOURCE_2` (0.161), and `EXT_SOURCE_1` (0.155), foreshadowing their rank in the information-value screening.

**Near-constant columns.** Twenty columns are near-constant (a single value in at least 99% of rows) and carry negligible variance: `FLAG_MOBIL` and `FLAG_CONT_MOBILE` (about 100% equal to 1), `AMT_REQ_CREDIT_BUREAU_DAY` and `AMT_REQ_CREDIT_BUREAU_HOUR` (about 100% equal to 0), and the sixteen document flags `FLAG_DOCUMENT_2`, `FLAG_DOCUMENT_4`, `FLAG_DOCUMENT_7`, `FLAG_DOCUMENT_9`, `FLAG_DOCUMENT_10`, `FLAG_DOCUMENT_11`, `FLAG_DOCUMENT_12`, `FLAG_DOCUMENT_13`, `FLAG_DOCUMENT_14`, `FLAG_DOCUMENT_15`, `FLAG_DOCUMENT_16`, `FLAG_DOCUMENT_17`, `FLAG_DOCUMENT_18`, `FLAG_DOCUMENT_19`, `FLAG_DOCUMENT_20`, `FLAG_DOCUMENT_21` (each under 1% equal to 1). These are removal candidates. The document flags that retain signal are `FLAG_DOCUMENT_3`, `FLAG_DOCUMENT_5`, `FLAG_DOCUMENT_6`, `FLAG_DOCUMENT_8`.

**Extreme outliers.** Four columns have a maximum above 20 times the 99th percentile: `AMT_INCOME_TOTAL` (1.17 × 10⁸), `AMT_REQ_CREDIT_BUREAU_QRT` (261), `OBS_30_CNT_SOCIAL_CIRCLE` (348), `OBS_60_CNT_SOCIAL_CIRCLE` (344). These require capping or winsorization before modeling.

**Transform and cardinality.** `AMT_INCOME_TOTAL` (skew 391) requires a log transform. `OCCUPATION_TYPE` (18 levels) and `ORGANIZATION_TYPE` (58 levels) require rare-category folding or target encoding.

**Sparse columns.** Forty-nine columns are missing in more than 40% of rows and require a missing indicator and binning. The 45 continuous columns are `EXT_SOURCE_1`, `OWN_CAR_AGE`, `TOTALAREA_MODE`, and the building descriptors:

- `APARTMENTS_AVG`, `APARTMENTS_MEDI`, `APARTMENTS_MODE`
- `BASEMENTAREA_AVG`, `BASEMENTAREA_MEDI`, `BASEMENTAREA_MODE`
- `COMMONAREA_AVG`, `COMMONAREA_MEDI`, `COMMONAREA_MODE`
- `ELEVATORS_AVG`, `ELEVATORS_MEDI`, `ELEVATORS_MODE`
- `ENTRANCES_AVG`, `ENTRANCES_MEDI`, `ENTRANCES_MODE`
- `FLOORSMAX_AVG`, `FLOORSMAX_MEDI`, `FLOORSMAX_MODE`
- `FLOORSMIN_AVG`, `FLOORSMIN_MEDI`, `FLOORSMIN_MODE`
- `LANDAREA_AVG`, `LANDAREA_MEDI`, `LANDAREA_MODE`
- `LIVINGAPARTMENTS_AVG`, `LIVINGAPARTMENTS_MEDI`, `LIVINGAPARTMENTS_MODE`
- `LIVINGAREA_AVG`, `LIVINGAREA_MEDI`, `LIVINGAREA_MODE`
- `NONLIVINGAPARTMENTS_AVG`, `NONLIVINGAPARTMENTS_MEDI`, `NONLIVINGAPARTMENTS_MODE`
- `NONLIVINGAREA_AVG`, `NONLIVINGAREA_MEDI`, `NONLIVINGAREA_MODE`
- `YEARS_BEGINEXPLUATATION_AVG`, `YEARS_BEGINEXPLUATATION_MEDI`, `YEARS_BEGINEXPLUATATION_MODE`
- `YEARS_BUILD_AVG`, `YEARS_BUILD_MEDI`, `YEARS_BUILD_MODE`

The 4 categorical columns are `EMERGENCYSTATE_MODE`, `FONDKAPREMONT_MODE`, `HOUSETYPE_MODE`, `WALLSMATERIAL_MODE`.

**Extreme tail: one error, several genuine rare events.** Screening for values at least 5 times the 99th percentile flags twelve numeric columns. `AMT_INCOME_TOTAL` dominates (max 117,000,000 = 248 times P99 472,500); 250 rows exceed 1,000,000, five exceed 5,000,000, three exceed 10,000,000. The top values (117,000,000 and 18,000,090) are implausible and consistent with data-entry errors; the remaining tail (3,950,059 to 13,500,000) may be genuine high-income clients. Treatment: cap `AMT_INCOME_TOTAL` at the 99.9th percentile (900,000). The remaining heavy tails are genuine rare counts rather than errors: `AMT_REQ_CREDIT_BUREAU_QRT` (max 261 = 131 times P99), `OBS_30_CNT_SOCIAL_CIRCLE` (348 = 35 times), `OBS_60_CNT_SOCIAL_CIRCLE` (344 = 34 times), `DEF_30_CNT_SOCIAL_CIRCLE` (34 = 17 times), `DEF_60_CNT_SOCIAL_CIRCLE` (24 = 12 times), `AMT_REQ_CREDIT_BUREAU_WEEK` (8 = 8 times), `AMT_REQ_CREDIT_BUREAU_MON` (27 = 7 times), `CNT_CHILDREN` (19 = 6 times). These are capped at the 99.9th percentile rather than deleted. `NONLIVINGAPARTMENTS_AVG`, `NONLIVINGAPARTMENTS_MEDI`, `NONLIVINGAPARTMENTS_MODE` also exceed five times P99, but this is an artifact of their normalized ratio (P99 near 0.1, max 1.0) and is handled with the sparse block.

**No extreme age or repayment ratio.** Age, from `DAYS_BIRTH` divided by 365.25, spans 20.5 to 69.1 years; no applicant exceeds 69.1. The repayment ratio `AMT_CREDIT` / `AMT_ANNUITY` spans 8.0 to 45.3 with median 20.0; no ratio exceeds 50. Neither field requires outlier treatment.

**Rare categories.** Categorical levels below 0.5% of rows are genuine, not errors, and are folded into "Other": `CODE_GENDER` = XNA (4 rows); `NAME_FAMILY_STATUS` = Unknown (2); `NAME_INCOME_TYPE` = Unemployed (22), Student (18), Businessman (10), Maternity leave (5); `NAME_EDUCATION_TYPE` = Academic degree (164); `NAME_TYPE_SUITE` = Other_A (866), Group of people (271); `NAME_HOUSING_TYPE` = Co-op apartment (1,122); `HOUSETYPE_MODE` = specific housing (1,499), terraced house (1,212); `OCCUPATION_TYPE` = Waiters/barmen staff (1,348), Secretaries (1,305), Realty agents (751), HR staff (563), IT staff (526); `ORGANIZATION_TYPE` = 29 of 58 levels (4.7% combined).

**Weak univariate association.** No single feature is a strong discriminator of `TARGET`. Across the 105 numeric columns the largest absolute point-biserial correlation is 0.179; across the 16 categorical columns the largest Cramér's V is 0.082. The leading numeric correlates are `EXT_SOURCE_3` (−0.179), `EXT_SOURCE_2` (−0.160), `EXT_SOURCE_1` (−0.155), `DAYS_BIRTH` (0.079), `DAYS_EMPLOYED` (0.075); the leading categorical correlates are `OCCUPATION_TYPE` (0.082), `ORGANIZATION_TYPE` (0.073), `NAME_INCOME_TYPE` (0.062), `NAME_EDUCATION_TYPE` (0.057), `CODE_GENDER` (0.055).

**Information value concentrates in the external scores.** Ranked by IV on the train fold, four features exceed 0.1: `EXT_SOURCE_3` (0.330), `EXT_SOURCE_2` (0.303), `EXT_SOURCE_1` (0.151), `DAYS_EMPLOYED` (0.112). The next tier, between 0.02 and 0.1, is led by `AMT_GOODS_PRICE` (0.091), `DAYS_BIRTH` (0.087), `OCCUPATION_TYPE` (0.083), `ORGANIZATION_TYPE` (0.068), `NAME_INCOME_TYPE` (0.056), `REGION_RATING_CLIENT_W_CITY` (0.052), `NAME_EDUCATION_TYPE` (0.049), `REGION_RATING_CLIENT` (0.048). Sixty-seven features fall below 0.02 and carry no usable univariate signal.

**Monotonicity is the exception.** Of the 72 continuous or ordinal columns, 18 show a monotonic default rate across ordered bins, 51 do not, and 3 have too few ordered bins to judge. Monotonic decreasing columns (higher value, lower default) are `EXT_SOURCE_1`, `EXT_SOURCE_2`, `EXT_SOURCE_3`, `FLOORSMAX_AVG`, `FLOORSMAX_MEDI`, `FLOORSMAX_MODE`, `LIVINGAREA_AVG`, `LIVINGAREA_MEDI`, `ELEVATORS_AVG`, `ELEVATORS_MEDI`, `ELEVATORS_MODE`, `AMT_REQ_CREDIT_BUREAU_MON`. Monotonic increasing columns are `DAYS_BIRTH`, `DAYS_ID_PUBLISH`, `REGION_RATING_CLIENT`, `REGION_RATING_CLIENT_W_CITY`, `DEF_30_CNT_SOCIAL_CIRCLE`, `DEF_60_CNT_SOCIAL_CIRCLE`.

**Employment tenure is predictive but not strictly monotonic.** Among employed applicants the `DAYS_EMPLOYED` default rate rises from 4.5% (longest tenure) to 11.6% (shortest tenure) before easing to 11.0% in the final bin; the column is recorded as non-monotonic. The 365,243 sentinel (unemployed, 44,143 rows in the train fold) is a separate bin defaulting at 5.4%, close to the longest-tenure group.

**Ratio features mostly do not improve on their raw parents.** Eleven ratio features (groups 1–4) were screened on the train fold against their raw parents. Only `ANNUITY_TO_CREDIT` beats both parents and is worth adopting; it ranks fifth overall. The rest are redundant or weaker than their better parent:

| Ratio | IV | Better parent | Parent IV |
|---|---|---|---|
| `ANNUITY_TO_CREDIT` | 0.0915 | `AMT_CREDIT` | 0.0448 |
| `EMPLOYED_TO_AGE` | 0.0907 | `DAYS_EMPLOYED` | 0.1115 |
| `CREDIT_TO_GOODS` | 0.0725 | `AMT_GOODS_PRICE` | 0.0914 |
| `ID_TO_AGE` | 0.0203 | `DAYS_BIRTH` | 0.0868 |
| `DEF60_TO_OBS60` | 0.0119 | `DEF_60_CNT_SOCIAL_CIRCLE` | 0.0138 |
| `CREDIT_TO_INCOME` | 0.0112 | `AMT_CREDIT` | 0.0448 |
| `DEF30_TO_OBS30` | 0.0110 | `DEF_30_CNT_SOCIAL_CIRCLE` | 0.0142 |
| `CHILDREN_TO_FAMILY` | 0.0068 | `CNT_CHILDREN` | 0.0068 |
| `ANNUITY_TO_INCOME` | 0.0063 | `AMT_ANNUITY` | 0.0247 |
| `REGISTRATION_TO_AGE` | 0.0047 | `DAYS_BIRTH` | 0.0868 |
| `INCOME_PER_MEMBER` | 0.0045 | `AMT_INCOME_TOTAL` | 0.0113 |

The scale-confound concern is valid for these columns, but the WoE binning of the raw amounts and counts already captures the target relationship, so the ratios add little in a univariate screen. Ratios may still help tree-based models through interactions, but they are not justified by univariate IV.

**Collinearity concentrates in the building block.** Spearman correlation on the 72 non-binary numeric columns (train fold) finds 14 groups of |r| > 0.9 covering 35 columns. Each building variable is stored three times (`_AVG`, `_MEDI`, `_MODE`) with mutual correlation above 0.98, so one aggregation per variable suffices; the area and year measures also cross-correlate and merge further. Representatives (highest IV per group) and the columns they replace:

| Representative | IV | Dropped |
|---|---|---|
| `AMT_GOODS_PRICE` | 0.0914 | `AMT_CREDIT` |
| `REGION_RATING_CLIENT_W_CITY` | 0.0516 | `REGION_RATING_CLIENT` |
| `FLOORSMAX_AVG` | 0.0379 | `FLOORSMAX_MEDI`, `FLOORSMAX_MODE` |
| `TOTALAREA_MODE` | 0.0352 | `LIVINGAREA_AVG`, `LIVINGAREA_MEDI`, `LIVINGAREA_MODE`, `APARTMENTS_AVG`, `APARTMENTS_MEDI`, `APARTMENTS_MODE`, `LIVINGAPARTMENTS_AVG`, `LIVINGAPARTMENTS_MEDI`, `LIVINGAPARTMENTS_MODE` |
| `ELEVATORS_AVG` | 0.0316 | `ELEVATORS_MEDI`, `ELEVATORS_MODE` |
| `YEARS_BEGINEXPLUATATION_MEDI` | 0.0285 | `YEARS_BEGINEXPLUATATION_AVG`, `YEARS_BEGINEXPLUATATION_MODE`, `YEARS_BUILD_AVG`, `YEARS_BUILD_MEDI`, `YEARS_BUILD_MODE` |
| `ENTRANCES_AVG` | 0.0271 | `ENTRANCES_MEDI`, `ENTRANCES_MODE` |
| `NONLIVINGAREA_AVG` | 0.0224 | `NONLIVINGAREA_MEDI`, `NONLIVINGAREA_MODE` |
| `BASEMENTAREA_AVG` | 0.0211 | `BASEMENTAREA_MEDI`, `BASEMENTAREA_MODE` |
| `FLOORSMIN_MEDI` | 0.0194 | `FLOORSMIN_AVG`, `FLOORSMIN_MODE` |
| `LANDAREA_AVG` | 0.0158 | `LANDAREA_MEDI`, `LANDAREA_MODE` |
| `COMMONAREA_AVG` | 0.0136 | `COMMONAREA_MEDI`, `COMMONAREA_MODE` |
| `NONLIVINGAPARTMENTS_MEDI` | 0.0111 | `NONLIVINGAPARTMENTS_AVG`, `NONLIVINGAPARTMENTS_MODE` |
| `OBS_30_CNT_SOCIAL_CIRCLE` | 0.0032 | `OBS_60_CNT_SOCIAL_CIRCLE` |

The non-building pairs are `AMT_CREDIT`–`AMT_GOODS_PRICE` (0.985), `REGION_RATING_CLIENT`–`REGION_RATING_CLIENT_W_CITY` (0.950), and `OBS_30_CNT_SOCIAL_CIRCLE`–`OBS_60_CNT_SOCIAL_CIRCLE` (0.997). These 35 columns are drop candidates; the remaining 37 numeric columns are pairwise distinct.

**Tree importance cross-checks the IV screen.** A histogram-gradient-boosting model fitted on the train fold (permutation importance, ROC AUC, three repeats on a 40,000-row subsample) yields importances whose Spearman rank correlation with IV is 0.59. The top ten by importance and their IV:

| Feature | Importance | IV |
|---|---|---|
| `EXT_SOURCE_3` | 0.0690 | 0.330 |
| `EXT_SOURCE_2` | 0.0497 | 0.303 |
| `EXT_SOURCE_1` | 0.0261 | 0.151 |
| `ORGANIZATION_TYPE` | 0.0238 | 0.068 |
| `AMT_GOODS_PRICE` | 0.0203 | 0.091 |
| `AMT_CREDIT` | 0.0160 | 0.045 |
| `CODE_GENDER` | 0.0087 | 0.038 |
| `DAYS_EMPLOYED` | 0.0082 | 0.112 |
| `DAYS_BIRTH` | 0.0078 | 0.087 |
| `AMT_ANNUITY` | 0.0071 | 0.025 |

The three external scores lead both rankings, and every feature with IV above 0.1 is in the top eight by importance, so the univariate screen misses none of the strong signal. `ORGANIZATION_TYPE` ranks fourth by importance but eighth by IV (0.068); its many levels are split finely by the tree. Tree-only candidates, important to the model but with IV below 0.02, are `NAME_CONTRACT_TYPE` (0.0031), `WEEKDAY_APPR_PROCESS_START` (0.0023), `AMT_INCOME_TOTAL` (0.0021), `AMT_REQ_CREDIT_BUREAU_YEAR` (0.0018), and `AMT_REQ_CREDIT_BUREAU_QRT` (0.0017); their absolute importance is small, so no material interaction-only feature is lost. The IV ranking is a sound basis for the column decisions.

---

## EDA 结论

**缺失具有信息量。** 缺失指标并非完全随机缺失，多个缺失携带违约信号。相对整体违约率 8.07%，缺失 `EXT_SOURCE_1`（56.4%）或 `EXT_SOURCE_3`（19.8%）的申请违约率更高（分别为 8.52% 与 9.31%，对照 7.50% 与 7.77%）；缺失 `OCCUPATION_TYPE`（31.4%）的申请违约率更低（6.51% 对照 8.79%），与 `DAYS_EMPLOYED = 365,243` 低风险群体一致。缺失建筑/区域信息的申请违约率更高（8.23% 对照 6.32%）。

**无泄漏，线性信号较弱。** 无特征与 `TARGET` 相同或互补，与 `TARGET` 的最大绝对相关系数为 0.179。线性相关最强的为 `EXT_SOURCE_3`（0.179）、`EXT_SOURCE_2`（0.161）、`EXT_SOURCE_1`（0.155），预示它们在信息值筛选中的排名。

**近常数列。** 20 列为近常数（单一取值占至少 99% 的行），方差可忽略：`FLAG_MOBIL` 与 `FLAG_CONT_MOBILE`（约 100% 为 1）、`AMT_REQ_CREDIT_BUREAU_DAY` 与 `AMT_REQ_CREDIT_BUREAU_HOUR`（约 100% 为 0），以及 16 个证件标志 `FLAG_DOCUMENT_2`、`FLAG_DOCUMENT_4`、`FLAG_DOCUMENT_7`、`FLAG_DOCUMENT_9`、`FLAG_DOCUMENT_10`、`FLAG_DOCUMENT_11`、`FLAG_DOCUMENT_12`、`FLAG_DOCUMENT_13`、`FLAG_DOCUMENT_14`、`FLAG_DOCUMENT_15`、`FLAG_DOCUMENT_16`、`FLAG_DOCUMENT_17`、`FLAG_DOCUMENT_18`、`FLAG_DOCUMENT_19`、`FLAG_DOCUMENT_20`、`FLAG_DOCUMENT_21`（均 <1% 为 1）。这些列为剔除候选。保留信号的证件标志为 `FLAG_DOCUMENT_3`、`FLAG_DOCUMENT_5`、`FLAG_DOCUMENT_6`、`FLAG_DOCUMENT_8`。

**极端离群值。** 4 列的最大值超过 99 分位数的 20 倍：`AMT_INCOME_TOTAL`（1.17 × 10⁸）、`AMT_REQ_CREDIT_BUREAU_QRT`（261）、`OBS_30_CNT_SOCIAL_CIRCLE`（348）、`OBS_60_CNT_SOCIAL_CIRCLE`（344）。需在建模前截断或缩尾处理。

**变换与基数。** `AMT_INCOME_TOTAL`（偏度 391）需对数变换。`OCCUPATION_TYPE`（18 类）与 `ORGANIZATION_TYPE`（58 类）需合并稀有类或目标编码。

**稀疏列。** 49 列缺失率超过 40%，需缺失指示与分箱。其中 45 个连续列为 `EXT_SOURCE_1`、`OWN_CAR_AGE`、`TOTALAREA_MODE`，以及建筑描述字段：

- `APARTMENTS_AVG`、`APARTMENTS_MEDI`、`APARTMENTS_MODE`
- `BASEMENTAREA_AVG`、`BASEMENTAREA_MEDI`、`BASEMENTAREA_MODE`
- `COMMONAREA_AVG`、`COMMONAREA_MEDI`、`COMMONAREA_MODE`
- `ELEVATORS_AVG`、`ELEVATORS_MEDI`、`ELEVATORS_MODE`
- `ENTRANCES_AVG`、`ENTRANCES_MEDI`、`ENTRANCES_MODE`
- `FLOORSMAX_AVG`、`FLOORSMAX_MEDI`、`FLOORSMAX_MODE`
- `FLOORSMIN_AVG`、`FLOORSMIN_MEDI`、`FLOORSMIN_MODE`
- `LANDAREA_AVG`、`LANDAREA_MEDI`、`LANDAREA_MODE`
- `LIVINGAPARTMENTS_AVG`、`LIVINGAPARTMENTS_MEDI`、`LIVINGAPARTMENTS_MODE`
- `LIVINGAREA_AVG`、`LIVINGAREA_MEDI`、`LIVINGAREA_MODE`
- `NONLIVINGAPARTMENTS_AVG`、`NONLIVINGAPARTMENTS_MEDI`、`NONLIVINGAPARTMENTS_MODE`
- `NONLIVINGAREA_AVG`、`NONLIVINGAREA_MEDI`、`NONLIVINGAREA_MODE`
- `YEARS_BEGINEXPLUATATION_AVG`、`YEARS_BEGINEXPLUATATION_MEDI`、`YEARS_BEGINEXPLUATATION_MODE`
- `YEARS_BUILD_AVG`、`YEARS_BUILD_MEDI`、`YEARS_BUILD_MODE`

4 个类别列为 `EMERGENCYSTATE_MODE`、`FONDKAPREMONT_MODE`、`HOUSETYPE_MODE`、`WALLSMATERIAL_MODE`。

**极端尾部：一处录入错误，其余为真实稀有事件。** 以「最大值 ≥ 第 99 分位数的 5 倍」筛查，共 12 个数值列命中。`AMT_INCOME_TOTAL` 最突出（最大值 117,000,000，为 P99 值 472,500 的 248 倍）；超过 1,000,000 的有 250 行、超过 5,000,000 的有 5 行、超过 10,000,000 的有 3 行。前两位（117,000,000 与 18,000,090）不合常理，符合录入错误特征；其余尾部（3,950,059 至 13,500,000）可能是真实的高收入客户。处理：将 `AMT_INCOME_TOTAL` 截断至第 99.9 分位数（900,000）。其余重尾为真实稀有计数而非错误：`AMT_REQ_CREDIT_BUREAU_QRT`（最大值 261，为 P99 的 131 倍）、`OBS_30_CNT_SOCIAL_CIRCLE`（348，35 倍）、`OBS_60_CNT_SOCIAL_CIRCLE`（344，34 倍）、`DEF_30_CNT_SOCIAL_CIRCLE`（34，17 倍）、`DEF_60_CNT_SOCIAL_CIRCLE`（24，12 倍）、`AMT_REQ_CREDIT_BUREAU_WEEK`（8，8 倍）、`AMT_REQ_CREDIT_BUREAU_MON`（27，7 倍）、`CNT_CHILDREN`（19，6 倍）。这些列在建模时截断至第 99.9 分位数而非删除。`NONLIVINGAPARTMENTS_AVG`、`NONLIVINGAPARTMENTS_MEDI`、`NONLIVINGAPARTMENTS_MODE` 亦超过 P99 的 5 倍，但这是其归一化比值的分布形态（P99 约 0.1，最大值 1.0），随稀疏区块一并处理。

**年龄与还款比无极端值。** 年龄（`DAYS_BIRTH` 除以 365.25）范围 20.5 至 69.1 岁，无申请人超过 69.1 岁。还款比 `AMT_CREDIT` / `AMT_ANNUITY` 范围 8.0 至 45.3、中位数 20.0，无比值超过 50。两字段均无需异常值处理。

**稀有类别。** 占比低于 0.5% 的类别为真实存在而非错误，处理为并入「Other」：`CODE_GENDER` = XNA（4 行）；`NAME_FAMILY_STATUS` = Unknown（2）；`NAME_INCOME_TYPE` = Unemployed（22）、Student（18）、Businessman（10）、Maternity leave（5）；`NAME_EDUCATION_TYPE` = Academic degree（164）；`NAME_TYPE_SUITE` = Other_A（866）、Group of people（271）；`NAME_HOUSING_TYPE` = Co-op apartment（1,122）；`HOUSETYPE_MODE` = specific housing（1,499）、terraced house（1,212）；`OCCUPATION_TYPE` = Waiters/barmen staff（1,348）、Secretaries（1,305）、Realty agents（751）、HR staff（563）、IT staff（526）；`ORGANIZATION_TYPE` = 58 类中的 29 类（合计 4.7%）。

**单变量关联较弱。** 无单一特征对 `TARGET` 具有强判别力。105 个数值列中最大的绝对点双列相关系数为 0.179；16 个类别列中最大的 Cramér's V 为 0.082。数值列前五为 `EXT_SOURCE_3`（−0.179）、`EXT_SOURCE_2`（−0.160）、`EXT_SOURCE_1`（−0.155）、`DAYS_BIRTH`（0.079）、`DAYS_EMPLOYED`（0.075）；类别列前五为 `OCCUPATION_TYPE`（0.082）、`ORGANIZATION_TYPE`（0.073）、`NAME_INCOME_TYPE`（0.062）、`NAME_EDUCATION_TYPE`（0.057）、`CODE_GENDER`（0.055）。

**信息值集中于外部评分。** 在训练折上按 IV 排序，四个特征超过 0.1：`EXT_SOURCE_3`（0.330）、`EXT_SOURCE_2`（0.303）、`EXT_SOURCE_1`（0.151）、`DAYS_EMPLOYED`（0.112）。次一级（0.02 至 0.1）由 `AMT_GOODS_PRICE`（0.091）、`DAYS_BIRTH`（0.087）、`OCCUPATION_TYPE`（0.083）、`ORGANIZATION_TYPE`（0.068）、`NAME_INCOME_TYPE`（0.056）、`REGION_RATING_CLIENT_W_CITY`（0.052）、`NAME_EDUCATION_TYPE`（0.049）、`REGION_RATING_CLIENT`（0.048）领衔。67 个特征低于 0.02，无可用的单变量信号。

**单调性是少数。** 72 个连续或有序列中，18 列违约率沿有序分箱单调变化，51 列不单调，3 列有序分箱过少无法判断。单调递减列（取值越高、违约率越低）为 `EXT_SOURCE_1`、`EXT_SOURCE_2`、`EXT_SOURCE_3`、`FLOORSMAX_AVG`、`FLOORSMAX_MEDI`、`FLOORSMAX_MODE`、`LIVINGAREA_AVG`、`LIVINGAREA_MEDI`、`ELEVATORS_AVG`、`ELEVATORS_MEDI`、`ELEVATORS_MODE`、`AMT_REQ_CREDIT_BUREAU_MON`。单调递增列为 `DAYS_BIRTH`、`DAYS_ID_PUBLISH`、`REGION_RATING_CLIENT`、`REGION_RATING_CLIENT_W_CITY`、`DEF_30_CNT_SOCIAL_CIRCLE`、`DEF_60_CNT_SOCIAL_CIRCLE`。

**雇佣时长有预测力但非严格单调。** 就业申请者中，`DAYS_EMPLOYED` 的违约率从最长工龄的 4.5% 升至最短工龄的 11.6%，末箱回落至 11.0%，该列记为非单调。365,243 哨兵值（无业，训练折中 44,143 行）为独立分箱，违约率 5.4%，接近最长工龄群体。

**比值特征大多未优于原始父列。** 在训练折上将 11 个比值（第 1–4 组）与其原始父列比较。仅 `ANNUITY_TO_CREDIT` 同时超过两个父列，值得采用，位列总排名第五。其余均冗余或弱于其较强父列：

| 比值 | IV | 较强父列 | 父列 IV |
|---|---|---|---|
| `ANNUITY_TO_CREDIT` | 0.0915 | `AMT_CREDIT` | 0.0448 |
| `EMPLOYED_TO_AGE` | 0.0907 | `DAYS_EMPLOYED` | 0.1115 |
| `CREDIT_TO_GOODS` | 0.0725 | `AMT_GOODS_PRICE` | 0.0914 |
| `ID_TO_AGE` | 0.0203 | `DAYS_BIRTH` | 0.0868 |
| `DEF60_TO_OBS60` | 0.0119 | `DEF_60_CNT_SOCIAL_CIRCLE` | 0.0138 |
| `CREDIT_TO_INCOME` | 0.0112 | `AMT_CREDIT` | 0.0448 |
| `DEF30_TO_OBS30` | 0.0110 | `DEF_30_CNT_SOCIAL_CIRCLE` | 0.0142 |
| `CHILDREN_TO_FAMILY` | 0.0068 | `CNT_CHILDREN` | 0.0068 |
| `ANNUITY_TO_INCOME` | 0.0063 | `AMT_ANNUITY` | 0.0247 |
| `REGISTRATION_TO_AGE` | 0.0047 | `DAYS_BIRTH` | 0.0868 |
| `INCOME_PER_MEMBER` | 0.0045 | `AMT_INCOME_TOTAL` | 0.0113 |

规模混杂的顾虑对这些列成立，但原始金额与计数的 WoE 分箱已捕捉到目标关系，故比值在单变量筛选中增益有限。比值仍可能通过交互作用帮助树模型，但单变量 IV 不足以支持预先采用。

**共线性集中于建筑区块。** 在训练折上对 72 个非二值数值列计算 Spearman 相关，得到 14 个 |r| > 0.9 的组，覆盖 35 列。每个建筑变量以 `_AVG`、`_MEDI`、`_MODE` 存储三份，两两相关高于 0.98，故每个变量保留一个聚合即可；面积与年份度量进一步交叉相关而合并。各组的代表列（组内 IV 最高）及其替换列：

| 代表列 | IV | 剔除列 |
|---|---|---|
| `AMT_GOODS_PRICE` | 0.0914 | `AMT_CREDIT` |
| `REGION_RATING_CLIENT_W_CITY` | 0.0516 | `REGION_RATING_CLIENT` |
| `FLOORSMAX_AVG` | 0.0379 | `FLOORSMAX_MEDI`、`FLOORSMAX_MODE` |
| `TOTALAREA_MODE` | 0.0352 | `LIVINGAREA_AVG`、`LIVINGAREA_MEDI`、`LIVINGAREA_MODE`、`APARTMENTS_AVG`、`APARTMENTS_MEDI`、`APARTMENTS_MODE`、`LIVINGAPARTMENTS_AVG`、`LIVINGAPARTMENTS_MEDI`、`LIVINGAPARTMENTS_MODE` |
| `ELEVATORS_AVG` | 0.0316 | `ELEVATORS_MEDI`、`ELEVATORS_MODE` |
| `YEARS_BEGINEXPLUATATION_MEDI` | 0.0285 | `YEARS_BEGINEXPLUATATION_AVG`、`YEARS_BEGINEXPLUATATION_MODE`、`YEARS_BUILD_AVG`、`YEARS_BUILD_MEDI`、`YEARS_BUILD_MODE` |
| `ENTRANCES_AVG` | 0.0271 | `ENTRANCES_MEDI`、`ENTRANCES_MODE` |
| `NONLIVINGAREA_AVG` | 0.0224 | `NONLIVINGAREA_MEDI`、`NONLIVINGAREA_MODE` |
| `BASEMENTAREA_AVG` | 0.0211 | `BASEMENTAREA_MEDI`、`BASEMENTAREA_MODE` |
| `FLOORSMIN_MEDI` | 0.0194 | `FLOORSMIN_AVG`、`FLOORSMIN_MODE` |
| `LANDAREA_AVG` | 0.0158 | `LANDAREA_MEDI`、`LANDAREA_MODE` |
| `COMMONAREA_AVG` | 0.0136 | `COMMONAREA_MEDI`、`COMMONAREA_MODE` |
| `NONLIVINGAPARTMENTS_MEDI` | 0.0111 | `NONLIVINGAPARTMENTS_AVG`、`NONLIVINGAPARTMENTS_MODE` |
| `OBS_30_CNT_SOCIAL_CIRCLE` | 0.0032 | `OBS_60_CNT_SOCIAL_CIRCLE` |

非建筑区块的配对为 `AMT_CREDIT`–`AMT_GOODS_PRICE`（0.985）、`REGION_RATING_CLIENT`–`REGION_RATING_CLIENT_W_CITY`（0.950）、`OBS_30_CNT_SOCIAL_CIRCLE`–`OBS_60_CNT_SOCIAL_CIRCLE`（0.997）。这 35 列为剔除候选；其余 37 个数值列两两独立。

**树重要性交叉印证 IV 筛选。** 在训练折上拟合直方图梯度提升模型（置换重要性，ROC AUC，40,000 行子样本上重复 3 次），其重要性与 IV 的 Spearman 秩相关系数为 0.59。重要性前十及对应 IV：

| 特征 | 重要性 | IV |
|---|---|---|
| `EXT_SOURCE_3` | 0.0690 | 0.330 |
| `EXT_SOURCE_2` | 0.0497 | 0.303 |
| `EXT_SOURCE_1` | 0.0261 | 0.151 |
| `ORGANIZATION_TYPE` | 0.0238 | 0.068 |
| `AMT_GOODS_PRICE` | 0.0203 | 0.091 |
| `AMT_CREDIT` | 0.0160 | 0.045 |
| `CODE_GENDER` | 0.0087 | 0.038 |
| `DAYS_EMPLOYED` | 0.0082 | 0.112 |
| `DAYS_BIRTH` | 0.0078 | 0.087 |
| `AMT_ANNUITY` | 0.0071 | 0.025 |

三个外部评分在两份排名中均居前列，且所有 IV 超过 0.1 的特征都进入重要性前八，故单变量筛选未遗漏任何强信号。`ORGANIZATION_TYPE` 重要性第四但 IV 第八（0.068），其多类别被树细粒度切分。仅对树重要、IV 低于 0.02 的候选为 `NAME_CONTRACT_TYPE`（0.0031）、`WEEKDAY_APPR_PROCESS_START`（0.0023）、`AMT_INCOME_TOTAL`（0.0021）、`AMT_REQ_CREDIT_BUREAU_YEAR`（0.0018）、`AMT_REQ_CREDIT_BUREAU_QRT`（0.0017）；其绝对重要性很小，故无实质性的交互型特征被遗漏。IV 排名是列决策的可靠依据。
