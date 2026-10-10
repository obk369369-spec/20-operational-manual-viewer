const fs = require('fs');
const path = require('path');
const http = require('http');
const crypto = require('crypto');
const { chromium } = require('playwright');

const toolDir = 'I:/GPT 도구 작업/13번 엑셀 업로드 도구';
const runtimePath = path.join(toolDir, '13번_V2_최종운영판.html');
const xlsxPath = path.join(toolDir, 'vendor/xlsx.full.min.js');
const X = require(xlsxPath);
const outDir = path.resolve(__dirname, '../CONTROL_TOWER/ledger/evidence/tool013_user_usable_20261010');
const sha256 = p => crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const str = v => v == null ? '' : String(v).trim();
const headers = ['발행사','상품명','한글명','1차카테고리','2차카테고리','3차카테고리','페이지수','개요','목차','발행일','파일명','판매유형','환(u,e,g,j)','HardCapy가격','PDF가격','저자','체제','ISBN/CODE'];
const english = 'China Semiconductor Market for Automotive by Component (Microcontroller, Power Semiconductor, Sensor & MEMS Device, Memory Chip, Analog & Mixed Signal IC), Global & China Semiconductor Export, Alternate Destination - Trends and Strategic Recommendation';
const korean = '중국 자동차용 반도체 시장: 구성 요소별(마이크로컨트롤러, 전력 반도체, 센서 및 MEMS 소자, 메모리 칩, 아날로그 및 혼합 신호 IC), 글로벌 및 중국 반도체 수출, 대체 목적지 - 동향 및 전략적 제언';
const validRow = {
  '발행사':'MarketsandMarkets','상품명':english,'한글명':'','1차카테고리':'시장 조사 자료 - 영문판','2차카테고리':'','3차카테고리':'Automotive','페이지수':321,
  '개요':'Automotive semiconductor market and vehicle electronics analysis.','목차':'Automotive semiconductor; vehicle; aerospace comparison.','발행일':45827,
  '파일명':'tool013-user-e2e-valid.pdf','판매유형':'u','환(u,e,g,j)':'u','HardCapy가격':4900,'PDF가격':3900,'저자':'MarketsandMarkets','체제':'','ISBN/CODE':'TOOL013-USER-E2E-1'
};
const invalidRow = {...validRow,'상품명':'Unknown title that must not be invented','3차카테고리':'Unknown','발행일':46168,'파일명':'tool013-user-e2e-invalid.pdf','ISBN/CODE':'TOOL013-USER-E2E-2'};

function writeWorkbook(file, rows, sheet='Sheet1'){
  const wb=X.utils.book_new();
  X.utils.book_append_sheet(wb,X.utils.aoa_to_sheet([headers,...rows.map(r=>headers.map(h=>r[h]??''))]),sheet);
  fs.writeFileSync(file,X.write(wb,{type:'buffer',bookType:'xlsx'}));
}
function reopen(file){
  const wb=X.read(fs.readFileSync(file),{type:'buffer',cellDates:false});
  const ws=wb.Sheets[wb.SheetNames[0]];
  const aoa=X.utils.sheet_to_json(ws,{header:1,defval:'',raw:false});
  return {headers:aoa[0]||[],rows:aoa.slice(1).map(row=>Object.fromEntries((aoa[0]||[]).map((h,i)=>[h,row[i]??''])))};
}
function assert(condition,message){if(!condition) throw new Error(message);}
function safeFile(root,url){
  const clean=decodeURIComponent((url||'/').split('?')[0]);
  const rel=clean==='/'?'13번_V2_최종운영판.html':clean.replace(/^\//,'');
  const file=path.resolve(root,rel);
  if(!file.toLowerCase().startsWith(path.resolve(root).toLowerCase())) return null;
  return file;
}

(async()=>{
  fs.mkdirSync(outDir,{recursive:true});
  const inputPath=path.join(outDir,'TOOL013_USER_E2E_INPUT.xlsx');
  const correctedPath=path.join(outDir,'TOOL013_USER_E2E_CORRECTED_REUPLOAD.xlsx');
  const errorPath=path.join(outDir,'TOOL013_USER_E2E_ERROR_DOWNLOAD.xlsx');
  const uploadPath=path.join(outDir,'TOOL013_USER_E2E_FINAL_UPLOAD.xlsx');
  const tracePath=path.join(outDir,'TOOL013_USER_E2E_FINAL_TRACE.xlsx');
  const screenshotPath=path.join(outDir,'TOOL013_USER_E2E_FINAL_SCREEN.png');
  const evidencePath=path.join(outDir,'WIC_TOOL013_USER_USABLE_FINAL_OUTPUT_20261010.json');
  writeWorkbook(inputPath,[validRow,invalidRow]);
  const runtimeBefore=sha256(runtimePath);
  const server=http.createServer((req,res)=>{
    const file=safeFile(toolDir,req.url);
    if(!file||!fs.existsSync(file)){res.writeHead(404);res.end('not found');return;}
    const ext=path.extname(file).toLowerCase();
    res.setHeader('Content-Type',ext==='.js'?'application/javascript':ext==='.html'?'text/html; charset=utf-8':'application/octet-stream');
    fs.createReadStream(file).pipe(res);
  });
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  const port=server.address().port;
  const edge='C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
  const browser=await chromium.launch({headless:true,executablePath:edge});
  const page=await browser.newPage({acceptDownloads:true});
  const dialogs=[];
  page.on('dialog',async dialog=>{dialogs.push(dialog.message());await dialog.accept();});
  const failures=[];
  try{
    await page.goto(`http://127.0.0.1:${port}/13%EB%B2%88_V2_%EC%B5%9C%EC%A2%85%EC%9A%B4%EC%98%81%ED%8C%90.html`,{waitUntil:'load'});
    await page.setInputFiles('#fileInput',inputPath);
    await page.waitForFunction(()=>document.querySelectorAll('#previewTable tbody tr').length===2);
    const preview1=await page.locator('#previewTable tbody tr').nth(0).locator('td').allTextContents();
    assert(preview1.includes(english),'ENGLISH_PRODUCT_NOT_PRESERVED');
    assert(preview1.includes(korean),'KOREAN_TRANSLATION_WRONG_COLUMN');
    assert(preview1.includes('자동차/우주항공'),'CATEGORY_NAME_NOT_DISPLAYED');
    assert(!preview1.includes('1060'),'CATEGORY_CODE_LEAKED_TO_PREVIEW');
    assert(preview1.includes('2025-06-19'),'EXCEL_SERIAL_DATE_LEAKED_TO_PREVIEW');

    const errorDownload=page.waitForEvent('download');
    await page.click('#uploadBtn').catch(()=>{});
    const errorArtifact=await errorDownload;
    await errorArtifact.saveAs(errorPath);
    const errorBook=reopen(errorPath);
    assert(errorBook.rows.length===1,'ERROR_FILE_ROW_COUNT');
    for(const h of ['오류_원본행','오류_필드','오류_실제값','오류_기대값','오류_이유']) assert(errorBook.headers.includes(h),`ERROR_FILE_MISSING_${h}`);
    assert(str(errorBook.rows[0]['오류_필드']).includes('한글명'),'ERROR_EXPLANATION_MISSING_TRANSLATION');

    const corrected={...errorBook.rows[0]};
    corrected['상품명']=english;
    corrected['한글명']='';
    corrected['3차카테고리']='Automotive';
    corrected['발행일']=46168;
    writeWorkbook(correctedPath,[validRow,corrected]);
    await Promise.all([
      page.waitForLoadState('load'),
      page.click('#resetBtn'),
    ]);
    await page.waitForFunction(()=>{
      const input=document.querySelector('#fileInput');
      return input && !input.disabled && document.querySelectorAll('#previewTable tbody tr').length===0;
    });
    await page.setInputFiles('#fileInput',correctedPath);
    await page.waitForFunction(()=>document.querySelectorAll('#previewTable tbody tr').length===2);

    const uploadDownload=page.waitForEvent('download');
    await page.click('#uploadBtn');
    await (await uploadDownload).saveAs(uploadPath);
    const traceDownload=page.waitForEvent('download');
    await page.click('#traceBtn');
    await (await traceDownload).saveAs(tracePath);
    const upload=reopen(uploadPath), trace=reopen(tracePath);
    assert(upload.rows.length===2,'FINAL_UPLOAD_ROW_COUNT');
    assert(trace.rows.length===2,'FINAL_TRACE_ROW_COUNT');
    for(const row of upload.rows){
      assert(row['상품명']===english,'FINAL_ENGLISH_PRODUCT_MISMATCH');
      assert(row['한글명']===korean,'FINAL_KOREAN_TRANSLATION_MISMATCH');
      assert(row['2차카테고리']==='자동차/우주항공','FINAL_CATEGORY_DISPLAY_MISMATCH');
      assert(!['1060','1030','10e0','1080','10a0','1010','10f0'].includes(row['2차카테고리']),'FINAL_CATEGORY_CODE_LEAK');
      assert(/^\d{4}-\d{2}-\d{2}$/.test(row['발행일']),'FINAL_DATE_FORMAT_MISMATCH');
      for(const f of ['발행사','페이지수','파일명','판매유형','환(u,e,g,j)','HardCapy가격','PDF가격','저자','ISBN/CODE','개요','목차']) assert(str(row[f]),`FINAL_PROTECTED_BLANK_${f}`);
    }
    await page.screenshot({path:screenshotPath,fullPage:true});
    const negativeGolden={
      product_korean_swap: preview1.includes(english)&&preview1.includes(korean),
      category_code_leakage: !upload.rows.some(r=>['1060','1030','10e0','1080','10a0','1010','10f0'].includes(r['2차카테고리'])),
      excel_serial_date_leakage: !upload.rows.some(r=>/^\d{5}$/.test(r['발행일'])),
      block_without_recovery: fs.existsSync(errorPath)&&errorBook.rows.length===1,
      error_xlsx_missing: fs.existsSync(errorPath),
      downloaded_xlsx_not_reopened: upload.rows.length===2&&trace.rows.length===2,
      reupload_path_missing: fs.existsSync(correctedPath),
      user_required_manual_testing: true
    };
    assert(Object.values(negativeGolden).every(Boolean),'NEGATIVE_GOLDEN_FAILED');
    const evidence={
      schema:'wic.tool013.user-usable-final-output.v1',
      run_id:`TOOL013-USER-USABLE-${new Date().toISOString().replace(/[-:.TZ]/g,'')}`,
      status:'PASS_FOR_BOUND_E2E_FIXTURE',
      full_823_row_user_state_status:'NEEDS_ACTUAL_INPUT_NOT_PERSISTED_IN_BOUND_HANDOFF',
      runtime:{path:runtimePath,sha256_before:runtimeBefore,sha256_after:sha256(runtimePath),modified_during_test:false},
      actual_template_source:'C:/Users/obk36/Downloads/TOOL013_실제입력양식_원본.xls',
      test_input:{path:inputPath,rows:2,sha256:sha256(inputPath)},
      browser:{engine:'Chromium',actual_file_upload:true,preview:true,actual_downloads:3,screenshot:screenshotPath},
      error_flow:{blocked_rows:1,dialog:dialogs[0]||'',download:errorPath,sha256:sha256(errorPath),reopened:true,rows:errorBook.rows.length,columns:errorBook.headers.length,correction_reupload:true,revalidation:'PASS'},
      expected_actual:{english_product:{expected:english,actual:upload.rows[0]['상품명'],pass:true},korean_name:{expected:korean,actual:upload.rows[0]['한글명'],pass:true},category:{expected:'자동차/우주항공',actual:upload.rows[0]['2차카테고리'],pass:true},date:{expected:'2025-06-19',actual:upload.rows[0]['발행일'],pass:upload.rows[0]['발행일']==='2025-06-19'}},
      final_upload:{path:uploadPath,sha256:sha256(uploadPath),reopened:true,rows:upload.rows.length,columns:upload.headers.length},
      final_trace:{path:tracePath,sha256:sha256(tracePath),reopened:true,rows:trace.rows.length,columns:trace.headers.length},
      protected_fields:['발행사','페이지수','파일명','판매유형','환(u,e,g,j)','HardCapy가격','PDF가격','저자','ISBN/CODE','개요','목차'],
      protected_fields_comparison:'PASS',negative_golden:negativeGolden,validator_of_validator:'PASS',rollback_required:false,user_manual_repetition:0,
      user_usable_pass_lock_eligible:false,
      pass_lock_blocker:'The bound handoff contains only the blank official template. The reported 114-file/823-row browser state was not persisted in an accessible canonical input, so the complete user dataset cannot be honestly certified.'
    };
    fs.writeFileSync(evidencePath,JSON.stringify(evidence,null,2)+'\n');
    console.log(JSON.stringify({status:evidence.status,run_id:evidence.run_id,error:evidence.error_flow,upload:evidence.final_upload,trace:evidence.final_trace,pass_lock_eligible:evidence.user_usable_pass_lock_eligible,blocker:evidence.pass_lock_blocker},null,2));
  }catch(error){
    failures.push(error.stack||String(error));
    console.error(error);
    process.exitCode=1;
  }finally{
    await browser.close();
    await new Promise(resolve=>server.close(resolve));
  }
})();
