from pathlib import Path
import re, shutil
import markdown
from playwright.sync_api import sync_playwright

root = Path("public")
root.mkdir(exist_ok=True)
css = """body{font-family:Arial,sans-serif;background:#f1f5f9;color:#172b44;margin:0;line-height:1.6}main{max-width:850px;margin:24px auto;padding:32px;background:white;border-radius:16px}h1,h2,h3{line-height:1.25;color:#123d69}a{color:#0665b7}table{border-collapse:collapse;width:100%;font-size:14px;display:block;overflow-x:auto}th,td{padding:10px;border-bottom:1px solid #dce4ed;text-align:left}th{background:#edf4fa}.nav{display:flex;gap:18px;flex-wrap:wrap;padding:14px 0;border-bottom:1px solid #ddd}@media(max-width:600px){main{margin:0;padding:18px;border-radius:0}h1{font-size:26px}}@media print{body{background:white;font-size:11pt}main{margin:0;padding:0;max-width:none}.nav{display:none}table{display:table;font-size:9pt}h2,h3{break-after:avoid}tr{break-inside:avoid}a{overflow-wrap:anywhere}}"""
def page(text, nav):
    body = markdown.markdown(text, extensions=["tables","fenced_code"])
    return '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Singapore Morning Briefing</title><style>'+css+'</style></head><body><main>'+nav+body+'</main></body></html>'
nav = '<nav class="nav"><a href="latest.pdf">Download PDF</a><a href="archive.html">Previous briefings</a></nav>'
current = Path("briefings/current.md").read_text()
(root/"index.html").write_text(page(current,nav))
entries = []
for item in sorted(Path("briefings").glob("????-??-??.md"), reverse=True):
    name = item.stem
    (root/(name+".html")).write_text(page(item.read_text(),'<nav class="nav"><a href="index.html">Latest briefing</a></nav>'))
    entries.append("- ["+name+"]("+name+".html)")
(root/"archive.html").write_text(page("# Previous briefings\n\n"+("\n".join(entries) or "No archived briefings yet."),'<nav class="nav"><a href="index.html">Latest briefing</a></nav>'))
with sync_playwright() as p:
    browser = p.chromium.launch()
    tab = browser.new_page()
    tab.goto((root/"index.html").resolve().as_uri())
    tab.pdf(path=str(root/"latest.pdf"),format="A4",print_background=True,display_header_footer=True,header_template="<span></span>",footer_template='<div style="font-size:9px;width:100%;text-align:center">Singapore Morning Briefing · <span class="pageNumber"></span> / <span class="totalPages"></span></div>',margin={"top":"18mm","bottom":"18mm","left":"15mm","right":"15mm"})
    browser.close()
(root/".nojekyll").touch()
