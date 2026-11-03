# SPE M19｜GitHub保全の実施可否と推奨手順（DRAFT）

**Status:** DRAFT / READ-ONLY INVESTIGATION / NOT OWNER ADJUDICATION
**Repository:** `spe-flatvat/SPE`  
**基準日:** 2026-11-03 PM（JST）  
**調査記録:** 2026-11-03T14:05:07+09:00 ～ 2026-11-03T14:15:57+09:00。継続的な監視ではない。
**状態維持:** M19–25・RP-023のHOLDを維持。正式受入、Finding Close、Canonical化、Freeze、GitHub保全実行を行わない。

## 1. 非破壊確認の結果

| 項目 | 結果 | 意味・限界 |
| --- | --- | --- |
| 接続済みGitHub連携からの読取 | 確認済み | spe-flatvat/SPEの17 branches・固定commit/tree・9実ファイル・repo権限メタデータを取得。 |
| 接続ユーザー | spe-flatvat | 認証情報の値・トークン・秘密鍵は表示していない。 |
| 利用者のrepo権限 | push=true、pull=true、admin=true、maintain=true、triage=true／collaborator=admin | ユーザーの権限メタデータ。GitHub App／連携トークンの有効scopeと同一ではない。 |
| 連携インストール | spe-flatvatの選択リポジトリ型installationメタデータを読取 | SPEへの読取アクセス成功。ただしこの応答からcontents:write等を独立確定できない。 |
| 書込用インターフェース | create_branch、create_file、create_blob、create_tree、create_commit、update_ref、create_pull_requestの提示あり | 関数の提示は実行権限・実際の成功を保証しない。すべて未呼出し。 |
| 実書込み／push／PR | 未実行・成功未検証 | 読み取り専用指示のためdry-run含むGit push、実試験ブランチ作成はしない。 |
| main／既存branch更新 | 未実行 | mainとWORKは終了側の再読取でも初回と同じSHA。 |
| ruleset等 | 今回未検証 | branchesのprotected=falseだけで全制約なしと判断しない。 |
| 本工程での実施可否 | DRAFT準備済み／GitHub実行は別途Owner承認待ち | 環境として実行成功を保証しない。過去の403報告を現在の成功・恒久不能の根拠にも使わない。 |

## 2. Ownerが承認できる具体的な保全案

- **対象:** 保全対象一覧の優先19原本、必要な補助6原本、今回の新規5DRAFTと索引・SHA一覧。受入証拠ZIP内の既存3ファイルとの重複は索引で明示する。
- **新規ブランチ案:** `preservation/m19-pm-handoff-20261103`。今回の17ブランチ一覧にはない。実行時に再照会し、既存なら作成・更新を中止する。
- **親commit案:** `049f47309df8d4c09610a1ce47f68bdfc71f35f2`（既存M19統合改訂・監査保全の系譜）。main `13c24ae8beb917289691a52f45cdd0beaeda02f9` と異なる。どちらを親にするかはOwnerが明示指定し、今回勝手に選択して書込まない。
- **新規パス案:** `reviews/M19-25/M19_20261103_PM_handoff/`。元の`engine/`、`tests/`、規範、レビュー原本、DecisionLogを変更しない。対象一覧の原本バイトと新規DRAFTだけを追加する。
- **除外:** main・既存ブランチ更新、PR、merge、実装配備、承認状態更新、設定変更、権限追加・認証操作。必要になった場合は別途Owner判断。

本案は保全用であり、ZIPの中のコードをリポジトリの稼働コードへ展開する提案ではない。ZIP等のバイナリを正確に保存できない手段は使用せず、テキストAPIへ無理に再符号化しない。

## 3. 承認後に実施する推奨手順（本工程では未実行）

1. **承認の固定:** 対象一覧の版・SHA、対象原本、親commit、新規branch名、許可操作（新規branch／保全commitの作成のみ等）を一括明記する。既存の11/3レビュー準備承認をGitHub書込承認として流用しない。
2. **読み取り再検証:** repository、親commitの存在、branch名不存在、保存先パス不存在、現行HEADと承認基準の差を確認する。branchが存在／親不明／原本SHA不一致なら書込を止める。現在mainを自動追従して固定親を差し替えない。
3. **バイト確保:** 既存原本を再取得し、本索引のSHA・サイズと照合する。05BQ ZIP、Stage20候補、各レシートは内容を変えない。既存別名保全が見つかった場合は重複を報告し、無断削除しない。
4. **ローカル構成検査:** 追加対象だけのmanifestを作り、既存パス変更0、削除0、原本SHA維持を確認する。DRAFT、ISSUED、NOT ACCEPTED、HOLD等の元表示を保存する。必要なバイナリ転送をサポートする承認済み手段を選ぶ。
5. **限定書込み:** Ownerが指定した新規ブランチと新規保全commitだけを作成する。force更新・main更新・既存原本上書きはしない。GitHub連携とローカルGit認証が共用できると推測しない。利用可能な承認済み経路がない場合はSTOP。
6. **再読取検証:** 新commitの親・branch SHA・追加パス一覧・各Git blob・実バイトSHAを取得し、保全前値と比較する。main不変を再確認する。単なる作成成功応答で完全性PASSにしない。
7. **保全レシート:** 実行した操作・結果・commit・path・SHA・時刻・差異を新規記録し、Ownerへ提出してSTOPする。保全commit日時を過去の承認／試験日時に置き換えない。PR作成・次工程へ自動移行しない。

## 4. STOP・エラー時

403・認証不足、branch名競合、固定SHA不一致、バイナリ完全性を維持できない場合、意図しない既存変更が必要な場合は、その操作と影響範囲を報告して停止する。別書込経路への無断切替、権限追加、再認証、設定変更はしない。部分書込が発生した場合も無断削除・force修正で隠さず、成功分／失敗分を記録する。

## 5. 今回の実行実績

**GitHubへの書込み0件。** commit、push、PR、branch作成、update_ref、create_blob/tree、Owner裁定、DecisionLog更新は実施していない。認証情報・秘密鍵の内容は取得・表示していない。既存原本を変更せず新規DRAFTのみ作成した。

**結論:** 読取・準備は実施可能で完了。実保全はOwnerの別途承認および実書込権限・完全性の検証を要する。成功は未実証。成果物提出でSTOP。
