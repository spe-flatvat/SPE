# SPE (SUZUME PolicyCraft Engine)

**政策を「提言」するのではなく、政策を「設計・検証・破壊・改善」するためのオープンな政策クラフト環境**

---

## SPEとは

SPEは、国家システムの限界を探るための実験的フレームワークです。

正解を提示するものではありません。

極端なシナリオを含むストレステストを通じて、「持続可能な制度設計とは何か」を探求することを目的としています。

- 特定の経済学派やイデオロギーを前提としません
- 制度変更が人・企業・国家の行動に与える影響を、整合的なシナリオで検証します
- 発動条件・出口戦略・自動修正条項を備えた政策設計を行います
- 失敗を前提とした多段階 fallback 設計（N3 → R4 → F3）を特徴とします

---

# オリジンストーリー

最初は、

「消費税5%にしたらどうなるんだろう」

という、ごく素朴な思考実験でした。

単純な税率変更を試すシミュレーションから始まりましたが、
検討を重ねるうちに、税制そのものだけでなく、
制度設計や経済全体の相互作用を比較できる共通基盤の必要性を感じるようになりました。

その結果、一つの政策を検証するためのシミュレーションではなく、
複数の政策を同一条件で比較・評価できるシミュレーション基盤として
SPEプロジェクトが生まれました。

---

## シリーズ構成

この思考実験から、複数の政策アーキテクチャが派生しました。

- **F系列**：包摂性と成長を重視した長期成長戦略
- **N3**：規律優先の生存戦略
- **R4**：N3の限界を受けたバランス型リブート
- **F3**：最終縮小・市場原理徹底路線（国家縮退フェーズ）

これらは優劣ではなく、

**異なる国家運営シナリオ**

として設計されています。

---

## 設計思想

SPEが一貫して重視している考え方があります。

> **包摂性と成長戦略のない国家運営は、最終的に国家の持続可能性を失わせる。**

そのため、

- 発動条件
- KPI
- 自動修正条項
- 出口戦略

まで含めて政策を設計しています。

政策は「成功する前提」ではなく、

**失敗した場合まで設計して初めて完成する**

という立場を採っています。

---

## このプロジェクトの特徴

- 発動条件・出口戦略・自動修正条項を明示
- 簡易シミュレーション条件（初期値・リスクイベント・弾性値）を公開
- ストレステストを前提とした政策設計
- AIとの共同設計・共同検証
- 「政策提言」ではなく「政策クラフト」のサンドボックス

---

## 今後の予定

- Google Colab版シミュレーションエンジン
- レポート自動生成
- パラメータ編集UI
- シナリオ比較ダッシュボード
- ランダムイベント実装
- コミュニティによる Fork・Pull Request

---

## 免責事項

本プロジェクトは一私人による個人的研究・思考実験です。

政党・政府・団体等の公式見解ではありません。

数値・シミュレーション結果は簡易モデルによる試算であり、実際の政策効果を保証するものではありません。

実在の個人・団体・組織を誹謗中傷することを目的とするものではなく、制度設計の比較検討を目的としています。

利用・引用・Forkは歓迎しますが、自己責任でお願いいたします。

---

> **SPEは、政策クラフトエンジンである前に、AI時代の知識管理実験でもあります。**

そして、

> **さあ、国家というシステムをクラフトしよう。**

## Documentation

Project documentation is organized under the `docs/` directory.

- **Workflow**: [docs/Workflow.md](docs/Workflow.md)
- **Project Roadmap**: [docs/ProjectRoadmap.md](docs/ProjectRoadmap.md)

Additional documentation (Decision Log, Development Story, etc.) will be added as the repository evolves.

## Repository Structure

- docs/              Governance, glossary, decision logs and errata.
- policies/          Policy specifications.
- specifications/    Simulation specifications.
- proposals/         Individual proposal documents.
- Inbox/             Working notes and temporary design documents.
- SimulationIdeas/   Historical simulation assumptions retained for reference.

