# SPE｜F・SQ・N3 共通指標の実行可能性確認・30年次比較・Claude独立検算用引渡し

**Status:** WORK EXECUTION REQUEST / OWNER AUTHORIZATION BY WORK MESSAGE / READ EXISTING + LIMITED NEW HANDOFF WRITE / NON-CANONICAL
**Repository:** `spe-flatvat/SPE` / **Branch:** `work/chatgpt-handoff`
**Period:** 2026–2055
**Starting fixed commit:** `89e5ee2eead0f1b846d33ed0c315168fc461ceb9`

## 目的と優先順位
F・Status Quo（SQ）・N3の既存計算原本を再利用し、同一定義・単位・価格年・人口前提・年次・施策範囲で実際に比較できる指標を特定して、**共通年次比較CSVと再実行可能な計算**を生成する。差が比較不能な場合は値を埋めずN/Aとし、理由と必要な実装を明示する。新たな施策の創作や政策本文の変更は行わない。

**順序:** ①原本と比較条件の回収 → ②同質な指標の実計算・照合 → ③比較不能な部分の限定診断と必要なら最小の接続補完 → ④成果引渡し・Claude独立検算パケット作成。4AI正式レビュー、Owner追加承認、採番/台帳増設は不要。

## 固定参照と自己回収
開始固定Commitの以下を優先して取得・再利用:
- F中間層統合 `handoff/chatgpt-f-middle-class-integrated-20261123/stage4-integrated/`（最終固定Commit `89e5ee2eead0f1b846d33ed0c315168fc461ceb9`）
- F統合 `handoff/f-integrated-20261121/`、F既存のマクロ・家計・財政診断。
- SQ `handoff/chatgpt-statusquo-common-macro-limited-diagnostic-20261123/`、`handoff/f-statusquo-provisional-20261115/` 等。**SQの複数variantを混ぜない**。比較対象のvariant/原本/計算式を固定する。
- N3の既存モデルと比較資料をGitHub内から探索し、`handoff/n3-f-parity-work-20261122/`、`handoff/claude-n3-f-parity-verification-request-20261122/` の既存成果/前提も確認。依頼書と計算原本を混同しない。
- F・N3・SQそれぞれの固定入力、リスクイベント、デフレーター、人口、政策開始年、ベースライン定義と既存PASS。取得できる原本を優先し、Ownerへ手動提出を要求しない。

## 作業1｜共通指標の比較契約を実証
各指標について、F/SQ/N3の実原本パス・固定SHA/Commit・年次範囲・計算式・単位・名目/実質・価格基準年・人口/リスク/施策カバレッジ・実装状態を一覧化し、**COMPARABLE / CONDITIONAL / NOT COMPARABLE / N/A** に分類。対象候補は実質/名目GDP、GDPデフレーター、人口、労働人口・就業、税収、賃金/所得、家計手取り/購買力、所得分布/ジニ、政府収支、国債発行/利払/債務、施策別財政。全国値と合成世帯診断、部分財政と全国財政を混同しない。条件付き比較は条件差を併記。

## 作業2｜共通年次の実計算・比較
最低限、原本が揃い比較条件が成立する指標を2026〜2055年の全30年で実際に抽出/再計算し、F・SQ・N3、F−SQ、F−N3、必要ならN3−SQの差を年次CSVで生成。2026・2035・2045・2055を要約。単なる過去レポートの数値転記ではなく、コードによる独立再集計・照合を実施。条件不一致の値を比較可能と表示しない。SQ variant差を明示し、固定FやN3を変更しない。Fの非採用中間層感度は固定F政策値とは別列/別表。

## 作業3｜限定的な比較不能要因の切分け
比較不能な指標は原因を①データ/コード未取得、②定義・単位・基準年差、③政策実装粒度差、④マクロ/家計/財政の接続不足、⑤政策上の未決定に分類。**既存入力と式で安全に接続できるものだけ**最小限の比較アダプタを実装して再実行。N3/SQにFの施策を勝手に移植せず、欠損値を外挿や架空の数値で埋めない。比較対象を広げるための大規模モデル改修は今回対象外。何が新たに比較可能になったかを明示。

## 作業4｜成果引渡しとClaude限定検算パケット
`handoff/chatgpt-f-sq-n3-common-indicators-20261123/` に、比較契約/Provenance（CSVまたはJSON）、2026〜2055年次比較CSV、主要年要約、再実行コードと依存固定参照、検証結果、日本語Report.md、Manifest/Custody、Claude検算用の短い `Claude_Verification_Request.md` を**個別原本**として格納。ZIP禁止。Claude用文書には、固定Commitでの原本独立取得、数値再計算、定義・価格年・SQ variantの整合、N/A境界、実バイトSHA/サイズ確認、差異の限定報告を指定する。**Claudeへの発出・Claudeの検算実施・正式Acceptanceは今回のWork実行には含めない**。Ownerが後からClaudeへ渡せる状態までを引渡し成果とする。

## 検証・保全
既存PASSを同一原本・同一条件で再利用。新規計算は年次完全性、基準年一致、差分算術、名目/実質/デフレーターの整合、人口単位、重複集計、再実行一致を確認。各原本の固定Commit事後取得、実バイトSHA-256、サイズ、保存先を照合した場合のみCUSTODY PASS。生成・実行・検証・GitHub引渡し・保全を分けて報告。

## 権限境界
書込みは `work/chatgpt-handoff` の新規成果ディレクトリのみ。main、政策本文・Annex、固定F/SQ/N3、DecisionLog、正式Acceptance/Freeze/Canonical、既存承認ゲートを変更しない。RP-023/M19–25 HOLD、RP-024 PENDING維持。Claude独立検算は**Work完了後の別実行**であり、Workの完了ゲートにしない。途中STOPは理由・範囲を限定し、比較可能な成果を先にGitHubへ引渡す。

**完了判定:** 実行可能性一覧、共通30年次の実計算・比較、限定接続の実成果、個別原本GitHub引渡し・保全、Claude検算用文書の作成。未達項目は未完了と記載。
