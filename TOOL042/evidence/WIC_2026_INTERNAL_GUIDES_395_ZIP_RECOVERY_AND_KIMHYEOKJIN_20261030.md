# WIC TOOL042 — 2026 내부 안내서 재확보 및 김혁진 후보 3종 (2026-10-30)

## 누락 재발 원인
기존 GitHub 440건 canonical registry는 원본 ZIP 바이너리 자체를 보존한 것이 아니었고, 원본 연결 및 cross-chat 재열기 경로가 불완전했다. 목록만 조회하고 실제 DOC 안내서를 열지 못하여 고객별 매칭이 중단되었다. 이는 '자료가 없음'과 다르다.

## 이번 사용자 업로드 ZIP
- 이름: Global Acrylate Monomers Market Size, Share, and Trends Analysis Report – Industry Overview and Forecast to 2033 -월드산업정보센터.zip
- 압축 내 엔트리: 395개
- ZIP 무결성: testzip() PASS (손상 엔트리 없음)
- 이전 440건 canonical registry와 개수가 다르므로 동일 집합으로 가정하거나 기존 440건 기록을 덮어쓰지 않는다.
- 실제 원본 ZIP은 이 대화창 첨부에 있으며 GitHub에 바이너리 업로드 완료된 것은 아니다. 원본 보존/재다운로드 검증은 별도 HOLD.

## DYETEC 김혁진 선임연구원 — 사용자 신규 안내 결정
- 2026-09 이후 발송 EML 없음. 2024-09-24 디지털 섬유 프린팅/디지털 패브릭 프린팅 기계 시장 2종 안내 이력은 중복 검사에 사용.
- 개인 최신 부서/직함/연구분야는 독립적인 최신 온라인 증거 미확보. 다음 3종은 과거 관심분야에 근거한 잠정 후보, 발송 확정 아님.

|순위|내부 DOC 정확한 제목|발행사|발행|페이지|공급가격|원문 링크|
|---|---|---|---|---:|---:|---|
|1|Digital Textile Printing Inks Market – Global Forecast 2026-2032|360iResearch|2026-09|192|5,435,000원|https://www.360iresearch.com/library/intelligence/digital-textile-printing-inks|
|2|Textile Coatings Market Report 2026|The Business Research Company|2026-09|250|6,196,000원|https://www.thebusinessresearchcompany.com/report/textile-coatings-global-market-report|
|3|Textile Chemicals Market (2026 - 2033)|Grand View Research|2026-06|80|8,211,000원|https://www.grandviewresearch.com/industry-analysis/textile-chemical-market|

각각 사용자 ZIP의 해당 DOC 파일을 antiword로 직접 읽어 메타데이터 및 목차 일부 확인. 보고서 발행사 웹사이트 최신성/거래 가능 여부는 별도 검증 필요.

## 재발 방지 조건
1. GitHub 레지스트리 → 실제 ZIP 원본의 지속 접근 가능한 위치/해시/무결성 → ZIP 내 개별 DOC 파일 → 제목·발행사·연도·목차까지 연결하여 검증한다.
2. 실제 DOC 읽기 전에는 '내부 안내서 전체 검색 완료' 또는 '내부에 자료 없음'을 선언하지 않는다.
3. 신규 ZIP은 440건 레지스트리와 파일명/해시 기준 차이 분석 후 별도 source ID로 연결한다.
4. 개인 최신 재직·직함·연구분야가 확인되지 않은 경우 잠정 매칭으로 표시하고 발송 확정하지 않는다.
5. 고객별 발송 EML과 제목·발행사 중복검사 후 최종 3종을 확정한다.
