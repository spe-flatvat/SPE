# FG-06｜裁定追跡可能性・回帰リスク検証 DRAFT

- 状態：ローカル静的検証完了／独立レビュー未実施／Finding Closeなし
- 基準元SHA-256：`fce55ac833abb06085340e6bb903939c2121bc6387d07c4d04ddd23cfde6b848`
- 統合候補SHA-256：`4a3b475abb1281c7bf25b27bc23c0e67b3f0abd3e494222404f607d7c6cc16c1`
- パッチSHA-256：`1f6a8ab716d470f665b39ff24561cfcbc71f9dacf9fcd09a16033cb8e233f220`
- 検証対象：固定ZIPの3DEC候補（実バイトSHA一致）と今回作成した統合DRAFT。GitHub固定commitのテキスト読取確認あり。GitHub raw実バイトとの直接照合は未了。

## 実施検証

| 項目 | 判定 | 範囲 |
|---|---|---|
| CC01 prohibition | PASS | 文字列／構造の静的検査のみ |
| CC03 pending | PASS | 文字列／構造の静的検査のみ |
| CC04 2026 split | PASS | 文字列／構造の静的検査のみ |
| CC05 Gate B NOT_EVALUATED | PASS | 文字列／構造の静的検査のみ |
| CC08 all contract conditions | PASS | 文字列／構造の静的検査のみ |
| CC12 unissued reservation resolution | PASS | 文字列／構造の静的検査のみ |
| CC13 comparison operation | PASS | 文字列／構造の静的検査のみ |
| 29 invariants | PASS | 文字列／構造の静的検査のみ |
| 13 CC sections | PASS | 文字列／構造の静的検査のみ |


- CC-01〜CC-13の13セクションを保持。
- 将来V&V invariant 1〜29の連番と件数を保持。**実際の29件テストは未実施**。
- R-02に必要な2026初期状態／2027+前年確定状態の条件分岐をCC-04の該当1文に導入。CC-05 Gate Aの既存2026/2027+区分と一致。
- R-03〜R-07に関係する既存規範は本文無変更。R-01はヘッダの現行起案根拠と歴史的根拠の区別を追加。
- 変更はヘッダ3箇所およびCC-04の対象文1箇所。差分パッチを別添。

## 回帰リスクと未解決点

1. **R-02の「2026切替候補」自体の許容性**：本改稿は2026年切替を新たに許可せず、候補が別途適法に存在する場合のGate C参照状態だけを定義。Gate B・予約・政策数値契約は別途必要。
2. **CC-06の切替後アンカー再基準化**：CC-06の「actual preceding-year result」は原文維持。2026に有効な切替候補が存在する場合、CC-04の新しい初期状態例外との整合を次の独立レビューで検証する必要がある。機械的な一括置換は行わない。
3. **歴史的根拠**：原承認IDの直接証拠およびE-03/E-04はNOT VERIFIED。新Owner裁定を起案根拠としたが、過去承認の証明にはしていない。
4. **4AI Finding**：固定crosswalkに記録された20件の独立Findingについて、今回の静的確認は正式DispositionやCloseを意味しない。特にCC-04/05、CC-03 pending、CC-04/12年度末、CC-01/08の回帰、ヘッダ表示は再レビュー対象。
5. **本文整合の限界**：CC-01〜13の全組合せに対する形式検証、実エンジン試験、29 invariantテスト、全Findingの原回答再評価は未実施。
6. **証拠経路**：配布ZIP内の固定3DEC候補は実バイトSHA再計算一致。固定GitHubファイルのraw bytesとは別経路のため、同一性を未検証と明記。

## 既存Findingの保全対象（独立ID、未Close）

`GPT6-FG06-01`, `GPT6-FG06-02`, `GPT6-FG06-03`, `GPT6-FG06-04`, `GPT6-FG06-05`, `GPT6-FG06-06`, `GPT6-FG06-07`, `CLD-01`, `CLD-02`, `CLD-03`, `CLD-04`, `CLD-05`, `CLD-06`, `GEMINI-01`, `GRK-01`, `GRK-02`, `GRK-03`, `GRK-04`, `GRK-05`, `GRK-06`。

全20件を保全対象として列挙したもので、個別Findingの解消認定ではない。FG-06の他段階にある42件の別マッピング等とも同一視しない。

## 次のOwner判断点

- 統合DRAFTと差分を独立再レビューへ付議するか。
- CC-06の2026初期状態境界を独立Findingとして追加検討するか。
- 固定GitHub raw実バイトの同一性検証と原レビュー証拠の照合をどの段階で要求するか。
- 上記のいずれも自動承認・自動Freezeしない。
