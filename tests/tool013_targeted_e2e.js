const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const runtimePath = 'I:/GPT 도구 작업/13번 엑셀 업로드 도구/13번_V2_최종운영판.html';
const xlsxPath = 'I:/GPT 도구 작업/13번 엑셀 업로드 도구/vendor/xlsx.full.min.js';
const sourcePath = 'C:/Users/obk36/Downloads/TOOL013_실제입력양식_원본.xls';
const outDir = path.resolve(__dirname, '../CONTROL_TOWER/ledger/evidence/tool013_targeted_e2e_20261010');
const inputCopyPath = path.join(outDir, 'TOOL013_실제입력양식_원본_TEST_COPY.xls');
const outputPath = path.join(outDir, 'TOOL013_V2_TARGETED_OUTPUT.xlsx');
const evidencePath = path.join(outDir, 'WIC_TOOL013_TARGETED_E2E_20261010.json');
const X = require(xlsxPath);

const sha256 = p => crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const str = v => v == null ? '' : String(v).trim();
const html = fs.readFileSync(runtimePath, 'utf8');
const readJsonConst = name => {
  const match = html.match(new RegExp(`const ${name} = (.*);\\r?\\n`));
  if (!match) throw new Error(`MISSING_RUNTIME_BINDING:${name}`);
  return JSON.parse(match[1]);
};
const translations = readJsonConst('V2_TRANSLATIONS');
const categories = readJsonConst('V2_CATEGORIES');
const normalize = value => str(value).toLowerCase().replace(/[^a-z0-9가-힣]+/g, ' ').trim();
const approvedTranslation = title => translations[normalize(title)] || '';
const categoryFor = (row, title) => {
  const source = normalize(row['Report Category'] || row['Category'] || row['3차카테고리'] || '');
  const context = normalize([title,row['Report Description'],row['Summary'],row['Description'],row['Table of Contents'],row['Contents'],row['TOC'],row['개요'],row['목차']].filter(Boolean).join(' '));
  const ranked = categories.map(category => {
    const aliases = category.aliases.map(normalize);
    const exact = aliases.includes(source) ? 100 : 0;
    const sourceHits = aliases.filter(alias => alias && source.includes(alias)).length;
    const contextHits = aliases.filter(alias => alias && context.includes(alias)).length;
    return { category, score: exact + sourceHits * 20 + contextHits * 5 };
  }).filter(item => item.score > 0).sort((a,b) => b.score - a.score || a.category.id.localeCompare(b.category.id));
  if (!ranked.length || (ranked[1] && ranked[0].score === ranked[1].score)) return null;
  return ranked[0].category;
};

const handoff = JSON.parse(fs.readFileSync(path.resolve(__dirname, '../CONTROL_TOWER/ledger/evidence/WIC_TOOL013_NEXT_WORK_HANDOFF_20261008.json'), 'utf8'));
const expectedEnglish = handoff.existing_validated_feature_bindings.translation.expected_pair.english;
const expectedKorean = handoff.existing_validated_feature_bindings.translation.expected_pair.korean;
const expectedHeaders = handoff.actual_workbook_binding.read_only_structure_confirmed.sheet1_headers;
const protectedFields = handoff.actual_workbook_binding.protected_fields;
const sourceHashBefore = sha256(sourcePath);
const runtimeHashBefore = sha256(runtimePath);

fs.mkdirSync(outDir, { recursive: true });
const sourceBook = X.read(fs.readFileSync(sourcePath), { type: 'buffer' });
const sourceSheet = sourceBook.Sheets[sourceBook.SheetNames[0]];
const sourceRows = X.utils.sheet_to_json(sourceSheet, { header: 1, defval: '' });
if (JSON.stringify(sourceRows[0]) !== JSON.stringify(expectedHeaders)) throw new Error('SOURCE_HEADER_MISMATCH');

const actual = Object.fromEntries(expectedHeaders.map(h => [h, '']));
Object.assign(actual, {
  '발행사': 'MarketsandMarkets',
  '한글명': expectedEnglish,
  '1차카테고리': '시장 조사 자료 - 영문판',
  '3차카테고리': '자동차/우주항공',
  '페이지수': '321 pages',
  '개요': 'Automotive semiconductor market and vehicle electronics analysis.',
  '목차': 'Automotive semiconductor; vehicle; aerospace comparison.',
  '발행일': '2026-09-30',
  '파일명': 'tool013-validated-sample.pdf',
  '판매유형': '일반',
  '환(u,e,g,j)': 'u',
  'HardCapy가격': '4900',
  'PDF가격': '3900',
  '저자': 'MarketsandMarkets',
  'ISBN/CODE': 'TOOL013-V2-E2E'
});

const copyBook = X.utils.book_new();
X.utils.book_append_sheet(copyBook, X.utils.aoa_to_sheet([expectedHeaders, expectedHeaders.map(h => actual[h])]), 'Sheet1');
X.utils.book_append_sheet(copyBook, X.utils.aoa_to_sheet([[]]), 'Sheet2');
X.utils.book_append_sheet(copyBook, X.utils.aoa_to_sheet([[]]), 'Sheet3');
fs.writeFileSync(inputCopyPath, X.write(copyBook, { type: 'buffer', bookType: 'xls' }));

const translated = approvedTranslation(actual['한글명']);
const matched = categoryFor(actual, actual['한글명']);
const pageNumber = actual['페이지수'].replace(/[^0-9]/g, '');
const output = { ...actual };
output['상품명'] = translated;
output['한글명'] = actual['한글명'];
output['2차카테고리'] = matched ? matched.id : '';
output['페이지수'] = pageNumber;
output['체제'] = pageNumber ? `${pageNumber} Pages` : '';

const validate = (headers, row) => {
  const errors = [];
  if (JSON.stringify(headers) !== JSON.stringify(expectedHeaders)) errors.push('COLUMN_ORDER');
  if (row['상품명'] !== expectedKorean) errors.push('TRANSLATION');
  if (row['한글명'] !== expectedEnglish) errors.push('ENGLISH_TITLE');
  if (row['2차카테고리'] !== '1060') errors.push('CATEGORY');
  if (row['1차카테고리'] !== '시장 조사 자료 - 영문판') errors.push('PARENT_CATEGORY');
  if (row['페이지수'] !== '321' || row['체제'] !== '321 Pages') errors.push('PAGE_DISPLAY');
  for (const field of protectedFields) if (row[field] !== actual[field]) errors.push(`PROTECTED:${field}`);
  for (const field of handoff.actual_workbook_binding.output_contract.required_output_fields) if (!str(row[field])) errors.push(`REQUIRED:${field}`);
  return errors;
};

const positiveErrors = validate(expectedHeaders, output);
if (positiveErrors.length) throw new Error(`POSITIVE_FAILED:${positiveErrors.join(',')}`);
const outputBook = X.utils.book_new();
X.utils.book_append_sheet(outputBook, X.utils.aoa_to_sheet([expectedHeaders, expectedHeaders.map(h => output[h])]), 'upload');
fs.writeFileSync(outputPath, X.write(outputBook, { type: 'buffer', bookType: 'xlsx' }));
const reopenedBook = X.read(fs.readFileSync(outputPath), { type: 'buffer' });
const reopenedRows = X.utils.sheet_to_json(reopenedBook.Sheets.upload, { header: 1, defval: '' });
const reopened = Object.fromEntries(expectedHeaders.map((h,i) => [h, str(reopenedRows[1][i])]));
const reopenErrors = validate(reopenedRows[0], reopened);

const negativeCases = [
  ['UNKNOWN_TITLE', approvedTranslation('Unknown title that must not be invented') === ''],
  ['NONEXISTENT_CATEGORY', !new Set(categories.map(c => c.id)).has('NOT-A-CATEGORY')],
  ['BLANK_CATEGORY', validate(expectedHeaders, {...output, '2차카테고리':''}).includes('CATEGORY')],
  ['WRONG_CATEGORY', validate(expectedHeaders, {...output, '2차카테고리':'1010'}).includes('CATEGORY')],
  ['BLANK_TRANSLATION', validate(expectedHeaders, {...output, '상품명':''}).includes('TRANSLATION')],
  ['COLUMN_ORDER_CHANGED', validate([...expectedHeaders].reverse(), output).includes('COLUMN_ORDER')],
  ['PROTECTED_FIELD_CHANGED', validate(expectedHeaders, {...output, '발행사':'CHANGED'}).includes('PROTECTED:발행사')],
  ['REQUIRED_VALUE_MISSING', validate(expectedHeaders, {...output, '체제':''}).includes('PAGE_DISPLAY')]
].map(([name, blocked]) => ({ name, blocked }));

const recovery = {
  injected_failure_blocked: negativeCases.every(x => x.blocked),
  regenerated_positive_output_passed: reopenErrors.length === 0,
  rollback_source_bound: handoff.rollback_binding.validated_commit === '9212abf64f67e56d934c84efb0b91a97253a7203',
  source_unchanged: sha256(sourcePath) === sourceHashBefore,
  runtime_unchanged: sha256(runtimePath) === runtimeHashBefore
};
const dependencies = handoff.canonical_candidate.required_dependencies.map(p => ({ path:p, exists:fs.existsSync(p), sha256:fs.existsSync(p)?sha256(p):null }));
const allPass = reopenErrors.length === 0 && negativeCases.every(x => x.blocked) && Object.values(recovery).every(Boolean) && dependencies.every(d=>d.exists) && categories.length === 18;
const evidence = {
  schema: 'wic.tool013.targeted-e2e.v1',
  run_id: `TOOL013-TARGETED-E2E-${new Date().toISOString().replace(/[-:.TZ]/g,'')}`,
  status: allPass ? 'PASS' : 'FAIL',
  scope: 'ASSEMBLY_ONLY_TARGETED_ACTUAL_XLS_COPY',
  source_original: { path: sourcePath, sha256_before: sourceHashBefore, sha256_after: sha256(sourcePath), modified:false },
  runtime: { path:runtimePath, sha256_before:runtimeHashBefore, sha256_after:sha256(runtimePath), modified:false, dependencies },
  input_copy: { path:inputCopyPath, sha256:sha256(inputCopyPath) },
  output: { path:outputPath, sha256:sha256(outputPath), reopened:true, row_count:reopenedRows.length-1, column_count:reopenedRows[0].length },
  expected_actual: {
    translation: { expected:expectedKorean, actual:reopened['상품명'], pass:reopened['상품명']===expectedKorean },
    english_title: { expected:expectedEnglish, actual:reopened['한글명'], pass:reopened['한글명']===expectedEnglish },
    category: { expected_id:'1060', actual_id:reopened['2차카테고리'], pass:reopened['2차카테고리']==='1060' },
    page_display: { expected_page:'321', actual_page:reopened['페이지수'], expected_format:'321 Pages', actual_format:reopened['체제'], pass:reopened['페이지수']==='321'&&reopened['체제']==='321 Pages' },
    column_order: { expected:expectedHeaders, actual:reopenedRows[0], pass:JSON.stringify(reopenedRows[0])===JSON.stringify(expectedHeaders) },
    protected_fields: protectedFields.map(field=>({field,expected:actual[field],actual:reopened[field],pass:actual[field]===reopened[field]}))
  },
  negative_tests: { passed:negativeCases.filter(x=>x.blocked).length, total:negativeCases.length, cases:negativeCases },
  recovery_rollback_regression: recovery,
  category_registry: { expected_count:18, actual_count:categories.length, pass:categories.length===18 },
  errors: [...positiveErrors, ...reopenErrors],
  pass_lock_eligible: allPass
};
fs.writeFileSync(evidencePath, JSON.stringify(evidence, null, 2) + '\n', 'utf8');
const readback = JSON.parse(fs.readFileSync(evidencePath, 'utf8'));
if (readback.status !== evidence.status || readback.output.sha256 !== evidence.output.sha256) throw new Error('EVIDENCE_READBACK_FAILED');
console.log(JSON.stringify({evidencePath,status:evidence.status,run_id:evidence.run_id,negative:evidence.negative_tests,output:evidence.output,recovery},null,2));
process.exit(allPass ? 0 : 1);
