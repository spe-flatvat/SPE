# SPE M19-FR-CV-08｜一次証拠不足・限定追加調査報告 DRAFT

**Status:** DRAFT / READ-ONLY / CONDITIONAL / STOP
**Repository:** spe-flatvat/SPE
**参照固定Commit:** C `d1c13df4f18246e1b52f50640dece5477132beb5`、探索用保全 `754c1e2907bce67f7d58d10bf36813ac76fd1ed0`。既存baseline/Dは変更しない。

## 実施と証拠境界

受領したStage C–F統合報告書を読み取り、ローカルファイルのSHA-256を計算した（`a9ba6ece627660ff2226cff308d670aa7543a423023b44ff8ea02c286325160a`）。独立した期待値は未提示のため、配布原本とのSHA一致とは判定しない。GitHub連携で固定Cの再帰tree 132件、探索用保全の再帰tree 139件を取得。双方 `truncated=false`。GitHubコード検索はデフォルト枝に対する補助探索に限り、固定Commitの不存在判定には用いない。

## G01｜PARTIAL / RECEIPT ONLY

固定CommitにCV05-N01/N02/N03個別Owner Decision Receipt、N01–N03 Integrated Owner Decision Register、Prospective Normative Decision Packetのパスを確認し、探索用保全CommitからN01レシート、統合記録、選択肢パケットの本文を取得。N01案A（現行Decision要件保全）、N02案B（CC-04参照句限定修文案の起案のみ）、N03案A（2026初期状態と切替認可の分離）は選択肢パケットと統合記録の意味上整合を確認。N01レシートの転記原文も統合記録と一致。**Owner原チャットの元メッセージ、時刻・スレッドIDの一次認証は未取得**。N02/N03個別レシート本文は今回の追加取得対象に含めず、前Stageの報告結果を継承。原会話との独立一致は未判定。

## G02｜NOT VERIFIED / SECONDARY ONLY

固定treeで `docs/DecisionLog.md` と `Step_6D35_Owner_Provided_Audit_Transcript_DRAFT.md` の所在を確認。後者は配布用転載であるとの前Stage留保を維持。CV07 Evidence Gap Register本文も取得し、E-1（非裁量型Decision省略の別承認契約）、E-2（2026切替候補の独立認可）を未取得とする記録を再確認。D25、D22/D23/D24、O、GATE、COMP、R、6D系列のOwner原裁定と承認効力・対象版の一次証拠は回収できず。DecisionLogの全原文と原裁定との逐条再照合は今回未実施。不存在とは判定しない。

## G06｜PARTIAL / ORIGINAL COLLECTION NOT VERIFIED

探索用保全CommitでCV07 Limited Cross Finding Matrix、Evidence Gap Register、Limited Cross Verification Report、4AIレビュー保存物のパスを確認し、Finding Matrix本文を取得。CV07新15件の原ID（GPT5、Gemini2、Grok2、Claude6）の派生対応表を確認。原32 OPEN、旧8未裁定、CLD3-01 Major OPEN、旧20＋新12処分案は別集合。原32・旧8・CLD3-01・旧20＋新12の原報告全文と原ID・Severity・Status・Dispositionの全件対応は未取得。4AI保存物があることと、旧集合の完全性は別問題。正式Closeなし。

## 未取得資料と次工程提案

| Gap | 必要な資料 | 推奨取得主体 | 未解決時の扱い |
|---|---|---|---|
| G01 | CV05-N01～N03のOwner原メッセージ、選択肢を示した原質問、時刻・スレッド識別情報 | Owner／原チャット保有者 | RECEIPT ONLY維持 |
| G02 | D25/D22/D23/D24、O/GATE/COMP/R/6D原裁定、E-1/E-2承認原契約とID・版・適用範囲 | Owner／原記録保有者 | NOT VERIFIED維持 |
| G06 | 原32、旧8、CLD3-01、旧20＋新12の原Finding台帳・元AI報告・Owner処分記録 | Owner／保全担当 | 完全性未検証維持 |

**提案:** 原記録保有者から上記の最小資料を固定版・取得元・真正性区分付きで提供してもらい、別工程で一次照合する。提供不能の場合は代替証拠の採用可否と新規裁定の必要性をOwnerへ付議する。現時点で採用・裁定は行わない。

**STOP:** 調査結果と不足一覧の提出により停止。GitHub書込・原本変更・Termux追加実行・Owner裁定・Finding Close・正式承認・Freeze・HOLD解除なし。M19–M25／RP-023 HOLD継続。
