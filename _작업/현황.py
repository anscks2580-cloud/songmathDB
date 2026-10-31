# 결과 폴더의 JSON을 세어 차수별 현황표를 만들고, 진행표.md의 "## 현황" 절 + 문제DB\현황.md·현황.html 을 갱신한다.
# 매 작업 끝에 실행: python3 _작업/현황.py
import json, glob, os, re, datetime, math
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES=os.path.join(ROOT,'결과')
PER_RUN=140; RUNS_PER_DAY=5   # 계획 속도(하루 회차 수). 실측 속도는 START_DATE 이후 누적 문항으로 자동 계산
START_DATE=datetime.date(2026,10,30)   # 본격 변환 시작일
TIER_EXTRA={'1차':['세쌍둥이 대수'],'3차':['세쌍둥이 공통수학2','세쌍둥이 미적분1']}   # 세쌍둥이는 같이 가는 차수에 얹어 날짜 계산
# (결과 폴더명, 추정 총 문항) — 차수별. 결과 폴더가 생기면 자동으로 집계됨
TIERS=[
 ('학원교재 (세쌍둥이, 쎈과 나란히)',[('세쌍둥이 공통수학1',594),('세쌍둥이 대수',658),('세쌍둥이 공통수학2',600),('세쌍둥이 미적분1',600)]),
 ('1차 — 2027년 1학기',[('쎈 공통수학1',1316),('쎈 대수',1250),('개념+유형 중1-1',1300),('개념+유형 중2-1',1350),('쎈 중1-1',1100),('쎈 중2-1',1300)]),
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
# 차수별 예상 완료일: 1차→2차→3차→4차 순서로 이어서 한다고 보고, 세쌍둥이 남은 분량은 TIER_EXTRA대로 얹음
elapsed=max(1,(today-START_DATE).days+1); measured=grand_done/elapsed; planned=PER_RUN*RUNS_PER_DAY
book_remain={name:max(0,est-count(name)[0]) for _,books in TIERS for name,est in books}
tier_eta=[]; cum=0
for tname,td,te,tp in tier_summary:
    if tname.startswith('학원교재'): continue
    key=tname[:2]; r=te-td+sum(book_remain.get(b,0) for b in TIER_EXTRA.get(key,[])); cum+=r
    tier_eta.append((key,r,today+datetime.timedelta(days=math.ceil(cum/measured)),today+datetime.timedelta(days=math.ceil(cum/planned))))
eta_md='| 차수 | 남은 문항(세쌍둥이 포함) | 실측 속도 기준 | 계획 속도 기준 |\n|---|---|---|---|\n'+'\n'.join(f"| {k} | 약 {r:,} | **{a:%Y-%m-%d}** | {b:%Y-%m-%d} |" for k,r,a,b in tier_eta)
foot=f"### 차수별 예상 완료일 ({today:%m/%d} 기준)\n\n{eta_md}\n\n- 실측 속도: {START_DATE:%m/%d}부터 {elapsed}일 동안 {grand_done:,}문항 → 하루 약 {measured:,.0f}문항. 계획 속도: 하루 {RUNS_PER_DAY}회 × {PER_RUN}문항 = {planned}문항\n- 1차→2차→3차→4차 순서로 쉬지 않고 이어서 한다고 가정한 날짜이며, 매 회차마다 다시 계산됨\n- 전체 남은 문항 약 {remain:,} (변형문제 3종은 포함되지 않음. 교재별 총 문항은 쪽수 기준 추정치 ±20%)"
md.append(foot); md='\n'.join(md)+'\n'
p=open(os.path.join(ROOT,'_작업','진행표.md'),encoding='utf-8').read()
p=re.sub(r'## 현황.*?(?=\n## |\Z)',md.rstrip()+'\n',p,flags=re.S) if '## 현황' in p else p.rstrip()+'\n\n'+md
open(os.path.join(ROOT,'_작업','진행표.md'),'w',encoding='utf-8').write(p)
open(os.path.join(ROOT,'현황.md'),'w',encoding='utf-8').write('# 문항 DB 현황\n\n'+md)
gp=round(100*grand_done/grand_est)
eta_map={k:a for k,r,a,b in tier_eta}
tier_cards=''.join(f"<div class='card'><div class='t'>{t[0].split(' — ')[0].split(' (')[0]}</div><div class='n'>{t[3]}%</div><div class='bar'><div style='width:{t[3]}%'></div></div><div class='s'>{t[1]:,} / 약 {t[2]:,}</div>"+(f"<div class='eta'>예상 완료 {eta_map[t[0][:2]]:%Y-%m-%d}</div>" if t[0][:2] in eta_map else ("<div class='eta'>완료</div>" if t[3]>=100 else "<div class='eta'>&nbsp;</div>"))+"</div>" for t in tier_summary)
eta_html='<table class="eta"><tr><th>차수</th><th>남은 문항(세쌍둥이 포함)</th><th>실측 속도 기준</th><th>계획 속도 기준</th></tr>'+''.join(f'<tr><td>{k}</td><td>약 {r:,}</td><td><b>{a:%Y-%m-%d}</b></td><td>{b:%Y-%m-%d}</td></tr>' for k,r,a,b in tier_eta)+'</table>'
foot_html='<h3>차수별 예상 완료일</h3>'+eta_html+'<br>'.join(l for l in foot.split(chr(10)) if l.startswith('- ')).replace('**','')
html=f"""<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>문항 DB 현황</title>
<style>body{{font-family:'Malgun Gothic',sans-serif;max-width:1000px;margin:30px auto;padding:0 20px;color:#222}}
h1{{font-size:22px;margin-bottom:4px}} .sub{{color:#888;font-size:13px;margin-bottom:18px}}
.total{{background:#f5f7fb;border-radius:10px;padding:16px 20px;margin-bottom:16px}} .total .n{{font-size:26px;font-weight:bold}}
.bar{{display:inline-block;width:120px;height:10px;background:#e6e8ee;border-radius:5px;vertical-align:middle;margin-right:8px;overflow:hidden}} .bar div{{height:100%;background:#3b7ddd}}
.bar.big{{display:block;width:100%;height:14px;margin:8px 0 0}} .total .bar{{display:block;width:100%;height:18px;margin-top:8px}}
.cards{{display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin-bottom:20px}} .card{{border:1px solid #e3e5ea;border-radius:10px;padding:12px}}
.card .t{{font-size:13px;color:#555;min-height:34px}} .card .n{{font-size:22px;font-weight:bold;margin:4px 0}} .card .bar{{display:block;width:100%;margin:4px 0}} .card .s{{font-size:12px;color:#888}} .card .eta{{font-size:12px;color:#1a5fb4;font-weight:bold;margin-top:6px}} h3{{font-size:15px;margin:18px 0 6px}} table.eta td b{{color:#1a5fb4}}
details{{border:1px solid #e3e5ea;border-radius:10px;padding:10px 14px;margin-bottom:12px}} summary{{cursor:pointer;font-size:15px;list-style:none}} summary::-webkit-details-marker{{display:none}}
table{{border-collapse:collapse;width:100%;margin-top:10px}} th,td{{border:1px solid #e3e5ea;padding:6px 10px;text-align:left;font-size:13px}} th{{background:#f5f5f5}} td.u{{color:#666;font-size:12px}}
.완료{{color:#1a7f37;font-weight:bold}} .진행중{{color:#b45309;font-weight:bold}} .대기{{color:#999}} .foot{{font-size:13px;line-height:1.8;color:#444;margin-top:16px}}</style></head><body>
<h1>송우찬수학학원 문항 DB 구축 현황</h1><div class="sub">{today:%Y년 %m월 %d일} 기준 · 원본 문항 기준(변형문제 제외)</div>
<div class="total"><div>전체 진행률</div><div class="n">{grand_done:,} / 약 {grand_est:,} 문항 ({gp}%)</div><div class="bar"><div style="width:{gp}%"></div></div></div>
<div class="cards">{tier_cards}</div>
{''.join(html_sections)}
<div class="foot">{foot_html}</div></body></html>"""
open(os.path.join(ROOT,'현황.html'),'w',encoding='utf-8').write(html)
print(md)
