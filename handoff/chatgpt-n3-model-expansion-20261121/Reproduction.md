# N3拡張の再実行

DRAFT / NON-CANONICAL。Python 3.10以上、標準ライブラリのみ。旧N3・共通エンジン・政策原本は変更しない。新規作業ディレクトリを使い、ZIPは作らない。

固定Git objectを保持するSPEリポジトリで、必要なら以下を実行する。既に同じ固定worktreeがあれば再作成不要。

```bash
git fetch origin ff6210061615105de9a0d64767c256796be80ed2
git fetch origin 3c77eafc2073fdaba4c129164817d2f57c9421b9
git fetch origin 64f2a317e6e9827e37346ad80de7cc0649357c05
git worktree add --detach /tmp/spe-n3-fixed-engine ff6210061615105de9a0d64767c256796be80ed2
git worktree add --detach /tmp/spe-n3-verification-source 3c77eafc2073fdaba4c129164817d2f57c9421b9
```

リポジトリルートから実行する。書込みは新規成果側だけ。Build_Resultsはルートのgit objectから固定参照を読む。指示Commitを通常の履歴付きfetchで取得すれば旧31d659/580438も含まれる。浅いcloneで欠ける場合はその完全SHAもfetchする。

```bash
export PYTHONDONTWRITEBYTECODE=1
python handoff/chatgpt-n3-model-expansion-20261121/N3_Expansion_Model.py handoff/chatgpt-n3-model-expansion-20261121/N3_Expansion_Inputs.json --engine /tmp/spe-n3-fixed-engine --source /tmp/spe-n3-verification-source --outdir handoff/chatgpt-n3-model-expansion-20261121 > handoff/chatgpt-n3-model-expansion-20261121/N3_Expansion_Run.txt 2>&1
python handoff/chatgpt-n3-model-expansion-20261121/N3_Expansion_Verify.py --engine /tmp/spe-n3-fixed-engine --source /tmp/spe-n3-verification-source --replay > handoff/chatgpt-n3-model-expansion-20261121/N3_Expansion_Test_Output.txt 2>&1
python handoff/chatgpt-n3-model-expansion-20261121/Build_Results.py /tmp/spe-n3-fixed-engine /tmp/spe-n3-verification-source
```

生成結果を変える再実行後に、旧Delivery_Verificationを新出力の保全証拠として使わない。Manifestは自身とDelivery_Verificationを除く個別原本を列挙する。

## 実接続

N3_Expansion_Modelは旧スクリプトをSHA検証して私有namespaceへ読み込み、既存Medical/CommonInterface呼出とSQエンジンの接続部を再利用する。ソース原本は変更しない。コードを文字列差替えする箇所は一意性assertを継承し、固定依存が変われば同じ検算を黙って通さない。

N3_Componentsは税・企業・積立・減免・給与の差額勘定を作り、旧医療とは別列に保つ。既存エンジンへ家計現金、直接税、政府費用、投資、サービス付加価値、新規雇用の労働だけを注入する。14旧条件では新部品がOFFで、元の非空契約列30,000セルが回帰一致する。税・保険者勘定の不足を見かけ上閉じる自動財源は作らない。

N3_Expansion_Annualは絶対値、N3_Expansion_Comparisonは共通ONのSQ差。N3_SQ_F_Comparisonは絶対・SQ・固定Fとの差を列で区別する。Fの医療VAT数量等との接続範囲差があり、厳密なパッケージ順位ではない。N3_Income_DistributionのDIは税/減免単独部品の代理で、年金/医療/企業など全N3効果を個々の世帯へ再配分した所得ではない。

VAT数量反応は既存regular_account/sector_accountへ候補弾力性を渡して実行し、数量と税収が変わることを確認する。家計価格/企業受取は固定量近似を保つため、独立の数量→実消費/GDP経路は無い。医療量→VAT基盤も未接続とする。影響を隠す追加GDP係数を置かない。

## 入力の境界

政策原文の20/30/40、75歳、16%のAND条件、500万円、共済10–15、N4、GDP比5%制約を保持する。所得源泉構成、企業利益/分布/基準税率、開始細則、給付/減免率、利回り、対象人数、給与、KPI閾値等は未較正・Owner未裁定候補であり、Inputs.parameter_provenanceに区別する。

所得・税・保険料の既存統計は固定FデータとSources_and_Mapを再利用。人口尺度・将来所得・個人/世帯・世帯属性の交差分布は代理で、全国の個票税務計算ではない。所得区分を一律30%とせず給与/事業30・金融20を分け、法人20/16は別勘定、消費20はVAT経路のみ。年金所得と地方税の再設計はOPEN、相続税ベースとEITC基準はnull。外国人材比率を人数に換算せず、外部比率の条件例だけ実行し人口追加は未接続。

年金の65–74歳は5歳階級内一様のコーホート近似で、過去の受給者の権利を取り消さない。拠出の基金振替は既存掛金の移動で家計へ再控除しない。運用益の相手方・全国保険制度・全国PB/国債はOPEN。新規実装は実装者の自動検査を受けたもので、旧独立検算PASSを新拡張全体へ読み替えない。

税・減免は2030開始・3年移行（原文フェーズ1内の候補）2条件を追加。既存44条件の2033開始は遅延感度として維持。合計46条件・1,380年次行。
