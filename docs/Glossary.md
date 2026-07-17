# Glossary

**Document:** Glossary.md

**Version:** v0.2-final

**Status:** Fixed

**Last Updated:** 2026-07-17

---

# Purpose

Glossary は SPE プロジェクトにおける **Single Source of Truth** として機能する。

すべての仕様書・README・Decision Log・Errata は、本 Glossary の定義を優先して参照する。

---

# Scope

本 Glossary は、

- 用語
- 数式記号
- モデル名称
- 出所
- 実装状態

を定義する。

設計思想・意思決定理由は **DecisionLog.md** を、
記載誤り・修正履歴は **Errata.md** を参照すること。

---

# Source Tags

| Tag | When to use |
|------|-------------|
| **[Document]** | 正式な政策本文や既存ドキュメントに明記されている内容 |
| **[User Design]** | プロダクトオーナー（ユーザー）が明示的に決定した設計内容 |
| **[Model Assumption]** | モデル実装上必要な論理的仮定・係数・補間値 |
| **[Co-design]** | AI共同レビュー・開発委員会で合意した内容 |
| **[Future Concept]** | 将来実装予定だが現時点では未実装の概念 |

---

# Part A — Current Simulation Model

## SUZUME Model

SPEで使用する統一シミュレーションモデル。

**Decision:** DL-001

**Status:** Current

**Source:** [Co-design]

---

## Cobb-Douglas Production Function

GDP推計に使用する生産関数。

労働項には人口フィードバックを組み込む。

---

## α (Alpha)

資本分配率。

**Value**

α = 0.35（固定）

**Decision:** DL-003

**Source:** [Model Assumption]

---

## φ (Phi)

出生率への実質賃金フィードバック弾性。

**Value**

φ = 0.15（固定）

**Decision:** DL-004

**Source:** [Model Assumption]

---

## Aging Drag

人口高齢化による潜在成長率低下を近似する補正項。

期間別補正値を使用する。

| Period | Definition |
|---------|------------|
| 2026–2032 | 補正値（仕様書参照） |
| 2033–2043 | 補正値（仕様書参照） |
| 2044–2045 | 補正値（仕様書参照） |
| 2046–2055 | 補正値（仕様書参照） |

詳細数値は Simulation Specification を参照。

**Source:** [Model Assumption]

---

## Anchor

政策本文に記載された値を正式値として採用する方式。

**Decision:** DL-005

---

## Mechanical Calculation

比較目的で機械的に再計算したケース。

正式値ではなく参考ケースとして扱う。

---

## Trigger Condition

政策発動条件。

具体的判定ロジックは
**SimulationSpecification_v5.md**
（次期 v6）を参照。

---

## Exit Condition

政策終了条件。

具体的判定ロジックは
**SimulationSpecification_v5.md**
（次期 v6）を参照。

---

## Stress Test

共通リスクイベント下で政策耐性を評価するシナリオ。

---

# Part B — SPE Architecture (Future)

> 以下は将来構想であり、現時点のシミュレーションには実装されていない。

---

## Boundary

制度の限界状態。

F3等は Failure ではなく、
SPEが扱う制度モデルの**Boundary（適用限界）**として定義する。

**Source:** [Future Concept]

---

## F3

制度世界の適用限界点。

現モデルが前提とする制度の終了境界。

**Source:** [Future Concept]

---

## Handoff

SPEの計算結果を人間へ返す境界。

F3到達時には
「答え」ではなく
「次の設計材料」を返す。

**Source:** [Future Concept]

---

## State

国家状態。

Candidate

- Healthy
- Warning
- Critical
- Emergency
- Recovering

**Source:** [Future Concept]

---

## State Machine

SPE全体を制御する状態遷移モデル。

**Decision:** DL-008

**Source:** [Future Concept]

---

## Transition

State間遷移。

**Source:** [Future Concept]

---

## Recovery

危機状態から正常状態への復帰プロセス。

**Source:** [Future Concept]

---

# Related Documents

- README.md
- DecisionLog.md
- Errata.md
- SimulationSpecification_v5.md
  （次期 v6 へ移行予定）

---

# Committee Note

本版の適用をもって、
Errata ER-003〜ER-009 は **Fixed** とする。

今後の更新は全文再生成ではなく、
**差分管理（Incremental Update）** を基本方針とする。

