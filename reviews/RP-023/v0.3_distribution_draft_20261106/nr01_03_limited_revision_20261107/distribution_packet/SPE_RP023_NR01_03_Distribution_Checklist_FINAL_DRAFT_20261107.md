# SPE RP-023 v0.3｜NR-01〜03 限定独立レビュー

**Status:** DRAFT / NON-CANONICAL / NOT ISSUED  
**Repository:** `spe-flatvat/SPE`  
**配布候補固定Commit:** `2d747d2b4162d11b915575ffc791607a37ef95df`  
**作成日:** 2026-11-07  

> 本書はレビュー準備の新規DRAFT。Owner-confirmed Snapshotの新規承認、正式発出、GitHub格納、レビュー開始を宣言しない。旧2026-11-06版§8限定改訂Snapshotを取り消さず、今回のNR-01〜03統合版とは別対象として識別する。

## 1. 発出前Checklist

- [x] 指定固定Commitの存在確認（接続済みGitHub）
- [x] NR-01〜03の7文書パス・サイズ・Git blob SHA-1を固定Commitツリーで確認
- [x] 旧発出文案の主対象が2026-11-06版であり、今回主対象と異なることを特定
- [x] NR-01〜03 Owner案Aの範囲を統合裁定台帳と突合
- [x] 規範副作用監査のNR-02解釈上の留保を明記
- [x] 7文書のGitHub固定Commit原文取得・実バイトSHA-256独立計算（7/7、既存期待値5/5一致）
- [x] 監査・統合台帳の欠落SHA-256新規計測、最終DRAFT Manifestへ反映
- [x] 新規3文書のローカル実バイトサイズ・SHA-256計測と台帳化
- [x] ZIP形式を生成・配布・引渡し・保全利用しないことを明記（Owner 2026-11-07指示）
- [ ] 新規3文書のGitHub格納、格納後の固定Commitから事後取得・SHA-256一致（Owner書込み承認が必要）
- [ ] 主対象のOwner-confirmed Snapshot確認（対象パス・Commit・SHA・レビュー範囲）
- [ ] 各AIへの取得経路確認、必要な補助資料の固定識別
- [ ] Ownerの正式発出承認（レビュー開始可否、期限、waiverを明示）

## 2. 受領・独立レビュー時Checklist（発出後）

- [ ] AI自身が固定原本の実バイトを取得しサイズ・SHA-256を照合、受領レシート作成
- [ ] 取得不能経路・代替参照先・残余STOPを限定記録。別AI申告を自己PASSとしない
- [ ] 同一対象・固定Commit・証拠条件の既存PASSのみ再利用
- [ ] 受領READY＋レビュー本文承認なら同一ターンで独立レビュー。受領のみ承認なら本文禁止
- [ ] 16原FindingのID/Severityを維持、NR-01〜03の規範差分・副作用・未検証を個別評価
- [ ] GitHub書込み、Finding Close、Acceptance、DecisionLog、Freeze、HOLD解除、Canonical化を行わない

## 3. STOP区分と判定

- **TECHNICAL STOP:** 特定取得経路やハッシュ実測手段の制約。影響範囲と代替経路を記録。
- **EVIDENCE STOP:** 固定版・実バイト・SHA不一致、必須原本欠落。未検証のPASS昇格禁止。
- **NORMATIVE STOP:** Scope Contract、Workflow、既存承認条件に抵触。
- **OWNER AUTHORIZATION PENDING:** 新Snapshot確認、GitHub書込み、正式発出等の承認待ち。

**現時点：DRAFT CREATION PASS / PRE-DISPATCH NOT READY / OWNER AUTHORIZATION PENDING。**

## 4. 最終DRAFT確定の判定

- 7原本の固定Commit SHA-256検証：**PASS（7/7）**。
- 3文書のローカル生成・同一性計測・相互参照：**PASS（3/3）**。
- 3文書のGitHub保全／CUSTODY PASS：**未実施**。
- 新Snapshot Owner確認・正式発出：**OWNER AUTHORIZATION PENDING**。
- 未検証の原裁定、配布先到達性、回答期限、waiver：未検証／未指定を維持。

## 5. 禁止形式

Owner明示指示（2026-11-07）：AI協業でZIP形式のパケット生成・配布・引渡し・保全利用は禁止。個別原本で受渡し、個別SHA-256と格納後の再取得一致で判定する。
