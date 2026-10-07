# 列级特征决策清单（给 ZHANG 的特征工程输入）

本文档将 EDA 第 8 步（关系分析）与第 6、7 步（分布、离群值）的结论合并为逐列决策，供特征工程与建模直接使用。所有统计均在固定划分的训练折（246,008 行）上计算，未触碰验证折。

## 决策总览

| 决策 | 数量 | 依据 |
|---|---|---|
| DROP（近常数） | 20 | ≥99% 行取单一值，无方差 |
| DROP（共线冗余） | 35 | 与更高 IV 代表列的 \|r\| > 0.9 |
| KEEP | 65 | 保留，按需变换 |
| ADD（派生） | 1 | `ANNUITY_TO_CREDIT`，唯一优于两个父列的比值 |
| **进模型合计** | **66** | 编码前宽度 |

## 决策规则与依据

| 规则 | 判定标准 | 依据（findings 段落 / 图） |
|---|---|---|
| 近常数删除 | 单一取值占比 ≥99% | 「近常数列」/ 图 05–06 |
| 共线删除 | Spearman \|r\| > 0.9，保留组内 IV 最高列 | 「共线性集中于建筑区块」/ 图 26 |
| IV 筛选 | IV < 0.02 无可用单变量信号，IV 排名与树重要性一致 | 「信息值集中于外部评分」/ 图 23、27 |
| 离群值截尾 | 最大值 > P99 的 20 倍，截断至 P99.9 | 「极端离群值」「极端尾部」/ 图 19–21 |
| 收入对数 | `AMT_INCOME_TOTAL` 偏度 391，取 log1p | 「变换与基数」/ 图 02 |
| 哨兵缺失 | `DAYS_EMPLOYED = 365243`（18%）视为缺失 | 「雇佣时长有预测力但非严格单调」/ 图 24 |
| 稀有类别 | 占比 <0.5% 并入 Other | 「稀有类别」/ 图 12–14 |
| 稀疏分箱 | 缺失率 >40% 加缺失指示并分箱 | 「稀疏列」/ 图 16–17 |

## DROP（近常数，20 列）

`FLAG_MOBIL`、`FLAG_CONT_MOBILE`、`AMT_REQ_CREDIT_BUREAU_DAY`、`AMT_REQ_CREDIT_BUREAU_HOUR`，以及 16 个证件标志 `FLAG_DOCUMENT_2`、`FLAG_DOCUMENT_4`、`FLAG_DOCUMENT_7`、`FLAG_DOCUMENT_9`、`FLAG_DOCUMENT_10`、`FLAG_DOCUMENT_11`、`FLAG_DOCUMENT_12`、`FLAG_DOCUMENT_13`、`FLAG_DOCUMENT_14`、`FLAG_DOCUMENT_15`、`FLAG_DOCUMENT_16`、`FLAG_DOCUMENT_17`、`FLAG_DOCUMENT_18`、`FLAG_DOCUMENT_19`、`FLAG_DOCUMENT_20`、`FLAG_DOCUMENT_21`。

## DROP（共线冗余，35 列，按代表列分组）

每组保留代表列（组内 IV 最高），删除其余。完整 14 组：

| 代表列 | IV | 删除列 |
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

说明：`AMT_CREDIT` 被删除，但其金额信号由派生特征 `ANNUITY_TO_CREDIT = AMT_ANNUITY / AMT_CREDIT` 吸收；计算该比值使用原始 `AMT_CREDIT`，仅将原始列排除在模型之外。

## ADD（派生，1 列）

| 派生特征 | 公式 | IV | 说明 |
|---|---|---|---|
| `ANNUITY_TO_CREDIT` | `AMT_ANNUITY / AMT_CREDIT`，零分母 → NaN | 0.0915 | 唯一优于两个父列（`AMT_ANNUITY` 0.0247、`AMT_CREDIT` 0.0448）的比值，总排名第五 |

其余 10 个比值（`EMPLOYED_TO_AGE`、`CREDIT_TO_GOODS`、`ID_TO_AGE`、`DEF60_TO_OBS60`、`CREDIT_TO_INCOME`、`DEF30_TO_OBS30`、`CHILDREN_TO_FAMILY`、`ANNUITY_TO_INCOME`、`REGISTRATION_TO_AGE`、`INCOME_PER_MEMBER`）不优于其较强父列，不采用。

## KEEP（65 列，按 IV 降序）

变换标记：`bin` = 缺失指示 + 分箱；`log` = log1p；`cap` = 截断至 P99.9；`sent` = 哨兵转缺失；`target` = 稀有合并 + 目标编码；`label` = 稀有合并 + 标签编码。

| 特征 | IV | 变换 |
|---|---|---|
| `EXT_SOURCE_3` | 0.3297 | — |
| `EXT_SOURCE_2` | 0.3031 | — |
| `EXT_SOURCE_1` | 0.1512 | bin |
| `DAYS_EMPLOYED` | 0.1115 | sent |
| `AMT_GOODS_PRICE` | 0.0914 | — |
| `DAYS_BIRTH` | 0.0868 | — |
| `OCCUPATION_TYPE` | 0.0832 | target |
| `ORGANIZATION_TYPE` | 0.0682 | target |
| `NAME_INCOME_TYPE` | 0.0559 | label |
| `REGION_RATING_CLIENT_W_CITY` | 0.0516 | — |
| `NAME_EDUCATION_TYPE` | 0.0492 | label |
| `DAYS_LAST_PHONE_CHANGE` | 0.0446 | — |
| `CODE_GENDER` | 0.0384 | label |
| `FLOORSMAX_AVG` | 0.0379 | bin |
| `DAYS_ID_PUBLISH` | 0.0359 | — |
| `TOTALAREA_MODE` | 0.0352 | bin |
| `REGION_POPULATION_RELATIVE` | 0.0342 | — |
| `FLAG_EMP_PHONE` | 0.0336 | — |
| `REG_CITY_NOT_WORK_CITY` | 0.0330 | — |
| `ELEVATORS_AVG` | 0.0316 | bin |
| `FLAG_DOCUMENT_3` | 0.0285 | — |
| `YEARS_BEGINEXPLUATATION_MEDI` | 0.0285 | bin |
| `DAYS_REGISTRATION` | 0.0274 | — |
| `ENTRANCES_AVG` | 0.0271 | bin |
| `WALLSMATERIAL_MODE` | 0.0271 | bin |
| `AMT_ANNUITY` | 0.0247 | — |
| `EMERGENCYSTATE_MODE` | 0.0236 | bin |
| `REG_CITY_NOT_LIVE_CITY` | 0.0235 | — |
| `NAME_FAMILY_STATUS` | 0.0233 | label |
| `OWN_CAR_AGE` | 0.0231 | bin |
| `NONLIVINGAREA_AVG` | 0.0224 | bin |
| `HOUSETYPE_MODE` | 0.0216 | bin |
| `BASEMENTAREA_AVG` | 0.0211 | bin |
| `FLOORSMIN_MEDI` | 0.0194 | bin |
| `AMT_REQ_CREDIT_BUREAU_YEAR` | 0.0176 | — |
| `AMT_REQ_CREDIT_BUREAU_QRT` | 0.0172 | cap |
| `NAME_HOUSING_TYPE` | 0.0160 | label |
| `LANDAREA_AVG` | 0.0158 | bin |
| `AMT_REQ_CREDIT_BUREAU_MON` | 0.0155 | — |
| `NAME_CONTRACT_TYPE` | 0.0149 | label |
| `DEF_30_CNT_SOCIAL_CIRCLE` | 0.0142 | — |
| `LIVE_CITY_NOT_WORK_CITY` | 0.0139 | — |
| `DEF_60_CNT_SOCIAL_CIRCLE` | 0.0138 | — |
| `COMMONAREA_AVG` | 0.0136 | bin |
| `AMT_REQ_CREDIT_BUREAU_WEEK` | 0.0134 | — |
| `FLAG_DOCUMENT_6` | 0.0121 | — |
| `FONDKAPREMONT_MODE` | 0.0118 | bin |
| `AMT_INCOME_TOTAL` | 0.0113 | log、cap |
| `NONLIVINGAPARTMENTS_MEDI` | 0.0111 | bin |
| `HOUR_APPR_PROCESS_START` | 0.0109 | — |
| `FLAG_WORK_PHONE` | 0.0102 | — |
| `FLAG_PHONE` | 0.0079 | — |
| `CNT_CHILDREN` | 0.0068 | — |
| `CNT_FAM_MEMBERS` | 0.0066 | — |
| `FLAG_OWN_CAR` | 0.0061 | label |
| `OBS_30_CNT_SOCIAL_CIRCLE` | 0.0032 | cap |
| `NAME_TYPE_SUITE` | 0.0022 | label |
| `FLAG_DOCUMENT_8` | 0.0010 | — |
| `WEEKDAY_APPR_PROCESS_START` | 0.0007 | label |
| `REG_REGION_NOT_WORK_REGION` | 0.0006 | — |
| `FLAG_OWN_REALTY` | 0.0005 | label |
| `REG_REGION_NOT_LIVE_REGION` | 0.0003 | — |
| `LIVE_REGION_NOT_WORK_REGION` | 0.0001 | — |
| `FLAG_DOCUMENT_5` | 0.0000 | — |
| `FLAG_EMAIL` | 0.0000 | — |

## 变换规则汇总

| 变换 | 适用列 |
|---|---|
| log1p | `AMT_INCOME_TOTAL` |
| 截断 P99.9 | `AMT_INCOME_TOTAL`（900,000）、`AMT_REQ_CREDIT_BUREAU_QRT`、`OBS_30_CNT_SOCIAL_CIRCLE` |
| 哨兵转缺失 | `DAYS_EMPLOYED`（365243 → NaN，缺失指示） |
| 稀有合并 + 目标编码 | `OCCUPATION_TYPE`、`ORGANIZATION_TYPE` |
| 稀有合并 + 标签编码 | `NAME_INCOME_TYPE`、`NAME_EDUCATION_TYPE`、`CODE_GENDER`、`NAME_FAMILY_STATUS`、`NAME_HOUSING_TYPE`、`NAME_CONTRACT_TYPE`、`NAME_TYPE_SUITE`、`WEEKDAY_APPR_PROCESS_START`、`FLAG_OWN_CAR`、`FLAG_OWN_REALTY` |
| 缺失指示 + 分箱 | 稀疏区块代表列（`FLOORSMAX_AVG`、`TOTALAREA_MODE`、`ELEVATORS_AVG`、`YEARS_BEGINEXPLUATATION_MEDI`、`ENTRANCES_AVG`、`NONLIVINGAREA_AVG`、`BASEMENTAREA_AVG`、`FLOORSMIN_MEDI`、`LANDAREA_AVG`、`COMMONAREA_AVG`、`NONLIVINGAPARTMENTS_MEDI`、`OWN_CAR_AGE`、`EXT_SOURCE_1`）与 4 个类别 MODE 列（`WALLSMATERIAL_MODE`、`EMERGENCYSTATE_MODE`、`HOUSETYPE_MODE`、`FONDKAPREMONT_MODE`） |

## 复现步骤

按依赖顺序运行，环境为 Anaconda（scikit-learn 1.4.2、scipy 1.13.1）：

```bash
cd msdm5054-home-credit

python scripts/eda/eda_univariate.py          # 近常数/稀疏/变换标志 → univariate_flags.json
python scripts/eda/eda_outliers.py            # 离群值 → outliers.json
python scripts/eda/eda_deepen_1_5.py          # 缺失与泄漏 → step1_5_deepen.json
python scripts/eda/eda_relationships.py       # WoE/IV/关联/单调 → iv_ranking.csv, woe_bins.json
python scripts/eda/eda_derived_iv.py          # 派生比值 → derived_iv_ranking.csv（依赖上一步）
python scripts/eda/eda_collinearity.py        # 共线性 → collinearity_groups.json（依赖 iv_ranking.csv）
python scripts/eda/eda_tree_importance.py     # 树重要性交叉印证 → importance_iv_crosscheck.csv（耗时较长）
python scripts/eda/make_column_decisions.py   # 本清单 → column_decisions.csv
python scripts/eda/make_eda_figures.py        # 图 00–27 → results/eda/figures/
```

机器可读的逐列清单见 `results/eda/column_decisions.csv`（列：`feature`、`decision`、`transform`、`reason`、`iv`、`type`）。
