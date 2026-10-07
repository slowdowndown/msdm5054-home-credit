## Data Overview

**Data source.** The dataset is the official Kaggle Home Credit Default Risk competition data. The analysis focuses on the main application table `application_train.csv` (307,511 rows × 122 columns) and its test counterpart `application_test.csv` (48,744 rows × 121 columns). Each row is one loan application, keyed by `SK_ID_CURR` (307,511 unique values; no duplicate rows or identifiers; no train–test overlap). The main table can be joined to the bureau and previous-application branches by `SK_ID_CURR`.

**Target and metric.** `TARGET` is binary: 1 denotes a client with payment difficulties, 0 otherwise. The positive rate is 8.07% (24,825 of 307,511). Given the class imbalance, performance is measured by ROC AUC.

**Variables.** Excluding the key and target, the table has 104 numeric and 16 categorical features. Of the numeric features, 32 are binary flags (20 `FLAG_DOCUMENT_*` plus 12 contact and region-mismatch flags), 10 are low-cardinality counts or ordinal ratings (e.g. `CNT_CHILDREN`, `REGION_RATING_CLIENT`), and 62 are continuous, about 48 of which are the sparse building-region descriptors. Categorical cardinality is low to moderate, the largest being `ORGANIZATION_TYPE` (58 levels) and `OCCUPATION_TYPE` (18 levels).

**Missing values.** Missingness is widespread but bounded: the maximum column rate is 69.9% and no feature exceeds 80%. At the row level, only 2.8% of applications are fully complete, and the median row is missing 36 of 122 columns. Missingness concentrates in the building/region descriptors (about 47 fields, e.g. `COMMONAREA_*`, `LIVINGAPARTMENTS_*`) and in a few scores and demographic fields: `EXT_SOURCE_1` (56.4%), `OCCUPATION_TYPE` (31.3%), `EXT_SOURCE_3` (19.8%). By contrast, `EXT_SOURCE_2` (0.2%), all 20 `FLAG_DOCUMENT_*` flags, and the core loan/income/demographic fields are effectively complete. No feature is constant.

**Anomalies.** Two anomalies merit attention. First, `DAYS_EMPLOYED` takes the sentinel value 365,243 in 18.0% of applications (55,374); this group has a lower default rate (5.40%) than the remaining applicants (8.66%), indicating the sentinel marks a distinct lower-risk population rather than a random missing value. Second, `AMT_INCOME_TOTAL` has a maximum of 1.17 × 10⁸, extreme relative to the typical income distribution.

---

## 数据概览

**数据来源。** 数据为 Kaggle Home Credit Default Risk 竞赛的官方数据。分析聚焦主表 `application_train.csv`（307,511 行 × 122 列）及其测试集 `application_test.csv`（48,744 行 × 121 列）。每行为一笔贷款申请，主键为 `SK_ID_CURR`（307,511 个唯一值；无重复行或重复主键；训练集与测试集无重叠）。主表可通过 `SK_ID_CURR` 与 bureau、previous-application 两个分支关联。

**目标与指标。** `TARGET` 为二分类：1 表示客户存在还款困难，0 表示否。正样本率为 8.07%（24,825 / 307,511）。鉴于类别不平衡，模型性能以 ROC AUC 衡量。

**变量。** 除主键与目标外，表含 104 个数值特征与 16 个类别特征。数值特征中，32 个为二进制标志（20 个 `FLAG_DOCUMENT_*` 及 12 个联系方式/地区不一致标志），10 个为低基数计数或序数（如 `CNT_CHILDREN`、`REGION_RATING_CLIENT`），62 个为连续变量，其中约 48 个是稀疏的建筑/区域描述字段。类别基数较低到中等，最大为 `ORGANIZATION_TYPE`（58 类）与 `OCCUPATION_TYPE`（18 类）。

**缺失值。** 缺失普遍但有界：最高列缺失率为 69.9%，无特征超过 80%。行级上，仅 2.8% 的申请完全无缺失，每行缺失列数中位数为 36（共 122 列）。缺失集中在建筑/区域描述字段（约 47 列，如 `COMMONAREA_*`、`LIVINGAPARTMENTS_*`）及少数评分与人口字段：`EXT_SOURCE_1`（56.4%）、`OCCUPATION_TYPE`（31.3%）、`EXT_SOURCE_3`（19.8%）。相反，`EXT_SOURCE_2`（0.2%）、全部 20 个 `FLAG_DOCUMENT_*` 标志及核心的贷款/收入/人口字段基本完整。无常数特征。

**异常值。** 两处异常值得注意。其一，`DAYS_EMPLOYED` 在 18.0% 的申请（55,374 人）中取哨兵值 365,243；该群体违约率（5.40%）低于其余申请人（8.66%），表明该哨兵值标记的是独立的低风险人群，而非随机缺失。其二，`AMT_INCOME_TOTAL` 最大值为 1.17 × 10⁸，相对典型收入分布而言极端。
