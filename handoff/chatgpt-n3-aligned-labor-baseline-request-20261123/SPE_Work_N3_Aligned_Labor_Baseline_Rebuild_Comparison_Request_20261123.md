# SPE｜N3変更労働基底の整合再構築とSQ・F・N3同条件比較

**Status:** OWNER-AUTHORIZED REQUEST / ISOLATED IMPLEMENTATION / DRAFT NON-CANONICAL  
**Repository:** `spe-flatvat/SPE`  
**Target branch:** `work/chatgpt-handoff`  
**Date:** 2026-11-23  
**Execution years:** 2026–2055

## 1. 目的と位置づけ

先行する人口・労働統計接続の実行成果を再利用し、未計算のN3変更枝を整合した基底で実行する。目標は、共通の労働投入条件でSQ・F・N3の年次結果を比較できるようにすること。これは既存の統計接続作業の次段階であり、運用障害のレビュー、正式採用、政策改訂ではない。

本書のOwnerによるWorkへの発出をもって、指定隔離ディレクトリでのコード・入力・年次成果の生成、実行、検証、および`work/chatgpt-handoff`への個別ファイル格納を承認する。

## 2. 固定参照・再利用

- 直近の人口・労働接続成果：`21de7c095b500575934f7c098d5bc6f183cc6710`、`handoff/chatgpt-labor-timing-older-workers-annual-hours-20261123/`。169個別原本、実行コード、Manifest、検証記録を優先再利用。先行Workの169/169事後照合・合計22,212,073 bytesは先行検証として区別。
- 直近依頼書：`8a117759906f0d89c8a57e0899c03e3697be70a1`。
- 前段全国統計接続：`78858034a8659fb21d01421168de6be0173ff0c5`。
- 既存SQ/F/N3三施策比較：`e981c924adbe9c7ca77b96d2dc94e40378186613`。
- 既存人口・労働診断：`9dcf953e949593e773bab906eb72577f0efec73e`。

最初に先行報告書、`Remaining_Statistics_Gaps_And_Next_Executable_Fixes.csv`、N3依存分析JSON、隔離再現コード、実行済みSQ9枝・F6対照・N3現行1枝を確認する。取得済み原本を不要に再収集・再計算しない。受領側が必要な原本同一性は自ら確認し、先行Workの自己検証と区別する。

## 3. 今回の実装範囲

1. **基底依存の特定：** 既存N3 Runnerの`base/sq`参照、医療初期化、賃金初期値、前年GDP参照、税・年金・価格・財政連鎖を、先行依存分析と実コードに照らして特定する。新たな包括的監査や政策改訂はしない。
2. **隔離した整合基底再構築：** 先行で実行済みの労働条件枝を入力として、対応SQの基底traceとN3政策計算が読む基底・キャッシュ・初期化を一貫して再生成する。SQのGDP差をN3最終GDPへ単純加算する方法は禁止。部分的な参照差替えだけで「整合」と判定しない。
3. **年次実行：** 2026〜2055年のN3変更枝を実行。優先対象は`BASE_SQ_UNCHANGED`、`PREVIOUS_FINE_AGE_HOURS`、`ANNUAL_ALIGNED_FULL_RATES`、`OCTOBER_NEAR_FULL_RATES`、`ANNUAL_FINE_WEEK_HOURS`、`ANNUAL_MONTH_HOURS_PROFILE`に対応するSQ/F/N3同条件比較。既存枝名との対応を固定し、未実行の枝は理由付きN/Aとする。
4. **二重計上・状態整合：** N3既存の政策・税・医療・価格・財政計算を維持し、変更した労働基底の効果を重複加算しない。共通2026初期条件、L/L0、29遷移、A、既存イベント、政策スイッチ、追加政府G/Iの既存設定を無断変更しない。
5. **比較：** SQ・F・N3について同じ労働条件の2026〜2055年次、2026/2030/2035/2039/2055主要年、2055実質GDP、現行との差、F−SQ・N3−SQ、財政・税・医療の整合指標を実値で比較。比較不能な指標はN/Aとし、結果を推測しない。

## 4. 実行・検証の条件

- 既存N3現行30年の再現（2055実質GDP 483.991492兆円）、既存SQ/Fの固定結果、2026基準年、政策スイッチ、財政・税・医療初期化、参照の一貫性、年次収支・単位、L/L0正規化を検査する。
- 新規N3変更枝では、各年のN3計算が対応する変更SQ基底と同じ版・同じ労働条件を参照することをコードと実行traceで検証する。旧基底参照が残る場合は当該枝をPASSにしない。
- 既存検証5,265件、N3現行748件、Claude既存2,845件を新規検証件数に加算しない。今回の検証件数・不一致・対象を別記する。
- N3の完全な整合基底を今回の隔離実装で構築できない場合は、実行済みのSQ/F比較を維持し、N3変更枝をN/Aとする。未達の依存箇所・具体的技術制約と、最小の次実装箇所を提示する。成功を装う代替計算はしない。

## 5. 成果物・引渡し

**新規格納先：** `handoff/chatgpt-n3-aligned-labor-baseline-20261123/`、branch `work/chatgpt-handoff`。

個別Markdown・CSV・JSON・Pythonを原本とし、ZIPは生成・配布しない。最低限以下を格納する。

- `SPE_N3_Aligned_Labor_Baseline_Comparison_Report_DRAFT_20261123.md`：前回から増えた実行能力、結果、SQ/F/N3比較、残課題。
- `N3_Baseline_Reference_And_Rebuild_Map.csv`：旧参照、変更基底、依存箇所、再生成・検証結果。
- `SQ_F_N3_Aligned_Labor_Annual_2026_2055.csv`：全30年・実行可能な全対照枝。
- `SQ_F_N3_Aligned_Labor_Key_Years.csv`：主要年比較。
- `N3_Changed_Baseline_Validation.json`：新規検証・不一致・対象・N/A理由。
- 隔離再現コード、入力・実行trace、Manifest、再生成照合、GitHub事後取得の保全記録。

生成・実行・検証・GitHub格納・固定Commit事後取得・CUSTODY PASSを別々に報告する。CUSTODY PASSは原本格納後、固定Commitから取得した実バイトSHA-256・サイズと回収原本の一致を確認した場合のみ宣言する。大容量一括格納に問題があれば、原本同一性を維持して分割格納する。

## 6. 境界と禁止事項

今回の対象は**N3変更労働基底の整合再構築**に限定する。年齢別の実測年間時間の新規探索、外国人固有率の創作、F追加政策コホートの完全FTE再設計、N3全政策再設計、人口2025年国勢調査基準への全面切替は含めない。これらの残課題は維持し、既存枝へ黙って混入しない。

main、既存共通エンジン、政策原文、固定成果は変更しない。正式Acceptance、PR、merge、DecisionLog更新、Finding Close、Canonical化、Freeze、HOLD解除は行わない。RP-023／M19–25 HOLD、RP-024 PENDINGを維持する。

原本取得不能や実行不能は具体的制約と影響範囲を限定し、実行できる部分を継続する。Ownerへの既存資料再提出要求、追加レビュー、管理文書の増殖は行わない。