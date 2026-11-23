# 再生成

Python 3標準ライブラリのみを使用する。カレントディレクトリをこのhandoffにする。

```sh
python Recalculate.py sources replay1
python Recalculate.py sources replay2
python Verify_Reproduction.py replay1 replay2 > Reproduction_Verification.json
```

`sources/`には固定版から回収した45原本を個別ファイルで収録する。各ファイルの固定Commit・Git blob SHA-1・実バイトSHA-256・サイズはSource_Manifest.jsonにある。実行開始時に全件照合する。既存リポジトリの外部ディレクトリやネットワークへの依存はない。

Worker.pyは固定Fアダプターを新規handoff内へ複製し、教育E・奨学金S・訓練TのON/OFF指定だけを追加した実行コード。既存エンジン原本を変更せず、同じ6労働条件・共通労働差・高齢者条件付き時間差を適用する。各組合せは独立Pythonプロセスで実行する。

基準はmask=7、全OFFは0。E=1、S=2、T=4のビット和を用いる。8組合せの出力を使い、Shapley値と完全要因分解を計算する。SQ/N3は固定比較原本を再利用し、今回の再実行件数には含めない。

CSVの空欄はN/A。GDP・支出・税・部分財政は兆円、賃金代理は万円、時間は年間時間、生産性は比率。教育の労働相当量は実測FTE・追加就業者数ではない。2035年参考警戒は自動拡大を実行しない。
