# 系统 EDA 框架与 application_train 落点

本文档界定系统性 EDA 的方法框架，并给出其在 Home Credit 主表（`application_train.csv`，307,511 行 × 122 列）上的具体落点，作为 Phase 1 第 1 部分（字段级 EDA）的执行依据。

## 1. 定位

EDA 是建模前的系统性数据检查，产出可交付物；与 CDA（验证性分析）相对，EDA 生成假设、发现问题，CDA 严格检验假设。

EDA 结束时应具备四类交付物：

| 交付物 | 内容 | 本项目对应物 |
|---|---|---|
| 数据字典 | 每列含义、单位、合法范围 | `docs/application_train_fields.md` |
| 质量报告 | 缺失、重复、异常、解析问题 | 本次 EDA 核心产出 |
| 风险清单 | 泄漏、混淆、哨兵值 | `DAYS_EMPLOYED=365243` 等 |
| 建模就绪判断 | 数据能否建模、尚缺什么 | 交接 ZHANG 的结论 |

## 2. 三层结构

按变量数量分层，构成 EDA 主线：

| 层级 | 范围 | 方法 |
|---|---|---|
| 单变量 | 一次一列 | 分布、缺失、异常、离群 |
| 双变量 | 两两关系 | 相关、分组比较，重点是每列与 `TARGET` 的关系 |
| 多变量 | 三个及以上变量 | 交互、相关矩阵、维度压缩 |

## 3. 有序检查流程

顺序不可调换：前置问题会污染后续结论。流程为：

```
数据规模 → 类型检查 → 缺失分析 → 主键/重复 → 目标检查 → 泄漏检查 → 分布 → 关系 → （可选）基线模型
```

各步骤在本数据的落点：

| 步骤 | 做什么 | application_train 落点 |
|---|---|---|
| 1 数据规模 | 行列数、来源、时间范围 | train 307,511×122；test 48,744×121（已记录于 `results/baseline/quality.json`） |
| 2 类型检查 | dtype、解析错误、类别层级 | `DAYS_*` 为负整数（距申请日天数）；`FLAG_*` 为 0/1；`NAME_*`/`ORGANIZATION_TYPE` 为字符串类别；`AMT_*` 为浮点 |
| 3 缺失分析 | 每列/每行缺失率、缺失模式 | 已有 `results/baseline/field_profile.csv`；重点识别 `DAYS_EMPLOYED=365243` 伪缺失（哨兵值），并检验缺失本身是否预测违约 |
| 4 主键/重复 | 主键唯一性 | `SK_ID_CURR` 应为 307,511 个唯一值，无重复贷款 |
| 5 目标检查 | 类别平衡、目标定义 | `TARGET` 正样本率 8.07%（24,825/307,511），高度不平衡，指标须用 ROC AUC |
| 6 单变量分布 | 直方图/箱线图、范围检查 | `AMT_INCOME_TOTAL` 约 1.17 亿极端值；`DAYS_EMPLOYED=365243` 尖峰；`CNT_FAM_MEMBERS`、`OBS_30_CNT_SOCIAL_CIRCLE` 长尾；`EXT_SOURCE_*` 为 0–1 归一化分数 |
| 7 异常值 | 极端值、稀有类别 | 收入 1.17 亿；年龄 >100 岁（`DAYS_BIRTH < -36500`）；贷款/年金比极端值。判断是错误还是真实稀有事件，不盲目删除 |
| 8 关系 | 相关、分组比较、散点 | 见第 4 节 WoE/IV；数值相关用 Pearson/Spearman，类别相关用 Cramér's V 或 Phik，识别多重共线性 |
| 9 泄漏检查 | 特征是否编码未来信息 | 主表内风险低；`SK_ID_CURR` 不得作为特征；多表 join 的时间对齐留待后续阶段 |

## 4. 信贷专项：WoE / IV 分箱

针对信用违约预测的双变量方法，用于特征筛选与可解释性，直接支撑 Phase 1 的约 10 个可解释特征。

做法：

1. 连续变量分箱（如年龄、`EXT_SOURCE_1` 各分 10 箱）。
2. 每箱计算违约率（`TARGET=1` 占比）。
3. WoE（证据权重）= ln(箱内好样本占比 / 箱内坏样本占比)，好样本为 `TARGET=0`。
4. IV（信息值）= Σ(好占比 − 坏占比) × WoE，衡量整列预测力。

IV 阈值：

| IV 值 | 预测力 |
|---|---|
| < 0.02 | 无 |
| 0.02–0.1 | 弱 |
| 0.1–0.3 | 中 |
| 0.3–0.5 | 强 |
| > 0.5 | 可疑，需查泄漏 |

对 122 列计算 IV 并排序，即可筛出最强可解释特征。同时检查单调性：特征分箱违约率应随取值单调变化，不单调需重新分箱或变换。

## 5. 工具

| 方式 | 工具 | 适用场景 |
|---|---|---|
| 手动 | pandas + `src/plotting.py` | 论文配图，黑白风格，精确控制 |
| 自动化 | ydata-profiling / sweetviz | 生成 HTML 总览，先扫全局再深挖 |

两者不冲突：自动化工具快速扫全局，论文图用手动黑白风格重绘。

## 6. 已知异常点

| 异常 | 说明 | 处理原则 |
|---|---|---|
| `DAYS_EMPLOYED=365243` | 哨兵值，表示失业/未填，非普通缺失 | 单独识别，不能当 NaN 中位数填充 |
| `AMT_INCOME_TOTAL` ≈ 1.17 亿 | 极端值，疑似录入错误 | 先判断来源，不盲目删除 |
| `FLAG_DOCUMENT_*`（20 列） | 大量缺失或单一取值 | 结合缺失率与 IV 决定保留或剔除 |

## 7. Phase 1 第 1 部分执行顺序

1. 运行 ydata-profiling 生成全局总览。
2. 逐域绘制单变量分布图（`src/plotting.py` 黑白风格）。
3. 逐域分析与 `TARGET` 的关系（分箱违约率 + IV 排名）。
4. 单独处理已知异常点（第 6 节）。
5. 每域写结论，汇总为字段级理解。

## 8. 参考来源

- Georgia Tech OMSCS 7641，Beginner's Guide to Exploratory Data Analysis
- Airbyte，Exploratory Data Analysis — A Complete Guide
- IBM，What is Exploratory Data Analysis
- TIBCO Documentation，Weight of Evidence (WoE) Overview
- ListenData，Weight of Evidence (WOE) and Information Value (IV) Explained
