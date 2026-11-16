# SPE｜Fマクロ動学モデル 読取テスト・レシート

Status: READ TEST COMPLETE / DRAFT / NON-CANONICAL
作成日: 2026-11-17（Asia/Tokyo）

## 実行範囲と取得元

Ownerの「作業ブランチ handoff の最新資料を読み取り、読み取り結果をレシートとして同一ディレクトリへ出力」の指示に基づく限定実行。
ブランチ検索により、引継ぎ指定と一致する `work/chatgpt-handoff` を対象とした。
Repository: `spe-flatvat/SPE`
読取時HEAD: `783b3de06961f0d38d330d0768489fb89dfa93c2`
対象ディレクトリ: `handoff/f-macro-dynamic-20261116/`
取得経路: 接続済みGitHub連携。ブランチAPIでHEADを確定後、fetch_fileのBase64出力を固定Commit指定で取得し、デコードした実バイトを測定した。
測定用ローカル保存先: `/workspace/scratch/a55a6a789c03/read-test/`
レシート保存先: 同一ブランチ・同一ディレクトリの `SPE_F_Macro_Dynamic_Read_Receipt_20261117.md`

## 本チャット自身の実測

|原本|bytes|実測SHA-256|引継ぎ期待値との照合|
|---|---:|---|---|
|SPE_F_Macro_Dynamic_Halation_DRAFT_20261116.py|29794|b497972ed514ea46474f86e89ffdceccd23b221989ea17559a6f6426fb3a200f|一致|
|SPE_F_Macro_Dynamic_Inputs_DRAFT_20261116.json|585464|49b14d866ede3d6761c4a571e2dde034c1a5581779b7a4dd0e350b8e72ccad7c|一致|
|SPE_F_Macro_Dynamic_Annual_Comparison_DRAFT_20261116.csv|614958|13417fc6d344e54f7732c9c19d460a69bb9ccbb3e77c88567e0d4059858180fe|一致|
|SPE_F_Macro_Dynamic_Run_Report_DRAFT_20261116.md|12607|468de76ed7da54b5b8c0ec889a715e47cd8d43e27957811af090ea242dee3111|一致|

4/4件のサイズ・SHA-256一致を本チャットで独立に確認した。前担当のPASS申告だけを自己検証結果へ転記したものではない。

## 読み取り結果

報告書全文を読取。入力JSONをパースし、parameters・sequence・sectors・households・casesを確認した。CSV全540行をパース。Pythonコードは構文解析と主要構造・入出力処理の読取を実施した。コード全体の意味論監査やシミュレーション再実行は今回の範囲に含めていない。

- 対象期間は2026〜2055年。入力の16動学ケースと2参照経路で18経路、540年次行。
- 基準シーケンスは2030年8%、2035年5%。部門課税化は教育2036年・賃貸2037年・医療2038年。給付は2027〜2029年、年1兆円の暫定設定。
- 消費・投資の調整係数は各0.6、減耗率0.05、投資支援フロー/GDP比0.004、教育フロー/GDP比0.003、供給吸収率0.5。いずれも実証校正済みとは扱わない。
- コードは旧固定成長加算を除いたCOREと政策動学を区別し、家計資金・消費、投資、資本、教育資源、供給制約、税収へ接続する構造。
- 読取CSVの2055年DYNAMIC_BASE実質GDPは460.23626324720533兆円、COREとの差は9.289645307201283兆円。報告書の丸め表示と一致する。
- 報告書の2055年macro税収は107.225864兆円、直接込み税収診断は96.812740兆円。両者を国庫純増額と解釈しない。
- 報告書のEARLY_5PCTは2055年GDP460.277998兆円、LATE_5PCTは460.110736兆円。最終制度を揃えた開始時期比較として記載されている。
- DYNAMIC_BASEは旧Fへ波及だけを追加したモデルではない。LEGACY_OFFとの差には旧固定加算除去が含まれるため、政策損失とは解釈しない。
- 医療支援は感度仮定であり必要給付額の裁定ではない。NO_CARRYは比較用診断。雇用・賃金は指数proxy。
- 反応係数・全国課税ベース・医療未財源等は未校正または未確定。金利、実際の国債発行、債務、PB、CPI、所得分布、食料品0%は未算定。
- 報告書内のモデル試験PASSとClaudeの旧Annex検証は既存記録として読んだ。今回それらを再実行・独立レビューしたとは主張しない。

## 状態と境界

今回の実成果は4原本の自己回収・読取・実バイト照合と、このレシートの新規出力である。
GitHubへの変更はこのレシート1件の新規追加に限定する。モデル・入力・CSV・報告書を改訂しない。
正式Acceptance・Finding Close・DecisionLog更新・Freeze・Canonical化は実施しない。
RP-023／M19–25 HOLD、RP-024 PENDINGを維持する。
レシート自身の保存後固定Commit・実バイト照合結果は回答で報告する。本文内で保存前にCUSTODY PASSを宣言しない。
