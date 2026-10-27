# SPE M19–25｜FG-06 修正候補専用 Common Independent Re-review Request — DRAFT

- 工程：FG-06 再レビュー配布準備／**未配布・未承認**
- パケットID：`SPE-M19-25-FG06-REREVIEW-3DEC-20261027-DRAFT-01`
- 唯一の評価対象：`inputs/FG06_CAND_Rev4_3DEC.md`
- 評価対象SHA-256：`fce55ac833abb06085340e6bb903939c2121bc6387d07c4d04ddd23cfde6b848`
- 比較原本：`inputs/FG06_ORIG_Rev4.md`、SHA-256 `d1b6e64caead960972f0e8c2b2edebb24deb36522cc41d65947ff0580a1bd04e`
- 3変更差分：`inputs/FG06_DIFF_3DEC.patch`、SHA-256 `3a1235ed56978d0410debd887a9e3186ef8ffceb71600c9f43098b3ae4f1c12c`

## 1. 依頼目的・権限

Ownerが案Aを選択したCC-03、CC-01、CC-08の3裁定を反映した**新しい全文候補**について、独立した規範レビューを行う。旧FG-06のRev.4原本（SHA `d1b6...`）を唯一のレビュー対象として再利用しない。旧FG-06のCommon Review Request/Packetは評価方法・証拠基準の参照であり、新候補の対象識別子を上書きしない。レビューAIは他AIの今回の再レビュー回答を参照しない。旧4AIレビューは既存Findingの追跡資料であり結論を拘束しない。

本書は**依頼書DRAFTであり、現時点では送付・レビュー開始を承認しない**。M19–25およびRP-023はHOLD継続。DecisionLog更新、正式Review Acceptance、Finding Close、Canonical化、Freeze、GitHub書込みは行わない。最終判断権限はOwner。

## 2. 入力検証・STOP条件

レビュー前に、候補・原本・patchのファイル名、byte count、実バイトSHA-256、取得経路を記録する。不一致、対象本文未取得、差分3変更ブロック以外の変更検出ならSTOPし報告する。本文を読めるがSHAを計算できない場合は`SHA NOT VERIFIED`と明示し、限定評価可否と根拠を示す。配布パケットの必須資料が欠ける場合は不足と影響範囲を記録し、推定補完しない。

比較元Rev.2、FG-05、Step 6D-35、Workflow、DecisionLogは旧FG-06パケットの要求する参照資料。**新配布セットへの実バイト同梱と版照合は未完了**。これらを欠いたまま旧FG-06と同等の完全レビューができたと宣言しない。

## 3. 必須レビュー質問

1. **CC-03／CLD-01**：`met/not_required`の持続発生に対する明示的fail-closedが復元されたか。transient扱い、Gate B、依存切替、incumbent continuation、多年度pendingと矛盾しないか。
2. **CC-01／GPT6-FG06-03・CLD-02・GRK-02**：`without separate approval`の削除によって、M10/M14/M17計算意味論・M18評価意味論の保護がRev.2と同等に戻ったか。他条項との権限衝突・新規回帰はないか。
3. **CC-08／GPT6-FG06-01・CLD-03・GRK-03**：comparison operationによるevaluation period、metrics、units、baseline/initial-state compatibility、methodology、**all expressly required contract conditions**の実質検証MUSTが復元されたか。ID/version、依存変更再検証、CC-13比較適格性と矛盾しないか。
4. **変更局所性**：原本との差分は上記3変更ブロックに限定されるか。意図しないMUST/MUST NOT/MAY、状態表、Reason taxonomy、29 Invariants、Freeze boundaryの変更はないか。
5. **横断整合性**：CC-01〜13、Gate A→C→B、2026初期状態と2027継承、Decision/Trigger/予約/比較/HOLDの整合性を検証する。架空の2025最終状態を作らない。
6. **残余Finding**：既存20件の各IDについて、`DIRECTLY ADDRESSED / POSSIBLY AFFECTED / UNCHANGED / NOT VERIFIED`を区別し、3裁定で自動Closeしない。FG05-N01〜N05も別集合として個別に追跡する。
7. **歴史的権限**：実質追加規範のOwner原裁定の所在・承認根拠は別の証拠論点として扱う。未取得を未承認・不存在と断定しない。E-03/E-04未検証を保持する。
8. **新規回帰・未解決**：3変更に起因する新規Findingと既存未解決Findingを区別し、Owner新裁定が必要な事項と原記録回収で足りる事項を分ける。
9. **Rev.2との規範保存**：全18セクションをKEEP / REPLACE / ADD / REVIEW（複数可）で評価し、既存の旧レビュー結果をそのまま転載しない。

## 4. 既存Finding IDの追跡

- **直接修正対象**：CC-03 `CLD-01`；CC-01 `GPT6-FG06-03`, `CLD-02`, `GRK-02`；CC-08 `GPT6-FG06-01`, `CLD-03`, `GRK-03`。
- **他の既存13件**：`GPT6-FG06-02, GPT6-FG06-04, GPT6-FG06-05, GPT6-FG06-06, GPT6-FG06-07, CLD-04, CLD-05, CLD-06, GEMINI-01, GRK-01, GRK-04, GRK-05, GRK-06`。
- GeminiのFG05-N01〜N05再評価は独立新規Findingとして重複計数しない。元の20件はID・重大度を維持し、横断論点の同一性だけで統合・Closeしない。

## 5. 回答形式（旧共通依頼書と互換）

A. Executive Verdict：`ACCEPT / CONDITIONAL ACCEPT / REVISE / REJECT`。対象・SHA・原本・参照資料の検証状態と理由を明記。旧準備書の`ACCEPT WITH CONDITIONS / STOP`を混用せず、停止事象は別途`STOP / NOT VERIFIED`と記録。

B. Finding Register：独自ID、Critical/Major/Minor/Editorial、ファイル・節・行、問題・成立条件・制御影響、Rev.2との関係、正確な原文引用、修正提案、Owner裁定必要性（既存根拠回収か新裁定か）、FG05-N01〜N05対応、確定問題/解釈リスク/証拠不足、3変更に起因するかを記録。

C. Normative Preservation Assessment：§0、CC-01〜13、Reason taxonomy、Invariants、Freeze boundary、Editorial notesの**18セクション**を評価。

D. Residual Risks：権限、証拠、仕様、実装境界を分離。E-03/E-04未検証を保持。

E. Review-to-Freeze Conditions：再レビューで検証できたことと、正式Freeze前にOwnerが別途判断すべきことを区別。

## 6. 独立性・配布前提

配布先4AIには同一候補バイトと同一依頼書を渡し、初回回答完了まで今回の相互回答を見せない。旧4AI原回答を配る場合は全4件を同条件で配布し、先行判定の誘導可能性を明記する。各AI固有Finding IDを保持。Owner配布承認、入力一式SHA照合、配布先・方法・時刻の記録までは**NOT DISPATCHED**。
