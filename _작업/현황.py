# 결과 폴더의 JSON을 세어 차수별 현황표를 만들고, 진행표.md의 "## 현황" 절 + 문제DB\현황.md·현황.html 을 갱신한다.
# 매 작업 끝에 실행: python3 _작업/현황.py
import json, glob, os, re, datetime, math
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES=os.path.join(ROOT,'결과')
PER_RUN=140; RUNS_PER_DAY=3   # 하루 실제 돌리는 횟수에 맞춰 수정
# (결과 폴더명, 추정 총 문항) — 차수별. 결과 폴더가 생기면 자동으로 집계됨
TIERS=[
 ('학원교재 (세쌍둥이, 쎈과 나란히)',[('세쌍둥이 공통수학1',594),('세쌍둥이 대수',600),('세쌍둥이 공통수학2',600),('세쌍둥이 미적분1',600)]),
 ('1차 — 2027년 1학기',[('쎈 공통수학1',1316),('쎈 대수',1100),('개념+유형 중1-1',1300),('개념+유형 중2-1',1350),('쎈 중1-1',1100),('쎈 중2-1',1300)]),
 ('2차 — 1학기 보강·심화 (고등 → 중1 → 중2)',[('개념원리 공통수학1',900),('RPM 공통수학1',1000),('풍산자 라이트유형 공통수학1',800),('풍산자 필수유형 공통수학1',900),('고쟁이 공통수학1',1300),('베이직 쎈 공통수학1',700),('개념+유형 공통수학1 개념편',600),
   ('개념원리 중1-1',900),('RPM 중1-1',1000),('일품 중1-1',600),('체크체크 중1-1',700),('블랙라벨 중1-1',500),('최상위 라이트 중1-1',600),
   ('개념+유형 중2-1 파워',900),('개념원리 중2-1',900),('RPM 중2-1',1000),('유형만렙 중2-1',1200),('일품 중2-1',600),('블랙라벨 중2-1',500)]),
 ('3차 — 2학기 (고등 → 중등)',[('쎈 공통수학2',1100),('쎈 미적분1',1000),('개념원리 공통수학2',900),('개념+유형 공통수학2',1200),('고쟁이 공통수학2',1300),
   ('쎈 중1-2',1100),('쎈 중2-2',1300),('개념+유형 중1-2',1300),('개념+유형 중2-2',1500),('개념원리 중1-2',900),('개념원리 중2-2',900),('RPM 중2-2',1000),('일품 중1-2',600),('일품 중2-2',600),('블랙라벨 중1-2',500),('블랙라벨 중2-2',500),('유형만렙 중2-2',1200),('최상위 라이트 중1-2',600)]),
 ('4차 — 초등 (초5·초6)',[('개념+유형 파워 5-1',900),('최상위S 5-1',500),('디딤돌 기본+유형 6-1',800),('디딤돌 응용 6-1',700),('풍산자 개념×서술형 6-1',500),('풍산자 유형 6-1',700),('최상위 6-1',500),('최상위S 6-1',500),
   ('개념+유형 파워 5-2',900),('최상위 5-2',500),('최상위S 5-2',500),('디딤돌 기본 6-2',700),('최상위 6-2',500),('최상위S 6-2',500),('최상위 부록 경시대회',800)]),
]
def count(name):
    n=0; units=[]
    for f in sorted(glob.glob(os.path.join(RES,name,'*.json'))):
        if os.path.basename(f).startswith(('concepts','_')): continue
        d=json.load(open(f,encoding='utf-8'))
        n+=sum(1 for p in d if not p.get('parent')); units.append(os.path.splitext(os.path.basename(f))[0].split('_',1)[-1])
    return n,units
today=datetime.date.today()
md=[f"## 현황 ({today:%Y-%m-%d} 기준)\n"]; html_sections=[]; grand_done=grand_est=0; tier_summary=[]
for tname,books in TIERS:
    rows=[]; td=te=0; hrows=[]
    for name,est in books:
        n,units=count(name); td+=n; te+=est
        pct=min(100,round(100*n/est)); st='완료' if n>=est*0.97 else ('진행중' if n else '대기')
        rows.append(f"| {name} | {st} | {n:,} / 약 {est:,} | {pct}% | {', '.join(units) if units else '—'} |")
        hrows.append(f"<tr><td>{name}</td><td class='{st}'>{st}</td><td>{n:,} / 약 {est:,}</td><td><div class='bar'><div style='width:{pct}%'></div></div>{pct}%</td><td class='u'>{', '.join(units) if units else '—'}</td></tr>")
    tp=round(100*td/te); grand_done+=td; grand_est+=te
    tier_summary.append((tname,td,te,tp))
    bar='█'*round(20*td/te)+'░'*(20-round(20*td/te))
    md.append(f"### {tname} — {td:,} / 약 {te:,} ({tp}%) {bar}\n\n| 교재 | 상태 | 완료 문항 | 진행률 | 완료 단원 |\n|---|---|---|---|---|\n"+'\n'.join(rows)+'\n')
    html_sections.append(f"<details {'open' if td else ''}><summary><b>{tname}</b> — {td:,} / 약 {te:,} 문항 ({tp}%)<div class='bar big'><div style='width:{tp}%'></div></div></summary><table><tr><th>교재</th><th>상태</th><th>완료 문항</th><th>진행률</th><th>완료 단원</th></tr>{''.join(hrows)}</table></details>")
remain=max(0,grand_est-grand_done); runs=math.ceil(remain/PER_RUN); days=math.ceil(runs/RUNS_PER_DAY); eta=today+datetime.timedelta(days=days)
t1=[t for t in tier_summary if t[0].startswith('1차')][0]; r1=math.ceil((t1[2]-t1[1])/PER_RUN)
foot=f"- 전체 남은 문항 약 {remain:,} → 1회 약 {PER_RUN}문항 기준 약 {runs}회, 하루 {RUNS_PER_DAY}회면 **약 {days}일** (예상 완료 {eta:%Y-%m-%d})\n- 1차만 보면 남은 약 {t1[2]-t1[1]:,}문항 → 약 {r1}회, 하루 {RUNS_PER_DAY}회면 약 {math.ceil(r1/RUNS_PER_DAY)}일\n- 변형문제(쉬움·비슷·어려움 3종)는 위 계산에 포함되지 않음. 교재별 총 문항은 쪽수 기준 추정치(±20%)"
md.append(foot); md='\n'.join(md)+'\n'
p=open(os.path.join(ROOT,'_작업','진행표.md'),encoding='utf-8').read()
p=re.sub(r'## 현황.*?(?=\n## |\Z)',md.rstrip()+'\n',p,flags=re.S) if '## 현황' in p else p.rstrip()+'\n\n'+md
open(os.path.join(ROOT,'_작업','진행표.md'),'w',encoding='utf-8').write(p)
open(os.path.join(ROOT,'현황.md'),'w',encoding='utf-8').write('# 문항 DB 현황\n\n'+md)
gp=round(100*grand_done/grand_est)
tier_cards=''.join(f"<div class='card'><div class='t'>{t[0].split(' — ')[0].split(' (')[0]}</div><div class='n'>{t[3]}%</div><div class='bar'><div style='width:{t[3]}%'></div></div><div class='s'>{t[1]:,} / 약 {t[2]:,}</div></div>" for t in tier_summary)
html=f"""<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>문항 DB 현황</title>
<style>body{{font-family:'Malgun Gothic',sans-serif;max-width:1000px;margin:30px auto;padding:0 20px;color:#222}}
h1{{font-size:22px;margin-bottom:4px}} .sub{{color:#888;font-size:13px;margin-bottom:18px}}
.total{{background:#f5f7fb;border-radius:10px;padding:16px 20px;margin-bottom:16px}} .total .n{{font-size:26px;font-weight:bold}}
.bar{{display:inline-block;width:120px;height:10px;background:#e6e8ee;border-radius:5px;vertical-align:middle;margin-right:8px;overflow:hidden}} .bar div{{height:100%;background:#3b7ddd}}
.bar.big{{display:block;width:100%;height:14px;margin:8px 0 0}} .total .bar{{display:block;width:100%;height:18px;margin-top:8px}}
.cards{{display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin-bottom:20px}} .card{{border:1px solid #e3e5ea;border-radius:10px;padding:12px}}
.card .t{{font-size:13px;color:#555;min-height:34px}} .card .n{{font-size:22px;font-weight:bold;margin:4px 0}} .card .bar{{display:block;width:100%;margin:4px 0}} .card .s{{font-size:12px;color:#888}}
details{{border:1px solid #e3e5ea;border-radius:10px;padding:10px 14px;margin-bottom:12px}} summary{{cursor:pointer;font-size:15px;list-style:none}} summary::-webkit-details-marker{{display:none}}
table{{border-collapse:collapse;width:100%;margin-top:10px}} th,td{{border:1px solid #e3e5ea;padding:6px 10px;text-align:left;font-size:13px}} th{{background:#f5f5f5}} td.u{{color:#666;font-size:12px}}
.완료{{color:#1a7f37;font-weight:bold}} .진행중{{color:#b45309;font-weight:bold}} .대기{{color:#999}} .foot{{font-size:13px;line-height:1.8;color:#444;margin-top:16px}}</style></head><body>
<h1>송우찬수학학원 문항 DB 구축 현황</h1><div class="sub">{today:%Y년 %m월 %d일} 기준 · 원본 문항 기준(변형문제 제외)</div>
<div class="total"><div>전체 진행률</div><div class="n">{grand_done:,} / 약 {grand_est:,} 문항 ({gp}%)</div><div class="bar"><div style="width:{gp}%"></div></div></div>
<div class="cards">{tier_cards}</div>
{''.join(html_sections)}
<div class="foot">{foot.replace(chr(10),'<br>').replace('**','')}</div></body></html>"""
open(os.path.join(ROOT,'현황.html'),'w',encoding='utf-8').write(html)
print(md)
