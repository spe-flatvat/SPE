# SPE RP-023 v0.3｜NR-01〜03 限定独立レビュー

**Status:** DRAFT / NON-CANONICAL / NOT ISSUED  
**Repository:** `spe-flatvat/SPE`  
**配布候補固定Commit:** `2d747d2b4162d11b915575ffc791607a37ef95df`  
**作成日:** 2026-11-07  

> 本書はレビュー準備の新規DRAFT。Owner-confirmed Snapshotの新規承認、正式発出、GitHub格納、レビュー開始を宣言しない。旧2026-11-06版§8限定改訂Snapshotを取り消さず、今回のNR-01〜03統合版とは別対象として識別する。

## 1. 依頼候補とレビュー範囲

対象AI：ChatGPT／Claude／Gemini／Grok。**正式発出前のため送付禁止。**

主対象はManifest記載のNR-01〜03全文統合改訂DRAFT。比較は固定v0.3編集基準 `f4939211f1ab5b5848d3aa5293078bb651e2028b`、さらに規範由来確認用のv0.2 `5f27d4e2fba90cda2cd69ee534e865174c31ba1f`。今回のレビューは既存16 Finding（Major 4／Minor 10／Editorial 2）のID・Severityを維持し、NR-01〜03限定追記の解消候補・残余・副作用を評価する。正式Finding Closeを行わない。

- **NR-01:** §7限定HOLD、§9 Workflow保護、§10証拠留保を維持し、未認証の原裁定を不存在・無効と扱わない。旧HOLD文の自動復活・新規HOLD義務を認めない。
- **NR-02:** §3区分別必須要件、§4.1共通識別要件、§8の未実施／未確認／適用外の意味論を維持。適用外理由記録MUST、必須要件の減免、新たな一般的使用制限を導入しない。特に例示の排他的解釈を検証。
- **NR-03:** 技術検証とOwner内容判断を区別し、既存Workflowの独立レビュー要件を保持。発出者と検証者の別人MUST・同一主体記録MUSTを新設しない。
- **共通:** M01〜M07、非遡及、DecisionLog、OD-03/05/06/08の時点別留保、原16 Finding追跡、§7/§8/§9/§10の規範副作用と差分の妥当性を確認。原裁定未照合をPASSへ昇格しない。

## 2. 受領・実行条件（正式発出時に適用する候補）

自己回収優先。固定Commitの原本を取得し、各AIが実バイトのサイズとSHA-256を照合し、取得経路・未検証・補完証拠を受領レシートに区別して記載する。既存PASSは同一対象・同一固定Commit・同一証拠条件の範囲で再利用し、未検証項目だけ補完する。単一取得経路のTECHNICAL STOPを全経路不能と扱わず、代替経路を探索し、同じ失敗を無意味に反復しない。

正式発出指示が**受領READY後の独立レビュー本文開始まで承認**する場合は、追加の開始指示を待たず同一ターンで本文へ進む。`RECEIPT VERIFICATION ONLY` の場合は本文を開始しない。証拠不一致・規範上のSTOP・Owner承認待ちは技術的STOPと区別する。他AIによるSHA一致報告は、Ownerが補完証拠採用を明示した場合のみ限定採用し、自己実測PASSとはしない。外部AIがアクセスできないChatGPT Project/Libraryを必須入力としない。

## 3. 要求回答

受領レシート、原16 FindingのID・原Severity・評価根拠・解消候補・残余・副作用、NR-01〜03ごとの規範増減評価、追加Findingの別記、未検証証拠、総合結論（Accepted / Revision Recommended / Rejected）。AI回答はOwner裁定、consensus、Review Acceptance、正式Dispositionではない。

## 4. 権限境界・未決

GitHub書込み、既存ファイル改変、DecisionLog更新、正式Acceptance、Finding Close、Freeze、HOLD解除、Canonical化、既存Owner裁定の再審は禁止。配布パケットの新Snapshot確認、正式発出、配布経路、回答期限、waiverはOwner別ゲート。RP-023／M19–25 HOLD維持。

## 5. 最終DRAFTパケットの固定条件

- 7原本の期待SHA-256と正確なパスは別個のMarkdown原本 `SPE_RP023_NR01_03_Review_Distribution_Manifest_FINAL_DRAFT_20261107.md` を参照。
- 配布3文書のローカル原本同一性は `LOCAL_FIXITY_REGISTER_NO_ZIP_DRAFT_20261107.md` に記録。GitHub格納後は別Commitと事後照合が必要。
- 本依頼文は**発出文案であり未発出**。Ownerが新主対象のSnapshot、発出、受領READY後の本文開始範囲を明示した場合にのみ、その承認範囲で使用する。

## 6. ZIP形式禁止（Owner明示指示 2026-11-07）

SPEのAI協業ではZIP形式のパケット生成・配布・引渡し・保全利用を禁止する。レビュー資料は個別の原本ファイルとして取得可能な経路で指定する。これは本依頼文の発出承認ではない。
