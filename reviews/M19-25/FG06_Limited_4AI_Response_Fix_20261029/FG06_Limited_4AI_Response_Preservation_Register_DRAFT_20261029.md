# SPE M19–25｜FG-06 限定再レビュー 4AI回答固定台帳（DRAFT）

対象日：2026-10-29  
固定配布Commit：`789403ae904594a0973ed7c7a142745a75595320`  
保全工程：**4/4回答のローカル保存ファイル作成・実バイトSHA-256計測完了／GitHub未保全**  
M19–25／RP-023：HOLD継続。

## 保存ファイル検査

| AI | 受領経路 | ファイル名 | サイズ（bytes） | 保存ファイルSHA-256 |
|---|---|---|---:|---|
| Claude | 添付Markdown | `M19_25_Claude_FG06_Limited_Rereview_Independent_Review_DRAFT.md` | 16592 | `af1fdcddb76db53b248ffeee2744dd6b71896314d505b3589820df2c1e37d50d` |
| ChatGPT | チャット貼付から再構成 | `M19_25_ChatGPT_FG06_Limited_Rereview_Independent_Review_DRAFT.md` | 9850 | `1717b82dcd5a0fff683a9d68b1710b4a0fe47c41e6364df5ca968f082fc13223` |
| Gemini | チャット貼付から再構成 | `M19_25_Gemini_FG06_Limited_Rereview_Independent_Review_DRAFT.md` | 9405 | `90836efda65ca339763064517e0ec013604a629f414238352d3e0770a546fb14` |
| Grok | チャット貼付から再構成 | `M19_25_Grok_FG06_Limited_Rereview_Independent_Review_DRAFT.md` | 7467 | `27cf4e312d7d82b6885f8b9e159b79e2fbdda84d91a7dc15c842284a108f466c` |

## 証拠の境界

- Claudeは添付原本の実バイトを保存。ChatGPT、Gemini、GrokはOwnerが認めた**チャット貼付本文からMarkdownを再構成**して保存した。後者3件は元AI環境の出力とのバイト一致を証明していない。
- 表中のSHA-256は**今回保存したファイル**に対する計測値であり、配布パケット、元AI出力、GitHub保存済みファイルのハッシュではない。
- Markdownの表示表現・改行・エスケープの再構成に伴う差異の可能性は残る。会話中の貼付本文を一次受領記録とする。
- ChatGPT／Grokによる**配布パケット**の独自実バイトSHA-256検証はNOT VERIFIEDのまま。Claudeの18/18補完証拠と混同しない。
- 配布パケット固定Commitと、今後の回答保全Commitは別物である。

## 回答識別（保全メタデータであり、Finding裁定ではない）

| AI | Verdict（報告値） | Finding（報告値） |
|---|---|---|
| ChatGPT | REVISE | FG06-GPT-RR-01〜04（Major 1、Minor 2、Editorial 1） |
| Gemini | CONDITIONAL ACCEPT | GEMINI-FG06-01（Editorial 1） |
| Grok | CONDITIONAL ACCEPT | GRK-LIM-01（Minor）、GRK-LIM-02（受領Editorial） |
| Claude | REVISE | CLD3-01〜05（Major 1、Minor 2、Editorial 2）、既存CLD2継続事項 |

## 未完了の固定ゲート

1. OwnerによるGitHub書込先・書込実施の承認。
2. 4回答ファイルと本台帳を専用保全先へGitHub保存し、保全Commit SHAを記録。
3. 保存先Commitから5ファイルを再取得または照合し、SHA-256・件数を確認。
4. Ownerへ保全COMPLETE判定を報告。

**未実施：** 横断検証、Finding統合・Close、Owner裁定、Review Acceptance、Freeze、HOLD解除。
