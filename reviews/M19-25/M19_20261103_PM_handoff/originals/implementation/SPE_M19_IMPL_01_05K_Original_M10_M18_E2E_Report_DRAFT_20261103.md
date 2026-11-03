# SPE M19-IMPL-01-05K｜固定M10 CLI／M18原本一気通貫回帰報告（DRAFT）

**Status:** DEVELOPMENT VERIFICATION PASS / FORMAL ACCEPTANCE NOT AUTHORIZED

## 1. 固定条件・権限

- Repository: `spe-flatvat/SPE`
- Fixed commit: `13c24ae8beb917289691a52f45cdd0beaeda02f9`
- Owner承認: M19-IMPL-01-03 Option A（Slice A限定実装・fixture検証）
- GitHub書込み・正式稼働・Finding Close・Freeze・HOLD解除は実施していない。

## 2. 原本取得・同一性

GitHub連携で固定コミットの原文を読み取り、ローカルに再構成。Git blob形式 `SHA1("blob " + length + NUL + content)` で照合した。

| 原本ファイル | Git blob SHA-1 | 結果 |
|---|---|---|
| engine/m10_results.py | f87d09ae6be51986aea984da4e52a167497b9d9e | PASS |
| engine/prototype.py | 71706c7d7d900cdffabd893aed8b9f82e6c5657f | PASS |
| engine/m13_input_validate.py | d31de0aa278e2c71afbceb5cac1830d76e203619 | PASS |
| engine/m14_wage_anchor.py | d98bef72dc763947073970fd0ff9da0dcd7e867c | PASS |
| engine/m17_gini_anchor.py | 6615cfbbb59935625dfe4a32a71dfb443c49f2b4 | PASS |
| scenarios/m8_baseline.json | 0c43c8ba032ed818796bb135bd8bdb2a38267da7 | PASS |
| engine/m18_evaluate.py | d9455f6150dd37e05af2e78cde175bec0d4cbc7e | PASS |
| engine/m12_validate.py | aa48e4014f6935c1810bf0fd67d3fdb67f7abda5 | PASS |
| engine/m16_result_validate.py | a948990ab9b09d79dfd0a72f7082eb37ecdcba70 | PASS |
| engine/m17_result_validate.py | da35ab1c857582894fa50129074e2b904a263e0c | PASS |

## 3. 実行回帰

`python reference/engine/m10_results.py` をsubprocess実行。原本の `m8_baseline.json` を入力し、2026～2029のJSON全体（schema_version、scenario、profile、全年度・全フィールド）をSlice A開発用アダプターと厳密一致で比較しPASS。

原本M10 CLI JSONを原本M18 `evaluate_result()` に直接渡し、開始2026／終了2029／2055 endpoint=false、GDP endpoint、国債発行endpointを検証しPASS。改ざんしたbonds値をM18原本が拒否することも確認。

追加でwage/gini anchorsを含む開発用シナリオをM10原本CLIに与え、m17.1出力と原本M18評価を実行しPASS（アンカー数値はfixtureであり政策仮定ではない）。

**全テスト：58/58 PASS**（05Jの53件＋05Kの5件）。

## 4. 受入条件の扱い

- **SA-08:** 固定M10原本CLIの基準シナリオ実行回帰 PASS。全シナリオ・全契約の網羅を意味しない。
- **SA-09:** 原本M10→原本M18（M12/M16/M17原本依存）の基準シナリオ一気通貫回帰 PASS。開発用fixture範囲。
- **未完了:** Gate A/C/B正式契約検証、2026初期状態の承認済み契約照合、並列ワーカーの排他的所有・リース、正式な比較適格性・証拠契約、IMPL-01-06正式受入。
- 2026初期値およびm8_baselineは既存M10の暫定値であり、SPEの正式政策値ではない。

## 5. 工程・Ownerアクション

- 工程：IMPL-01-05K DRAFT／開発検証PASS。正式受入未準備。
- **Ownerアクション：不要。**
- **継続可否：可能。**
- 区切り理由：チャット実行上の区切り。Owner裁定待ちではない。
- 次の作業：正式契約の所在・条件を原文で照合し、承認済み範囲のfail-closed実装／テストを進める。規範変更や正式稼働には別途Owner裁定が必要。
