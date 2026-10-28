3変更の周辺とCC-08以降を再取得し、共通パケット形式で独立再レビュー本文を作成します。

# SPE M19–25｜FG-06 独立再レビュー報告（Grok）

**モデル名:** Grok（xAI）  
**版:** 本環境では公式ビルド版番号を確認できず  
**実施日時:** 2026-10-28（JST）  
**固定 commit:** `13c24ae8beb917289691a52f45cdd0beaeda02f9`  
**Packet ID:** `SPE-M19-25-FG06-REREVIEW-3DEC-20261027-DRAFT-01`  
**評価対象:** `inputs/FG06_CAND_Rev4_3DEC.md`  
**表示SHA-256:** `fce55ac833abb06085340e6bb903939c2121bc6387d07c4d04ddd23cfde6b848`  
**実バイトSHA再計算:** **SHA NOT VERIFIED**（受領記録に保持。本文は raw 取得済）  
**比較原本:** `inputs/FG06_ORIG_Rev4.md`（表示SHA `d1b6e64…`／**SHA NOT VERIFIED**）  
**3変更差分:** `inputs/FG06_DIFF_3DEC.patch`（表示SHA `3a1235ed…`／**SHA NOT VERIFIED**）  
**他AIの今回再レビュー回答:** 未参照  
**過去4AI原回答:** 配布指定の参考証拠として扱い、結論拘束なし  
**本報告の権限:** 独立レビュー報告のみ。Finding Close / Review Acceptance / Canonical化 / Freeze / ファイル修正・commit・push・PR は行わない。M19–25／RP-023 HOLD 継続。

---

## A. Executive Verdict

**CONDITIONAL ACCEPT**

**意味すること**
- 3裁定反映候補は、対象3変更について**規範上の復元方向が妥当**であり、共通パケットが求める再レビュー可能な完成度にある。
- CC-01・CC-03・CC-08 の変更は、それぞれ Rev.2 側の禁止強度／fail-closed／比較条件検証義務に近づく、または明示的に復元している。
- 配布 patch 上、差分は **3 hunk に限定**され、意図しない広範置換は本文比較の範囲では検出していない。

**意味しないこと**
- Freeze、Canonical化、Finding Close、正式 Review Acceptance、Owner裁定の確定。
- 表示SHAとの実バイト一致証明。
- 既存20 Finding の一括解消。
- Authority basis（D25/O/GATE 等）の歴史的原裁定完全照合。

**条件**
1. SHA は受領記録どおり **NOT VERIFIED** のまま扱う。不一致が後から出た場合は対象同一性を再確認。
2. 3変更で **DIRECTLY ADDRESSED** と評価した Finding も、正式 Close は Owner 工程に留保。
3. 3変更外の既存論点（多年度 pending の承認根拠、Invariant 増分、E-03/E-04 等）は **UNCHANGED / NOT VERIFIED** を維持。

---

## B. Finding Register（再レビュー）

### GRK-R2-01（旧 GRK-02 / GPT6-FG06-03 / CLD-02 対応）
- **重大度:** Editorial（本候補では**解消方向が成立**。正式Closeではない）
- **対象:** CC-01（候補 L56 付近）
- **問題（旧）:** 旧Rev.4 は `without separate approval` により、M10/M14/M17/M18 意味論変更を条件付き許容する読みがあった。
- **本候補:**  
  > It MUST NOT modify M10/M14/M17 calculation semantics or M18 evaluation semantics.
- **評価:** Rev.2 の無条件禁止と文言上同等に復元。Control Contract 内の「別承認窓口」弱化は解消。
- **副作用:** 「別途承認された計算契約の改訂」自体を禁止するわけではなく、**本コントローラが意味論を改変しない**境界の明確化。競合は未検出。
- **区分:** DIRECTLY ADDRESSED（3変更起因の修復）
- **推奨:** 正式台帳上は Owner が Close 判定。追加修正は不要。

### GRK-R2-02（旧 CLD-01 対応）
- **重大度:** Editorial（本候補では**解消方向が成立**）
- **対象:** CC-03 状態表 `met` / `not_required` 行
- **問題（旧）:** 旧Rev.4 は transient 強制はあるが、**持続時の明示的 fail-closed** が表行に無く、Rev.2 より弱い読みがあった。
- **本候補:**  
  > Transient only while requesting Decision; MUST settle to `pending`, `approved`, or `rejected` before dependent Gate B completion. **Persistent occurrence fails closed for the dependent switch.**
- **評価:** Rev.2 表行（persistent fail-closed）と整合。CC-02 の「settled Gate B として持続禁止」、CC-03 の「invalid combination は進行中 Decision を自動破棄しない」「incumbent continuation は無関係失敗で止めない」とも矛盾しない。
- **区分:** DIRECTLY ADDRESSED
- **推奨:** 追加修正不要。運用上は reason code（例: 持続 `met`+`not_required`）の機械可読列挙は別契約でよい。

### GRK-R2-03（旧 GRK-03 / GPT6-FG06-01 / CLD-03 対応）
- **重大度:** Editorial（本候補では**解消方向が成立**。軽微な非対称は残る）
- **対象:** CC-08（候補 L281–283）
- **問題（旧）:** 旧Rev.4 は契約の**識別**列挙が中心で、Rev.2 の「all expressly required contract conditions」を**検証する MUST** が落ちていた。
- **本候補 追加文:**  
  > The comparison operation MUST validate the approved comparison contract's evaluation period, metric definitions, units, baseline and initial-state compatibility, and evaluation methodology, **plus all expressly required contract conditions.**
- **評価:** 実質検証 MUST が復元。後続の版一致検証・依存影響分析・非影響未確立時の publication withhold（L287–291）と整合。CC-13 の適格付与権限とも矛盾しない。
- **残余の軽微非対称:** 識別 MUST（L281）は ID/version と required dependencies を含む一方、検証 MUST（L283）の列挙は ID/version を明示再掲しない。ただし L287 の「exact approved contract and dependency versions」検証で実質補完される。
- **区分:** DIRECTLY ADDRESSED（核）／解釈上の軽微リスク（列挙の対称性）
- **推奨:** 任意で検証文に `contract ID/version` を列挙へ戻すと読みが一意になる。必須ではない。

### GRK-R2-04（変更局所性）
- **重大度:** Editorial（確認結果）
- **対象:** 全体／`FG06_DIFF_3DEC.patch`
- **評価:** patch は 3 hunk（CC-01、CC-03 表行、CC-08）。原本と候補の該当箇所以外を抜き読みした範囲で、Reason taxonomy・29 Invariants 見出し・Freeze boundary の意図しない置換は**検出していない**。
- **区分:** 局所性は patch 表示上成立。**実バイト一致は SHA NOT VERIFIED** のため完全証明ではない。
- **推奨:** Owner 側で同一ファイルの `sha256` 再計測。

### GRK-R2-05（旧 GRK-01 ほか・3変更外）
- **重大度:** Major（**UNCHANGED**／証拠）
- **対象:** 多年度 `pending`、計算再試行、atomic/idempotent 年度末、異常年度末、Invariant 増分、Authority basis と DecisionLog 対応
- **評価:** 3変更はこれらを改変・承認・否認しない。内容の内部整合は前回同様「高いが歴史的原裁定未照合」。
- **区分:** UNCHANGED / NOT VERIFIED（承認根拠）
- **推奨:** Freeze 前に裁定 ID マッピング。未マッピングは `evidence: unverified` 維持。

### GRK-R2-06（SHA・証拠）
- **重大度:** Editorial
- **対象:** 受領記録
- **評価:** 本文評価は可能。表示SHAとの実バイト一致は未証明。
- **区分:** 証拠不足（受領と本文評価を混同しない）

### 既存 Finding ID 追跡（要約）

| ID群 | 本候補での扱い |
|------|----------------|
| CLD-01；GPT6-FG06-03, CLD-02, GRK-02；GPT6-FG06-01, CLD-03, GRK-03 | **DIRECTLY ADDRESSED**（文言修復。正式Closeではない） |
| GRK-01 および権限・原裁定系 | **UNCHANGED / NOT VERIFIED** |
| GRK-04, GRK-05, GRK-06 | **UNCHANGED**（3変更の対象外） |
| その他 GPT6/CLD/GEMINI 系（列挙13件側） | 3変更による自動解消は**しない**。個別に UNCHANGED または NOT VERIFIED |
| FG05-N01〜N05 | N02/N03 は改善方向。N01 は承認根拠未検証のまま。N04/N05 は3変更非対象 |

---

## C. Normative Preservation Assessment（18セクション）

| セクション | 分類 | 注記 |
|------------|------|------|
| §0 | KEEP | 3変更の影響なし |
| CC-01 | KEEP + REPLACE（狭義） | `without separate approval` 削除。Rev.2禁止強度へ復元 |
| CC-02 | KEEP | transient 規律は CC-03 修復と整合 |
| CC-03 | KEEP + ADD | 表行に persistent fail-closed を明示。Rev.2方向 |
| CC-04 | KEEP | 3変更非対象。A→C→B・2026初期は維持 |
| CC-05〜07 | KEEP | 副作用未検出 |
| CC-08 | KEEP + ADD | 全明示条件の検証 MUST を復元 |
| CC-09〜13 | KEEP | 比較権限・監査は CC-08 と整合 |
| Reason taxonomy | KEEP | |
| Invariants | KEEP / REVIEW | 3変更非対象。増分の裁定根拠は未検証のまま |
| Freeze boundary | KEEP | |
| Editorial notes | KEEP | |

**REPLACE** は「3変更箇所の文言置換が確認できた」意味であり、**歴史的 Owner 承認の証明**ではない。

---

## D. Residual Risks

| 区分 | 内容 |
|------|------|
| 権限 | 3変更自体は候補DRAFT。採択・Close・Freezeは Owner。Authority basis の DecisionLog 対応は未了 |
| 証拠 | 全指定SHA **NOT VERIFIED**。E-03/E-04 未検証を維持。Step 6D-35 元発言との逐語同一性は未検証 |
| 仕様 | 3修復後も、多年度 pending・異常年度末等の**承認境界**は残る。CC-08 検証列挙と識別列挙の対称性は任意改善点 |
| 実装 | fail-closed の reason code 機械可読集合、比較契約の「追加条件」登録方法は別契約 |

---

## E. Review-to-Freeze Conditions

**今すぐ言えること（本再レビュー）**
- 3変更は、指摘されていた規範弱化（CC-01 条件付き禁止、CC-03 持続 fail-closed 欠落、CC-08 全条件検証欠落）を**文言上修復**している。
- patch 表示上、変更は局所的。

**Freeze／正式 Close 前に Owner が別途判断すべきこと**
1. 実バイト SHA の独立一致確認  
2. DIRECTLY ADDRESSED 各 ID の正式処分（Close 可否）  
3. GRK-01 系・原裁定マッピング／E-03/E-04  
4. 残る既存 Finding の個別処置  
5. Workflow に沿う snapshot・DecisionLog・Freeze の別承認  

**実行しないこと**  
ファイル修正、commit/push/PR、Finding Close、Review Acceptance、Canonical化、Freeze。

---

## 必須質問 1–9（要約）

1. **CC-03／CLD-01:** 持続 `met`+`not_required` の明示 fail-closed は復元。transient・Gate B・incumbent continuation・多年度 pending と矛盾せず。  
2. **CC-01／GRK-02系:** `without separate approval` 削除により、Rev.2 同等の無条件禁止へ復元。新規権限衝突は未検出。  
3. **CC-08／GRK-03系:** 全明示条件の検証 MUST を復元。版一致・再検証・CC-13 と整合。  
4. **変更局所性:** patch 3 hunk。広範な MUST 群・taxonomy・Invariants・Freeze の意図しない変更は、読取範囲で未検出（SHA未検証のため完全証明ではない）。  
5. **横断整合:** Gate A→C→B、2026初期／2027継承の枠は3変更で壊していない。架空2025は引き続き禁止。  
6. **残余Finding:** 上記追跡表。3裁定で自動 Close しない。  
7. **歴史的権限:** 未取得を未承認・不存在と断定しない。E-03/E-04 未検証保持。  
8. **新規回帰:** 3変更起因の Critical/Major 新規回帰は未検出。列挙対称性は Minor/Editorial 級。  
9. **Rev.2規範保存:** 3焦点については復元方向。文書全体の ADD 部分（多年度等）の承認根拠は REVIEW 継続。

---

**総括:**  
`FG06_CAND_Rev4_3DEC.md` は、Owner案Aの3裁定を反映した候補として、**規範修復の方向は妥当**であり、独立再レビューとしては **CONDITIONAL ACCEPT**。  
これは候補品質の評価であり、正式受理・Close・Freeze ではない。Owner による確認・保存を前提とした独立報告とする。
