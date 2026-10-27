# SPE M19–25｜Rev.4 Independent Review Manifest DRAFT
工程ID：FG-06／工程名：Rev.4 Independent Review Packet Preparation  
作成日：2026-10-25（日本時間）  
パケットID：SPE-M19-25-REV4-FG06-20261025-DRAFT-01  
状態：DRAFT／NON-CANONICAL／配布未承認・未実施

## 1. 唯一のレビュー対象
`inputs/M19_Control_Contract_v0.4_DRAFT_Rev4_EDITORIAL_CANDIDATE.md`  
SHA-256：`d1b6e64caead960972f0e8c2b2edebb24deb36522cc41d65947ff0580a1bd04e`  
Version：ファイル本文のRev.4 Candidate。別のRev.4_CANDIDATE/Rev.3は代用しない。
原本冒頭NOT REVIEW-ACCEPTEDは固定時点の記述として保持した。後続OD-12は下記の限定状態として別記する。

## 2. 入力資料・ハッシュ
| パス | bytes | 行数 | SHA-256 | 出典・検証 |
|---|---:|---:|---|---|
| inputs/M19_Control_Contract_v0.4_DRAFT_Rev4_EDITORIAL_CANDIDATE.md | 37939 | 531 | `d1b6e64caead960972f0e8c2b2edebb24deb36522cc41d65947ff0580a1bd04e` | 今回添付の実ファイルを無変更コピー。固定SHA一致 |
| inputs/M19_Control_Contract_v0.4_DRAFT_Rev2.md | 28034 | 183 | `6a55197c1e530fbbcd222f859107573c04326254c1dfb6524b7ab001d7b58cea` | 前工程のLibrary全文取得テキスト。Library ID libfile_3c05bb3cfbd081919ffff1e2f9439201、version 4（文書Rev.4の意味ではない）。元添付失敗とは区別 |
| inputs/SPE_M19_25_FG05_Rev2_Rev4_Independent_Audit_20261025.md | 38515 | 362 | `d3cc9aa36577cefcdfa6c049ccbb6d4a0d90b5d5b288aac3cf2cd18bf65c5099` | 前工程で生成・保存したFG-05報告書の無変更コピー。既知SHA一致 |
| inputs/Step_6D35_Owner_Provided_Audit_Transcript_DRAFT.md | 9689 | 183 | `55ab7ad1b9f7edac54685eadc4a546525a2eccb65af9564575b79c6fbc7837ed` | 今回会話でOwner提供のStep 6D-35本文を配布用全文転記。元メッセージの日時/リンク/バイト未検証 |
| references/docs/Workflow.md | 3402 | 62 | `b9727a775f8d0d25a7b5fc57bd4c74a8df289f92666ed6d8bd889bc084559e14` | GitHub連携GET、基準SHA指定。返却テキストのGit blob 9293cbfce3532cc815c20ef20c4bd76377dd8598 がツリーと一致 |
| references/docs/DecisionLog.md | 7691 | 114 | `a9863a6c3b5b5bf32aa1de6e328c6f6ad7e007bbda4ffd35bfd8af63788f0ae1` | GitHub連携GET、基準SHA指定。返却テキストのGit blob 9d1fdbe86567be56c19be051262f92746a984704 がツリーと一致 |

行数はバイト列をsplitlines()した数。SHA-256はhashlib.sha256(read_bytes())で計算。Rev.4とFG-05は前工程の既知SHAとも照合。Git blob確認はSHA-1(blobヘッダ+取得バイト列)を取得ツリー値と照合したもので、Owner承認の証明ではない。元ファイルへの書込みは行っていない。

Rev.2は取得テキストから固定された内容。Step 6D-35は提供全文の配布用転記。これらの配布ファイルハッシュと原添付/原チャットのバイト同一性は区別する。
ZIPに含まれる同梱入力が評価の基準であり、Library内部のversion番号を文書Rev.番号へ読み替えない。

## 3. 取得経路と版の固定
- GitHub連携GETで取得時mainを観測：`8e46e5b8af6f2c5936d3d166d1b8c69680713d72`。
- 候補本文がOwner-confirmedと記載するreview baseline：`e2238922193107f204805d9f25d6ddd6f764eced`。
- 両SHA指定の再帰ツリーはtruncated=false。Workflow/DecisionLogのblobは両方で同一だった。
- references/docsの2ファイルは後者の基準SHAをURLに明示して取得。今回のスナップショットをOwnerが配布用基準として再確認した原発言は未取得。
- 技術的に取得できたことはOwner-confirmed snapshotを成立させない。今回の基準確認はDistribution Checklistに留保する。
- 取得時mainをレビューbaselineへ自動変更しない。SHAの新旧・最新性はこの取得応答の範囲で扱い、別の未取得履歴を推定しない。

### 取得した参照URL
- [Workflow（固定基準）](https://github.com/spe-flatvat/SPE/blob/e2238922193107f204805d9f25d6ddd6f764eced/docs/Workflow.md)
- [DecisionLog（固定基準）](https://github.com/spe-flatvat/SPE/blob/e2238922193107f204805d9f25d6ddd6f764eced/docs/DecisionLog.md)
- 取得APIは上記同一pathにref=e2238922193107f204805d9f25d6ddd6f764ecedを指定したGitHub連携のfetch。公開Web検索・直接curl取得へ切替えていない。

### 任意資料の取得結果
| 任意資料 | 取得結果 |
|---|---|
| M19_25_Rev2_Finding_Closure_Register.md | 指定2スナップショットの全ツリーに該当名なし。reviews/M19-25/同名パスの履歴APIは空配列。未取得。 |
| M19_25_Evidence_Decision_Correspondence_DRAFT.md | 同上。未取得。 |
| M19_25_Review_Manifest.md | 同上。未取得。別経路の既存Manifestを代用しない。 |
| D22/D23/D24/D25/6D38等のOwner裁定原記録 | 指定2スナップショットの取得ツリーとDecisionLog本文から原裁定は回収できず。別パス・別ブランチ・過去チャット・未同期履歴における有無は未判定。 |

任意参照3台帳とOwner裁定原記録はGitHub連携で回収を試みたが今回未取得。検索した範囲は固定基準 e2238922193107f204805d9f25d6ddd6f764eced と取得時main 8e46e5b8af6f2c5936d3d166d1b8c69680713d72 の非省略再帰ツリー、および reviews/M19-25/ 配下の3既知ファイル名に対する履歴API。履歴応答は各空配列。全履歴・全ブランチの不存在証明ではない。
docs/Workflow.mdとdocs/DecisionLog.mdは基準SHAを指定して連携GETし、保存テキストのGit blob SHA-1が取得ツリー記載と一致した。取得したDecisionLog本文ではD22/D23/D24/D25/6D38等の指定IDは検出されなかったが、歴史的原裁定の不存在は意味しない。
旧Manifestを今回のRev.4固定候補の証明として同梱・採用していない。原裁定IDの不検出を原裁定不存在や未承認へ変換しない。

## 4. 現在の承認・監査状態
- OD-12：Rev.4固定候補に対する条件付きReview Acceptance。対象はRev.2四AIレビュー18件の規範上の処理に限定。全仕様・歴史的証拠の全面承認へ拡張しない。
- Step 6D-35の5件：FG-05では規範対応5/5 PASS。ただしこれは先行監査の判断であり、今回のレビューアーを拘束しない。正式Finding Closeではない。
- E-03／E-04：未検証。
- Owner裁定の原記録：完全照合未了。未回収を直ちに未承認・不存在と判定しない。
- DecisionLog対応：正式Freeze前の確認事項。
- Rev.4：DRAFT／NON-CANONICAL。Canonical化・Freeze：未承認。
- 原本冒頭の NOT REVIEW-ACCEPTED は固定時点の記述として保存し、後続OD-12条件付き受理と別管理する。

## 5. 4成果物と配布構成
| Artifact | ファイル | bytes | 行数 | SHA-256 |
|---|---|---:|---:|---|
| B | M19_25_Rev4_Common_Review_Packet_DRAFT.md | 8806 | 77 | `b7eac2a3a798aaae8e0fe5bac6bf2db73adeb23e7a6e733c8b0d757d0ea2cd98` |
| C | M19_25_Rev4_Common_Review_Request_DRAFT.md | 8377 | 81 | `55acd8cdbdf162f754e24f1d519d15f758692bd858d601d8b94f6594811d9c23` |
| D | M19_25_Rev4_Distribution_Checklist_DRAFT.md | 4305 | 54 | `d8d7a83767f4550aead695c985180c01597cb249660746ecb36fa13f58f1b5eb` |

Artifact A（本Manifest）の自身のサイズ/行数/SHAは自己参照循環を避け、別ファイルFG06_Artifact_Inventory.tsvとSHA256SUMS.txt、および作成完了報告に記録する。checksumファイル自身とZIP自身はその内部チェックサム一覧に含めない。ZIP自身のSHAは外部の作成完了報告で照合する。

ZIP構成：4成果物、inputs/の必須4資料、references/docs/の2参照、SHA256SUMS.txt、FG06_Artifact_Inventory.tsv。内部作業記録・転送helper・他AI今回回答は含めない。
Markdown内リンクはZIPを展開した同じディレクトリ構造で解決する。個別ダウンロードした4成果物だけでは必須添付は揃わない。配布はZIP一式が基本。

## 6. レビュー権限境界・独立性
本資料は新規DRAFTのレビュー準備資料であり、レビュー送付、正式Review Acceptance、Finding Close、DecisionLog更新、GitHub書き込み、commit/push/PR、Canonical化、Freezeを承認しない。Ownerが最終判断する。今回の条件付き移行判定はこれらの権限を代替しない。
FG-05は既存監査資料であり優越性を持たない。初期レビューで他AI今回回答を相互に見せない。モデル固有の評価誘導や既定結論は設けない。各Finding IDを保存し統合は別工程。
レビュー回答4値は候補品質の評価であり、Workflowの正式登録はOwnerが別途扱う。固定候補のヘッダやDecisionLogを書き換える依頼ではない。

## 7. 未検証・Owner確認待ち
- 今回の配布セットに対するOwner確認と配布承認。
- 対象repository baselineの今回レビュー用確認。
- Owner原裁定完全照合、任意3台帳、E-03/E-04、DecisionLogとの裁定別対応。
- Step 6D-35元チャットの発言者/日時/原リンクと元バイト同一性。
- 各AIが同じ入力を実際に受領・読取・SHA計算できるか。
- FG05-N01〜N05の独立評価、実装V&V、最終裁定、正式Close/Canonical化/Freeze。

## 8. 作成者の完了判定
FG-06はパケット作成・同一性検証に限りCOMPLETE。任意参照の未取得は明示した。
他AIレビュー開始可否はCONDITIONAL READY：Ownerが候補/基準/セットを確認し配布承認した後、同一入力で開始する。今この文書を作成したことを送付・レビュー開始・正式受理と扱わない。
