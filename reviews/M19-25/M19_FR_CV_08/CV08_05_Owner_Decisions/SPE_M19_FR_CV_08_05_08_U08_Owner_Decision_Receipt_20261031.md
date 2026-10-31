# SPE M19-FR-CV-08-05-08｜U08 Owner裁定受領レシート

**正式名称：** SPE M19-FR-CV-08-05-08｜U08 参照GitHub原本の実バイトSHA-256全件照合に関する実施条件 Owner裁定受領レシート  
**Status:** OWNER DECISION RECEIVED / FULL-SCOPE BYTE VERIFICATION AUTHORIZED / RECEIPT ONLY / NOT VERIFICATION COMPLETE / HOLD  
**Date:** 2026-10-31（会話上の日付。独立時刻証明なし）  
**Repository:** `spe-flatvat/SPE`  
**Reference commit:** `754c1e2907bce67f7d58d10bf36813ac76fd1ed0`（CV-08調査の参照固定Commit。変更なし）  
**Decision ID:** `CV-08-05-08 / U08`  
**Decision:** 案A採用

## 1. Owner応答原文

> CV-08-05-08 U08のOwner裁定：案Aを採用します。追加条件：レシート発出ください。裁定レシートを発出し、U01〜U08の裁定結果を統合整理してください。

「追加条件：レシート発出ください」は事務的なレシート発出指示として扱う。原文を変更せず保存する。

## 2. 採用案Aの範囲

CV-08の参照GitHub原本について、固定Commit原本の**全件実バイトSHA-256照合**を行うための作業方針・範囲を承認する。対象を明確に列挙し、各ファイルごとに以下を記録する。

1. Repository、固定Commit、相対ファイルパス、取得経路。
2. Git blob SHA-1（Gitの識別子）と、取得した原本バイト列から計算したSHA-256（別種の値）。
3. 独立した期待SHA-256値の有無、出典、対象Commit・パス・版との対応。
4. 計算可否、期待値との一致・不一致、未照合理由、取得不能・検証不能の区別。

**期待値が未提示・出典不明の場合は、SHA-256の計算成功のみを記録し、期待値との一致を主張しない。** UTF-8再エンコードや改行正規化後のバイト列を原本の実バイト検証として代用しない。Git blob SHA-1を実バイトSHA-256と混同しない。

## 3. 権限とSTOP条件

- 読み取り専用の取得・ハッシュ計算・証拠台帳DRAFT作成を許可する。
- ファイル取得不能、期待値欠落、不一致、固定Commit不一致等を個別に明示し、推測でPASSにしない。
- 不一致が発生した対象は検証上STOPとし、原資料を改変・補正しない。全件一致を前提とする次の処理には進まない。
- 本レシートは**照合の実施結果ではない**。全件実バイトSHA-256照合は未実施であり、別途作業開始指示・対象一覧・実施記録が必要。
- GitHub書込、原本変更、DecisionLog更新、Finding Close、Severity・Status・Disposition変更、Control Contract正式承認、Acceptance/Freeze、M19–M25／RP-023 HOLD解除は禁止。

## 4. 工程の終端

U08案Aを受領。U01～U08統合整理は別のDRAFT成果物として提出する。U08の承認をもって調査や検証の実施済みとはしない。

**STOP:** レシート発出・統合整理の提出で本裁定工程を終了し、次の実行工程に自動移行しない。M19–M25／RP-023 HOLD継続。
