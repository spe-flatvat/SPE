# SPE RP-023｜v0.3 §8限定修正・全文差分再検証 DRAFT

Version: v0.1  
Status: DRAFT / NON-CANONICAL / NOT APPROVED  
Last Updated: 2026-11-06  
Updated By: RP-023

## 対象・権限

- 入力：`SPE_RP023_v0.3_Integrated_DRAFT_20261106.md`（17,123 bytes、SHA-256 `3945f1e172804315c9e065409fa8ec0d87a06a641f6a77106350282e7af7d8be`）
- 出力：`SPE_RP023_v03_Section8_Limited_Revision_DRAFT_20261106.md`（17,154 bytes、SHA-256 `4f99df2849d0264938cb9b223e9c020a89e6e33eabd7e1f84a06259c0fa62c56`）
- 差分：`SPE_RP023_v03_Section8_Limited_Revision_Unified_Diff_20261106.diff`（2,931 bytes、SHA-256 `50951332607daebdc023dde3225e7eefb7cdbbdc94ddb9d8ba7f9e55eecd0fbc`）
- 操作：新規ローカルDRAFT生成のみ。固定v0.2、先行v0.3、GitHub、DecisionLogは変更なし。

## RD-01 限定修正内容

§8の第1段落末尾に連結されていた二つ目の「共通項目は、」を、空行を挟んだ独立段落「なお、共通項目の記録に際しては、」へ変更。旧段落の全文と、補足段落の後続全文は保持した。

## 検証結果

| ID | 検証項目 | 判定 | 方法 |
|---|---|---|---|
| V-01 | 入力原本の前工程SHA一致 | PASS | ローカル実バイトSHA-256 |
| V-02 | 限定置換の一意性 | PASS | 置換対象出現回数1件 |
| V-03 | §8以外のバイト不変 | PASS | 変更前後のprefix/suffix厳密比較・置換逆変換一致 |
| V-04 | A/B/C必須要件の文字列保持 | PASS | 必須文言の存在・出現数照合 |
| V-05 | §4.1・§3参照と非減免条項保持 | PASS | 該当全文の存在・出現数照合 |
| V-06 | 新版とUnified Diff生成 | PASS | ローカル実ファイル生成・SHA-256計算 |
| V-07 | 規範意味論の独立第三者承認 | 未検証 | 本工程は編集・静的照合のみ |
| V-08 | 07A/P0原裁定の独立認証 | 未検証 | 今回対象外 |
| V-09 | Owner-confirmed Snapshot／正式レビュー発出 | STOP | Owner明示確認・発出未実施 |

## M01〜M07保護と残余

§8以外の全文を不変としたため、先行M01〜M07統合文案は今回の編集によって変更されていない。§8については旧必須項目と追補の非減免条項を残した。ただし、先行監査の条件付き評価を正式PASSやFinding Closeへ昇格しない。

CLD-03（検証担当独立性）はOwner判断留保。OD-03/05/08の後続裁定、07A/P0原発言、DecisionLog対応、証拠HEAD比較、旧07C-03 `.diff` は前工程の残余台帳の状態を維持する。これらを今回の編集で解消したとは扱わない。

## 次工程ゲート

限定修正候補本文・差分・本報告をOwnerに提示し、対象版・SHA-256・レビュー範囲を明示したOwner-confirmed Snapshot確認を求める。確認前の正式配布・レビュー発出はSTOP。RP-023／M19–25 HOLD継続。GitHub書込み、Owner裁定、正式Disposition、Finding Close、Freeze、HOLD解除なし。
