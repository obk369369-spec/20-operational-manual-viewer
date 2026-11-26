import sys, json, os
from playwright.sync_api import sync_playwright

def audit_html(file_path):
    res = {"file": file_path, "pass": True, "errors": [], "metrics": {}}
    if not os.path.exists(file_path):
        res["pass"] = False
        res["errors"].append("FILE_NOT_FOUND")
        return res
    url = "file://" + os.path.abspath(file_path)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page_errors = []
        page.on("pageerror", lambda err: page_errors.append(str(err)))
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=15000)
            page.wait_for_timeout(500)
            text_len = len(page.inner_text("body").strip())
            btn_cnt = page.locator("button, input[type=button], input[type=submit]").count()
            input_cnt = page.locator("input, select, textarea").count()
            html_raw = page.content()
            forbidden = ["TODO:", "FIXME:", "not implemented", "구현 예정", "createInitialSampleData", "sample-1"]
            found_bad = [k for k in forbidden if k in html_raw]
            res["metrics"] = {"text_len": text_len, "buttons": btn_cnt, "inputs": input_cnt, "forbidden": found_bad}
            if text_len < 30:
                res["pass"] = False
                res["errors"].append("EMPTY_RENDER_BODY")
            if page_errors:
                res["pass"] = False
                res["errors"].extend(["JS_RUNTIME_ERROR: " + e for e in page_errors[:3]])
            if found_bad:
                res["pass"] = False
                res["errors"].append("FORBIDDEN_STUB_OR_SAMPLE: " + ",".join(found_bad))
        except Exception as e:
            res["pass"] = False
            res["errors"].append("LOAD_FAIL: " + str(e))
        finally:
            browser.close()
    return res

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else ""
    print(json.dumps(audit_html(target), ensure_ascii=False))
