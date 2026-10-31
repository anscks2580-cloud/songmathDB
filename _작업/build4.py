# 사용: python3 build4.py <출력json이름> [추가로 합칠 완료 json ...]
# out/batch_*.json, out/variants_*.json 을 읽어 그림을 big/q-PPP.png(300dpi)에서 잘라 넣고 병합.
import json, glob, base64, io, os, sys
from PIL import Image
S=300/130
def crop_fig(fig, pid):
    if not fig: return ""
    if isinstance(fig,str): return fig
    page=int(fig['page']); half=fig['half']; x1,y1,x2,y2=fig['bbox']
    im=Image.open(f'big/q-{page:03d}.png'); W,H=im.size
    off = 0 if half=='L' else (W//2 - int(20*S))
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
outname=sys.argv[1]
json.dump(DB,open(outname,'w',encoding='utf-8'),ensure_ascii=False,indent=1)
ALL=list(DB)
for extra in sys.argv[2:]: ALL+=json.load(open(extra,encoding='utf-8'))
UNITS=json.load(open('units.json',encoding='utf-8'))
html=open('template2.html',encoding='utf-8').read().replace('__DATA__',json.dumps(ALL,ensure_ascii=False)).replace('__UNITS__',json.dumps(UNITS,ensure_ascii=False))
open('학습지만들기_시범.html','w',encoding='utf-8').write(html)
print('html',len(html),'총문항',len(ALL))
