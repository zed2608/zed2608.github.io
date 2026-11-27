"""Run: python -m pip install playwright; python -m playwright install chromium; python tests/browser_smoke.py."""
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
from playwright.sync_api import sync_playwright
import os, json, time
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
 p.locator('#credential-deans').evaluate("e=>{e.closest('details').open=true}");p.locator('#credential-deans').click();assert p.locator('#certificate-large img').count()==0;assert p.locator('#certificate-large small').inner_text()=='';assert 'official certificate image pending' not in p.locator('#credential-deans').inner_text().lower();p.locator('#credential-detail-close').click();results.append('Dean’s List contains no portrait, fabricated certificate or pending wording')
 p.evaluate("location.hash='journey'");p.wait_for_timeout(300);p.locator('#journey-1 .chapter-open').click();assert p.locator('#chapter-detail').is_visible();p.locator('#chapter-detail-close').click();results.append('Journey detail')
 for w in [320,390,768,1024]:
  p.set_viewport_size({'width':w,'height':844});p.evaluate("location.hash='welcome'");p.wait_for_timeout(250);assert p.evaluate('document.documentElement.scrollWidth <= innerWidth+2'),w
  if w==390:p.screenshot(path=output/'mobile.png')
  results.append(f'{w}px home width')
 context.close()
 # Full-motion path, verify arrival and exact page marker positioning after settled navigation.
 c=browser.new_context(viewport={'width':1440,'height':900},reduced_motion='no-preference');p=c.new_page();p.on('pageerror',lambda e:errors.append(str(e)))
 if 'INLINE_PREVIEW' not in os.environ:
  p.add_init_script("""window.__boInitialFrames=[];function sample(){const shell=document.querySelector('.shell'),arrival=document.querySelector('#arrival-21');if(shell&&!document.documentElement.dataset.scene){window.__boInitialFrames.push({shellHidden:getComputedStyle(shell).opacity==='0',loaderVisible:!!arrival&&getComputedStyle(arrival).display!=='none'});}if(!document.documentElement.dataset.scene)requestAnimationFrame(sample);}requestAnimationFrame(sample);""")
  def delay_main(route):
   time.sleep(.7);route.continue_()
  p.route('**/js/portfolio.js*',delay_main)
 p.set_content(Path(os.environ['INLINE_PREVIEW']).read_text(),wait_until='load') if 'INLINE_PREVIEW' in os.environ else p.goto(url,wait_until='networkidle');p.wait_for_timeout(11000);assert p.locator('#arrival-21').is_hidden();assert p.locator('#v26-thread').count()==1;assert float(p.locator('#arrival-21').get_attribute('data-orbit-degrees'))==360;assert float(p.locator('#arrival-21').get_attribute('data-title-orbit-degrees'))==100;assert p.locator('#v26-thread').is_enabled();assert p.locator('.formal-portrait').evaluate('e=>e.naturalWidth===540 && e.naturalHeight===675 && e.currentSrc.includes("profile-photo.webp")');p.locator('#v26-thread').hover();p.locator('#v26-thread').click();p.wait_for_function("document.querySelector('#v26-thread').dataset.lastRocketSound === 'click'");assert p.locator('#v26-thread').evaluate("e=>e.classList.contains('dock-pulse')");p.mouse.move(20,20);p.locator('#v26-thread').hover();p.wait_for_function("document.querySelector('#v26-thread').dataset.lastRocketSound === 'hover'");assert not p.locator('html').evaluate("e=>e.classList.contains('portfolio-boot')");assert p.evaluate("""()=>{const r=document.querySelector('#v26-thread').getBoundingClientRect(),a=document.querySelector('.profile>.comet-home').getBoundingClientRect();return Math.hypot((r.left+r.width/2)-(a.left+a.width/2),(r.top+r.height/2)-(a.top+a.height/2))<2}""");p.evaluate("location.hash='work'");p.wait_for_function("document.querySelector('#v26-thread').dataset.engineSound === 'playing'");p.wait_for_timeout(4500);assert p.locator('#work').is_visible();assert p.locator('#v26-thread').get_attribute('data-engine-sound')=='stopped';p.evaluate("location.hash='welcome'");p.wait_for_timeout(4500);assert p.locator('#welcome').is_visible();results.append('Full-motion full orbit, enhanced portrait, rocket dock interaction and forward/reverse navigation')
 p.evaluate("location.hash='contact'");p.wait_for_timeout(4500);assert p.locator('.profile .portrait-mark').is_hidden();results.append('No duplicate contact signature')
 p.evaluate("location.hash='welcome'");p.wait_for_timeout(4500);p.locator('#menu-trigger').click();p.locator('#theme-light').click();p.locator('#menu-close').click();p.wait_for_timeout(350);p.locator('.profile').hover();p.wait_for_timeout(500);assert p.locator('.profile').evaluate("e=>getComputedStyle(e,'::before').opacity")=='1';results.append('Light profile hover effect')
 p.locator('.pet-cat').click();assert 'Meow!' in p.locator('#pet-status').inner_text();p.wait_for_function("(document.querySelector('#cat-voice').currentTime > .04 || document.querySelector('#pet-station').dataset.soundBackend === 'webaudio') && document.querySelector('#pet-station').dataset.lastSound === 'cat'");p.wait_for_timeout(900);p.locator('.pet-dog').click();assert 'Woof!' in p.locator('#pet-status').inner_text();p.wait_for_function("(document.querySelector('#dog-voice').currentTime > .04 || document.querySelector('#pet-station').dataset.soundBackend === 'webaudio') && document.querySelector('#pet-station').dataset.lastSound === 'dog'");results.append('Both pet audio assets play after desktop clicks')
 p.wait_for_timeout(900);p.evaluate("() => { document.querySelector('#cat-voice').play=()=>Promise.reject(new Error('simulated media block')); }");p.locator('.pet-cat').click();p.wait_for_function("document.querySelector('#pet-station').dataset.soundBackend === 'webaudio' && document.querySelector('#pet-station').dataset.lastSound === 'cat'");results.append('Pet Web Audio fallback after blocked media')
 p.locator('#menu-trigger').click()
 assert p.locator('#creative-toggle,#pet-sound-toggle,#rocket-sound-toggle,#sound-toggle,#ambience-toggle').count()==0
 assert p.locator('#effects-sound-toggle,#site-sound-toggle').count()==2
 assert p.locator('#replay-arrival').count()==0
 assert p.evaluate("creative && document.documentElement.classList.contains('creative-mode') && pets && !paused")
 assert p.locator('#site-sound-toggle').get_attribute('aria-pressed')=='true';assert p.locator('#effects-sound-toggle').get_attribute('aria-pressed')=='true'
 p.wait_for_function('sfx && ambience && ambientNodes.length > 0')
 p.locator('#effects-sound-toggle').click();assert p.locator('#effects-sound-toggle').get_attribute('aria-pressed')=='false';assert p.evaluate('!petSounds && !rocketSounds')
 p.locator('#site-sound-toggle').click();assert p.evaluate('!sfx && !ambience && ambientNodes.length === 0 && !petSounds && !rocketSounds')
 p.locator('#site-sound-toggle').click();p.wait_for_function('sfx && ambience && ambientNodes.length > 0');assert p.locator('#site-sound-toggle').get_attribute('aria-pressed')=='true';assert p.evaluate('!petSounds && !rocketSounds')
 p.locator('#effects-sound-toggle').click();p.wait_for_function('petSounds && rocketSounds');assert p.locator('#effects-sound-toggle').get_attribute('aria-pressed')=='true'
 p.locator('#site-sound-toggle').click();assert p.evaluate('!sfx && !ambience && ambientNodes.length === 0 && petSounds && rocketSounds')
 p.locator('#menu-close').click();results.append('Two independent grouped sound controls; creative toggle removed')
 if 'INLINE_PREVIEW' not in os.environ:
  frames=p.evaluate('window.__boInitialFrames');assert frames and all(f['shellHidden'] and f['loaderVisible'] for f in frames),frames;results.append('No portfolio flash before delayed startup')
 # A real touch/mobile browser context, not merely a narrow desktop viewport.
 mobile=browser.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,device_scale_factor=3,reduced_motion='no-preference')
 mp=mobile.new_page();mp.on('pageerror',lambda e:errors.append(str(e)))
 if 'INLINE_PREVIEW' not in os.environ:
  mp.goto(url,wait_until='domcontentloaded');assert mp.locator('#arrival-21').is_visible();assert mp.locator('#v26-thread').count()==1
  if mp.locator('#arrival-rocket-audio').get_attribute('aria-label')=='Play arrival and site audio': mp.locator('#arrival-rocket-audio').tap()
  mp.wait_for_function("document.documentElement.dataset.audioState === 'running' && document.querySelector('#v26-thread').dataset.engineSound === 'playing' && ambientNodes.length > 0")
  results.append('Arrival engine and ambient audio enabled together on mobile activation')
  mp.wait_for_timeout(10000);assert mp.locator('#arrival-21').is_hidden();assert mp.locator('#welcome').is_visible()
  assert mp.evaluate("document.documentElement.scrollWidth <= innerWidth+2")
  mp.locator('.rail a[href="#work"]').tap();mp.wait_for_timeout(4500);assert mp.locator('#work').is_visible()
  mp.locator('.rail a[href="#welcome"]').tap();mp.wait_for_timeout(4500);assert mp.locator('#welcome').is_visible()
  mp.locator('.pet-cat').tap();mp.wait_for_function("(document.querySelector('#cat-voice').currentTime > .04 || document.querySelector('#pet-station').dataset.soundBackend === 'webaudio') && document.querySelector('#pet-station').dataset.lastSound === 'cat'")
  results.append('Touch/mobile arrival, forward/reverse transitions and pet audio playback')
 mobile.close();browser.close()
 if 'INLINE_PREVIEW' not in os.environ:
  autoplay_browser=pw.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium') if Path(os.environ.get('CHROMIUM_PATH','/usr/bin/chromium')).exists() else None,args=['--no-sandbox','--autoplay-policy=no-user-gesture-required'])
  ap=autoplay_browser.new_page();ap.on('pageerror',lambda e:errors.append(str(e)));ap.goto(url,wait_until='domcontentloaded')
  ap.wait_for_function("document.documentElement.dataset.audioState==='running' && document.querySelector('#v26-thread').dataset.engineSound==='playing' && ambientNodes.length>0")
  ap.wait_for_function("document.documentElement.dataset.openingSound==='playing' || document.documentElement.dataset.openingSound==='ended'")
  assert ap.locator('#arrival-rocket-audio').get_attribute('aria-label')=='Mute all audio';autoplay_browser.close();results.append('Autoplay-permitted browser starts opening cue, engine and ambience without interaction')
server.shutdown();print(json.dumps({'checks':results,'page_errors':errors,'failed_http':failed},indent=2));assert not errors and not failed
