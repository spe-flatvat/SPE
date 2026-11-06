# SPE RP-023 v0.3｜NR-01〜03 統合Owner裁定台帳

**Document ID:** RP023-v03-NR01-03-OWNER-DECISION-REGISTER-DRAFT-20261107  
**Version:** v0.1  
**Status:** OWNER DECISIONS RECORDED / INTEGRATED REGISTER DRAFT / NON-CANONICAL  
**作成日:** 2026-11-07  
**Repository:** `spe-flatvat/SPE`  
**権限:** 既存Owner判断の統合記録・新規DRAFT作成のみ。GitHub書込み、既存ファイル変更、DecisionLog更新、正式Acceptance、Finding Close、Freeze、HOLD解除は行わない。

## 1. 台帳の目的と判定境界

NR-01〜03について本チャットで明示されたOwnerの案A採用を、個別レシートと突合して一覧化する。**Ownerの方針選択PASS**と、**次版DRAFTへの反映、独立レビュー、正式Disposition／Finding Close、正式規範発効**は別状態として管理する。既存裁定の取消し・再承認、原証拠未認証事項のPASS昇格を行わない。

## 2. 統合裁定一覧

| ID | 対象・関連Finding | Owner原指示の裁定部分 | 採用方針・次版DRAFTで許される範囲 | 新設しないもの | 状態 |
|---|---|---|---|---|---|
| NR-01 | 旧HOLD表現／`RP23V3-CLD-01`、B-01 | 「NR-01のOwner判断として案Aを採用します」 | §7限定HOLD、§9 Workflow保護、§10証拠留保を維持。OD-03／05／08等の出典・原裁定照合状態への注記・相互参照を補強。原証拠未認証を未決・無効と同一視しない | 旧HOLD文の自動復活、新規HOLD義務、既存裁定の遡及取消し・再承認 | **Owner方針PASS／本文未反映** |
| NR-02 | §8「適用外」／`RP23V3-CLD-02`、ChatGPT `NEW-01` | 「NR-02のOwner判断として案Aを採用します」 | §3区分別必須要件、§4.1共通識別要件、§8の「未実施／未確認／適用外」を維持。既存意味論の範囲で説明・例示・参照を整序 | 適用外の理由記録MUST、新たな一般的使用制限、必須要件の減免、解消済み§8重複の再修正 | **Owner方針PASS／本文未反映** |
| NR-03 | 検証担当の独立性／原`RP23-CLD-03`、OD-06 | 「NR-03のOwner判断として案Aを採用します」 | 技術検証とOwner内容判断の分離、既存Workflowの独立レビュー要件、個別担当指定・Owner権限留保を維持。必要な場合のみ既存条項の説明・相互参照を整序 | 発出者と検証担当の別人MUST、同一主体時の一律記録MUST、新たな独立検証主体指定義務 | **Owner方針PASS／本文未反映** |

**注:** 上表の関連Findingは追跡用であり、正式Finding DispositionやCloseを宣言しない。NR-03の「案A」は新しい独立性要件を追加しない判断であって、既存の独立レビューを免除する判断ではない。

## 3. 個別Ownerレシートの固定識別・ローカル実バイト照合

| 裁定 | Receipt ID | 原本ファイル名 | bytes | SHA-256（本台帳作成時のローカル実測） | 状態 |
|---|---|---|---:|---|---|
| NR-01 | `RP023-v03-NR01-OWNER-RECEIPT-20261107` | `SPE_RP023_v03_NR01_Owner_Decision_Receipt_20261107.md` | 3573 | `8a46a5fc881255e8ae264adaf3e98be509d7fb77560f58a299ba886a74275b6e` | 取得・SHA照合PASS／GitHub未保全 |
| NR-02 | `RP023-v03-NR02-OWNER-RECEIPT-20261107` | `SPE_RP023_v03_NR02_Owner_Decision_Receipt_20261107.md` | 4126 | `3eee74a2b4b695dcde1c31034c9ed08d3752bbc5f506a51d564ec71ea54b06db` | 取得・SHA照合PASS／GitHub未保全 |
| NR-03 | `RP023-v03-NR03-OWNER-RECEIPT-20261107` | `SPE_RP023_v03_NR03_Owner_Decision_Receipt_20261107.md` | 4679 | `20a01c3a9ac4f7dd1fb0170a00a2be70856c02a7fd8f820bf7f29fb63fa433ea` | 取得・SHA照合PASS／GitHub未保全 |

照合対象は現在の実行環境に存在する個別Markdown原本。SHA一致は原本のローカル同一性の証拠であり、GitHub保全や正式裁定登録を意味しない。各レシート中の「次工程待ち」は**発行当時の時点記録**であり、本台帳では後続Owner指示による3件採用を反映する。個別レシートは改変しない。

## 4. 監査・比較固定参照

| 区分 | 固定Commit |
|---|---|
| Work横断監査4文書のGitHub保全 | `d74fd7e78866413ab4e47080e285e1f82e0853fd` |
| 4AI回答 | `8f0964fae445a66f377a3e04d180a72d44a14f6f` |
| v0.3配布・編集基準 | `f4939211f1ab5b5848d3aa5293078bb651e2028b` |
| v0.2比較基準 | `5f27d4e2fba90cda2cd69ee534e865174c31ba1f` |

Work収束候補原本：`reviews/RP-023/v0.3_distribution_draft_20261106/cross_ai_audit_20261107/SPE_RP023_v03_Convergence_and_Owner_Decision_Candidates_DRAFT_20261107.md`（上記Work保全Commit）。同一ディレクトリのMatrix、Normative Delta Audit、Evidence Gap Registerを補助参照とする。これらのGitHub保全済み事実を、今回のレシート3件・本台帳のGitHub保全と混同しない。

## 5. 証拠留保・非昇格

- **NR-01:** 旧v0.2局所HOLD文の削除は監査済み。全体の承認・Workflow保護が失われたとの結論ではない。OD-03／OD-08の原裁定照合は未検証。OD-05は判断レシート回収報告があるが、原発言の独立認証と同一ではない。
- **NR-02:** §8必須非減免は維持。非必須共通項目の「適用外」の解釈余地は編集上の説明対象として残る。Gemini指摘の§8近接重複は固定v0.3で解消済みとの監査結果を維持。
- **NR-03:** OD-06原裁定は未照合。未照合を不存在・無効と判定しない。別人性の新規一般義務を導入しない。
- **共通:** DecisionLog個別対応および元07C-03 `.diff` の原本照合には未検証項目が残る。4AIレビュー結果の正式Acceptance、原FindingのDisposition／Closeは未実施。未検証の証拠をPASSに昇格しない。

## 6. 次工程と実行ゲート

1. **次版DRAFTの限定編集（未実施）:** v0.3配布固定版を不変の比較基準として別名の新規DRAFTを作成。NR-01出典注記、NR-02状態例示、NR-03現行保護維持の範囲に限定。関連する既存の条項・参照の意味論を変更しない。
2. **差分・副作用監査（未実施）:** 固定v0.3と次版DRAFTの差分、§3／§4.1／§7／§8／§9／§10、Workflow、関連Findingの整合性を検証。既存PASSを同一性確認の範囲で再利用し、未検証事項だけ補完。
3. **証拠ギャップの個別管理（継続）:** 原裁定・DecisionLog・元diffの未照合を範囲限定で記録。全件の再提出や再レビューを自動要求しない。
4. **レビュー準備（未実施）:** 新規DRAFT、差分、固定識別、個別レシート3件、未検証一覧を整理。正式レビュー実施・採否・規範発効は別ゲート。
5. **GitHub保全（未実施）:** 本台帳および個別レシートはローカル生成済み。GitHub書込みにはOwnerの別途明示承認が必要。保存後の固定Commit・原本SHA照合をもって保全判定する。

## 7. 状態一覧

| 状態対象 | 判定 |
|---|---|
| NR-01〜03 Owner方針選択 | **PASS（3/3、全件案A）** |
| 個別レシート取得・ローカルSHA-256照合 | **PASS（3/3）** |
| 本統合台帳の生成 | **PASS** |
| 次版DRAFT反映 | **未実施** |
| 未検証原証拠・DecisionLog個別照合 | **PARTIAL／未検証を維持** |
| 個別レシート・本台帳のGitHub保全 | **未実施** |
| 正式Acceptance／Finding Close／DecisionLog更新／Canonical化／Freeze／HOLD解除 | **未実施** |

**最終状態:** DRAFT / NON-CANONICAL。RP-023／M19–25 HOLD継続。Ownerの最終判断権限と既存ガバナンスを変更しない。
