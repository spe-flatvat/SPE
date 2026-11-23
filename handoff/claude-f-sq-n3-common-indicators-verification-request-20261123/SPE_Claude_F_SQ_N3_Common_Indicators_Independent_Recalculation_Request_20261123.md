# SPE｜Claude限定独立検算依頼：F・SQ・N3共通指標 2026〜2055

**Status:** OWNER-REQUESTED / LIMITED INDEPENDENT RECALCULATION / NON-CANONICAL
**Repository:** `spe-flatvat/SPE`
**Work成果固定Commit（payload）:** `7c9d33205297365e5c6536a84e302eff1d26a3fc`
**Work保全込み最終固定Commit:** `8a8edb403b960cceb535f9b70461646e9374c229`
**Work対象:** `handoff/chatgpt-f-sq-n3-common-indicators-20261123/`
**Claude書込み先branch:** `work/claude-handoff`
**Claude新規成果先:** `handoff/claude-f-sq-n3-common-indicators-verification-20261123/`

## 目的と範囲
Workの2026〜2055年F・SQ・N3比較の**固定原本同一性、数値再計算、比較契約の条件整合、N/A境界**をClaudeが独立検算する。Workの3,142新規PASS、上流9経路270年次、49原票/7生成ファイルのバイト一致、13原本CUSTODY PASSは**先行者の報告**として扱い、Claude自身の検証結果と混同しない。既存実装の再設計、政策本文改訂、F/SQ/N3の施策追加、4AIレビュー、正式Acceptanceは対象外。

## 固定取得リンク
- **Work成果本文（Report.md）:** https://github.com/spe-flatvat/SPE/blob/8a8edb403b960cceb535f9b70461646e9374c229/handoff/chatgpt-f-sq-n3-common-indicators-20261123/Report.md
- **Work同梱のClaude依頼（先行案）:** https://github.com/spe-flatvat/SPE/blob/8a8edb403b960cceb535f9b70461646e9374c229/handoff/chatgpt-f-sq-n3-common-indicators-20261123/Claude_Verification_Request.md
- **比較契約:** https://github.com/spe-flatvat/SPE/blob/8a8edb403b960cceb535f9b70461646e9374c229/handoff/chatgpt-f-sq-n3-common-indicators-20261123/Comparison_Contract.csv
- **30年次比較:** https://github.com/spe-flatvat/SPE/blob/8a8edb403b960cceb535f9b70461646e9374c229/handoff/chatgpt-f-sq-n3-common-indicators-20261123/Annual_Comparison.csv
- **依存固定原本:** https://github.com/spe-flatvat/SPE/blob/8a8edb403b960cceb535f9b70461646e9374c229/handoff/chatgpt-f-sq-n3-common-indicators-20261123/Dependencies.json
- **Manifest:** https://github.com/spe-flatvat/SPE/blob/8a8edb403b960cceb535f9b70461646e9374c229/handoff/chatgpt-f-sq-n3-common-indicators-20261123/Manifest.json
- **保全記録:** https://github.com/spe-flatvat/SPE/blob/8a8edb403b960cceb535f9b70461646e9374c229/handoff/chatgpt-f-sq-n3-common-indicators-20261123/Custody.json
- **再計算コード:** https://github.com/spe-flatvat/SPE/blob/8a8edb403b960cceb535f9b70461646e9374c229/handoff/chatgpt-f-sq-n3-common-indicators-20261123/Run.py

実際の対象13原本の一覧は固定Commitのディレクトリ一覧とManifestを正とする。URL例示にないファイルも必要なら自力回収する。依存原票はDependencies.jsonに指定された**各固定Commit・path**から独立取得する。単一URL取得失敗を全件STOPとせず、Git object/API等の代替取得経路を試す。

## 独立検算項目
1. **原本同一性:** payload commitと最終commitの役割を区別。Manifest・Custodyと原本の実バイトSHA-256/サイズをClaude自身で照合。取得できた件数、未取得件数、各原本の状態を報告。先行WorkのCUSTODY PASSをClaudeの自己検証PASSに置換しない。
2. **比較契約:** SQは `CURRENT_REFERENCE_UNCHANGED_COMMON_ON`（SQ_COMMON_ON）、Fは共通医療参照接続後、N3は `BASE_REPLAY`・追加G/I OFF。2026初期値は実質GDP580兆円、名目600兆円、人口122,618,024人。各枝の人口、実効労働、価格・リスク入力、施策範囲、年次・単位を独立照合。SQの旧variant、固定F native、N3の別候補を混入させない。
3. **独立数値再計算:** 依存原票からWorkのRun.pyとは**別の計算式/短い独立コード**で、2026〜2055年の実質/名目GDP、暗黙GDPデフレーター、人口、実効労働、実質GDP成長率、一人当たり実質/名目GDP、入力インフレ、適用実質リスク、およびF−SQ/F−N3/N3−SQの差を照合。全30年、2026成長率N/A、人口単位、価格年、名目/実質整合、GDP÷人口の復元、丸め誤差を確認。Run.py再実行は補助的再現性検証として可。
4. **主要値:** 2055実質GDP F540.275/SQ528.962/N3 483.991兆円、差F−SQ+11.312、F−N3+56.283、N3−SQ−44.971兆円を原票から再導出。2026/2035/2045/2055の主要値も照合。F共通医療参照の接続前後差、N3/SQ実効労働差ゼロの意味、デフレーターが入力インフレと異なることを検証。
5. **比較可能性/N/A:** 8指標はCONDITIONAL、共通入力2項目はCOMPARABLE。全国の就業者数、税収、賃金/所得、家計手取り/購買力、ジニ、政府PB/国債/債務、施策別財政、投資・消費・基金は条件不一致ならN/A維持。F合成世帯の非採用感度を全国値やSQ/N3共通値に格上げしない。**数値が一致しても政策効果の因果比較や同等実装の証明とはしない**。
6. **差異報告:** 不一致は指標・年・ケース・固定原本path・期待値/独立再計算値・単位/原因・再現方法を記録。丸め誤差、実装条件差、真の算術不整合、未検証を区別。既存上流のPASSを重複監査しない。重大差異を発見しても主対象を無断修正しない。

## 判定・成果物
項目別および総合を **PASS / PASS_WITH_LIMITATIONS / FAIL / NOT_VERIFIED** で評価。検算件数と対象範囲、実際に再実行できた範囲、未検証と限界を明示。成果は日本語 `Report.md`、独立再計算コード、必要な差異/照合CSV、`Source_Identity.json` またはManifest、`Validation.json`、保全記録を**個別原本**として `work/claude-handoff` の指定新規ディレクトリへcommit/push（ZIP禁止）。固定Commitからの事後取得、実バイトSHA-256・サイズの一致が確認できた場合のみCUSTODY PASS。完了時はClaude側最終固定Commit、原本リンク、検算判定、差異、保全状態を報告。

## 権限境界
ClaudeのGitHub書込みは**自身の `work/claude-handoff` 新規成果ディレクトリのみ**。Work原本、main、政策本文/Annex、固定F/SQ/N3、DecisionLog、正式Acceptance/Freeze/Canonicalは変更しない。RP-023/M19–25 HOLD、RP-024 PENDINGを維持。検算だけで正式政策採用・レビューClose・HOLD解除を行わない。追加のOwner承認や4AI工程を新設しない。技術的STOPは対象を限定し、進められる検算と成果引渡しを継続。

**完了条件:** Claude独立の原本取得・数値検算・比較条件判定・個別原本GitHub引渡しと保全。計画やWork申告の転記だけでは未完了。
