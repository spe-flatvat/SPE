# SPE M19-FR-CV-05｜新規規範裁定パケット DRAFT

**Status:** DRAFT / NOT APPROVED / NO OWNER ADJUDICATION
**Repository:** `spe-flatvat/SPE`
**Fixed candidate commit:** `a00c96252ee1260a909be8775511c420685b51d8`
**CV-02 preservation commit (authoritative):** `0e3860e6ed9276db9a07b5793066a6068b183660`
**Authority:** Owner requests a prospective normative choice with explicit evidentiary limits. This packet does not itself approve anything.

## 1. 証拠の階層

- **P1 原文:** 固定Commitの契約候補、条項・行、Git blob。Git blob SHAとファイルSHA-256は別物。
- **P2 未検証:** E-1 非裁量型の別途承認契約、E-2 2026切替候補の生成・利用・予約権限。未発見は不存在の証明ではない。
- **P3 Owner新裁定:** 旧裁定の存在を遡及的に認定せず、将来の規範方針として範囲・発効条件を明示。
- **P4 規範化:** 文案、CC-03/04/05/09/12、Gate A/C/B、29 invariants、既存Findingとの整合を別途検証。
- **P5 検証・承認:** 独立4AIレビュー、個別Finding処分、DecisionLog、正式Acceptance/Freezeは別工程。

## 2. 原文に基づく固定事項

- CC-03 L119: 非裁量型切替は別途承認済み契約を要する。
- CC-04 L138–152: 2026初期状態は承認済みBaseline Initial-State Contractを要する。L152は2026切替候補を許可しない。
- CC-12 L403: 予約前に切替先・年・帰属可能なTrigger/Decision証拠・競合予約を検証する。
- CC-09 L331–341: Freeze前の先行裁定照合、DecisionLog対応、個別Finding処分が必要。
- docs/DecisionLog.md（同固定Commit）: DL-001〜012はあるが、M19原裁定との対応は今回未確認。

## 3. 新規裁定候補 CV05-N01（O-1：Decision要否）

**推奨案A — 現行規範保全・将来例外は別契約:** 現在の標準切替予約経路はCC-03の裁量型条件およびCC-12のTrigger/Decision証拠検証を維持する。非裁量型のDecision省略は、この裁定だけでは許可しない。別途承認済み契約の識別子・版・適用範囲・Trigger/Decision相当の権限証拠・CC-12予約条件・Gate Bとの関係が明示され、必要な規範改訂と再レビューを終えるまで当該経路をfail-closedとする。既存の独立に正当なincumbent計算は不必要に停止しない。

**案B — 非裁量型例外を将来導入する方針承認:** 別契約の整備を許可するが、契約の正式承認、CC-12整合、テスト・レビューまでは実行許可を与えない。

**案C — 判断保留:** 追加原裁定探索を継続する。現行未検証状態を維持。

**裁定効果の限界:** A/Bいずれも旧裁定の存在や個別の非裁量型切替を遡及承認しない。契約候補自体の正式承認でもない。

## 4. 新規裁定候補 CV05-N02（O-2：CC-04の参照句）

**推奨案B（条件付き起案方針）:** `other applicable approved requirements` を無制限の例外根拠として扱わない。適用契約ID・版・承認証拠・優先順位・Decision適用性を特定できる表現へ限定する修文案の起案を許可する。実際の条文採用はN01の結果とCC-03/12との整合確認後、別承認とする。

**代替案A:** 現行文言維持＋外部台帳で不変参照。**代替案C:** 句削除（適用範囲の縮小リスクあり）。

## 5. 新規裁定候補 CV05-N03（O-3：2026候補）

**推奨案A — 証拠充足まで実行不可:** 2026初期状態の検証と、2026適用の政策切替候補の生成・利用・予約・効力発生を分離する。現時点では後者の権限証拠が未検証であり、CC-04 L152を許可根拠に用いない。別途承認済み契約または将来の明示的承認で、対象施策・生成者・適用年・Decision要否・予約条件・数値契約・Gate条件を特定しない限り依存切替はfail-closed。架空の2025最終状態を作らない。

**代替案B:** 新しい2026候補専用契約の起案を許可。ただし本裁定だけで予約・切替を許可しない。

## 6. レビュー耐性の検査条件

1. Owner裁定のID・日時・対象Commit・採用選択肢・理由・未検証事項・有効範囲を保存する。
2. 過去承認の推認・後付け認定をしない。新規裁定の効力は将来の起案・承認経路に限定する。
3. 規範改訂差分と承認証拠を一対一で追跡し、CC-03/04/05/09/12を横断検証する。
4. 32原Finding OPEN、8新Finding未裁定、CLD3-01 Major OPENを維持。関連付けはCloseを意味しない。
5. 4AI独立レビューの共通パケットに本裁定原文と証拠留保を同一条件で含める。
6. 29 invariantsと実装テストは未実施と記録し、後工程で検証する。
7. DecisionLog追記・GitHub書込・正式Acceptance/Freeze・M20–25/RP-023 HOLD解除は別承認。

## 7. Owner応答欄（未記入）

- CV05-N01: A / B / C / 修正指示
- CV05-N02: A / B / C / 修正指示
- CV05-N03: A / B / 修正指示
- 裁定理由、追加制約、発効条件: （Owner記入）

**STOP:** 本書は裁定要求の準備資料であり、Owner回答前に採用扱いにしない。まずCV05-N01から個別裁定を受ける。
