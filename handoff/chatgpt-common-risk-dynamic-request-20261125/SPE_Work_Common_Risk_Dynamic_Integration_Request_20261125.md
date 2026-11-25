# SPE｜共通リスク回復モデルの動学接続・年次再計算
Status: OWNER AUTHORIZATION BY WORK MESSAGE / LIMITED EXECUTION / NON-CANONICAL
Repository: spe-flatvat/SPE
Branch: work/chatgpt-handoff
成果先: handoff/chatgpt-common-risk-dynamic-20261125/

## 目的・固定参照
固定実質経路への価格接続から、回復条件を上流ランタイムに実装し、価格依存・所得・需要・税・給付・財政の既存計算を年次再実行する段階へ進む。F/SQ/N3、2026–2055。
- 共通指標 8a8edb403b960cceb535f9b70461646e9374c229 / handoff/chatgpt-f-sq-n3-common-indicators-20261123/ の Dependencies.json、Run.py、Report.md と指定上流実装。
- GDP原因分解 adb373d87c5beb68b35f84be9e504c84d67014e0
- リスク回復 ff2e8c3d78d1c64c1d79f8d39dee3a9de786a6d8 / handoff/chatgpt-risk-specific-recovery-20261124/
- 価格接続 2d8cb85878c931d9d127755af6d2eb336c04c04d / handoff/chatgpt-common-price-nominal-real-20261125/
- F最新統合 3d3507e2df9218a6bbda587e9b8b0c0d423ae2ac / handoff/chatgpt-f-latest-integration-20261125/ の Run.py、Dependencies.json、Report.md、Inclusion.csv、Unconnected.csv、Funding_Residual.csv。
既存Claude検算 da79ab621de27a1a2df8dd3edf050e4f02fac63a は固定対象のみ再利用。政策原本・Annex・仕様と固定実装の差を維持し、非採用感度を正式採用しない。

## 実装・実行
1. 現行Aを固定再利用し、上流ランタイムの年次依存順序、状態変数、価格・財政境界を確認。既存Aの再現確認は必要最小限。固定原本を変更せず成果先の実行コードで回復状態を実装する。
2. C（紛争・南海トラフ5年、定期災害・気候1年）とD（同5年、同2年）を実装。イベント年損失を保持し、k年後残余=損失×max(0,1−k/n)、重複は独立乗算。リスクOFFのコア水準に適用し、成長率への再減算・回復の二重計上禁止。固定比較では2027紛争5%、2031地震3%、2029起点3年毎災害1%、2028起点2年毎気候0.5%、初期油OFFを維持。原本との起点差・油OFFを明記し、別途原本整合候補として実行可能なら分離診断（初期580/600を無断変更しない）。慢性的気候生産性損失を勝手に一時ショックと同定しない。
3. P2価格経路（基調2%、2027のみ7%、以降2%、価格水準上振れ持続）を共通接続。初期係数600/580、価格圧力は既存供給制約式で毎年再計算。入力物価率、暗黙GDPデフレーター、家計バスケットを分離。回復による物価自動反落なし。現行加算規約とP2の差を分離。
4. 上流の人口・労働・生産・供給・賃金・所得・消費・輸入・税収・保険料・給付・医療教育費・政府需要・財源・債務について既存式の依存順に年次再生成。前年状態を次年へ渡す。Fは採用済みF1相当を主系列とし、F2の非採用家計感度は別枝でC/Dに接続し、価格基準・適格性再判定が根拠ある範囲で実施。N3は既存償還配分・G/I条件維持。政府/地方/保険者別勘定、ストック・フロー、未割当財源を保持。根拠のない全国推計・MPC・VAT転嫁・自動起債・勘定間充当を禁止。未定義の反応は固定またはN/Aと明示し、実行可能部分を継続。完全動学と称するのは必要な依存が実際に再生成された範囲のみ。
5. 主系列C/D×F/SQ/N3×30年=180新規ケース年次、F非採用感度C/D×30=60追加を基本とする。A90年次、前回P3/P4およびF最新F3を対照再利用。未実行枝を計算済みと数えない。主要年2026/2030/2035/2043/2045/2055、実質・名目GDP、人口、一人当たりGDP、価格、所得・消費・給付・税・財政・債務の接続可能指標、政策差、回復年、累積GDP差を出力。固定経路診断との差を価格・需要・供給・財政等に分解し、交互作用・残差明記。

## 成果・検証・引渡し
Report.md、Annual.csv、Key_Years.csv、Dynamic_Bridge.csv、Connection_Status.csv、Fiscal_Residual.csv、Run.pyおよび必要実行モジュール、Dependencies.json、Validation.json、Manifest.json、Custody.jsonを個別原本として成果先に格納。年次状態遷移、初期値、回復残余、名実恒等式、供給制約、二重計上、会計閉合、固定枝不変、差分閉合、再実行一致を検証。新規件数と既存PASSを区別。固定版事後取得・実バイトSHA-256・サイズ一致時のみCUSTODY PASS。ZIP禁止。追加Claudeレビュー不要。
main、固定F/SQ/N3、政策原本・Annex、DecisionLog、正式Acceptance/Freeze/Canonical、RP-023/M19–25 HOLD、RP-024 PENDING、既存承認ゲート維持。書込みは指定成果先のみ。N3償還比率変更・正式採用・仕様改訂は対象外。実計算・引渡し優先、未達範囲を明示。
