"""Dependency-free static check for the release package."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
from collections import Counter
from xml.etree import ElementTree
ROOT=Path(__file__).resolve().parents[1]
class Audit(HTMLParser):
 def __init__(self): super().__init__(); self.ids=[]; self.links=[]; self.cases=0; self.images=0
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id' in a:self.ids.append(a['id'])
  if tag=='article' and 'case' in a.get('class','').split():self.cases+=1
  if tag=='img' and a.get('src'):self.images+=1;assert a.get('alt'),a['src']
  for k in ('src','href'):
   if a.get(k):self.links.append(a[k])
p=Audit();p.feed((ROOT/'index.html').read_text(encoding='utf8'));assert p.cases==9;assert all(n==1 for n in Counter(p.ids).values())
for link in p.links:
 u=urlsplit(link)
 if u.scheme or u.netloc:continue
 if not u.path:assert not u.fragment or u.fragment in p.ids,link
 else:assert (ROOT/unquote(u.path)).is_file(),link
assert (ROOT/'.nojekyll').exists();assert (ROOT/'documents/resume.pdf').read_bytes().startswith(b'%PDF');ElementTree.parse(ROOT/'sitemap.xml');assert (ROOT/'assets/social-preview.png').is_file()
print(f'Passed: {p.cases} case studies, {p.images} image references, {len(p.ids)} unique IDs, all local links resolve.')
