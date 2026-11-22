# 出典と適用境界

2026-11-22取得。以下は公的資料・一次研究であり、SPE係数の全国較正完了を意味しない。

| 資料・取得先 | 確認内容 | 本診断への使い方・制約 |
|---|---|---|
| [内閣府・経済財政社会保障の長期推計テクニカルペーパー（2024年）](https://www5.cao.go.jp/keizai2/keizai-syakai/shisan/tyouki2.pdf) p.10–13 | 医療・介護の年齢構成と単価、年金と制度間移転、試算期間以降の名目GDPに応じた歳入・歳出延伸、実効金利と債務計算を区別している | 2040年名目据置だけで持続可能性を認定できない根拠。異なる基準の系列をSPEへ直接上書きせず、SQ名目延伸、社会保障・金利ストレスを感度として実行。公式の将来GG財政系列として使っていない |
| [財務省・令和8年度予算の後年度歳出歳入への影響試算（2026年2月）](https://www.mof.go.jp/policy/budget/topics/outlook/sy2026a.htm) | 利払い、社会保障、地方交付税、その他、基礎的経費、税収・その他収入を分け、予算一般会計とSNA国地方PBの定義を区別 | 既存固定財政原本の費目分離を維持。社会保障の新規全国推計や全制度の移転表へ置換していない |
| [JICA緒方研究所・Discussion Paper No.21（2024年3月）](https://www.jica.go.jp/jica_ri/publication/discussion/1535110_24127.html) | 日本の公共資本の一次メタ分析。生産弾力性0.146という集約結果と、地域・分野・時期の異質性を報告 | 弾力性は年次供給増／資本係数と単位が異なる。0.146をcapital_yieldへ転用していない。0〜0.1は未較正感度 |
| [内閣府ESRI DP397（2024年8月）論文本体](https://www.esri.cao.go.jp/jp/esri/content/e-dis397.pdf)、[概要](https://www.esri.cao.go.jp/jp/esri/archive/e_dis/2024/e_dis397.html) | 社会資本の供給効果は仕様・無形資産との補完性に依存し、単独の社会資本外部性は正で有意とならない仕様を含む | 公共資本供給係数ゼロを含めて検証。国全体で常に0.1という前提を公的根拠で確定しない |
| [内閣府・2020年SNA産業連関表結果概要](https://www.esri.cao.go.jp/jp/sna/data/data_list/sangyou/files/contents/pdf/h27/snaio_gaiyou2020.pdf) | 最終需要・公私固定資本形成・輸入と生産誘発の区分がある | この概要表だけから本政策支出構成の輸入誘発係数は同定できない。国内比率0.6/0.8/1.0は実測値ではない。レオンチェフ生産誘発倍率をGDP倍率として加算しない |

## 固定済み統計原本

`handoff/chatgpt-national-fiscal-closure-20261121/` の `Official_Fiscal_Baseline_2025_2040.csv`、`Statistical_Source_Receipts.json`、`Statistical_Cell_Map.csv`、`SNA2024_Sector_Snapshot.csv` を同一固定依頼Commitから再利用した。公式系列は2025〜2040年の国地方見通しでありSPEの同一経済シナリオではない。2024年のSNA部門スナップショットには社会保障基金・内部移転・一般政府連結があるが、2026〜2055年の給付・拠出・内部移転の将来系列を埋めるものではない。

新規 `Fiscal_Official_Baseline_Boundary_Map.csv` は一般会計・地方普通会計の移転控除後proxyと公式SNA国地方PBの残余を明示する。社会保障基金の将来給付・拠出・内部移転、GA/地方普通会計からSNAへの費目別調整、満期別国債発行、SFAの実体配賦が未接続のため、一般政府閉合は未完了。

既存の税・医療・年金の全国較正も未完了。財政ストレスで支出制限・GDP不足が計算できても、実現可能な全国財政計画を確定したとは扱わない。
