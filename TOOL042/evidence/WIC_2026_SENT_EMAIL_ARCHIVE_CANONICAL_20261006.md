# WIC 2026 Sent Email Archive — Canonical Dedup Source

STATUS: ARCHIVE_VERIFIED / BINARY_GITHUB_UPLOAD_BLOCKED_BY_SIZE
DATE: 2026-10-06
PURPOSE: Cross-chat customer-guide send deduplication

SOURCE_ZIP: (2026년 5월 12일 견적건) 계산서 발행 문의드립니다, 탄소수소산업연구조합 김유리 선임연구원님.zip
SOURCE_SIZE_BYTES: 163862063
SOURCE_SHA256: 5cddf76e5106a3d763213bfe17a4a14ddb425fe4a647a7c9aab184582f3a57a3
ZIP_ENTRY_COUNT: 1144
ZIP_INTEGRITY_TEST: PASS

## Mandatory rule
All WIC customer matching / TOOL042 / travel-customer / textile-customer workflows MUST consult this 2026 sent-email archive before recommending or sending a guide.
Match at minimum customer/institution + material/report/book title + send history.
If already sent, block duplicate recommendation unless an explicit, verified new-edition/update rule permits it.
Chat separation must not create a separate send-history truth.

## Binary preservation status
The source ZIP is 163,862,063 bytes (~156.3 MiB), above GitHub's normal single-file 100 MB limit. Therefore the binary itself is NOT falsely marked as stored in the normal GitHub repository.
Canonical binary storage requires Git LFS or another immutable binary store; GitHub remains the canonical registry/evidence/control point.

## Examples observed in archive
The archive includes 2026 customer mail for institutions including 한국생산기술연구원, 한국섬유개발연구원, DYETEC연구원, 한국탄소산업진흥원, 한국화학연구원, 탄소수소산업연구조합 and others.

## Acceptance gate
DEDUP_SOURCE_REGISTERED=PASS
ZIP_INTEGRITY=PASS
NORMAL_GITHUB_BINARY_STORED=NO_SIZE_LIMIT
CROSS_CHAT_DEDUP_RULE=ACTIVE
