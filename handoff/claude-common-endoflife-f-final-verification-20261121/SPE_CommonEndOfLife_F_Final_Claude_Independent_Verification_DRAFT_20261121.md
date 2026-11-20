# SPE｜終末期医療共通化・F再計算 Claude独立検算報告（DRAFT / NON-CANONICAL）2026-11-21

- Repository: `spe-flatvat/SPE`
- 依頼書固定Commit: `b90554f619c70d41dc5ce4e608f838e834d69d95`
- 検算対象固定Commit: `ff6210061615105de9a0d64767c256796be80ed2`（`handoff/f-common-endoflife-finalization-20261121/`、tree `d82d7d45…`）
- 照合記録（ChatGPT側）: Commit `6a9ccc854f7088339d58c9490174cc1463d2a203` の `Delivery_Verification.json`（リポジトリから自己回収）
- 立場: 読み取り専用の独立検算。Acceptance、政策値の採用、規範レビュー、HOLD/PENDING の変更は行わない。RP-023／M19–25 HOLD、RP-024 PENDING、政策原文、正式承認状態は維持。
- 既存の旧版Claude検算（Commit `995cbca9…`）は旧固定版へのPASSであり、本報告では変更箇所を新たに独立検算した。

## 1. 判定一覧

| # | 観点 | 判定 | 要旨 |
|---|---|---|---|
| 1 | 固定原本受領・実バイト同一性 | PASS | Manifest 51/51、実行時依存 12/12、フォルダ実在52ファイル（＝Manifest51＋Manifest.json）、tree ID一致、記録 Delivery_Verification 52/52 が私の実バイトと一致。 |
| 2 | 再実行・出力バイト再現性 | PASS | 手順書どおりの再実行で、フォルダ内52ファイルすべてバイト一致。 |
| 3 | 独立算術・供給制約 | PASS | 別構造の再実装で55条件×30年、176,550セル一致（最大誤差 2.6e-10）。容量超過なし。報告の2035/2040/2055数値を再確認。 |
| 4 | 会計・請求整合 | PASS（限界あり） | 請求恒等式・財源台帳・債務/資産ストック・上限監査144例が一致。ただしWork側の誤差注入検査は実質無効（§6-4）。 |
| 5 | 本人意思保護・施策セット間共通化 | PASS（試験の弱さを注記） | 保護フラグと供給配分は呼出元の財源・配賦に依存しない。セット名は共通モジュールの引数にそもそも存在しない。 |
| 6 | FとSQの比較可能性・未接続範囲 | PASS（非対称は明示済み） | 共通OFFのSQは固定SQと一致（最大差 4.9e-9）。共通ONのFとSQは医療VAT数量フックと健康/QOLの接続範囲が異なる。 |
| 7 | N3固有実装へ進めるか | **CONDITIONAL GO** | 共通比較基盤としては使える。進める前に、または並行して、§7の条件を扱うこと。 |

## 2. 固定原本と再現性（検算A）
- 取得: GitHub から固定Commitを取得し、`git archive` で展開。原本とは独立の環境で実施。
- Manifest.json は51原本を列挙（Manifest自身とDelivery_Verificationを除く）。フォルダ内の実在ファイルは52（Manifest51＋Manifest.json）。Work報告の「52原本」は後者の数え方で、Delivery_Verification.json は52件（Manifest.json を含む）を記録。数え方は矛盾しない。Delivery_Verification.json 自体は別Commit `6a9ccc85…`（原本Commitの後）に格納されている。
- 実行時依存12原本（Inputs.runtime_dependencies）は固定パスでサイズ・SHA-256とも一致。
- 再実行: `Model.py`、`CommonBaseline.py`、`Finalize.py`、`Verify.py --replay`、`ExtendedVerify.py`、`ReportResults.py` をコピーに対して実行（Finalize は旧Claude検算Commit `995cbca9` のgit objectを必要とするため事前に取得）。再生成された出力は52ファイルすべて原本とバイト一致（固定参照の3条件を含む58条件・1,740行、うち修正F 55条件×30年＝1,650行を確認）。
- 手順書の `-I` 非対応: `ReportResults.py` だけでなく `CommonBaseline.py` も兄弟モジュールを import するため `python3 -I` では動かない（通常起動なら動く）。手順書はこの点を `ReportResults` についてのみ記載しており、`CommonBaseline` も同様と補足するとよい。実害なし。
- 旧版との一致は「結果が同じ」ことの確認にとどまり、独立算術検証ではない。

## 3. 供給能力と患者集合（検算B、最優先）
**数式（新モデル）**: 緩和ケアの対象集団 `target = max(universal_need × 実施率, transition_need)`。移行対象は対象集団の部分集合。全員に共通のアクセス確率 `a = min(1, 容量 ÷ (target + (k−1)×transition_need))`（`OVERLAP_EQUAL_ACCESS` は k=1、`EXTRA_TRANSITION_RESOURCE` は k=2）。提供数＝a×target、移行数＝a×transition_need、資源使用＝a×(target＋(k−1)×transition_need)。

**独立検算**:
- Workのコード（min と除算を使う逐次式）とは別に、上の閉形式で全条件を再計算し、176,550セル（Common_EndOfLife 全列、Medical_Accounts、Demography_Demand）が一致。
- 不変条件（1,650条件年）: 資源使用≦容量（最大比 1.000000）、移行≦重複≦提供、重複排除の恒等式（一意患者＝移行＋提供−重複）、サービス件数＝移行＋提供、移行のアクセス確率＝緩和ケアのアクセス確率、OVERLAP では資源使用＝提供数、EXTRA では資源使用＝提供＋移行。違反0。
- モジュールを直接呼ぶ境界試験（16シナリオ×5年＝80呼出）: 容量0、容量ほぼ0、需要0、登録率0／1、撤回100%、明示意思0、確認0、実質的に全員希望、EXTRA k=2/5、緩和ケア無効、供給不足、制度無効、遅延3年。すべて閉形式と一致し、`unknown_wish_assumed_refusal=0`、`treatment_automatically_stopped=0`、`active_life_termination=0`、`registration_changes_palliative_priority=0` を維持。登録率0・撤回・明示意思0・確認0では移行が0。
- 登録者と未登録者の差別: 登録率0.1と0.9でアクセス確率は同じ（0.3175）。供給不足時は対象集団の全員が同じ確率で配分される。登録の有無で優先順位は付かない。
- 主要数値（LATEST_F）の再確認:

| 年 | 新・移行 | 新・緩和提供 | 容量 | 旧・移行 | 旧・移行＋提供 |
|---|---|---|---|---|---|
| 2035 | 2,391 | 61,696 | 61,696 | 12,474 | 74,171（容量超過） |
| 2040 | 14,479 | 93,392 | 93,392 | 50,257 | 143,649 |
| 2055 | 13,207 | 85,186 | 85,186 | 52,929 | 138,115 |

- 旧版との差の説明: 旧版は移行と緩和提供が同じ容量を別々に使っていた。新版は移行を緩和対象の部分集合として扱い、容量を共有する。そのため提供数（容量で決まる）は旧版と同じで、移行だけが減る（2035年 12,474→2,391、アクセス確率19.2%）。
- 未充足需要は隠されていない: `transition_unmet`（2035年10,083）と `universal_palliative_unmet` が出力されている。「未充足を隠して人数を削った」兆候はない。
- 前提の未裁定性: 「移行は緩和対象の部分集合」「追加資源1単位」「緩和ケア対象は全episodeの70%」「容量10万/年」はいずれも未較正・Owner未裁定の候補。コード上も `allocation_status='UNCALIBRATED_OWNER_UNDECIDED'`。

## 4. 共通政策の施策セット非依存性（検算C）
- `CommonEndOfLife.py` と `CommonInterface.py` の import は `math` と自己のみ。FMedical・N3・セット名への参照なし。`run_common` は施策セット名を引数に取らない。
- 財源配分の家計比率を0／0.3／1に変えても、移行数・提供数・重複・資源使用・法制化・実施率・適格要求数は不変、患者負担だけが変わる（0.0、0.00086、0.00287兆円）。
- `Set_Interface_Tests.csv`（5セット×30年＝150行）: セット間で変わる列は患者負担・公費・保険者・家計現金・借入・取り崩しだけ。非支払者列の差はなし。
- 注意: この150回の試験は呼出名を引数に渡していないため、「セット名が結果を変えない」ことの証拠としては弱い（名前が入る経路がそもそもない）。意味のある証拠は上の静的確認と私の財源比率試験。これを「N3政策モデル実装済み／N3政策値採用」と読んではならない。N3固有の患者負担ルール・財源・税制・マクロ接続は呼出元から注入する必要があり、現状残っているのはF用の請求計算クロージャ（FMedical内）のみ。

## 5. F年次再計算と共通ON/OFF SQ（検算D）
- 件数: Annual.csv 1,740行＝58条件×30年。うち修正F 55条件（1,650行）、固定参照3条件（SQ_FIXED、OLD_EDUCATION_F、OLD_MEDICAL_F）。Common_EndOfLife は55条件1,650行。
- 旧版との比較: LATEST_F 2055年実質GDP 540.274554375（新）対 540.274388667（旧）、差＋0.000166兆円。年次の最大差は2040年の0.000352兆円で、符号は30年間に2回反転。差が小さい理由（私の推定。経路ごとの分解までは未実施）: 変わったのは移行数（旧52,929→新13,207）とそれに連動するケア費用・家計の追加費用で、緩和提供数と容量は旧版と同じ。共通政策の費用規模はもともと対GDPで小さい（旧版でも共通のGDP限界効果は最大0.0003兆円）。`MEDICAL_OFF` は新旧で完全一致（差 0）、他条件（NO_VAT、NO_EDUCATION、F_ONLY_NO_COPAY）の変化も最大0.00037兆円で、既存施策の意図しない回帰なし。
- Before_After.csv（19,530行）、Supply_Before_After.csv（6,240行）は、両固定フォルダのAnnual／Common_EndOfLifeから再構成して全行一致。
- 共通OFFのSQ再実行は固定SQと一致（180セルで最大差 4.9e-9）。共通ONのSQとの差は実質GDPが2035年＋0.00005、2040年＋0.00003、2055年−0.00012兆円。税（診断値）は＋0.003〜＋0.007兆円、家計消費は−0.004〜−0.008兆円で、費用・家計現金・税/保険料は年次エンジンに接続されている。投資は変化なし（I_policy_real・資本とも差0）。
- FとSQ（共通ON）の比較: 2055年 実質GDP差＋11.31兆円。F側は医療VAT数量フックが接続、SQ側は未接続（Common_ON_F_SQ_Comparison.csv の `scope_difference` に明記）。SQ側は健康/QOL経路も未接続。**この差をF固有施策の厳密な因果効果とは呼べない。**
- 非加法性: Nonadditivity.csv を Policy_Effects／Annual から再計算して一致（最大差 4.4e-12）。2055年 leave-one-out 合計 13.314 − 全体差 11.312 ＝ **2.002190兆円**。`additive_attribution=False`。限界効果を寄与分解として使わないこと。
- INVESTMENT: Policy_Effects の300行すべてに `connection_status=UNCONNECTED`。`NO_INVESTMENT` は LATEST_F と同一。ゼロ効果ではなく未接続の扱い。
- 独立再実装していない範囲: 動学マクロ本体（`Model.run` の中のGDP・消費・資本の連鎖）。GDPの水準そのものはエンジン出力を信頼している。独立に確認したのは医療・共通・需要ブロック、会計恒等式、比較表の再構成、ON/OFFの整合。

## 6. 会計・患者負担・表示（検算E）と指摘事項
**確認済み**:
- 請求恒等式（患者＋公費＋保険者＝臨床費）最大差 1e-11。財源台帳（利用＝税＋保険料＋他支出＋債発行−償還−資産＋未充当）最大差 1e-12。債務・資産ストックのフロー整合 6e-12。`financing_account_status`: OPEN_UNASSIGNED 1,300行、CLOSED_PARTIAL_ONLY 350行。`post_financing_transfer_residual` は空欄で、PASS根拠から外されている。
- Patient_Cap_Audit 144例を別実装の請求計算で再計算し、全例一致（差0円）。限界自己負担率は0〜0.30の範囲内。普遍的緩和ケアの患者負担は費用の0.7〜0.8%（2035年0.70%、2040年0.82%、2055年0.69%）で、既存の月額上限に達した後の限界自己負担であり、Fの名目3割とは別物。
- Household_Sensitivity.csv の最小・最大を再計算して90行すべて一致。家計直接現金負担（共通モジュール分）の感度幅は2035年−46〜＋16億円、2040年−91〜＋97億円、2055年**−132〜＋120億円/年**で、**25年（2031年以降）で符号反転**。旧版（2055年−73〜＋461億円）より幅が縮んだのは、移行数が約4分の1になり、在宅ケア等の追加費用が減ったため。
- 財源の税・保険料（2035年で各約0.009兆円）と家計直接負担は別列で分離されている。

**指摘事項**（番号は影響の大きい順。修正要否を付記）:
1. **【Owner判断事項・設計】容量が常に拘束的で、移行のアクセス確率が低い。** 実施率1の1,003条件年のうち982で容量が拘束。LATEST_Fでは、支援を受けた意思表示者の移行が満たされるのは19.2%（2035）、28.8%（2040）、25.0%（2055）。登録者への優先を付けない設計の帰結で実装誤りではないが、移行数は「意思」ではなく容量パラメータ（候補10万/年）でほぼ決まる。N3移行時は `transition_unmet` を必ず併記すること。修正は不要、判断はOwner。
2. **【表示・軽微】未充足列が実施前も計上される。** `universal_palliative_unmet` は実施率0の2026年にも315,000、2031年に319,903。`capacity_unmet` は実施率で割り引いていない `willing` を使うため、2031〜2034年は `transition_unmet` より大きい。N3以降で集計する場合は `implementation_phase≥1` で絞るか `transition_unmet` を使う。修正推奨（軽微）。
3. **【表示・符号】Household.csv の `positive_sign=burden_increase` が全列に付いているが、`total_medical_household_cash_delta_trn` だけは現金増減（負＝家計の負担増）。** 2035年は−0.494兆円で、通常医療の患者負担増（＋0.627兆円）などの合計に負号を付けたもの。直接負担列（正＝負担増）と並べると符号を取り違えやすい。列ごとの符号規約の注記を推奨。
4. **【検査の限界】Final_Checks の `source_error_injection_detected` は固定値True（Finalize.py 82行目）。** 検査本体は `near(uses, sources)` を通した直後に `assert not isclose(uses, sources+.01)` を置くだけで、これは前者が通れば常に成り立ち、誤差を実際には注入していない。私の注入試験（財源3列×1,650行に0.01兆円を加算）では、税と債発行の誤りは全件検出、**他支出（crowd）の誤りは利用側にも財源側にも入るため検出不能**（4,950試行中3,300検出）。台帳は同じ列から作られるため、同一の誤りを共有する限界もある。実害は未確認、検査の説明を修正するのが望ましい。
5. **【堅牢性・軽微】`CommonEndOfLife.calculate` は `age_demand_episodes` を渡しても `clinical_strata` の欠落で KeyError になる**（`dict.get` の既定値が先に評価されるため）。N3から呼ぶときは `clinical_strata` を含めること。修正推奨（軽微）。
6. **【再現手順】`-I` 非対応の範囲を `CommonBaseline.py` にも明記。**

## 7. N3実装への移行判断: CONDITIONAL GO
**進めてよい根拠**: 同一性・再現性・独立算術・会計恒等式がPASS。供給上限の二重利用は解消され、患者集合と資源使用量の関係が検算可能な式で示されている。共通呼出はセット名に依存しない。GDPの変化は新旧で最大0.0004兆円と小さく、既存Fの比較基準を揺らさない。

**条件（N3側で守ること）**:
1. 共通政策の数値（容量、緩和ケア対象70%、アクセス配分方式、登録率、効果）を採用政策値として扱わない。移行数は容量依存であることを前提に、`transition_unmet` と `universal_palliative_unmet` を併記する（指摘1・2）。
2. N3固有の患者負担ルール・財源・税制・マクロ接続は呼出元に必要。現在あるのはF用の請求クロージャのみで、N3では別途実装・検算が必要。
3. FとSQの差を「F固有施策の効果」と呼ばない（SQ側の医療VAT数量・健康/QOL未接続）。leave-one-out の合計を寄与分解として使わない（非加法差2.00兆円）。INVESTMENTは「未接続」と表示する。
4. 家計負担は幅（2055年−132〜＋120億円/年）で示し、符号を断定しない。通常医療の患者負担・保険料・財源税は別列で扱い、列ごとの符号規約を確認する（指摘3）。
5. 会計の独立検査は台帳の再構成のみで、他支出の誤りは検出できない（指摘4）。全国財政の閉鎖は未実施で、`OPEN_UNASSIGNED` が1,300行残る。

## 8. 限界
- 動学マクロ本体の独立再実装は未実施（§5）。政策値・係数・臨床効果の妥当性、実証的較正は判定していない。
- 独立再計算は Inputs.json、Labor.csv、Demography_Demand.csv（人口の閉合確認後データとして使用）、価格指数を共有。
- 私の旧検算成果（Evidence_*）がWork側フォルダに再利用されている件は、4ファイルが私のCommit `995cbca9` の実バイトと一致することを確認したのみで、本検算の根拠には使っていない。

## 9. 格納ファイルと実行方法
格納先: `handoff/claude-common-endoflife-f-final-verification-20261121/`
- `SPE_CommonEndOfLife_F_Final_Claude_Independent_Verification_DRAFT_20261121.md`（本報告）
- `SPE_CommonEndOfLife_F_Final_Integrity_Check_DRAFT_20261121.py`
- `SPE_CommonEndOfLife_F_Final_Independent_Recalc_DRAFT_20261121.py`
- `SPE_CommonEndOfLife_F_Final_Supplementary_Checks_DRAFT_20261121.py`
- `SPE_CommonEndOfLife_F_Final_Verification_Output_DRAFT_20261121.txt`（実出力、実行コマンド付き）

実行は出力ファイル先頭の `# commands` 行を参照（固定Commit `ff621006…` と `6986bb7d…` のtreeを展開して引数に渡す）。個別原本のサイズ・SHA-256と事後照合結果は、格納後にOwnerへの完了報告で別途示す。
