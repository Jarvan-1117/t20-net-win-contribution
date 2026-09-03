# T20 Net Win Contribution 项目阶段报告

## 项目目标

以国际 T20 球赛的 ball-by-ball 数据建立击球队获胜概率模型，并将每个
recorded event 造成的概率变化汇总为球员的 Net Win Contribution（NWC）。
模型按性别及局数分别训练：女子第一局、女子第二局、男子第一局、男子第二局。

## Phase 01：数据审计与清洗

**目标：** 建立可复现、无明显结果泄漏、顺序正确的基础事件流。

**方法：** 将 match 与 delivery 数据按 `match_id` 连接；保留原始
`source_row` 作为事件顺序，而不是按显示的 over/ball 排序；从事件流推断
innings，并排除 D/L、tie、no result、awarded、super over、无有效胜者、超过
120 legal balls 和终局不一致的比赛。

**结果：** 原始 5,602 场比赛中，4,975 场符合二元结果的标准 T20I 基线；保留
1,156,215 个 recorded deliveries。124,994 个事件参与了重复的显示
over/ball 坐标，验证了必须使用原始顺序。

**产出：** `phase_01_cleaned_deliveries.csv.gz`、数据审计指标和
`01_data_audit_and_cleaning.ipynb`。

## Phase 02：比赛状态特征

**目标：** 为每个 delivery 构造 post-delivery 的比赛状态特征，并防止
second-innings 信息泄漏到 first-innings 模型。

**方法：** 构造累计得分、wickets、legal-ball clock、剩余资源、比赛阶段和最近
10 个事件的先前 runs/wickets。将数据物理拆分为四个 gender–innings 表；
target、runs to win、required run rate、run-rate differential 和 target progress
只存在于第二局表。

**结果：** 女子第一/第二局分别为 235,716 / 200,554 行；男子第一/第二局分别为
382,777 / 337,168 行。第一局表中没有任何 chase-only feature。

**产出：** 四个 `phase_02_<track>.csv.gz` 文件与
`02_game_state_features.ipynb`。

## Phase 03：历史表现特征

**目标：** 加入球员、球队与场地的历史强度，同时保持严格的时间有效性。

**方法：** 每项历史只使用严格早于当前 match date 的比赛；同一天的比赛被视为
simultaneous，不能互相更新。加入 25 项历史 predictor，包括 striker/non-striker
的 batting exposure 与 rates、bowler 的 economy/strike/dot-ball rates、两队的长期
胜率与 10 场半衰期的指数加权近期胜率，以及 venue 的历史胜率。

**结果：** 四个表的行数完全保留；每个第一局表为 65 列、第二局表为 70 列。
新球员或无历史分母时保留 null，留待训练阶段作训练集内处理。

**产出：** 四个 `phase_03_<track>.csv.gz` 文件与
`03_historical_features.ipynb`。

## Phase 04：获胜概率模型

**目标：** 比较模型并以 log loss 选择每个 track 的最终模型。

**方法：** 每局新增一个 synthetic pre-innings state，使第一球拥有明确的先验
概率。按完整 match 与完整日期组进行 chronological 70%/15%/15%
train/validation/test split。依次比较 naïve training-prevalence baseline、L2
Logistic Regression 和 Random Forest；median imputation、missing indicators 和
standardisation 均只在训练集拟合。`batting_team` 和 `bowling_team` 作为类别
predictor，只在训练数据上拟合 one-hot encoding，并允许测试时出现未知队伍。
唯一模型指标为 log loss。

**结果：** 加入队伍身份、长期胜率与近期状态后，Random Forest 在四个 track 的
validation log loss 均最低。每个 track 分别通过三个 expanding temporal validation
windows 比较同一组 8 个 RF 参数；四组均选择 `max_features=0.25` 和 500 棵树，
同时保持 `max_depth=14` 与 `min_samples_leaf=50`。整个调参过程不使用 test period。

| Track | Test naïve | Test Logistic Regression | Test Random Forest |
|---|---:|---:|---:|
| Female innings 1 | 0.691459 | 0.691732 | **0.510914** |
| Female innings 2 | 0.675578 | 0.344246 | **0.273831** |
| Male innings 1 | 0.693698 | 0.754022 | **0.495486** |
| Male innings 2 | 0.688326 | 0.425597 | **0.292898** |

**产出：** 模型 artifacts、四个带预测概率的 state 文件、feature data dictionary
workbook 和 `04_model_training.ipynb`。

## Phase 05：Net Win Contribution

**目标：** 将选中模型的逐球概率变化转换为球员贡献。

**方法：** 在每个 innings 内计算：

\[
\Delta W_d=W_d-W_{d-1}
\]

striker 获得 `+ΔW` 的 batting NWC；bowler 获得 `-ΔW` 的 bowling NWC。第一球
使用 pre-innings state；两局交界不归因；第一局终点保留模型概率，第二局最后
一个 state 则锚定到已知比赛结果。
所有 recorded events（含 wides、no-balls、byes、leg-byes、penalties 和
dismissals）采用同一 baseline striker–bowler interaction rule。主要球员排名只
使用 untouched test split：女子 281 场、男子 466 场。

**结果：** 生成 1,156,215 个逐球 NWC 记录、102,924 个 player-match 记录和
2,651 个 test-split 球员汇总。逐球配对和为 0；单场球员总和最大误差为
`3.33e-16`；逐局概率变化核对最大误差为 `2.22e-16`，均为浮点精度残差。

**限制：** 原始数据没有接球者或制造 run-out 的守场员身份，因此此版本是零和的
striker–bowler interaction metric，不是完整的 fielding 或因果归因模型。

**产出：** delivery、player-match 与 test-player NWC 文件、核对指标，以及
`05_nwc_attribution.ipynb`。完整归因规则统一记录在 `docs/methodology.md`。

## 总结

项目已形成一条完整、可运行的 Phase 01–05 流程：先审计和清洗事件流，再构建
局数安全与时间安全的特征，选择概率模型，最后把概率变化转换为可核对的 NWC。
当前最适合报告的模型结论是：Random Forest 在四个独立模型 track 中均取得最低
validation log loss；四组 RF 参数均通过预先进行的滚动时间验证选择，而不是依据
test set 改选。当前最适合报告的球员结果是来自 untouched test split 的 NWC 汇总，
而不是训练集内排名。
