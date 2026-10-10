# application_train 字段清单

来源：`HomeCredit_columns_description.csv`（官方描述）+ `application_train.csv`（类型、缺失率、示例）。主表共 122 列。

缺失率与唯一值取自 results/baseline/field_profile.csv（完整训练集）；示例为样本前 2000 行中该字段的第一个非空值。

## 0. 主键与目标

| 字段 | 类型 | 缺失率 | 唯一值 | 示例 | 含义 | 官方描述 |
|---|---|---|---|---|---|---|
| SK_ID_CURR | int64 | 0.0% | 307511 | 100002 | 贷款申请编号（主键） | ID of loan in our sample |
| TARGET | int64 | 0.0% | 2 | 1 | 还款困难标志（1=有困难） | Target variable (1 - client with payment difficulties: he/she had late payment more than X days on at least one of the first Y installments of the loan in our sample, 0 - all other cases) |

## 1. 贷款信息

| 字段 | 类型 | 缺失率 | 唯一值 | 示例 | 含义 | 官方描述 |
|---|---|---|---|---|---|---|
| NAME_CONTRACT_TYPE | object | 0.0% | 2 | Cash loans | 贷款类型（现金贷/循环贷） | Identification if loan is cash or revolving |
| AMT_CREDIT | float64 | 0.0% | 5603 | 4.066e+05 | 贷款金额 | Credit amount of the loan |
| AMT_ANNUITY | float64 | 0.0% | 13672 | 2.47e+04 | 贷款年金（每期还款额） | Loan annuity |
| AMT_GOODS_PRICE | float64 | 0.1% | 1002 | 3.51e+05 | 消费贷对应商品价格 | For consumer loans it is the price of the goods for which the loan is given |
| WEEKDAY_APPR_PROCESS_START | object | 0.0% | 7 | WEDNESDAY | 申请日星期 | On which day of the week did the client apply for the loan |
| HOUR_APPR_PROCESS_START | int64 | 0.0% | 24 | 10 | 申请时点（小时） | Approximately at what hour did the client apply for the loan |

## 2. 客户人口统计

| 字段 | 类型 | 缺失率 | 唯一值 | 示例 | 含义 | 官方描述 |
|---|---|---|---|---|---|---|
| CODE_GENDER | object | 0.0% | 3 | M | 性别 | Gender of the client |
| CNT_CHILDREN | int64 | 0.0% | 15 | 0 | 子女数 | Number of children the client has |
| NAME_TYPE_SUITE | object | 0.4% | 7 | Unaccompanied | 申请时随行人员 | Who was accompanying client when he was applying for the loan |
| NAME_INCOME_TYPE | object | 0.0% | 8 | Working | 收入类型 | Clients income type (businessman, working, maternity leave,…) |
| NAME_EDUCATION_TYPE | object | 0.0% | 5 | Secondary / secon... | 最高学历 | Level of highest education the client achieved |
| NAME_FAMILY_STATUS | object | 0.0% | 6 | Single / not marr... | 婚姻状况 | Family status of the client |
| NAME_HOUSING_TYPE | object | 0.0% | 6 | House / apartment | 居住状况 | What is the housing situation of the client (renting, living with parents, ...) |
| OCCUPATION_TYPE | object | 31.3% | 18 | Laborers | 职业 | What kind of occupation does the client have |
| CNT_FAM_MEMBERS | float64 | 0.0% | 17 | 1 | 家庭人数 | How many family members does client have |
| ORGANIZATION_TYPE | object | 0.0% | 58 | Business Entity T... | 雇主机构类型 | Type of organization where client works |

## 3. 收入

| 字段 | 类型 | 缺失率 | 唯一值 | 示例 | 含义 | 官方描述 |
|---|---|---|---|---|---|---|
| AMT_INCOME_TOTAL | float64 | 0.0% | 2548 | 2.025e+05 | 年收入 | Income of the client |

## 4. 房产与车辆

| 字段 | 类型 | 缺失率 | 唯一值 | 示例 | 含义 | 官方描述 |
|---|---|---|---|---|---|---|
| FLAG_OWN_CAR | object | 0.0% | 2 | N | 是否有车 | Flag if the client owns a car |
| FLAG_OWN_REALTY | object | 0.0% | 2 | Y | 是否有房产 | Flag if client owns a house or flat |
| OWN_CAR_AGE | float64 | 66.0% | 62 | 26 | 车龄（年） | Age of client's car |

## 5. 时间字段（相对申请日）

| 字段 | 类型 | 缺失率 | 唯一值 | 示例 | 含义 | 官方描述 |
|---|---|---|---|---|---|---|
| DAYS_BIRTH | int64 | 0.0% | 17460 | -9461 | 出生距申请日天数（负） | Client's age in days at the time of application |
| DAYS_EMPLOYED | int64 | 0.0% | 12574 | -637 | 当前工作开始距申请日天数（负；365243=未就业） | How many days before the application the person started current employment |
| DAYS_REGISTRATION | float64 | 0.0% | 15688 | -3648 | 变更登记地址距申请日天数 | How many days before the application did client change his registration |
| DAYS_ID_PUBLISH | int64 | 0.0% | 6168 | -2120 | 换发身份证距申请日天数 | How many days before the application did client change the identity document with which he applied for the loan |
| DAYS_LAST_PHONE_CHANGE | float64 | 0.0% | 3773 | -1134 | 换手机号距申请日天数 | How many days before application did client change phone |

## 6. 联系方式标志

| 字段 | 类型 | 缺失率 | 唯一值 | 示例 | 含义 | 官方描述 |
|---|---|---|---|---|---|---|
| FLAG_MOBIL | int64 | 0.0% | 2 | 1 | 提供手机号 | Did client provide mobile phone (1=YES, 0=NO) |
| FLAG_EMP_PHONE | int64 | 0.0% | 2 | 1 | 提供工作电话 | Did client provide work phone (1=YES, 0=NO) |
| FLAG_WORK_PHONE | int64 | 0.0% | 2 | 0 | 提供单位电话 | Did client provide home phone (1=YES, 0=NO) |
| FLAG_CONT_MOBILE | int64 | 0.0% | 2 | 1 | 手机可接通 | Was mobile phone reachable (1=YES, 0=NO) |
| FLAG_PHONE | int64 | 0.0% | 2 | 1 | 提供家庭电话 | Did client provide home phone (1=YES, 0=NO) |
| FLAG_EMAIL | int64 | 0.0% | 2 | 0 | 提供邮箱 | Did client provide email (1=YES, 0=NO) |

## 7. 地区

| 字段 | 类型 | 缺失率 | 唯一值 | 示例 | 含义 | 官方描述 |
|---|---|---|---|---|---|---|
| REGION_POPULATION_RELATIVE | float64 | 0.0% | 81 | 0.0188 | 居住地区人口（标准化） | Normalized population of region where client lives (higher number means the client lives in more populated region) |
| REGION_RATING_CLIENT | int64 | 0.0% | 3 | 2 | 居住地评分（1/2/3） | Our rating of the region where client lives (1,2,3) |
| REGION_RATING_CLIENT_W_CITY | int64 | 0.0% | 3 | 2 | 含城市地评分（1/2/3） | Our rating of the region where client lives with taking city into account (1,2,3) |
| REG_REGION_NOT_LIVE_REGION | int64 | 0.0% | 2 | 0 | 常住地与联系地址不同区 | Flag if client's permanent address does not match contact address (1=different, 0=same, at region level) |
| REG_REGION_NOT_WORK_REGION | int64 | 0.0% | 2 | 0 | 常住地与工作地址不同区 | Flag if client's permanent address does not match work address (1=different, 0=same, at region level) |
| LIVE_REGION_NOT_WORK_REGION | int64 | 0.0% | 2 | 0 | 联系地址与工作地址不同区 | Flag if client's contact address does not match work address (1=different, 0=same, at region level) |
| REG_CITY_NOT_LIVE_CITY | int64 | 0.0% | 2 | 0 | 常住地与联系地址不同城市 | Flag if client's permanent address does not match contact address (1=different, 0=same, at city level) |
| REG_CITY_NOT_WORK_CITY | int64 | 0.0% | 2 | 0 | 常住地与工作地址不同城市 | Flag if client's permanent address does not match work address (1=different, 0=same, at city level) |
| LIVE_CITY_NOT_WORK_CITY | int64 | 0.0% | 2 | 0 | 联系地址与工作地址不同城市 | Flag if client's contact address does not match work address (1=different, 0=same, at city level) |

## 8. 外部评分

| 字段 | 类型 | 缺失率 | 唯一值 | 示例 | 含义 | 官方描述 |
|---|---|---|---|---|---|---|
| EXT_SOURCE_1 | float64 | 56.4% | 114584 | 0.08304 | 外部信用评分 1（标准化） | Normalized score from external data source |
| EXT_SOURCE_2 | float64 | 0.2% | 119831 | 0.2629 | 外部信用评分 2（标准化） | Normalized score from external data source |
| EXT_SOURCE_3 | float64 | 19.8% | 814 | 0.1394 | 外部信用评分 3（标准化） | Normalized score from external data source |

## 9. 居住建筑信息

此组为 14 个基础指标 × 3 种聚合（`_AVG` 均值 / `_MODE` 众数 / `_MEDI` 中位数），均为标准化值；另含 5 个类别型建筑字段。官方描述统一为：

> Normalized information about building where the client lives, What is average (_AVG suffix), modus (_MODE suffix), median (_MEDI suffix) apartment size, common area, living area, age of building, number of elevators, number of entrances, state of the building, number of floor

| 字段 | 类型 | 缺失率 | 唯一值 | 示例 | 含义 | 官方描述 |
|---|---|---|---|---|---|---|
| APARTMENTS_AVG | float64 | 50.7% | 2339 | 0.0247 | 公寓面积（均值） |  |
| BASEMENTAREA_AVG | float64 | 58.5% | 3780 | 0.0369 | 地下室面积（均值） |  |
| YEARS_BEGINEXPLUATATION_AVG | float64 | 48.8% | 285 | 0.9722 | 建筑启用年份（均值） |  |
| YEARS_BUILD_AVG | float64 | 66.5% | 149 | 0.6192 | 建成年份（均值） |  |
| COMMONAREA_AVG | float64 | 69.9% | 3181 | 0.0143 | 公共区域面积（均值） |  |
| ELEVATORS_AVG | float64 | 53.3% | 257 | 0 | 电梯数量（均值） |  |
| ENTRANCES_AVG | float64 | 50.3% | 285 | 0.069 | 入口数量（均值） |  |
| FLOORSMAX_AVG | float64 | 49.8% | 403 | 0.0833 | 最高楼层（均值） |  |
| FLOORSMIN_AVG | float64 | 67.8% | 305 | 0.125 | 最低楼层（均值） |  |
| LANDAREA_AVG | float64 | 59.4% | 3527 | 0.0369 | 土地面积（均值） |  |
| LIVINGAPARTMENTS_AVG | float64 | 68.4% | 1868 | 0.0202 | 居住公寓数（均值） |  |
| LIVINGAREA_AVG | float64 | 50.2% | 5199 | 0.019 | 居住面积（均值） |  |
| NONLIVINGAPARTMENTS_AVG | float64 | 69.4% | 386 | 0 | 非居住公寓数（均值） |  |
| NONLIVINGAREA_AVG | float64 | 55.2% | 3290 | 0 | 非居住面积（均值） |  |
| APARTMENTS_MODE | float64 | 50.7% | 760 | 0.0252 | 公寓面积（众数） |  |
| BASEMENTAREA_MODE | float64 | 58.5% | 3841 | 0.0383 | 地下室面积（众数） |  |
| YEARS_BEGINEXPLUATATION_MODE | float64 | 48.8% | 221 | 0.9722 | 建筑启用年份（众数） |  |
| YEARS_BUILD_MODE | float64 | 66.5% | 154 | 0.6341 | 建成年份（众数） |  |
| COMMONAREA_MODE | float64 | 69.9% | 3128 | 0.0144 | 公共区域面积（众数） |  |
| ELEVATORS_MODE | float64 | 53.3% | 26 | 0 | 电梯数量（众数） |  |
| ENTRANCES_MODE | float64 | 50.3% | 30 | 0.069 | 入口数量（众数） |  |
| FLOORSMAX_MODE | float64 | 49.8% | 25 | 0.0833 | 最高楼层（众数） |  |
| FLOORSMIN_MODE | float64 | 67.8% | 25 | 0.125 | 最低楼层（众数） |  |
| LANDAREA_MODE | float64 | 59.4% | 3563 | 0.0377 | 土地面积（众数） |  |
| LIVINGAPARTMENTS_MODE | float64 | 68.4% | 736 | 0.022 | 居住公寓数（众数） |  |
| LIVINGAREA_MODE | float64 | 50.2% | 5301 | 0.0198 | 居住面积（众数） |  |
| NONLIVINGAPARTMENTS_MODE | float64 | 69.4% | 167 | 0 | 非居住公寓数（众数） |  |
| NONLIVINGAREA_MODE | float64 | 55.2% | 3327 | 0 | 非居住面积（众数） |  |
| APARTMENTS_MEDI | float64 | 50.7% | 1148 | 0.025 | 公寓面积（中位数） |  |
| BASEMENTAREA_MEDI | float64 | 58.5% | 3772 | 0.0369 | 地下室面积（中位数） |  |
| YEARS_BEGINEXPLUATATION_MEDI | float64 | 48.8% | 245 | 0.9722 | 建筑启用年份（中位数） |  |
| YEARS_BUILD_MEDI | float64 | 66.5% | 151 | 0.6243 | 建成年份（中位数） |  |
| COMMONAREA_MEDI | float64 | 69.9% | 3202 | 0.0144 | 公共区域面积（中位数） |  |
| ELEVATORS_MEDI | float64 | 53.3% | 46 | 0 | 电梯数量（中位数） |  |
| ENTRANCES_MEDI | float64 | 50.3% | 46 | 0.069 | 入口数量（中位数） |  |
| FLOORSMAX_MEDI | float64 | 49.8% | 49 | 0.0833 | 最高楼层（中位数） |  |
| FLOORSMIN_MEDI | float64 | 67.8% | 47 | 0.125 | 最低楼层（中位数） |  |
| LANDAREA_MEDI | float64 | 59.4% | 3560 | 0.0375 | 土地面积（中位数） |  |
| LIVINGAPARTMENTS_MEDI | float64 | 68.4% | 1097 | 0.0205 | 居住公寓数（中位数） |  |
| LIVINGAREA_MEDI | float64 | 50.2% | 5281 | 0.0193 | 居住面积（中位数） |  |
| NONLIVINGAPARTMENTS_MEDI | float64 | 69.4% | 214 | 0 | 非居住公寓数（中位数） |  |
| NONLIVINGAREA_MEDI | float64 | 55.2% | 3323 | 0 | 非居住面积（中位数） |  |
| FONDKAPREMONT_MODE | object | 68.4% | 4 | reg oper account | 维修基金账户类型 |  |
| HOUSETYPE_MODE | object | 50.2% | 3 | block of flats | 房屋类型 |  |
| TOTALAREA_MODE | float64 | 48.3% | 5116 | 0.0149 | 建筑总面积 |  |
| WALLSMATERIAL_MODE | object | 50.8% | 7 | Stone, brick | 墙体材料 |  |
| EMERGENCYSTATE_MODE | object | 47.4% | 2 | No | 是否危房状态 |  |

## 10. 社交圈

| 字段 | 类型 | 缺失率 | 唯一值 | 示例 | 含义 | 官方描述 |
|---|---|---|---|---|---|---|
| OBS_30_CNT_SOCIAL_CIRCLE | float64 | 0.3% | 33 | 2 | 社交圈可观察 30 DPD 违约数 | How many observation of client's social surroundings with observable 30 DPD (days past due) default |
| DEF_30_CNT_SOCIAL_CIRCLE | float64 | 0.3% | 10 | 2 | 社交圈实际 30 DPD 违约数 | How many observation of client's social surroundings defaulted on 30 DPD (days past due)  |
| OBS_60_CNT_SOCIAL_CIRCLE | float64 | 0.3% | 33 | 2 | 社交圈可观察 60 DPD 违约数 | How many observation of client's social surroundings with observable 60 DPD (days past due) default |
| DEF_60_CNT_SOCIAL_CIRCLE | float64 | 0.3% | 9 | 2 | 社交圈实际 60 DPD 违约数 | How many observation of client's social surroundings defaulted on 60 (days past due) DPD |

## 11. 提供文件标志

| 字段 | 类型 | 缺失率 | 唯一值 | 示例 | 含义 | 官方描述 |
|---|---|---|---|---|---|---|
| FLAG_DOCUMENT_2 | int64 | 0.0% | 2 | 0 | 是否提供文件 2 | Did client provide document 2 |
| FLAG_DOCUMENT_3 | int64 | 0.0% | 2 | 1 | 是否提供文件 3 | Did client provide document 3 |
| FLAG_DOCUMENT_4 | int64 | 0.0% | 2 | 0 | 是否提供文件 4 | Did client provide document 4 |
| FLAG_DOCUMENT_5 | int64 | 0.0% | 2 | 0 | 是否提供文件 5 | Did client provide document 5 |
| FLAG_DOCUMENT_6 | int64 | 0.0% | 2 | 0 | 是否提供文件 6 | Did client provide document 6 |
| FLAG_DOCUMENT_7 | int64 | 0.0% | 2 | 0 | 是否提供文件 7 | Did client provide document 7 |
| FLAG_DOCUMENT_8 | int64 | 0.0% | 2 | 0 | 是否提供文件 8 | Did client provide document 8 |
| FLAG_DOCUMENT_9 | int64 | 0.0% | 2 | 0 | 是否提供文件 9 | Did client provide document 9 |
| FLAG_DOCUMENT_10 | int64 | 0.0% | 2 | 0 | 是否提供文件 10 | Did client provide document 10 |
| FLAG_DOCUMENT_11 | int64 | 0.0% | 2 | 0 | 是否提供文件 11 | Did client provide document 11 |
| FLAG_DOCUMENT_12 | int64 | 0.0% | 2 | 0 | 是否提供文件 12 | Did client provide document 12 |
| FLAG_DOCUMENT_13 | int64 | 0.0% | 2 | 0 | 是否提供文件 13 | Did client provide document 13 |
| FLAG_DOCUMENT_14 | int64 | 0.0% | 2 | 0 | 是否提供文件 14 | Did client provide document 14 |
| FLAG_DOCUMENT_15 | int64 | 0.0% | 2 | 0 | 是否提供文件 15 | Did client provide document 15 |
| FLAG_DOCUMENT_16 | int64 | 0.0% | 2 | 0 | 是否提供文件 16 | Did client provide document 16 |
| FLAG_DOCUMENT_17 | int64 | 0.0% | 2 | 0 | 是否提供文件 17 | Did client provide document 17 |
| FLAG_DOCUMENT_18 | int64 | 0.0% | 2 | 0 | 是否提供文件 18 | Did client provide document 18 |
| FLAG_DOCUMENT_19 | int64 | 0.0% | 2 | 0 | 是否提供文件 19 | Did client provide document 19 |
| FLAG_DOCUMENT_20 | int64 | 0.0% | 2 | 0 | 是否提供文件 20 | Did client provide document 20 |
| FLAG_DOCUMENT_21 | int64 | 0.0% | 2 | 0 | 是否提供文件 21 | Did client provide document 21 |

## 12. 征信局查询次数

| 字段 | 类型 | 缺失率 | 唯一值 | 示例 | 含义 | 官方描述 |
|---|---|---|---|---|---|---|
| AMT_REQ_CREDIT_BUREAU_HOUR | float64 | 13.5% | 5 | 0 | 征信局查询次数（申请前 1 小时） | Number of enquiries to Credit Bureau about the client one hour before application |
| AMT_REQ_CREDIT_BUREAU_DAY | float64 | 13.5% | 9 | 0 | 征信局查询次数（前 1 天） | Number of enquiries to Credit Bureau about the client one day before application (excluding one hour before application) |
| AMT_REQ_CREDIT_BUREAU_WEEK | float64 | 13.5% | 9 | 0 | 征信局查询次数（前 1 周） | Number of enquiries to Credit Bureau about the client one week before application (excluding one day before application) |
| AMT_REQ_CREDIT_BUREAU_MON | float64 | 13.5% | 24 | 0 | 征信局查询次数（前 1 月） | Number of enquiries to Credit Bureau about the client one month before application (excluding one week before application) |
| AMT_REQ_CREDIT_BUREAU_QRT | float64 | 13.5% | 11 | 0 | 征信局查询次数（前 3 月） | Number of enquiries to Credit Bureau about the client 3 month before application (excluding one month before application) |
| AMT_REQ_CREDIT_BUREAU_YEAR | float64 | 13.5% | 25 | 1 | 征信局查询次数（前 1 年） | Number of enquiries to Credit Bureau about the client one day year (excluding last 3 months before application) |
