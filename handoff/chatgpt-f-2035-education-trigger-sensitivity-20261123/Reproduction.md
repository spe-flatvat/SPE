# 再生成

Python 3標準ライブラリのみ。カレントディレクトリを本handoffとする。

```sh
python Recalculate.py sources replay1
python Recalculate.py sources replay2
python Verify_Reproduction.py replay1 replay2 > Reproduction_Verification.json
```

30の固定入力・コード原本をsources/へ個別収録する。原本同一性・固定版・取得元はSource_Manifest.jsonに記録し、実行時にサイズ・SHA-256を照合する。先行固定成果のCUSTODY PASSを再利用し、既存48経路の再実行は行わない。今回の基準Fと感度枝だけを独立Pythonプロセスで実行する。

基準Fを先に実行し、2035年実質GDP／2034年実質GDP−1を一度だけ計算する。1.2倍、1.1倍、1.3倍の枝はこの同じ介入前の成長率で判定し、2036〜2055年に教育施設・サービスの投入係数と訓練税控除率係数を拡大する。奨学金・政策原文・既存エンジンは変更しない。NO_FIRE_EQUAL_THRESHOLDは閾値を基準成長率と等しく置く試験専用枝で、実行した非発動経路を基準と照合する。

Prior_Worker.pyは先行固定版から変更しない。Worker.pyは教育クラスの当年パラメータのみを一時的に変更し、年度末に元へ戻す。既存の2035年自動トリガーはOFFを維持し、介入後成長率で再判定しない。訓練控除の実現額は追加訓練反応を含むため、控除率係数を1.2倍にしても控除実現額・訓練時間がちょうど1.2倍になるとは限らない。

金額は兆円、賃金代理は万円、時間は年次時間、生産性は比率。空欄はN/A。一般政府PB・国債総発行・実測FTEは算定しない。SQ/N3は固定比較値を再利用する。全枝は非採用の診断である。
