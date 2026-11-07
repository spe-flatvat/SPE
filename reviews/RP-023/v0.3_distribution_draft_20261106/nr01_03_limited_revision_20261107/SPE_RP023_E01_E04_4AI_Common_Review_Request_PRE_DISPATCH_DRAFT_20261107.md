# SPE RP-023｜E-01〜E-04反映版 4AI共通独立レビュー依頼書 DRAFT

**Status:** CONTENT-COMPLETE DRAFT / PRE-DISPATCH VALIDATION PENDING / NON-CANONICAL / NOT ISSUED
**Repository:** `spe-flatvat/SPE`
**主対象固定Commit:** `6b8406a966a464de5b29199b4c12e0535e6ac827`
**主対象パス:** `reviews/RP-023/v0.3_distribution_draft_20261106/nr01_03_limited_revision_20261107/SPE_RP023_v03_NR01_NR03_Post_Cross_Audit_Revision_Candidate_DRAFT_20261107.md`
**主対象サイズ:** 20,128 bytes
**主対象SHA-256:** `b0e770dd696da7f161d8a8e9c9372a88780c70a1224d6bf09a3bd73f58cb82e5`
**作成日:** 2026-11-07
**権限:** Owner承認済みレビュー発出準備のみ。正式発出・新Snapshot承認・GitHub書込み・レビュー開始は未承認。


## 1. レビュー目的と共通契約

既存NR-01〜03統合版（固定Commit `2d747d2b4162d11b915575ffc791607a37ef95df`、19,595 bytes）からE-01〜E-04のみを限定修正した20,128 bytes版を主対象とする。旧発出指示書の19,595 bytes Snapshotを今回の主対象として誤用しない。既存16原Finding（Major 4 / Minor 10 / Editorial 2）のID・原Severityを維持し、解消候補・残余・副作用を個別に評価する。NR-01〜03のOwner裁定を再審しない。

## 2. 重点質問

- NR-01：§7限定HOLD・§9 Workflow保護・§10原裁定証拠留保が維持されているか。未認証を不存在・無効と扱っていないか。
- NR-02：§3・§4.1・§8の既存必須要件を維持し、「適用外」例示を排他的条件・新規一般MUSTと解していないか。
- NR-03：技術的検証とOwner内容判断の区別を保ち、別人／別AIの一般必須化や同一主体記録MUSTを新設していないか。
- E-01：§8の非排他的例示と既存要件の維持。
- E-02：§7の原裁定証拠留保を§3・§6・§10と整合的に解釈できるか。
- E-03：§7の「検証担当」の解釈を§8と整合させ、不要な主体分離義務を生じないか。
- E-04：ヘッダー日付だけが2026-11-07へ更新され、Version/Status/Updated Byは保持されたか。
- 共通：M01〜M07、非遡及、OD-03/05/06/08、DecisionLog、§7/8/9/10の規範増減と副作用、原16 Findingの追跡、未検証証拠の扱い。

## 3. AI別の配布経路

- ChatGPT／Claude／Grok：GitHub固定Commit直接参照型。Manifestの固定パスを最初から使用する。
- Gemini：**全必須資料収録済みの検証済み統合Markdown添付型**。GitHub直接取得を要求しない。統合原本が未完成の場合は発出しない。
- いずれも各AIが自身の受領経路と検証結果を記録する。他AIのSHA申告を自己実測PASSとしない。取得経路の試行錯誤を正式発出後の初期手順に組み込まない。

## 4. 受領・レビュー・回答

正式発出承認で同一ターン実行が許可された場合のみ、受領READY後、追加指示なく独立レビュー本文を実施する。`RECEIPT VERIFICATION ONLY`なら本文は禁止。受領レシート、原16 Finding個別評価、NR-01〜03・E-01〜E-04の副作用評価、新規Finding、未検証、総合結論（Accepted / Revision Recommended / Rejected）を**単一の個別Markdown回答原本**として提出する。

STOPはTECHNICAL / EVIDENCE / NORMATIVE / OWNER AUTHORIZATION PENDINGを分離し、範囲・既存PASS・代替経路を記録する。回答を二重生成しない。

## 5. 禁止・留保

ZIPは禁止。GitHub書込み、Finding Close、正式Acceptance、DecisionLog更新、Freeze、HOLD解除、Canonical化、既存Owner裁定の再審は禁止。RP-023・M19–25 HOLD維持。回答期限・waiver未指定。配布資料の新規固定・正式発出はOwner別承認ゲート。

## 6. 参照資料と差分の優先順位

レビュー主対象はE-01〜E-04反映済み20,128 bytes原本のみ。Step29Hの4AI回答は**原16 Findingの由来と論点の照合資料**であり、今回の4AIレビュー回答ではない。旧NR-01〜03統合版・差分・副作用監査・Owner裁定レシートは比較・証拠資料。新旧で文言が異なる場合は、変更箇所を明示して新主対象の適否を判定する。旧版の文言を新主対象に読み替えてはならない。

各Findingは「ID／原Severity／該当節／確認した証拠／評価（解消候補・残余・副作用・未検証）／推奨措置」を記録する。既存16件以外の新規Findingは独立採番候補として別枠に記載し、原Findingの件数・Severityを勝手に変更しない。正式発出後の回答には取得したファイルごとの受領検証状態も併記する。

**発出前ゲート:** 本依頼書が完成していても、Manifest記載の必須原本識別・実バイト照合、Gemini統合原本完成、Owner新Snapshot確認と正式発出承認までは配布禁止。
