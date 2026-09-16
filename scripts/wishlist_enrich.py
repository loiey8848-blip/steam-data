import json,time
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen
ROOT=Path('data'); p=ROOT/'wishlist.json'
if not p.exists(): raise SystemExit('wishlist.json missing')
data=json.loads(p.read_text(encoding='utf-8')); games=data.get('games',[])
def fetch(appid):
 u='https://store.steampowered.com/api/appdetails?'+urlencode({'appids':appid,'cc':'cn','l':'schinese'})
 with urlopen(Request(u,headers={'User-Agent':'SteamWishlistEnricher/1.0'}),timeout=20) as r: return json.loads(r.read().decode())
for i,g in enumerate(games):
 a=int(g['appid']); g['steam_url']=f'https://store.steampowered.com/app/{a}/'
 try:
  d=fetch(a).get(str(a),{}); x=d.get('data',{}) if d.get('success') else {}; q=x.get('price_overview') or {}
  g.update(name=x.get('name') or g.get('name'),type=x.get('type'),is_free=x.get('is_free'),currency=q.get('currency'),price_initial_cny=round(q['initial']/100,2) if q else None,price_final_cny=round(q['final']/100,2) if q else None,discount_percent=q.get('discount_percent') if q else None)
 except Exception as e: print('metadata skipped',a,e)
 if i and i%40==0: time.sleep(1)
p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
cheap=[g for g in games if g.get('price_final_cny') is not None and g['price_final_cny']<=20]
(ROOT/'wishlist-under-20.json').write_text(json.dumps({'updated_at_utc':data.get('updated_at_utc'),'count':len(cheap),'games':cheap},ensure_ascii=False,indent=2),encoding='utf-8')
print('Wishlist enriched:',len(games),'Steam <=20 CNY:',len(cheap))