"""Build a single-file ROMA atlas and its offline edition."""
from pathlib import Path
import json,base64,argparse
from versioning import stamp
ROOT=Path(__file__).resolve().parents[1];DOCS=ROOT/'docs';SRC=ROOT/'src'
def uri(name):return 'data:image/png;base64,'+base64.b64encode((DOCS/'assets'/name).read_bytes()).decode()
def encode(value):return json.dumps(value,ensure_ascii=False).replace('<','\\u003c')
def build(export):
 data=json.loads((ROOT/'content.json').read_text());ids={p['id'] for p in data['people']};sources={s['id'] for s in data['sources']}
 assert len(ids)==4 and len({c['id'] for c in data['cards']})==len(data['cards'])
 for p in data['people']:
  assert set(p['sources'])<=sources
  for e in p['events']:assert set(e.get('related',[]))<=ids
 for e in data['intersections']:assert set(e['people'])<=ids and set(e['sources'])<=sources
 assets={p['id']:(DOCS/'assets'/(p['id']+'.svg')).read_text() for p in data['people']}
 html=(SRC/'shell.html').read_text()
 for key,val in {'/*__CSS__*/':(SRC/'style.css').read_text()+'\n'+(SRC/'updater.css').read_text(),'__ICON__':uri('mark-96.png'),'<!--__QR__-->':(DOCS/'assets/qr.svg').read_text(),'/*__DATA__*/':'const CONTENT='+encode(data)+';const ASSETS='+encode(assets)+';','/*__LEARNING__*/':(SRC/'learning.js').read_text(),'/*__APP__*/':(SRC/'app.js').read_text(),'/*__UPDATER__*/':(SRC/'updater.js').read_text()}.items():assert key in html;html=html.replace(key,val)
 html=stamp(html,'roma',DOCS);(DOCS/'index.html').write_text(html)
 offline=html.replace('<link rel="manifest" href="site.webmanifest">','')
 for icon in ['favicon-32.png','apple-touch-icon.png']:offline=offline.replace('href="assets/'+icon+'"','href="'+uri(icon)+'"')
 offline=offline.replace('<a class="text-button" href="ROMA.html" download>Скачать для чтения без сети ↓</a>','<span>Открыта автономная копия</span>')
 (DOCS/'ROMA.html').write_text(offline);(DOCS/'.nojekyll').touch()
 if export:export.mkdir(parents=True,exist_ok=True);(export/'ROMA.html').write_text(offline)
 print(f'ROMA: {len(html.encode()):,} bytes; {len(data["cards"])} cards; {len(data["sources"])} sources')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--export',type=Path);build(p.parse_args().export)
