# SPE M19–25｜FG-06 3裁定反映候補 Common Re-review Packet — DRAFT

- パケットID：`SPE-M19-25-FG06-REREVIEW-3DEC-20261027-DRAFT-01`
- 状態：`DRAFT / NON-CANONICAL / DISTRIBUTION HOLD`

## 1. 唯一の候補と版の境界

- 新候補：`inputs/FG06_CAND_Rev4_3DEC.md` SHA-256 `fce55ac833abb06085340e6bb903939c2121bc6387d07c4d04ddd23cfde6b848`（38,214 bytes）。
- 比較原本：`inputs/FG06_ORIG_Rev4.md` SHA-256 `d1b6e64caead960972f0e8c2b2edebb24deb36522cc41d65947ff0580a1bd04e`（37,939 bytes）、GitHub commit `b81f7057e84ad285e2e87e3263bffe6f31f8f9a9`。
- 差分：`inputs/FG06_DIFF_3DEC.patch` SHA-256 `3a1235ed56978d0410debd887a9e3186ef8ffceb71600c9f43098b3ae4f1c12c`。
- 新候補はOwner裁定3件を反映した**未承認のDRAFT**。旧Rev.4と同一のSHAとして扱わない。

## 2. 裁定対応（裁定レシートはDRAFT）

| 裁定候補 | 条項 | 案Aの目的 | 既存Finding |
|---|---|---|---|
| DEC-CAND-01 | CC-03 | met/not_required持続時の明示的fail-closed復元 | CLD-01 |
| DEC-CAND-02 | CC-01 | 別承認例外句の除去 | GPT6-FG06-03, CLD-02, GRK-02 |
| DEC-CAND-03 | CC-08 | 比較契約全明示条件の検証義務復元 | GPT6-FG06-01, CLD-03, GRK-03 |

裁定反映の技術検証と、規範的な採否・歴史的Owner裁定の完全性は別問題。3修正以外のFindingを解消済みと推定しない。

## 3. 参照資料と出典

旧共通パケット：`references/FG06_OLD_Packet.md`、旧共通依頼書：`references/FG06_OLD_Request.md`。旧パケットManifestとDistribution Checklistは旧配布セットの証拠であり新セットのManifestではない。

既存4AIレビュー（GitHub固定commit `231a983d4467c3427f6a782bf336e5b3f49ced2f`）：GPT-6 7件、Claude 6件、Gemini 1件、Grok 6件、計20独立Finding。原回答4件は固定GitHub blobとの対応を確認し、実バイトSHA-256照合済み（ChatGPT/Gemini/GrokはTermux回収ZIPから再読込、ClaudeはLibrary raw_file回収）。配布用原回答は `prior_reviews/` に同梱。`references/FG06_4AI_CROSSWALK_DRAFT.md`は二次整理であり原回答そのものではない。

旧FG-06のRev.2、FG-05、Step 6D-35配布用転記、Workflow、DecisionLogは `old_packet/` に同梱し、固定SHA-256を照合済み。4AI原回答は `prior_reviews/` に同梱し、実バイトSHA-256照合済み。Step 6D-35配布用転記と元Owner発言の逐語同一性、および歴史的Owner裁定の完全性は未検証であり、これらを承認済みと推定しない。

## 4. 対象の主要構造

§0、CC-01〜CC-13、Reason taxonomy、29 Invariants、Freeze boundary、Editorial notes。特にCC-02/03/04/05/07/08/09/12/13、Gate A→C→B、2026初期状態と2027継承、予約/Decision/比較/HOLDの制御境界を重点検証。元Rev.4の見出し・行番号は変更後にずれる可能性があるため、引用は新候補本文の行番号を再計算する。

## 5. 先行Findingと留保

旧FG-05のN01〜N05、Step 6D-35の5件、Rev.2四AI18件、旧FG-06の20件は別集合。今回の3裁定だけで一括処分しない。OD-12の条件付きReview AcceptanceはRev.2四AI18件の規範処理に限定。固定旧Rev.4冒頭の`NOT REVIEW-ACCEPTED`と後続OD-12を別管理。E-03/E-04と歴史的Owner裁定の完全照合は未検証。DecisionLogの正式対応はOwner別裁定。

## 6. レビュー独立性とSTOP

同一資料・同一質問・同一候補SHAを配布し、今回の回答を相互に見せない。候補SHA不一致、必要資料欠落の無申告、意図しない変更、無承認配布はSTOP。レビューの4値判定は候補品質に対するもので、正式Review AcceptanceやFreezeを意味しない。
