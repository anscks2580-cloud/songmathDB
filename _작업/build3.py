import json, glob, base64, io, os
from PIL import Image
S=300/130
def crop_fig(fig, pid):
    if not fig: return ""
    if isinstance(fig,str): return fig
    page=int(fig['page']); half=fig['half']; x1,y1,x2,y2=fig['bbox']
    im=Image.open(f'big/q-{page:03d}.png'); W,H=im.size
    off = 0 if half=='L' else (W//2 - int(30*S))
    box=(max(0,int(x1*S)+off-8), max(0,int(y1*S)-8), min(W,int(x2*S)+off+8), min(H,int(y2*S)+8))
    c=im.crop(box).convert('RGB'); os.makedirs('figs',exist_ok=True); c.save(f'figs/{pid}.png')
    b=io.BytesIO(); c.save(b,'PNG',optimize=True)
    return "data:image/png;base64,"+base64.b64encode(b.getvalue()).decode()
DB=[]
for f in sorted(glob.glob('out/batch_*.json'))+sorted(glob.glob('out/variants_*.json')):
    for p in json.load(open(f,encoding='utf-8')):
        p.setdefault('parent',''); p.setdefault('variant','')
        p['figure']=crop_fig(p.get('figure'), p['id'])
        if p.get('choicesFigure'): p['choicesFigure']=crop_fig(p['choicesFigure'], p['id']+'-choices')
        DB.append(p)
byid={p['id']:p for p in DB}
for p in DB:
    if p['figure']=='=parent': p['figure']=byid.get(p['parent'],{}).get('figure','')
order={'':0,'easy':1,'similar':2,'hard':3}
DB.sort(key=lambda p:(p['num'][:4], order.get(p['variant'],9)))
print('원본',sum(1 for p in DB if not p['parent']),'변형',sum(1 for p in DB if p['parent']))
UNITS=json.load(open('units.json',encoding='utf-8'))
html=open('template2.html',encoding='utf-8').read().replace('__DATA__',json.dumps(DB,ensure_ascii=False)).replace('__UNITS__',json.dumps(UNITS,ensure_ascii=False))
open('학습지만들기_시범.html','w',encoding='utf-8').write(html)
json.dump(DB,open('문항DB_공수2_1단원.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
print('html',len(html))
