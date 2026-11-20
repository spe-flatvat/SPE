# 再実行とファイル案内

DRAFT / NON-CANONICAL。Python 3.10以上、外部パッケージ不要。GitHub固定Commitからこのディレクトリを個別ファイルで取得する。ZIPは使わない。

```bash
python Model.py Inputs.json --outdir replay
python Verify.py
```

Model.pyは埋込みの前回家計モデル・年金・外国人材・動学モデルの解凍実バイトをサイズ・SHA-256確認して呼び出す。入力JSONは圧縮原本を含むため大きい。書換えた入力で実行した結果は別成果として扱う。旧成果を上書きしないようoutdirを必ず別にする。

- Annual.csv：46条件×30年、旧スキーマの未算定欄は空欄。
- Comparison.csv／Summary.csv：旧F・新VAT無効・SQとの比較。
- Tax_Decomposition.csv：率・参照ベース・税収・売買両側控除。
- Sonzei_Incidence.csv：分野別損税、価格・賃金・投資・利益、数量・主体間移転。
- Price_Incidence.csv：家計・政府・保険者・事業者への帰属と消費接続。
- Household_Income.csv：引継ぎの所得階層別A/B/C勘定。VATの全国実測所得分布ではない。
- C_Funding.csv：直接価格便益、給付、財源、基金、前回差。
- Interactions.csv：率・ベース・控除・Cの差分と相互作用。
- StatusQuo_Fixed.csv：前回固定SQ。StatusQuo_Updated.csv：現行と提案感度。
- Inputs.json：政策候補・係数・旧原本・前回比較値。
- Model.py／Verify.py：計算本体・追加検証。
- Validation.json／Verification.json：内蔵確認と追加確認・再実行の結果。
- Sources_and_Map.md／Source_Integrity.json：原文対応・資料根拠・取得経路と実バイト記録。
- Report.md：結果・解釈・限界。
- SHA256SUMS.json：引渡し原本のサイズ・SHA-256（自分自身を除く）。
- Delivery_Verification.json：GitHub格納後の固定Commit事後取得照合。原本データCommitと記録追加Commitを区別する。

金額は原則兆円。GDPはreal／nominalを区別。損税参照市場は年1.5%伸長、通常課税ベースは既存coreNに接続するため成長率が異なる。現行／Fの同年比較はVAT_F_minus_current_SQ、初期予算伸長基準との差はVAT_delta_vs_fixed_referenceを使う。

OFFは新VAT効果とCを無効化したF背景、OLDとEXTRA_ZEROは前回F家計成果の再現。MM／ZZの意味と政策解釈はReport.mdを参照。FULL_ADDITIONALは中間候補であって公式F採用条件ではない。

SHA256SUMS.jsonのfilesについて、取得したファイルの実バイト長とhashlib.sha256を一致照合する。Verify.pyは数値ファイルを一時フォルダに再生成し、12ファイル全てを原本とbyte比較する。ローカルPASSとGitHub事後照合は別の証拠である。
