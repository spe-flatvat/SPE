# FG-06｜統合DRAFT限定・非極小レビュー範囲契約 v0.1 DRAFT
- Status: DRAFT / NON-CANONICAL / NOT FOR DISPATCH
- Repository: `spe-flatvat/SPE` (read-only)
- Fixed preservation commit: `0a7e3af9e73f37821c3de05f06ebb043965b274e`
- Original 3DEC SHA-256 (previously verified local distribution): `fce55ac833abb06085340e6bb903939c2121bc6387d07c4d04ddd23cfde6b848`
- Integrated candidate SHA-256 (locally reverified): `4a3b475abb1281c7bf25b27bc23c0e67b3f0abd3e494222404f607d7c6cc16c1`
- Integrated patch SHA-256 (locally reverified): `1f6a8ab716d470f665b39ff24561cfcbc71f9dacf9fcd09a16033cb8e233f220`
- Authority: Owner 2026-10-28 approval for design/drafting/self-check/STOP only; no dispatch or review start.
- M19–25 / RP-023 HOLD; no Finding Close, Review Acceptance, Freeze, DecisionLog update, or GitHub writes.

## 目的と深度
- L1 全差分：統合候補対固定3DECの変更全行と前後文脈、R-01〜R-07裁定追跡を逐条審査。ヘッダの権限表示とCC-04のGate C 2026例外を含む。
- L2 直接依存：CC-04/05/06、Gate A→C→B、2026初期状態と2027+前年確定状態、切替アンカー、CC-03/12予約・pending、CC-08/13比較権限、CC-01変更禁止を実質審査。
- L3 横断：CC-01〜CC-13全文の相互矛盾・回帰、六状態領域、29将来V&V Invariantsの文言整合、既存20独立Finding IDの再発・残存・新規副作用を確認。全行の新規独立校閲を要求するものではない。
- L4 証拠：既存レビュー原本・旧裁定・E-03/E-04・42件の別マッピングは必要時のみ原本照合。参照未取得の証拠は未検証と記す。既存Findingは自動Closeしない。
## 必須の判定対象
1. R-01案Aの新規起案根拠と歴史的証拠未検証の分離。全文承認・遡及承認を含意しないこと。
2. R-02案B2：2026年切替候補のGate C参照を承認済2026 Baseline Initial-State Contractに限定し、2027+は前年確定値。2026候補の存在・切替・数値自体は未承認。
3. CC-06 `actual preceding-year result` と2026初期状態境界の整合性。矛盾の有無と最小修正案を明示。
4. R-03〜R-07の既存文言が裁定の条件・禁止・監査要件を満たすか。
5. 29 Invariantsは将来検証義務であり、PASS済みと表現しないこと。
## 除外
- 数値係数、2026初期値、政策効果、実装/API、エンジン実行、実V&V、全過去レビューの全面再実施、正式承認・Freeze。
- 除外事項にレビュー対象条項との重大な依存・矛盾が見つかった場合、理由を記録しOwner判断へエスカレーション。
## 拡張・STOP
- Major級矛盾、裁定逸脱、証拠不足、SHA不一致、既存Findingの実質的再発が発見された場合、関連条項・必要原本への範囲拡張候補を提案。無断で全面レビューへ拡張しない。
- 対象同一性が確認できない場合は配布STOP。限定範囲内の未解決Majorはレビュー結論に残し、Close/Acceptance/Freezeへ進めない。
- AI間は相互回答を閲覧せず、同一固定パケット・質問・評価基準を使用する。
