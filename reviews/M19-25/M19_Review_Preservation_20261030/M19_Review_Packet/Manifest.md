# M19｜Review Packet Manifest DRAFT

Status: **DRAFT / NOT DISTRIBUTED / NOT FROZEN / NO REVIEW START**
Date: 2026-10-30
Repository: `spe-flatvat/SPE`
Planned directory: `reviews/M19-25/M19_Review_Packet/` (not created in GitHub)

## Packet structure
Four new Markdown files in one directory. No `cat`/`split` bundle, no per-AI folders.

## Local packet component hashes

| File | SHA-256 |
|---|---|
| `Common_Review_Request.md` | `b85826b3690202d61447fd4203824ee71b217cf495baa7271ff6b3c5a84f4217` |
| `Review_Checklist.md` | `34bc7b14728a30f3307d2c9efea592decb42bd10bcbff87d629cb9a94b9e32d1` |
| `Evidence_Index.md` | `376bcdbc5a88f1d0dda521788f466be634e378593ba6e3944d3d7a289b05d943` |
| `Manifest.md` | Self-hash excluded (avoid circular hash) |

## Referenced source inputs
See `Evidence_Index.md` for seven existing local source files and their byte hashes. **Those sources are not copied into this four-file packet.** Reviewers must receive identical immutable access to them, not merely filenames or mutable local paths.

## Pre-distribution STOP conditions
- Current M19 local inputs have **no verified GitHub fixed commit**. A fixed distribution commit and paths (or separately Owner-approved equivalent immutable delivery) are required before review issuance.
- Verify byte-level SHA-256 of all referenced inputs and these packet components after final packaging; record the immutable reference and a receipt. Hashing the manifest itself is done in an external receipt after creation.
- Owner has authorized M19 limited drafting/verification, **not** GitHub writing, formal review start, Finding Close, canonical approval, Freeze or M20–25 release.
- Historical E1, E-03/E-04, CLD2 remain NOT VERIFIED; no retrospective search is mandated.

## Source provenance
FG-06 fixed distribution commit: `789403ae904594a0973ed7c7a142745a75595320`; current M19 candidate and supporting reports are local artifacts created after this commit, so that commit does not authenticate their bytes.
