# SPE｜N3 79ケース限定独立検算 Claude実行依頼書

**Status:** OWNER-DIRECTED / LIMITED INDEPENDENT CALCULATION / DRAFT / NON-CANONICAL  
**Date:** 2026-11-21  
**Repository:** `spe-flatvat/SPE`  
**Reviewer:** Claude  
**Input fixed commit:** `556953292e24615cee47d92bb27e85badf12329c`  
**Input directory:** `handoff/chatgpt-n3-gap-closure-20261121/`  
**Output branch:** `work/claude-handoff`  
**Output directory (new):** `handoff/claude-n3-gap-independent-verification-20261121/`

## 1. 目的・作業権限

ChatGPT Workが実装・実行したN3拡張79ケース×2026–2055年＝2,370年次行について、**Claude自身の独立再実行・主要計算経路の別実装検算・差分の原因特定**を行う。既存のWork PASSは入力側の自己検査として扱い、Claudeの独立PASSに読み替えない。全行を漫然と再レビューするのではなく、今回新規33ケースと新規経路を優先する。

対象原本の取得、読み取り、ローカル再実行、独立検算コード/CSV/報告の生成、指定Claude側handoffブランチの**新規ディレクトリへの個別ファイル格納**をOwnerが承認する。入力固定版・既存原本・政策原文・他ブランチの改変、merge、正式Acceptance、Finding Close、DecisionLog更新、Freeze、Canonical化は禁止。RP-023/M19–25 HOLD、RP-024 PENDINGを維持。追加のレビュー制度・Owner開始承認を設けない。

**完了条件:** 固定入力の取得と必要な原本同一性確認、実コード実行、重要な新接続の独立計算、差分評価、Claude側GitHub成果引渡し。報告書作成だけでは完了としない。

## 2. 入力・取得と既存PASSの再利用

1. **主対象:** Commit `556953292e24615cee47d92bb27e85badf12329c`、`handoff/chatgpt-n3-gap-closure-20261121/`。最初に `README.md`, `Report.md`, `Research_and_Boundaries.md`, `Dependency_Pins.json`, `Gap_Model.py`, `Gap_Components.py`, `Gap_Inputs.json`, `Reproduce.py`, `Gap_Annual.csv`, `SQ_F_N3_Comparison.csv`, `VAT_Price_Quantity_Income.csv`, `Partial_Fiscal_Financing.csv`, `Gap_Foreign_Bridge.csv`, `Gap_Semi_Medical.csv`, `Checks.json`, `Delivery_Verification.json` を確認。追加の依存ファイルはREADME/Manifestから自己回収。
2. **前工程46ケース:** Commit `444a34e5349099482c0e51f9ccf9efef199a652b`、`handoff/chatgpt-n3-model-expansion-20261121/`。前工程の旧46ケース回帰一致を、同じ入力・同じ出力列に限って再利用・限定確認。
3. **共通F/SQ基盤:** Commit `ff6210061615105de9a0d64767c256796be80ed2`、`handoff/f-common-endoflife-finalization-20261121/`。Claudeの同一版検算Commit `4924c8e4be45e1f0b66013ef4aa87d139ff7c7b5` は同じ固定対象のみ既存PASSを再利用。
4. **政策原文:** Commit `5804388482864af08204ba0d0e76a46206dacdbd`、`policies/New3linesPolicies.md`。政策値の採否を裁定せず、原文値・未裁定感度・OPENを区別。
5. Workの`Delivery_Verification.json`は「39成果原本＋Manifest」の自己申告記録。Claudeは**自分が実際に取得した固定原本**のSHA-256・サイズを確認し、Workの照合を自己検証と呼ばない。大量ファイルの検証は分割可。取得できた部分は維持し、限定STOPで他の検算を進める。

## 3. 独立検算の優先順位

### A. VAT数量→実消費→GDP（最優先）

同じ価格転嫁率0.8で弾力性0/0.25/0.75を比較。報告の2055実質GDP `526.234068 / 523.596278 / 518.464138` 兆円を再現し、独立に価格比、数量 `q=clip(p^(-elasticity),0.7,1.3)`、市場別旧税込基準価格消費差、Ctargetへの置換、domestic_share/デフレータ/平滑化/供給上限/所得feedback/税反応を計算。旧価格便益の二重計上、売上減のGDP再加算、VAT税額の二重計上、非家計・医療非課税の混入を確認。数量弾力性を変えたときGDPが動く**計算経路**と結果の経済解釈を区別。特にゼロ弾力性の意味と旧価格モデルとの比較条件を確認。

### B. 部分財政・国債・保険勘定

既存医療純金融源を除いた追加政府未配賦、候補利率0/2/4%、借入・償還・利払・資産の年次恒等式を独立計算。税80兆アンカーの国/地方/SI境界、全国債務初期値、全国償還・保険者残高が欠落しているため**全国PB・全国債務はnullのまま**であることを確認。残余勘定の初期値0を全国債務0と誤認していないか、政策税/VAT/医療財源の二重計上がないか確認。PARTIAL_CLOSUREの範囲を明示。

### C. フラット税・相続贈与・所得源泉感度

`FLAT_HH_SURVEY` の2055 SQ比GDP差約−34.609662兆円、`FLAT_SOURCE_LOW_LABOUR` 約−23.554667兆円、政策税差代理110.345869→75.099265兆円を独立に検算し、課税ベース・世帯/個人・源泉仮定とマクロ反応の寄与を区別。相続申告課税価格23.3846兆円/旧税3.2446兆円、贈与課税価格2.6761兆円/旧税0.3178兆円の固定入力と40%との差額、2026基準への近似、MPC候補を確認。全国控除廃止後の税源と誤認しない。EITC基準はOPEN維持。

### D. 外国人材・半官営保険・年金相手方

外国人材5%のWAGE_BILL/ VALUE_ADDED定義、既存SQ人口ストック・追加受入の上限判定、保持率・単価・N4・地域条件、2055追加在留就業成人 `68,953.6 / 0.0`、GDP SQ差 `+0.579240 / 0.000000` の算術を確認。共有SQ人口を改変せず、人口/有効労働ブリッジとVAを混同していないか、既存ストック超過時に新規0とする挙動を確認。半官営医療25%/50%の同額移管はGDP/公費の架空節減を生まないこと、2%準備金追加保険料は家計負担と基金資産に対応すること、年金運用益の金融部門相手方・拠出二重請求を検査。

### E. 再現性・回帰・比較表示

`README.md`の再現コマンド `python handoff/chatgpt-n3-gap-closure-20261121/Reproduce.py --outdir /tmp/n3-gap-reproduction` を実行可能なら実行し、主要CSVの数値・行数・必要なら実バイト一致を確認。旧46ケース年次177,396セル、部品271,964セル一致というWork報告を独立にスポット/全量検査できる範囲で確認し、実際の検査件数を記録。Fは固定`ff621006`のLATEST_F参照30行であり**今回Fを再実行したのではない**点、F/N3の接続範囲が異なり因果順位を確定できない点を保持。単独差・併用差・交互作用を混同しない。

## 4. 判定・不一致時の対応

結果は`PASS`（実施範囲で再現・整合）、`PASS_WITH_LIMITATIONS`（算術整合だが境界・仮定に留保）、`FAIL`（再現可能な不一致）、`NOT_VERIFIED`（未検証）を項目ごとに明記。重大な不一致はケース名・年・列・期待値・実測値・差・再現手順・影響する比較を記載。原文曖昧さや係数未較正を直ちに実装バグと混同しない。

検算のために対象モデルを修正してPASSへ合わせない。必要なら修正候補を提案し、**対象修正の実施は別途Owner判断**。既存PASSは維持し、部分的な技術制約があっても検証可能な領域を継続。形式的な4AIレビューや新たな承認ゲートを追加しない。

## 5. Claude側handoffへの成果引渡し

**書込み先:** `work/claude-handoff` ブランチの新規 `handoff/claude-n3-gap-independent-verification-20261121/` のみ。既存原本を上書きしない。ZIP禁止。

最低限、(a)独立検算のMarkdown報告、(b)実際に使用した独立検算コードと実行方法、(c)検算結果CSV/JSON（主要ケース・年次・差分・検査件数）、(d)実行ログ/再現性結果、(e)ファイルごとのSHA-256・サイズ・固定Commit事後取得の照合結果を個別原本で格納。新たな数値を出していない項目は未実施と明示し、既存Workの表を転載しただけで独立検算と呼ばない。

GitHub保存後にClaude側の**固定Commitを取得し直し**、原本と取得物の実バイトSHA-256・サイズ一致を確認できた場合のみ`ARTIFACT READY`/`CUSTODY PASS`を宣言。保存だけ、git status確認だけ、他AIの照合報告だけでは不可。固定Commit・成果ディレクトリURL・実施検算範囲・主要不一致・残るOPEN・次に必要な最小アクションをOwnerへ簡潔に報告。

**最終判定:** 実コードによる独立検算・再実行・比較・Claude側GitHub引渡しの成否を区別して明記。N3全政策完成や正式Acceptanceは宣言しない。
