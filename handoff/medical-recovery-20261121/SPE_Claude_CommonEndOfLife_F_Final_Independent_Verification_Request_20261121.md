# SPE｜終末期医療共通化・F再計算 Claude独立検算依頼書

**Status:** OWNER-DIRECTED / INDEPENDENT VERIFICATION AUTHORIZED / READ-ONLY SOURCE / DRAFT / NON-CANONICAL  
**対象AI:** Claude  
**Repository:** `spe-flatvat/SPE`  
**対象期間:** 2026〜2055年  
**目的:** 修正済み共通終末期医療モジュールとF統合計算の独立検算を完了し、N3実装への移行可否・留意点を事実に基づき判定する。

## 1. Owner依頼と境界

ChatGPT Workが供給上限の二重利用修正、表示・会計検証修正、終末期医療政策の施策セット間共通化、Fの年次再計算、GitHub引渡しを行った。Claudeには**この新固定版の独立検算**を依頼する。

既存の旧版検算PASSを再利用し、今回変更された部分を優先して独立に検証する。追加の規範レビュー、承認ゲート、全政策の再較正、新しい政策実装、Ownerへの原本再提出依頼は不要。結果は算術・会計・制度ロジック・比較可能性を区別して記す。政策原文や正式承認状態を変更しない。

**検算のための原本取得はREAD-ONLY。検算成果物の新規ファイルに限り `work/claude-handoff` への書込みをOwnerが承認する。** `work/chatgpt-handoff`、`main`、`policies/`、`Inbox/`、既存成果の上書きは禁止。正式Acceptance/Canonical/Freeze、RP-023／M19–25 HOLD解除、RP-024 PENDING変更は禁止。

## 2. 固定対象と比較原本

### 主対象：ChatGPT Work修正版
- Repository：`spe-flatvat/SPE`
- Branch：`work/chatgpt-handoff`
- **固定Commit：`ff6210061615105de9a0d64767c256796be80ed2`**
- Directory：`handoff/f-common-endoflife-finalization-20261121/`
- 主要原本：`Report.md`、`Reproduction.md`、`Manifest.json`、`Inputs.json`、`Model.py`、`CommonEndOfLife.py`、`CommonInterface.py`、`FMedical.py`、`CommonBaseline.py`、`Finalize.py`、`Verify.py`、`ExtendedVerify.py`、`Annual.csv`、`Common_EndOfLife.csv`、`Supply_Before_After.csv`、`Before_After.csv`、`SQ_Common_Annual.csv`、`Common_ON_F_SQ_Comparison.csv`、`Independent_Callers.csv`、`Set_Interface_Tests.csv`、`Fiscal.csv`、`Medical_Accounts.csv`、`Household_Sensitivity.csv`、`Nonadditivity.csv`、`Patient_Cap_Audit.csv`、`Final_Checks.json`、`Extended_Checks.json`、`Verification.json`、`Validation.json`。

Workは52原本の固定Commit事後取得SHA一致とCUSTODY PASSを報告。**この申告をClaude自身の原本同一性検証PASSとして流用しない。** 固定Commitから実バイトを取得し、Manifest記載のサイズ/SHA-256と照合する。Manifest対象数、成果原本数、別Commitの照合記録の数え方を明確に区別する。照合記録 `Delivery_Verification.json` とその記録CommitはRepositoryから自己回収し、確認できなければその範囲だけ未確認と記す。

### 比較・旧独立検算
- 直前F統合モデル固定Commit：`6986bb7d11dc25a84189192963da878abd6d6572`
- 直前F事後照合記録Commit：`b42c0c5daa2c2cad5875055583c7c3ea2d236f8f`
- Claude旧版独立検算固定Commit：`995cbca98935752234452c6a6760150e639b312d`
- Work実行指示固定Commit：`12f8f43b874940cb695da54168f97ff5beb6a4a8`
- 政策原文：`policies/FreedomPolicies.md`、`policies/FreedomPolicies_Annex.md`、`Inbox/End-of-Life_Stage.md`（原本の参照のみ）。

旧Claude検算のManifest37/37、依存12/12、16出力バイト一致、154,440セル独立再計算一致は**旧固定版へのPASS**。新修正版での変更箇所の独立検算を省略する根拠にはしない。

## 3. 検算A：再現性と依存同一性

1. 主対象固定Commitの原本を取得し、Manifest、実行時依存原本、重要コードと生成結果のサイズ・実バイトSHA-256を検証。取得経路・固定Commit・件数・不一致・未取得を記録。
2. `Reproduction.md` に従い、`Model.py`、`CommonBaseline.py`、`Finalize.py`、`Verify.py --replay`、`ExtendedVerify.py`、`ReportResults.py` を独立環境で実行。出力CSV/JSONの実バイト一致を検証し、再生成対象と固定参照を区別。
3. 実行不能なら具体的なコマンド・エラー・依存・影響範囲を報告し、検証できた項目は維持する。手順書の `-I` 非対応についても必要なら記録。
4. 旧モデルとの比較は固定原本を使用し、結果の単なる一致と新たな独立算術検証を区別。

## 4. 検算B：供給能力と患者集合（最優先）

旧問題：`chosen_transitions` と `universal_palliative_served` が同じ `transition_capacity` を別々に使い、2035年は12,474＋61,696が上限61,696を超過していた。

新モデルの `OVERLAP_EQUAL_ACCESS` は移行対象を緩和ケア対象の部分集合と仮定し、患者和集合を供給使用数とする。`EXTRA_TRANSITION_RESOURCE` は移行に追加資源1単位を仮定。いずれも未較正・Owner未裁定。

**独立に確認すること：**
- 患者集合の包含、同一患者の重複排除、サービス件数と供給資源使用量の区別が数式・実装・CSVで一致するか。
- 両配分条件の2026〜2055年、全実行条件で容量超過がないか。整数丸め、境界値、需要0、容量0、極端な登録率、撤回、意思不明も確認。
- 供給不足時、登録者・未登録者の緩和ケア提供確率に差別がないか。本人の明示意思なしに延命拒否を推定しないか。移行は意思確認・臨床適合条件に従うか。
- 需要、移行、緩和提供、未充足、資源使用、追加資源の恒等関係を**元コードとは別構造の算式または独立スクリプト**で検算。
- 既存報告の2035年（新移行2,391、緩和提供61,696、容量61,696）、2040年（14,479／93,392／93,392）、2055年（13,207／85,186／85,186）を検算し、旧版との差を説明。
- 仮定した「移行は緩和対象の部分集合」「追加資源1単位」の政策・実証上の未裁定性を明記。供給上限を守るために対象人数を不当に削ったり、未充足需要を隠したりしていないか。

## 5. 検算C：共通政策の施策セット非依存性

`FMedical → CommonInterface.run_common → CommonEndOfLife.calculate` の実接続を確認。共通モジュールがF固有モデルをimportせず、施策セット名によって資格・優先度・供給制約・本人意思を変更しないことを検査。

- F/N3/N/F3/R4を想定した5種類・150回の異なる負担/公費配賦の実呼出を再現。
- 同じ需要・共通政策入力なら、セット名・患者負担・財源入力を変えても**共通の適格性、本人意思保護、供給配分、施行時期**は変わらず、請求/財源結果だけが制度条件に応じて変わるか。
- 2030法制化、2032〜2035施行、2035全国運用、2040登録60%候補、登録撤回、意思不明、未登録者緩和ケアを確認。
- 呼出テストを「N3政策モデル実装済み」「N3政策値採用」と解釈しない。N3固有制度接続に残る入力を明示。

## 6. 検算D：F年次再計算、共通ON/OFF SQ、比較可能性

Work報告では修正F **55実行条件×30年＝1,650行**、固定参照3条件を含む **58条件・1,740行**。これらの件数をCSVで区別して検証する。

- F 2026〜2055年の年次連鎖、既存施策の回帰、医療変更に伴うGDP/消費/投資/資本/税/家計/部分財政収支の変化を検算。
- 2055年 `LATEST_F` 実質GDP：旧540.274388667兆円→新540.274554375兆円、差約+0.000166兆円。差が小さい理由と年次経路を点検。
- 共通ON/OFFのSQを同一設定で再実行し、共通OFFが固定SQと一致するか。共通ONの費用・家計現金・税/保険料・投資が年次エンジンへ接続されているか。
- 共通ONのSQとFを比べる際、**SQ側医療VAT数量フックと健康/QOL経路が未接続**という非対称性を明示。厳密なF固有因果効果や全政策の実証較正と呼ばない。
- 新旧の2026〜2055年差を比較し、2035/2040/2055の主要値・符号・単位・年次異常を検査。

## 7. 検算E：会計、患者負担、表示

- `post_financing_transfer_residual` の恒等的相殺をPASS根拠から除外しているか。患者/公費/保険者請求と臨床資源費、税/保険料/他支出/債/償還/資産からの**独立台帳再構成**を検算。未充当・部分閉鎖・全国財政未閉鎖を区別。
- `Finalize.py` の0.01兆円の誤差注入検出が実際に機能するか。独立台帳が同一誤りを共有する限界も評価。
- 緩和ケア患者負担約0.9%は既存月額上限の限界自己負担であり、Fの名目3割と混同していないか。`Patient_Cap_Audit.csv` 144例と期間・所得・年齢・療養先感度を検算。
- `Nonadditivity.csv` でleave-one-out限界差を加法寄与として表示しないこと、2055年非加法差約2.002190兆円の算術を検算。
- `INVESTMENT` は未接続（`investment_flow_share=null`）と表示し、ゼロ効果と混同しないこと。
- 家計直接負担の感度幅がゼロをまたぐことを年次で確認。新報告の2055年−132.021〜+120.000億円/年など、旧版からの変化を検算。財源税・保険料と家計直接負担を混同しない。

## 8. 判定と報告の書き方

判定は少なくとも以下を分ける：
1. **固定原本受領・実バイト同一性**
2. **再実行・出力バイト再現性**
3. **独立算術・供給制約**
4. **会計・請求整合**
5. **本人意思保護・セット間共通化**
6. **FとSQの比較可能性・未接続範囲**
7. **N3固有実装へ進めるか（GO / CONDITIONAL GO / STOP、根拠付き）**

重要指摘は、再現可能なファイル/関数/行または列、条件、期待値と実測値、影響範囲、修正要否を明示。独立再実装していないマクロ部分はその範囲を明記。政策・係数の採用、正式Acceptance、HOLD解除は判定しない。未較正パラメータ、全国財政閉鎖、健康/QOL、N3固有モデルの未実装は既知の限界として扱い、無制限な追加工程を要求しない。

## 9. Claude成果物のGitHub引渡し（Owner承認）

**書込み先Branch：`work/claude-handoff` のみ**  
**新規ディレクトリ：`handoff/claude-common-endoflife-f-final-verification-20261121/`**

最低限、個別原本で格納：
- `SPE_CommonEndOfLife_F_Final_Claude_Independent_Verification_DRAFT_20261121.md`：結論、証拠、問題、N3移行判断
- 独立検算スクリプト（実際に実行したもの、1件以上）
- 検算の実出力・再実行コマンド・対象固定Commitと照合結果（テキストまたはJSON）
- 必要な場合のみ補助資料

ZIP禁止。各原本のサイズ・実バイトSHA-256と格納先を記録。GitHub格納後に**Claude側の成果固定Commitを取得し、固定Commitから事後取得して実バイトSHA-256一致を確認**する。確認できた場合のみCUSTODY PASS。報告書と検算スクリプトの固定URL、成果Commit、検証範囲、STOPがあれば技術的理由をOwnerに返す。

**完了条件：** 原本取得・必要な独立検算・結果報告・Claude側GitHub引渡し・事後照合まで実施。文書作成のみ、試験PASSのみでは完了としない。
