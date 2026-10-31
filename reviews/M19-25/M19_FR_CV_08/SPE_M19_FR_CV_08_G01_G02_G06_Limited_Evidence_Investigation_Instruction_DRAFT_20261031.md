# SPE M19-FR-CV-08｜G01・G02・G06 限定証拠調査指示書（DRAFT）

**Status:** DRAFT / READ-ONLY / NOT AN OWNER DECISION / HOLD
**基準保全Commit:** `3e7c1814e2d31fd9373f58e4d88410d382abd8bb`
**原配布固定Commit D:** `e195b9ecdc0e6930f44fce2b598e2c60887c92e4`
**先行保全固定Commit C:** `d1c13df4f18246e1b52f50640dece5477132beb5`

## 1. 目的・実施境界

CV-07証拠不足台帳のG01・G02・G06について、一次証拠の所在、証拠系列、原文と派生レシートの対応、および未取得事項を明確化する。既存のCV05裁定を再裁定せず、過去承認を推定せず、原FindingのSeverity/Status/Dispositionを変更しない。

この文書は**調査実施のための指示案**であり、未取得の一次証拠へのアクセスやOwner私的記録の開示を自動的に許可しない。公開・接続済み資料は指定Commitに固定して読み取り専用で確認する。アクセス不能ならNOT RETRIEVEDと記録する。

## 2. G01｜CV05-N01～N03のOwner原会話

**既存の根拠:** 個別Owner Decision Receipt 3件、Integrated Owner Decision Register、Prospective Normative Decision Packet。これらは帰属付き転載／二次記録であり、元会話との独立一致は未検証。

**調査対象:** (1) 各N01/N02/N03のOwner原メッセージ、(2) 当該応答に先行する選択肢A/Bの原文・質問、(3) 時点・スレッド・引用範囲、(4) 原メッセージと個別レシートの差分。

**照合方法:** 元記録の取得経路と識別子を記録し、転載原文を文字列照合する。改行・空白の違いは明示する。元記録が取得できない場合、レシートの存在と原発言認証を混同しない。

**判定:** `PRIMARY VERIFIED`（元記録と対応を直接照合）／`RECEIPT ONLY`（レシートのみ）／`CONFLICT`（原文相違）／`NOT RETRIEVED`（元記録未取得）。一次証拠の正式採用は別途Owner判断。

## 3. G02｜歴史的裁定・E-1/E-2・DecisionLog

**調査対象:** 関連する契約ID・版・承認根拠・有効範囲・適用年・操作範囲・優先順位・Decision要否。E-1（Decision省略に関する別承認契約）とE-2（2026切替候補生成／利用／予約等の独立認可）の原記録、およびCanonical DecisionLogとの対応。

**調査方法:** 対象条項CC-03/04/05/09/12とCV05-N01～N03に関係する履歴だけを抽出。各証拠に`source/path`, `fixed commit/version`, `approval attribution`, `scope`, `effective date`, `operation`, `original vs derivative`を付す。検索対象と不達範囲を明示する。

**禁止推論:** 「指定パケットにない」「探索で発見できない」から「承認が存在しない」へ推論しない。CV05-N01～N03の将来方向の裁定を歴史的承認の遡及証明にしない。

**判定:** `MATCHED TO PRIMARY`／`SECONDARY ONLY`／`NOT LOCATED WITHIN SCOPE`／`CONFLICT`。承認の法的・規範的効力の採否はOwner留保。

## 4. G06｜旧Finding集合の完全性と対応

**別集合:** 原32件OPEN、旧8件未裁定、CLD3-01 Major、およびCV07新15件を混合しない。旧20＋新12から成る「32件処分案」は正式Closeではない。

**調査対象:** 各集合の原報告・原ID・Severity・Status・版・根拠・処分案・正式Owner Decisionの有無。`CLD2等`の参照は原資料でIDを確定するまで独立の確定件数に数えない。

**照合方法:** 原IDごとに1行のトレーサビリティ表を作成し、派生処分案と原Findingを一対一照合。集合間の重複は「同一論点」と「同一Finding ID」を分離して表示する。

**判定:** `ORIGINAL MATCHED`／`DERIVED ONLY`／`MISSING ORIGINAL`／`ID OR STATUS CONFLICT`。未確認のFindingはOPEN等の既存状態を保持し、正式Closureを推定しない。

## 5. 提出形式とSTOP

提出物（案）：①G01原会話対照表、②G02承認・契約証拠所在表、③G06 Finding原ID対照表、④不足・衝突一覧、⑤取得経路・実バイトSHA-256検証レシート。各表は `evidence ID / source / fixed revision / byte hash (if measured) / verified scope / unresolved / owner-required` を含める。

**STOP:** 原記録へのアクセス不可、Commit不一致、原文衝突、権限不明の場合は当該項目をSTOP/未検証として記録。GitHub書込・原本変更・新規規範採用・Owner裁定・Finding Close・正式承認・Freeze・HOLD解除は禁止。提出後の次工程への自動移行は禁止。

## 6. 参照資料

- `SPE_M19_FR_CV_07_Evidence_Gap_Register_20261031.md` G01/G02/G06
- `SPE_M19_FR_CV_07_Limited_Cross_Verification_Report_20261031.md` T04/T05/T07等
- `SPE_M19_FR_CV_05_N01-N03_Integrated_Owner_Decision_Register_DRAFT_20261031.md`
- CV05-N01/N02/N03個別Owner Decision Receipts

**注意:** 本指示書は原資料の取得・一次認証を実施した結果報告ではない。
