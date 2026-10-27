# SPE M19–25｜FG-06 修正候補専用 Distribution Checklist — DRAFT

- 状態：`PRE-DISPATCH / STOP / OWNER APPROVAL PENDING`
- パケットID：`SPE-M19-25-FG06-REREVIEW-3DEC-20261027-DRAFT-01`

## 1. 入力固定

- [x] 旧Rev.4原本の実バイトSHA-256：`d1b6e64caead960972f0e8c2b2edebb24deb36522cc41d65947ff0580a1bd04e`
- [x] 新候補の実バイトSHA-256：`fce55ac833abb06085340e6bb903939c2121bc6387d07c4d04ddd23cfde6b848`
- [x] 3変更patchの実バイトSHA-256：`3a1235ed56978d0410debd887a9e3186ef8ffceb71600c9f43098b3ae4f1c12c`
- [x] 旧Common Packet / Request / Checklistの記録済みSHA-256とLibrary回収原本の一致
- [x] 既存4AIの20独立Finding ID対応表を参照
- [x] 新候補・旧原本・patchの差分局所性を配布直前に再検証
- [x] 旧4AI原回答4件の実バイトSHA-256と配布用原本照合
- [x] Rev.2、FG-05、Step 6D-35、Workflow、DecisionLogの固定版取得・同梱・SHA照合
- [x] 4AIの同一条件配布用入力一式を完全固定（ZIP/manifest/hash list）

## 2. 配布判断

- [x] 配布候補ZIPの全同梱ファイルSHA-256照合・固定（本工程）
- [ ] 配布直前にZIPのSHA-256とOwner承認対象の一致を再確認

- [ ] Ownerが今回の候補・baseline・配布資料・欠落証拠を確認
- [ ] Ownerが**再レビュー開始・送付を明示承認**
- [ ] 配布先（4AI）、同一入力・依頼書、配布方法、配布時刻を記録
- [ ] 送付前の各ファイルSHA再計算／受領後の各AI実バイトSHA確認
- [ ] 配布証跡・回答保全先・受付IDを確定

## 3. 停止条件

候補不一致、3変更以外の無承認差分、必須証拠未固定、同条件性欠落、Owner承認未取得の場合、**配布STOP**。限定レビューに切り替える場合もOwnerの別途明示判断を要する。M19–25／RP-023 HOLD維持。正式Finding Close、Review Acceptance、DecisionLog更新、Canonical化、Freeze、GitHub書込みなし。
