from pathlib import Path
import re, html
import markdown
from playwright.sync_api import sync_playwright

ROOT = Path('public')
ROOT.mkdir(exist_ok=True)
CSS = r'''
:root{--ink:#183348;--muted:#586d7d;--teal:#007d79;--line:#dce5e9;--paper:#fff}*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#edf2f4;color:var(--ink);font:16px/1.7 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}a{color:#006e79;text-underline-offset:3px;overflow-wrap:anywhere}a:focus-visible{outline:3px solid #eeb65b;outline-offset:4px}.masthead{background:#102e40;color:white;padding:36px max(24px,calc((100vw - 1080px)/2))}.brand{font-size:12px;letter-spacing:.18em;text-transform:uppercase;color:#91ddd6}.masthead h1{color:white;font-size:clamp(30px,5vw,48px);letter-spacing:-.035em;line-height:1.15;margin:12px 0}.masthead p{color:#c5d9e3;margin:8px 0;font-size:14px}.toolbar{display:flex;flex-wrap:wrap;gap:12px;margin-top:24px}.button{display:inline-block;padding:10px 18px;border-radius:9px;text-decoration:none;background:#a6ece0;color:#102e40;font-weight:700}.button.secondary{background:#294656;color:white}main{max-width:1080px;margin:28px auto;padding:0 24px}.contents{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:24px}.contents a{font-size:13px;background:white;border:1px solid var(--line);padding:6px 12px;border-radius:30px;text-decoration:none}.section{background:white;border:1px solid var(--line);border-radius:16px;padding:28px;margin-bottom:22px;box-shadow:0 4px 16px #16354904;scroll-margin-top:20px}h2{font-size:23px;line-height:1.3;letter-spacing:-.02em;display:flex;gap:12px;align-items:center;margin:0 0 22px}h3{line-height:1.35}.icon{display:inline-flex;align-items:center;justify-content:center;width:38px;height:38px;background:#e5f4f1;color:var(--teal);border-radius:10px;flex-shrink:0}.icon svg{width:22px;height:22px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}p{margin:0 0 15px}li{margin-bottom:10px}ul,ol{padding-left:24px}.overview{background:#e9f6f2;border-color:#c4e2d9}.overview ul{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;padding:0;list-style:none}.overview li{background:white;border:1px solid #d7e8e2;border-radius:12px;padding:18px;margin:0;font-size:15px}.overview li strong{color:#005f5a}.news-card{border-left:3px solid #47a69a;padding:5px 0 5px 18px;margin:20px 0}.news-card p{margin:0}.table-wrap{overflow-x:auto;border:1px solid var(--line);border-radius:10px;margin:20px 0}table{width:100%;border-collapse:collapse;font-size:14px}th{background:#153c50;color:white;font-weight:600}th,td{text-align:left;padding:12px 14px;border-bottom:1px solid var(--line);vertical-align:top}tbody tr:nth-child(even){background:#f4f8f9}td:not(:first-child){font-variant-numeric:tabular-nums}.up{color:#007469;font-weight:700}.down{color:#b43844;font-weight:700}.status{color:#795213;background:#fff4d9;border-radius:5px;padding:2px 5px;font-size:12px}.footnote{font-size:12px;color:var(--muted);padding:8px 0 28px}.section a{font-size:13px}.section li a{font-size:inherit}@media(max-width:700px){main{padding:0 14px;margin-top:18px}.masthead{padding:28px 20px}.section{padding:20px;border-radius:12px}h2{font-size:20px}.overview ul{grid-template-columns:1fr;gap:10px}table{min-width:550px}.contents{gap:6px}}
@page{size:A4;margin:16mm 14mm 18mm}@media print{body{background:white;font-size:10pt;line-height:1.5;-webkit-print-color-adjust:exact;print-color-adjust:exact}.masthead{padding:22px 24px;border-radius:12px}.masthead h1{font-size:26pt}.masthead p{font-size:9pt}.brand{font-size:8pt}main{margin:18px 0 0;padding:0;max-width:none}.toolbar,.contents{display:none}.section{box-shadow:none;padding:17px;margin-bottom:16px;border-radius:10px}h2{font-size:15pt;margin-bottom:13px;break-after:avoid}.icon{width:30px;height:30px}.icon svg{width:18px;height:18px}.overview ul{display:block;margin:0}.overview li{padding:10px 13px;margin-bottom:8px;font-size:10pt;break-inside:avoid}.news-card{break-inside:avoid;margin:13px 0;padding-left:12px}p{orphans:3;widows:3;margin-bottom:10px}.table-wrap{overflow:visible; border-radius:0;break-inside:auto}table{display:table;min-width:0;font-size:8.5pt}thead{display:table-header-group}tr{break-inside:avoid}th,td{padding:7px 8px}.section a{font-size:8pt}.footnote{font-size:8pt}li{break-inside:avoid}.status{font-size:8pt}}
/* Newspaper edition */
body{background:#eef0f1;color:#273139;font-size:16px}
.masthead{background:#fff;color:#273139;max-width:900px;margin:24px auto 0;padding:32px 26px;border-top:4px solid #ad8537;border-bottom:1px solid #d7dadd}
.masthead h1{color:#24313a;font-family:Georgia,serif;font-size:clamp(42px,7vw,58px);letter-spacing:-.04em}.masthead p{color:#58636a}.brand{color:#98752e}
main{max-width:900px}.section{border-radius:3px;border-left:4px solid #b28b42;box-shadow:none;padding:24px}
h2{font:700 12px/1.5 ui-monospace,monospace;letter-spacing:.14em;text-transform:uppercase}
h3{font:700 25px/1.25 Georgia,serif}.icon{background:#f7f2e7;color:#96722a;border-radius:3px}
.button,.button.secondary{border-radius:3px;background:#f3ead6;color:#453a24}.contents a{border-radius:3px}
.overview{background:#fff}.overview li{border-radius:3px;border-top:3px solid #b28b42}.overview li strong{color:#453a24}
.tech{border-left-color:#76529b}.tech .icon{color:#76529b;background:#f1edf7}
.market-value{font:700 32px/1.3 ui-monospace,monospace}.badge{display:inline-block;border:1px solid #d8d9db;padding:3px 6px;font:12px ui-monospace,monospace}
.editorial-columns{display:grid;grid-template-columns:1fr 1fr;gap:24px}.editorial-column{min-width:0}
th{background:#f2eee5;color:#3b3b36}td{overflow-wrap:anywhere}table{table-layout:fixed}.table-wrap{border-radius:0}
@media(max-width:700px){.masthead{margin:0}.section{padding:18px}table{min-width:0}.editorial-columns{grid-template-columns:1fr}
thead{position:absolute;clip:rect(0,0,0,0);width:1px;height:1px;overflow:hidden}
table,tbody,tr,td{display:block;width:100%}tr{border-bottom:1px solid #cfd4d7;padding:8px 0}
td{display:grid;grid-template-columns:minmax(95px,35%) 1fr;border:0;padding:6px 10px;gap:10px}
td:before{content:attr(data-label);font-weight:700;color:#596269;font-size:12px}}
@media print{.masthead{margin:0;padding:14px 0;background:white;border-radius:0}.masthead h1{font-size:32pt}.section{border-radius:0;padding:14px}h3{font-size:16pt;break-after:avoid}.editorial-columns{display:block}.market-value{font-size:22pt}thead{position:static;clip:auto;width:auto;height:auto;display:table-header-group}table{display:table;table-layout:fixed}tbody{display:table-row-group}tr{display:table-row}td{display:table-cell;width:auto}td:before{display:none}}

'''

def icon(title):
    paths = {
        'overview':'<path d="m13 2-8 12h6l-1 8 9-13h-7z"/>',
        'news':'<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M7 7h10M7 11h10M7 15h4M7 18h10"/>',
        'finance':'<path d="M3 9h18L12 3zM5 9v10m7-10v10m7-10v10M3 21h18"/>',
        'stocks':'<path d="M3 3v18h18M6 16l5-5 4 3 6-8m-5 0h5v5"/>',
        'global':'<circle cx="12" cy="12" r="9"/><ellipse cx="12" cy="12" rx="4" ry="9"/><path d="M3 12h18M5 7h14M5 17h14"/>',
        'watch':'<circle cx="12" cy="12" r="9"/><path d="M12 6v6l4 2"/>',
        'takeaways':'<path d="m4 6 2 2 4-4m-6 10 2 2 4-4m-6 10 2 2 4-4M13 6h8M13 14h8M13 22h8"/>',
    }
    key=next((k for k in paths if k in title.lower()),'news')
    if '60-second' in title: key='overview'
    if '3 things' in title: key='takeaways'
    return '<span class="icon" aria-hidden="true"><svg viewBox="0 0 24 24">'+paths[key]+'</svg></span>'

def render(text, archive=False):
    chunks=re.split(r'^##\s+(.+)$',text,flags=re.M)
    intro=chunks[0]
    title=re.search(r'^#\s+(.+)',intro,re.M)
    title=title.group(1) if title else 'Singapore Morning Briefing'
    intro=re.sub(r'^#\s+.+\n?', '',intro,flags=re.M)
    md=lambda s: markdown.markdown(s,extensions=['tables','fenced_code'])
    sections=[]; links=[]
    for i in range(1,len(chunks),2):
        heading=chunks[i]; body=md(chunks[i+1]); sid='section-'+str(i)
        if 'developments' in heading.lower():
            body=re.sub(r'(<p><strong>\d+\..*?</p>)',r'<article class="news-card">\1</article>',body,flags=re.S)
        def label_table(match):
            table=match.group(0)
            labels=re.findall(r'<th[^>]*>(.*?)</th>',table,flags=re.S)
            def row(m):
                idx=iter(labels)
                return re.sub(r'<td([^>]*)>',lambda cell: '<td'+cell.group(1)+' data-label="'+html.escape(re.sub('<.*?>','',next(idx,'')),quote=True)+'">',m.group(0))
            return re.sub(r'<tr>.*?</tr>',row,table,flags=re.S)
        body=re.sub(r'<table>.*?</table>',label_table,body,flags=re.S)
        body=re.sub(r'<table>(.*?)</table>',r'<div class="table-wrap"><table>\1</table></div>',body,flags=re.S)
        body=re.sub(r'<td>([+]\d[^<]*)</td>',r'<td class="up">\1</td>',body)
        body=re.sub(r'<td>([−-]\d[^<]*)</td>',r'<td class="down">\1</td>',body)
        body=re.sub(r'<td>(Conflicting|Unverified)</td>',r'<td><span class="status">\1</span></td>',body)
        klass='section overview' if '60-second' in heading else ('section tech' if 'TECH & AI' in heading else 'section')
        sections.append(f'<section class="{klass}" id="{sid}"><h2>{icon(heading)}{html.escape(heading)}</h2>{body}</section>')
        links.append(f'<a href="#{sid}">{html.escape(heading)}</a>')
    nav='<a class="button" href="latest.pdf">Download PDF</a><a class="button secondary" href="archive.html">Past briefings</a>'
    if archive: nav='<a class="button" href="index.html">Latest briefing</a>'
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Singapore morning news, finance and markets with dated quotes and linked sources."><title>{html.escape(title)}</title><style>{CSS}</style></head><body><header class="masthead"><div class="brand">Harbour Dispatch / Singapore</div><h1>{html.escape(title)}</h1>{md(intro)}<nav class="toolbar" aria-label="Downloads and archive">{nav}</nav></header><main><nav class="contents" aria-label="Briefing sections">{''.join(links)}</nav>{''.join(sections)}<footer class="footnote">Sources are linked beside each item. Quote dates and verification limits appear with the relevant figures. All times are Singapore time unless stated otherwise.</footer></main></body></html>'''

current=Path('briefings/current.md').read_text()
(ROOT/'index.html').write_text(render(current))
entries=[]
for item in sorted(Path('briefings').glob('????-??-??.md'),reverse=True):
    name=item.stem
    (ROOT/(name+'.html')).write_text(render(item.read_text(),True))
    entries.append(f'- [{name}]({name}.html)')
(ROOT/'archive.html').write_text(render('# Previous briefings\n\n## Archive\n\n'+'\n'.join(entries),True))
with sync_playwright() as p:
    browser=p.chromium.launch()
    tab=browser.new_page()
    tab.goto((ROOT/'index.html').resolve().as_uri())
    tab.pdf(path=str(ROOT/'latest.pdf'),format='A4',print_background=True,display_header_footer=True,header_template='<span></span>',footer_template='<div style="font-family:Arial;font-size:9px;width:100%;text-align:center;color:#586d7d">HARBOUR DISPATCH · Singapore Morning Briefing &nbsp; | &nbsp; <span class="pageNumber"></span> / <span class="totalPages"></span></div>',margin={'top':'16mm','bottom':'18mm','left':'14mm','right':'14mm'})
    browser.close()
(ROOT/'.nojekyll').touch()
