# RP-023｜Step 29E GitHub DRAFT保全準備

- Version: v0.1
- Status: DRAFT / PREPARATION ONLY / GIT WRITE NOT AUTHORIZED
- Last Updated: 2026-10-26
- Updated By: RP-023
- Repository: `spe-flatvat/SPE`
- Dedicated worktree: `/storage/emulated/0/Documents/SPE-RP023`
- Branch: `rp-023/document-issuance-draft`
- Expected pre-operation HEAD: `52ac73915beb5a3664ad8535cb5d7a4b80c28f91`

## 1. Scope

Prepare, but do not perform, DRAFT preservation of the five Step29B artifacts plus Step29D audit report. This preparation does not authorize copying, staging, committing, pushing, issuing four-AI requests, or modifying canonical documents. The three v0.3 packet documents are review *candidates*, not an Owner-fixed dispatch set.

## 2. Proposed repository destinations and SHA-256

All paths below are relative to the dedicated worktree and are **proposed**, not confirmed as written.

| No. | Destination | SHA-256 |
|---|---|---|
| 1 | `reviews/RP-023/RP-023_4AI_Common_Review_Manifest_v0.3_DRAFT.md` | `6c38a02bad82ae1988a3503e4e0dfa6337eafb4acaa89feb09c15757c662236d` |
| 2 | `reviews/RP-023/RP-023_4AI_Common_Review_Contract_v0.3_DRAFT.md` | `9abc3b67cfecbc6a86c54f4fc22cb135cd3a3b2794cf792c6f38ab3372f42245` |
| 3 | `reviews/RP-023/RP-023_4AI_Standard_Review_Request_v0.3_DRAFT.md` | `8b9360c89ce3229985ad05b25bb576cb7cc39fd1cd58b4b0dafcc7bdcc34a343` |
| 4 | `reviews/RP-023/RP-023_Step29B_External_Distribution_Hash_Register_DRAFT.md` | `17e58ea58104d6094901e3ec547abe7867be201bb93496ef3c9686d03649d388` |
| 5 | `reviews/RP-023/RP-023_Step29B_Revision_Check_Report_DRAFT.md` | `1c58bdb11d9bbdfa759a1454c7449459d4f8de9bbd7f35670d97ef1d7d9538a9` |
| 6 | `reviews/RP-023/RP-023_Step29D_Cross_Consistency_Audit_DRAFT.md` | `1ee0e42578d29e46386067842ad6494e120fa56332c1a9c8d6c3be203169b7ff` |

Step29C Owner Termux verified files 1–5, 5/5 PASS. File 6 requires separate Owner-side receipt/hash verification. Current assistant runtime SHA for all six matches the table; this is **not** Owner-side verification of file 6.

## 3. Read-only Termux preflight (no filesystem or Git writes)

Save the Step29D report to Android Download before running. This script checks both repository preconditions and all six downloaded source files; it does **not** copy, stage, or commit anything.

```bash
cd /storage/emulated/0/Documents/SPE-RP023
EXPECTED_BRANCH='rp-023/document-issuance-draft'
EXPECTED_HEAD='52ac73915beb5a3664ad8535cb5d7a4b80c28f91'
SOURCE='/storage/emulated/0/Download'

echo '=== STEP29E PRECHECK ==='
if [ "$(git branch --show-current)" != "$EXPECTED_BRANCH" ] ||
   [ "$(git rev-parse HEAD)" != "$EXPECTED_HEAD" ] ||
   [ -n "$(git status --porcelain)" ]; then
  echo 'STOP: repository branch, HEAD or cleanliness mismatch'
else
  echo 'PASS: repository preconditions'
  echo '=== SIX SOURCE HASHES ==='
  if (
    cd "$SOURCE" || return 1
    printf '%s\n' \
      '6c38a02bad82ae1988a3503e4e0dfa6337eafb4acaa89feb09c15757c662236d  RP-023_4AI_Common_Review_Manifest_v0.3_DRAFT.md' \
      '9abc3b67cfecbc6a86c54f4fc22cb135cd3a3b2794cf792c6f38ab3372f42245  RP-023_4AI_Common_Review_Contract_v0.3_DRAFT.md' \
      '8b9360c89ce3229985ad05b25bb576cb7cc39fd1cd58b4b0dafcc7bdcc34a343  RP-023_4AI_Standard_Review_Request_v0.3_DRAFT.md' \
      '17e58ea58104d6094901e3ec547abe7867be201bb93496ef3c9686d03649d388  RP-023_Step29B_External_Distribution_Hash_Register_DRAFT.md' \
      '1c58bdb11d9bbdfa759a1454c7449459d4f8de9bbd7f35670d97ef1d7d9538a9  RP-023_Step29B_Revision_Check_Report_DRAFT.md' \
      '1ee0e42578d29e46386067842ad6494e120fa56332c1a9c8d6c3be203169b7ff  RP-023_Step29D_Cross_Consistency_Audit_DRAFT.md' |
      sha256sum -c
  ); then
    echo 'PASS: 6/6 source hashes verified'
  else
    echo 'STOP: source file missing or SHA mismatch'
  fi
  echo '=== READ-ONLY END ==='
  git status --short
fi
```

**Note:** For robust Termux shell compatibility, the `cd "$SOURCE" || return 1` line is executed within a subshell grouped in the `if` condition. If a particular shell rejects `return` outside a function, replace it with `cd "$SOURCE" && printf ... | sha256sum -c` before execution; do not use `exit` or `set -e`.

## 4. Subsequent gates

1. Owner verifies file 6 and preflight six-file set; all six must pass.
2. Owner separately authorizes copying **only** these six files to `reviews/RP-023/` in dedicated worktree, followed by destination hash and diff inspection.
3. Owner separately authorizes `git add`, `commit`, and `push` only after confirming the exact staged file list and hashes; record resulting local and remote SHA.
4. Owner separately fixes the final 14-file dispatch set and recipient verification process; Git preservation alone does not constitute dispatch authorization.

## 5. STOP and exclusions

STOP on wrong worktree, branch, HEAD, dirty worktree, missing file, SHA mismatch, or unexpected preexisting destination. No edits to main, canonical documents, existing v0.2 documents, or unrelated files. OD-03/05 remain unresolved; 07A original remains unverified. No four-AI dispatch, Review Acceptance, DecisionLog update, Canonicalization, Freeze, or Close.

**Step29E status: PREPARATION DRAFT COMPLETE / OWNER-SIDE FILE6 VERIFICATION PENDING / GIT WRITE HOLD / DISPATCH HOLD.**
