"""Run: python -m pip install playwright; python -m playwright install chromium; python tests/browser_smoke.py."""
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
from playwright.sync_api import sync_playwright
import os, json
ROOT=Path(__file__).resolve().parents[1]
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args): pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT))); Thread(target=server.serve_forever,daemon=True).start();url=f'http://127.0.0.1:{server.server_port}/'
output=Path(os.environ.get('PREVIEW_DIR','/tmp/bo43_previews'));output.mkdir(exist_ok=True,parents=True)
errors=[];failed=[];results=[]
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium') if Path(os.environ.get('CHROMIUM_PATH','/usr/bin/chromium')).exists() else None,args=['--no-sandbox'])
 context=browser.new_context(viewport={'width':1440,'height':900},reduced_motion='reduce',color_scheme='light');p=context.new_page();p.on('pageerror',lambda e:errors.append(str(e)));p.on('response',lambda r: failed.append(f'{r.status} {r.url}') if r.status>=400 and r.url.startswith(url) else None)
 p.set_content(Path(os.environ['INLINE_PREVIEW']).read_text(),wait_until='load') if 'INLINE_PREVIEW' in os.environ else p.goto(url,wait_until='networkidle');assert p.locator('html').get_attribute('data-ajr-theme')=='dark';p.screenshot(path=output/'home_dark.png');results.append('Dark opens on light-preference browser')
 p.locator('#menu-trigger').click();p.locator('#theme-light').click();assert p.locator('html').get_attribute('data-ajr-theme')=='light';p.locator('#menu-close').click();p.wait_for_timeout(350);p.screenshot(path=output/'home_light.png');p.locator('#menu-trigger').click();p.locator('#theme-dark').click();p.locator('#menu-close').click();p.wait_for_timeout(350);results.append('Theme toggle')
 assert p.locator('a[aria-label="View public résumé (PDF)"]').count()==2;assert (ROOT/'documents/resume.pdf').is_file();results.append('Public résumé link')
 routes=['work','project-index','journey','credentials','about','contact']+['project-'+x for x in ['thesis','champion','bytesize','lokal','golden','shrms','quizzify','jonas','rps']]
 for r in routes:
  p.evaluate('(r)=>location.hash=r',r);p.wait_for_timeout(350)
  visible=p.locator('#'+r);assert visible.is_visible(),r
  assert p.evaluate('document.documentElement.scrollWidth <= innerWidth+2'),r
  imgs=visible.locator('img');
  for i in range(imgs.count()):
   img=imgs.nth(i);assert img.evaluate('(e)=>{e.loading="eager";return e.decode().then(()=>e.naturalWidth>0).catch(()=>false)}'),(r,i)
  if r in ['work','project-index','credentials','contact','project-thesis']:p.screenshot(path=output/(r+'.png'))
  results.append(r+' renders, no horizontal overflow, images decode')
 p.evaluate("location.hash='work'");p.wait_for_timeout(300);p.locator('[data-album="2"]').click();p.wait_for_timeout(250);assert 'ByteSize' in p.locator('#gallery-name').inner_text();results.append('Album selection')
 p.evaluate("location.hash='project-thesis'");p.wait_for_timeout(300);p.locator('#project-thesis [data-gallery]').first.click();p.wait_for_timeout(150);assert p.locator('#portfolio-lightbox').is_visible();p.locator('#showcase-next').click();assert p.locator('#showcase-count').inner_text().startswith('02');p.locator('#showcase-close').click();results.append('Gallery opens and advances')
 p.evaluate("location.hash='credentials'");p.wait_for_timeout(300);p.locator('#credential-sap-ai').click();assert p.locator('#credential-detail').is_visible();assert p.locator('#certificate-large img').count()==1;p.locator('#credential-detail-close').click();results.append('Certificate detail')
 p.locator('#credential-deans').evaluate("e=>{e.closest('details').open=true}");p.locator('#credential-deans').click();assert p.locator('#certificate-large img').count()==0;assert 'pending' in p.locator('#certificate-large small').inner_text().lower();p.locator('#credential-detail-close').click();results.append('Pending credential contains no portrait or certificate image')
 p.evaluate("location.hash='journey'");p.wait_for_timeout(300);p.locator('#journey-1 .chapter-open').click();assert p.locator('#chapter-detail').is_visible();p.locator('#chapter-detail-close').click();results.append('Journey detail')
 for w in [320,390,768,1024]:
  p.set_viewport_size({'width':w,'height':844});p.evaluate("location.hash='welcome'");p.wait_for_timeout(250);assert p.evaluate('document.documentElement.scrollWidth <= innerWidth+2'),w
  if w==390:p.screenshot(path=output/'mobile.png')
  results.append(f'{w}px home width')
 context.close()
 # Full-motion path, verify arrival and exact page marker positioning after settled navigation.
 c=browser.new_context(viewport={'width':1440,'height':900},reduced_motion='no-preference');p=c.new_page();p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(Path(os.environ['INLINE_PREVIEW']).read_text(),wait_until='load') if 'INLINE_PREVIEW' in os.environ else p.goto(url,wait_until='networkidle');p.wait_for_timeout(10000);assert p.locator('#arrival-21').is_hidden();assert p.locator('#v26-thread').count()==1;assert not p.locator('html').evaluate("e=>e.classList.contains('portfolio-boot')");assert p.evaluate("""()=>{const r=document.querySelector('#v26-thread').getBoundingClientRect(),a=document.querySelector('.profile>.comet-home').getBoundingClientRect();return Math.hypot((r.left+r.width/2)-(a.left+a.width/2),(r.top+r.height/2)-(a.top+a.height/2))<2}""");p.evaluate("location.hash='work'");p.wait_for_timeout(4500);assert p.locator('#work').is_visible();p.evaluate("location.hash='welcome'");p.wait_for_timeout(4500);assert p.locator('#welcome').is_visible();results.append('Full-motion arrival and forward/reverse navigation');browser.close()
server.shutdown();print(json.dumps({'checks':results,'page_errors':errors,'failed_http':failed},indent=2));assert not errors and not failed
