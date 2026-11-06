# SPE RP-023 v0.3｜Gemini転載全文 GitHub保全検証レシート

- Status: CUSTODY VERIFICATION PASS / GEMINI SERVICE ORIGINAL UNVERIFIED
- Repository: `spe-flatvat/SPE`
- Branch: `review/rp023-v03-distribution-draft-20261106`
- Distribution Fixed Commit (unchanged): `f4939211f1ab5b5848d3aa5293078bb651e2028b`
- Verified file snapshot commit: `3c57cb8a9ab5727605ba759e63b3eec9dcb797c1`
- Directory: `reviews/RP-023/v0.3_distribution_draft_20261106/responses/`
- Source: Owner-provided Gemini chat transcriptions (2026-11-06). These are not Gemini-service original bytes.
- Method: GitHub connector `fetch_file` at the fixed snapshot; independently computed SHA-256 of UTF-8 encoded fetched content; readback equality was checked at initial commit.
- Hash implementation sanity check: SHA-256("abc") = `ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad` (PASS).

| ID | File | UTF-8 bytes | Git Blob SHA-1 | Retrieved-file SHA-256 | State |
|---|---|---:|---|---|---|
| G-01 | `SPE_RP023_v03_Gemini_G01_Full_Chat_Transcription_20261106.md` | 1944 | `6a3d747edf81a411624ea6db879af99b85350faa` | `c3c4a6623399981797b7b6adf38f6f91d86fc99036fb707066e02ad480aaa817` | PASS |
| G-02 | `SPE_RP023_v03_Gemini_G02_Full_Chat_Transcription_20261106.md` | 5228 | `8c277ada278c85da254cb661e0f76363c008e84f` | `17218164e375b14b944166e217c9472459aa559bfdb7ab479403c597f472e278` | PASS |
| G-03 | `SPE_RP023_v03_Gemini_G03_Full_Chat_Transcription_20261106.md` | 11235 | `ad31bc9ba54ad8dcd2897b5fb05463b45974629b` | `c13083bc91979a3efc84faf5a060631c7fc95ddca815dc44883bc099eb6df586` | PASS |

## Scope and limits

1. This receipt certifies the fixed GitHub transcription files and their retrieved bytes, not the Gemini service original response bytes.
2. Chat UI transcription may normalize whitespace and newlines; identity with Gemini service output is unverified.
3. Previously committed extracted DRAFTs and custody index remain distinct derived artifacts; no overwrites were performed.
4. Gemini's own review receipt reports individual source-document binary SHA-256 as not independently measured; this status remains unchanged.
5. No formal review Acceptance, Finding Close, DecisionLog update, Freeze or HOLD release is authorized or performed.
6. The receipt is a new auxiliary custody artifact; the original distribution commit is unchanged.
