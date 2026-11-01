# SPE M19-FR-CV-08｜Stage C–F 限定証拠調査統合報告

**Status:** DRAFT / READ-ONLY / CONDITIONAL / STOP AFTER SUBMISSION  
**Repository:** `spe-flatvat/SPE`  
**参照固定Commit:** baseline `3e7c1814e2d31fd9373f58e4d88410d382abd8bb`; D `e195b9ecdc0e6930f44fce2b598e2c60887c92e4`; C `d1c13df4f18246e1b52f50640dece5477132beb5`; 探索用保全 `754c1e2907bce67f7d58d10bf36813ac76fd1ed0`。  
**証拠レベル:** GitHub連携による固定Commit本文読取とtree一覧確認。Stage BはOwner側Termuxログに基づく22/22 PASS。今回新規の実バイトSHA-256再計算はなし。

## Stage C｜G01 原会話とCV05-N01～N03対照

| Evidence ID | 固定資料 | 記載されたOwner応答 | 受領レシート上の結果 | 一次照合 | 判定 |
|---|---|---|---|---|---|
| G01-N01 | `M19_FR_CV_07/SPE_M19_FR_CV_05_N01_Owner_Decision_Receipt_20261031.md` | 「M19-FR-CV-05 CV05-N01のOwner裁定：案Aを採用します。追加理由・制約：レシート発出ください この裁定を原文として整理し、次の裁定項目へ進んでください。」 | 案A、現行Decision要件維持、将来例外は別承認 | 元会話未取得、案Aの元質問未取得 | RECEIPT ONLY |
| G01-N02 | `M19_FR_CV_07/SPE_M19_FR_CV_05_N02_Owner_Decision_Receipt_20261031.md` | 「M19-FR-CV-05 CV05-N02のOwner裁定：案Bを採用します。裁定レシートを発出し、次の裁定項目へ進んでください。」 | 案B、CC-04参照句の限定修文案起案のみ | 元会話未取得、案Bの元質問未取得 | RECEIPT ONLY |
| G01-N03 | `M19_FR_CV_07/SPE_M19_FR_CV_05_N03_Owner_Decision_Receipt_20261031.md` | 「M19-FR-CV-05 CV05-N03のOwner裁定：案Aを採用します。裁定レシートを発出し、CV05-N01〜N03の裁定結果を統合整理してください。」 | 案A、2026初期状態と切替認可を分離 | 元会話未取得、案Aの元質問未取得 | RECEIPT ONLY |

上記のファイル名は共通基準ディレクトリ `reviews/M19-25/` 以下の相対表記。各レシートの固定Cにおけるバイト数／SHA-256は順に `2525 / 6e8fa6a515c3c95642e6cbae7a42e14b1a3f9e74d974ebf640ad086cfe73049d`、`2515 / ac63247a04901364335189cb6ace5799846b7e577eeecb7f8a48ea13d02f5f0f`、`2667 / f7c183bed4fc395ee334dc96212cc40a3c0a0f12a55494c7e93a208900d2eab4`（Stage B提出ログ）。転記と統合記録は一致するが、原会話との文字列比較・時刻・スレッドIDの一次認証は不可。CONFLICTは観測されていないが、未照合を一致とみなさない。

## Stage D｜G02 歴史的裁定・E-1/E-2・DecisionLog

| Evidence ID | source / fixed revision | 発見事項 | 原本性・適用範囲 | 判定 |
|---|---|---|---|---|
| G02-DL | `docs/DecisionLog.md` at `754c1e29…` | v0.4、DL-001～DL-012。DL-010はAIレビューのOwner確認スナップショット等のガバナンス原則、DL-012はRP-022/M18財政モデルの限定裁定 | Canonical DecisionLog文書として読取。M19 CC-03/04/05/09/12のE-1/E-2承認根拠との対応は未成立 | NOT MATCHED TO TARGET PRIMARY |
| G02-D25 | CV05統合記録§3、6D35配布用転載 | D25とD22/D23/D24の照合必要性が記載 | 元Owner裁定本文・原スレッド未取得 | SECONDARY ONLY |
| G02-O/GATE/COMP/R/6D | CV05統合記録§3、Step 6D35転載 | 歴史的裁定系列の存在を示す参照表記 | 各原契約ID、承認者、適用年、操作、優先順位、実効版の一次照合未了 | NOT LOCATED WITHIN SCOPE |
| G02-E1 | CV05-N01レシート、CV07証拠不足台帳G02 | 非裁量型Decision省略を許可する別承認契約の所在未確認 | 契約ID・版・明示承認・Decision適用範囲は未検証 | NOT LOCATED WITHIN SCOPE |
| G02-E2 | CV05-N03レシート、CV07証拠不足台帳G02 | 2026切替候補の生成・利用・予約・効力発生の独立認可は未確認 | 2026通常初期化の許可は切替認可を意味しない | NOT LOCATED WITHIN SCOPE |

`Step_6D35_Owner_Provided_Audit_Transcript_DRAFT.md` は `reviews/M19-25/FG06-REREVIEW-3DEC-20261027-DRAFT-01/old_packet/inputs/` にある**配布用転載**であり、元会話の発言者・日時・原バイト未検証と自ら明記。一次裁定と扱わない。参照範囲は前掲の固定Commitツリー（`truncated=false`）および限定ファイル読取。探索対象外の場所・私的会話に存在しないことは証明しない。CC-03/04/05/09/12への歴史的承認の遡及認定は行わない。

## Stage E｜G06 Finding集合の分離と原ID追跡

| 集合 | 件数（資料上） | 取得した資料 | 原ID／Severity／Statusの完全性 | 判定 |
|---|---:|---|---|---|
| 原32 OPEN | 32 | CV05統合記録、CV07不足台帳・横断報告 | 32件の原ID、個別Severity、原報告全文を取得できず | MISSING ORIGINAL |
| 旧8未裁定 | 8 | 同上 | 8件の原ID・原報告・個別Disposition未取得 | MISSING ORIGINAL |
| CLD3-01 Major OPEN | 1 | CV05統合記録で存在言及 | 原Finding全文、版、原Statusの独立確認なし | DERIVED ONLY |
| 旧20＋新12の「32件処分案」 | 32（処分案、原32 OPENとは別） | CV08調査指示の区別規定 | 各原IDとの一対一対応・Owner正式処分未取得 | MISSING ORIGINAL |
| CV07新15件 | 15 | `M19_FR_CV_07/cross_verification/SPE_M19_FR_CV_07_Limited_Cross_Finding_Matrix_20261031.md`、4AI回答・保全レシート（固定C） | 15原ID、原Severity、原Statusの記載／未記載を派生Matrixで確認。原回答の保存物はStage BでSHA一致。ただし元AIサービス応答真正性は未検証 | DERIVED MAPPING WITH PRESERVED RESPONSE FILES |
| FG06 Rev4 4AI独立Finding | 20 | `FG06-REREVIEW-3DEC-20261027-DRAFT-01/references/FG06_4AI_CROSSWALK_DRAFT.md`（固定baseline） | GPT6-FG06-01～07、CLD-01～06、GEMINI-01、GRK-01～06の20原IDを派生表で確認。原32・旧8との同一性は未立証 | DERIVED ONLY; SEPARATE SET |

CV07新15件のIDは `CV07-GPT-01`～`05`、`CV07-GEM-01`～`02`、`GRK-CV07-01`～`02`、`CLD5-01`～`06`。原SeverityはGPT Minor3/Major2（条件付き表記を保持）、Gemini Editorial1/Minor1、Grok Editorial2、Claude Minor5/Editorial1。原StatusはGPT全体の暫定注記以外、個別Statusの未記載がある。これらの件数は別集合を足し引きしたものではない。FG06の20件も原32 OPENと同一集合であるとの主張はしない。

**G06完全性判定:** 原32 OPEN・旧8・CLD3-01・旧20＋新12について原IDごとの完全トレーサビリティ表は**作成不可**。未取得を創作IDで埋めない。原Severity/Status/Dispositionを変更しない。CV07新15件の派生対応表は確認できるが、これによって旧集合を正式Closeしない。

## Stage F｜不足・衝突・証拠レシート・終了

| Gap | 未解消事項 | 必要となる一次証拠 | Owner-required |
|---|---|---|---|
| G01 | CV05 N01/N02/N03のOwner原メッセージ・選択肢原質問・時刻・スレッド | 原会話を識別可能な一次記録 | 追加証拠の採用範囲判断のみ（今は裁定しない） |
| G02 | D25/D22/23/24、O、GATE、COMP、R、6Dの原裁定、E-1/E-2の原契約、DecisionLog対応 | 原文、承認証拠、契約ID/版、対象年・操作・優先順位 | 承認効力・例外採否はOwner留保 |
| G06 | 原32 OPEN・旧8・CLD3-01・旧20＋新12の全原IDと原Status | 原報告・原Finding台帳・Owner処分記録 | Findingの正式採否・CloseはOwner留保 |

**衝突検出:** 本調査で原文対原文の直接CONFLICTは判定できない。原本が欠落しているためであり、無矛盾の証明ではない。N01=A/N02=B/N03=Aは固定レシート間で整合。原32 OPENと旧20＋新12の32件処分案は同数でも別集合。

**取得・ハッシュの証拠階層:** 固定GitHub tree（`truncated=false`）・固定ファイル本文をGitHub連携で取得。Stage Bの固定C 22/22はOwner側Termuxログに基づく `PASS=22 FAIL=0 NOT_RETRIEVED=0`、今回のChatGPTによる再計算ではない。固定CのレシートSHAは上記G01に記録。Git blob SHA-1をSHA-256と混同しない。G02/G06の未取得原本についてハッシュを創作しない。

**総合判定:** `LIMITED INVESTIGATION COMPLETED / PRIMARY EVIDENCE GAPS REMAIN / CONDITIONAL / STOP`。Stage C/D/Eの指定範囲内の資料照合・不足の明示とStage F報告を完了。一次証拠の全件照合PASSではない。GitHub書込、原本変更、Owner裁定、Finding Close、正式承認、Freeze、HOLD解除、次工程自動開始は実施していない。**M19–M25／RP-023 HOLD継続。**
