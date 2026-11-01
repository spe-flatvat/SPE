# SPE M19-CC09-IR-01｜Termux格納前引き継ぎ票 DRAFT

**Status:** LOCAL PACKAGE READY / GITHUB WRITE NOT EXECUTED / OWNER APPROVAL REQUIRED FOR WRITE

## 対象
- Repository: `spe-flatvat/SPE`
- 審査対象固定Commit: `edc47652f986b75341404154bfd3057da89e9329`
- 推奨格納先（未承認）: `reviews/M19-25/M19_CC09_IR01/integrated_4ai_results_20261101/`
- 格納対象: `originals/`（ChatGPT/Grok/ClaudeのファイルコピーとGeminiの会話抽出記録）、`analysis/`（横断検証DRAFTと本引き継ぎ）、`SHA256SUMS.txt`、`SHA256_MANIFEST_DRAFT_20261101.json`

## 重要な出典区分
1. ChatGPT/Grok/Claude: この作業環境で確認できた報告書ファイルのバイトコピー。原AI発話との独立同一性は別途未検証。
2. Gemini: 会話で提示されたレビュー内容を再構成した抽出記録。**逐語的な原回答全文の保全ではない**。原文完全保全が必要なら、別途Gemini回答の原文ファイルまたは全文コピーを追加する。
3. 横断検証: 二次分析のDRAFT。正式Finding台帳・Owner裁定ではない。

## Termux作業前の確認事項
- Ownerが格納先、作業ブランチ、基準Commit、GitHub書込許可を明示すること。
- 既存ファイルと衝突しない新規パスを選ぶこと。
- パッケージ解凍後 `sha256sum -c SHA256SUMS.txt` で各ファイル一致を確認すること（パッケージのルートから実行）。
- GitHub格納後に固定Commitと全ファイルの実バイトSHA-256を再照合すること。
- mainへの直接変更、原本上書き、DecisionLog更新、Finding正式Close、Freeze、HOLD解除は行わないこと。

## STOP
上記のOwner指示が未発出のため、Termux操作・GitHub書込・commit・push・PR作成は実施しない。
