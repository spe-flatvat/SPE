# SPE M19-IMPL-01 Slice A｜受入収束パケット（DRAFT）

**状態：SUBMITTED FOR OWNER REVIEW / NOT ACCEPTED**  
**対象：05BQ Local DRAFT（固定入力ZIP SHA-256: `5d65d9df18d3ab12863cf6b7cbbec08c7055ef0c0a3a8cd5b72ee506b7d17b12`）**  
**権限：ローカル読取・検証・新規DRAFTのみ。GitHub書込みなし。M19–25／RP-023 HOLD維持。**

## 1. 結論（受入判断のための整理）

- **ローカル実装・回帰検証：PASS。** 05BQの入力ZIPを展開して再実行した `PYTHONWARNINGS=error::ResourceWarning python -m unittest discover -s tests -q` は **191 tests / OK / 30.957秒 / exit 0**。証拠ログSHA-256: `8084d43b06f4682f8275355e401651a9efc4019fccb7f7026816a42e8bd6272d`。
- **正式なControl Contract適合性：未判定。** このパケットには固定版Control Contractの原文・逐条マッピング・正式Owner裁定証拠が揃っていない。実装テストPASSを契約適合PASSに読み替えない。
- **正式受入：未実施。** 本パケットは技術的な受入判断を可能にするための証拠整理であり、HOLD解除・Freeze・canonical更新・正式Closeを含まない。

## 2. 受入対象の境界

対象はSQLiteベースのM19 Slice AローカルDRAFT。通常のPython実行入口は `engine/m19_execution_api.py::execute_year` → `engine/m19_strict_entry.py::run_year_strict` → `engine/m19_guarded_runner.py::run_year_bound`。`run_year_strict` は `(owner_id, generation)` のfenceを検証し、後続のfenced更新へ委譲する。lease操作は `engine/m19_worker_lease.py` に実装。

**対象外**：本番配備、外部Owner承認の真正性認証、改変コードからの直接fixture API呼出しの防止、複数ホスト／分散DBでの線形化保証、固定Control Contractの逐条適合認証。`README.md` は旧05AR表記のままで、現行の検証状況を反映していない（文書整備課題）。

## 3. 証拠一覧と受入チェック

| 受入観点 | 証拠・確認結果 | 判定 |
|---|---|---|
| 全件回帰 | 今回実測191/191 PASS、exit 0 | PASS（ローカル） |
| リソース警告 | `ResourceWarning` エラー化で191/191 PASS | PASS（今回条件） |
| テスト重複 | 05BQ報告：191件／ユニーク191件 | 先行報告を採用（今回再収集集計なし） |
| strict fence入口 | `run_year_strict` がfence形式を検査し、トランザクション内で照合 | コード確認＋回帰PASS |
| lease異常系 | 05BQ報告：旧owner release、不正TTL、旧generationを拒否 | 先行テストPASS、今回全件回帰に包含 |
| 実プロセス異常系 | 05BM–05BO報告：強制終了時rollback、lease競合、PENDING回復など | 先行テストPASS、今回全件回帰に包含 |
| 外部承認真正性 | `m19_guarded_runner.py` にfixture-onlyの参照照合、認証なしと明記 | 未充足／対象外 |
| Control Contract逐条適合 | 固定契約本文との照合未実施 | **OPEN** |
| 年度確定処理中のOS強制停止 | 既存試験はSQLite rollback等。年度確定内部の全停止点を網羅していない | **OPEN（残余リスク）** |
| 複数ホスト競合 | SQLite単一ローカルfixtureの範囲外 | **OPEN（対象外）** |

## 4. 受入に直結する残余リスク

**R1 / 契約適合証拠の不足（受入ブロッカー）**：固定Control Contract原文と各規範条項の対応表、Owner承認証跡を照合していない。最終受入前に、固定版と照合して「適合／未適合／非適用／未確認」を分類する。これは実装に新しい要求を無制限に追加するための工程ではない。

**R2 / 実装境界の制約（スコープ明示で管理）**：通常APIはstrictだが、fixture/legacy APIはPythonから直接import可能。コード改変や悪意ある呼出しに対する安全境界ではない。Slice Aの受入対象をローカル開発fixtureに限定する場合は制約として記録し、production安全性を主張しない。

**R3 / 強制停止の網羅性（条件付き残余リスク）**：プロセス強制終了時のSQLite rollbackは先行試験で確認。ただし、年度確定中の全ステップに対するkill point網羅や分散競合は未検証。受入範囲が単一ホストSQLite fixtureであることを明記する。

**R4 / 文書整合性（非ブロッカー候補）**：READMEが05AR時点のまま。受入時にはパケットを最新の検証状態の根拠とし、後続文書更新を課題登録する。

## 5. 受入判断案（Owner裁定を最小化）

- **技術的検証の収束**：今回の191/191 PASSをSlice AローカルDRAFTの回帰基準として採用可能。新規テストを無期限に追加することは推奨しない。
- **正式受入判定**：現段階では **PENDING（契約適合の証拠不足）**。R1を照合し、R2/R3の適用範囲を明記した上で一括判定する。
- **Ownerに必要な判断は最終段階の一括裁定のみ**：受入対象をローカルSlice A fixtureに限定するか、本番安全境界まで含めるか、および残余リスクを許容するか。ここで事前承認を要求して開発・検証を停止しない。

## 6. 完了までの最短ルート

1. 固定Control Contract本文とOwner裁定原記録を取得し、要求事項と実装・試験の対応を**一括で**作成する。
2. 重大な未適合のみ是正または受入範囲から除外する。軽微な文書整備は後続課題にする。
3. 同一固定版に対する最終回帰を一度実行し、Ownerへ**一回の受入判定パケット**として提示する。

**STOP条件**：現時点では外部規範原文の未照合が正式受入の制約。これはローカル技術検証の停止理由ではなく、正式判定に必要な証拠の欠落である。

## 7. 証拠の出所・限界

このパケットはユーザー提供の05BQローカルZIPと、過去工程の報告内容を基礎とする。今回新規に実行したのは警告検査付き191件の全件回帰および実装コードの読取確認。先行工程の個別テスト結果は先行報告として区別し、今回独立にすべての異常系条件を再構築したとは主張しない。
