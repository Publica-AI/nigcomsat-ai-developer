"""The animated web-slide engine.

A deck is one self-contained .html file: no internet needed, no installs.
Keys: → / Space next · ← back · F fullscreen · N speaker notes · Home/End.
URL options: ?print (all slides, final state, for PDF) · ?shot=5 (one slide, final state).
"""
from __future__ import annotations

import html
import json

from common import BRAND as B

CSS = r"""
:root{
  --space:%(space)s; --space2:%(space2)s; --line:%(line_dark)s;
  --text:#EAF2FB; --muted:%(muted_dark)s;
  --blue:%(blue_d)s; --teal:%(teal_d)s; --amber:%(amber_d)s; --gold:%(gold)s;
  --good:#3CCB7F; --bad:#FF6B6F;
  --font:"Avenir Next","Segoe UI","SF Pro Display",-apple-system,"Helvetica Neue",Arial,sans-serif;
  --mono:"SF Mono",Menlo,Consolas,"Liberation Mono",monospace;
}
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%%;background:var(--space);color:var(--text);font-family:var(--font);overflow:hidden}
#viewport{position:fixed;inset:0;display:flex;align-items:center;justify-content:center}
#stars{position:fixed;inset:0;width:100%%;height:100%%}
#deck{position:relative;width:1600px;height:900px;flex:none;transform-origin:center center}
.slide{position:absolute;inset:0;padding:70px 90px 90px;display:flex;flex-direction:column;
  opacity:0;visibility:hidden;transition:opacity .6s ease,transform .6s ease;transform:translateX(40px)}
.slide.active{opacity:1;visibility:visible;transform:none}
.slide.past{transform:translateX(-40px)}
.slide.center{justify-content:center;align-items:center;text-align:center}
/* type */
.kicker{font-size:22px;letter-spacing:.22em;text-transform:uppercase;color:var(--teal);font-weight:700;margin-bottom:18px}
h1{font-size:96px;line-height:1.02;font-weight:800;letter-spacing:-.02em}
h2{font-size:62px;line-height:1.08;font-weight:800;letter-spacing:-.01em;margin-bottom:28px}
h3{font-size:34px;font-weight:700;margin-bottom:10px}
p,li{font-size:30px;line-height:1.4;color:var(--text)}
.sub{font-size:34px;color:var(--muted);line-height:1.35}
.small{font-size:22px;color:var(--muted)}
.muted{color:var(--muted)}
.hl{color:var(--gold)} .blue{color:var(--blue)} .teal{color:var(--teal)} .good{color:var(--good)} .bad{color:var(--bad)}
b,strong{font-weight:800}
.mono{font-family:var(--mono)}
/* layout */
.row{display:flex;gap:36px;align-items:stretch}
.col{display:flex;flex-direction:column;gap:24px}
.grow{flex:1}
.grid2{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:32px}
.grid3{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:32px}
.grid4{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:28px}
.grid5{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:24px}
.card{background:var(--space2);border:1px solid var(--line);border-radius:28px;padding:34px 36px;position:relative}
.card.glow{box-shadow:0 0 0 1px rgba(59,139,224,.35),0 20px 60px rgba(0,0,0,.45)}
.icon{font-size:72px;line-height:1;margin-bottom:16px}
.pill{display:inline-block;white-space:nowrap;padding:8px 22px;border-radius:999px;background:rgba(59,139,224,.16);color:#BFDcff;font-size:24px;font-weight:700;margin:4px 8px 4px 0}
.pill.teal{background:rgba(22,163,148,.18);color:#9EEBE0}
.pill.gold{background:rgba(245,184,61,.16);color:#FFE3A3}
.pill.bad{background:rgba(229,72,77,.18);color:#FFC2C4}
.stat{font-size:110px;font-weight:800;line-height:1;letter-spacing:-.03em}
.stat-label{font-size:24px;color:var(--muted);margin-top:8px}
.big-emoji{font-size:150px;line-height:1}
.num{display:inline-flex;align-items:center;justify-content:center;width:58px;height:58px;border-radius:50%%;
  background:var(--blue);color:#fff;font-weight:800;font-size:28px;flex:none}
/* code */
pre.code{font-family:var(--mono);font-size:27px;line-height:1.55;background:#07101A;border:1px solid var(--line);
  border-radius:22px;padding:28px 34px;white-space:pre;color:#D7E3F1;overflow:hidden}
.k{color:#7FB8FF}.s{color:#9EEBC2}.c{color:#6F8399;font-style:italic}.n{color:#FFD27A}.f{color:#E9A8FF}
/* flow diagram */
.flow{display:flex;align-items:center;gap:0}
.flow .box{background:var(--space2);border:2px solid var(--line);border-radius:22px;padding:22px 26px;text-align:center;min-width:220px}
.flow .box.on{border-color:var(--blue);box-shadow:0 0 30px rgba(59,139,224,.35)}
.flow .arrow{width:70px;height:4px;background:linear-gradient(90deg,var(--blue),var(--teal));position:relative;flex:none}
.flow .arrow:after{content:"";position:absolute;right:-4px;top:-9px;border:11px solid transparent;border-left:14px solid var(--teal)}
/* footer */
.foot{position:absolute;left:90px;right:90px;bottom:28px;display:flex;align-items:center;justify-content:space-between;font-size:18px;color:var(--muted);letter-spacing:.04em}
.foot .brand{display:flex;align-items:center;gap:14px}
.lg{display:inline-block;background-repeat:no-repeat;background-position:center;background-size:contain}
.lg-pub{background-image:url(%(pub)s)}
.lg-nig{background-image:url(%(nig)s)}
.foot .lg-pub{width:38px;height:30px}
.foot .chip{background:#fff;border-radius:10px;padding:3px 8px;display:flex;align-items:center}
.foot .chip .lg-nig{width:52px;height:44px}
/* animation primitives */
.anim{opacity:0;transform:translateY(28px);transition:opacity .7s ease,transform .7s cubic-bezier(.2,.7,.2,1);transition-delay:var(--d,0s)}
.anim.a-pop{transform:scale(.6)}
.anim.a-left{transform:translateX(-60px)}
.anim.a-right{transform:translateX(60px)}
.anim.a-fade{transform:none}
.active .anim,.anim.shown{opacity:1;transform:none}
.step{opacity:0;transform:translateY(20px);transition:opacity .55s ease,transform .55s ease}
.step.on{opacity:1;transform:none}
svg .draw{transition:stroke-dashoffset var(--dur,2.4s) cubic-bezier(.45,.05,.2,1);transition-delay:var(--d,.2s)}
svg text{font-family:var(--font)}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes floaty{0%%,100%%{transform:translateY(0)}50%%{transform:translateY(-14px)}}
@keyframes pulse{0%%,100%%{opacity:1}50%%{opacity:.35}}
@keyframes blink{0%%,49%%{opacity:1}50%%,100%%{opacity:0}}
.spin{animation:spin var(--t,24s) linear infinite}
.floaty{animation:floaty 5s ease-in-out infinite}
.pulse{animation:pulse 1.8s ease-in-out infinite}
/* HUD */
#progress{position:fixed;left:0;right:0;bottom:0;height:5px;background:rgba(255,255,255,.06)}
#progress i{display:block;height:100%%;width:0;background:linear-gradient(90deg,var(--blue),var(--teal));transition:width .5s ease}
#hud{position:fixed;right:18px;bottom:14px;font-size:14px;color:var(--muted);opacity:.0;transition:opacity .4s}
body:hover #hud{opacity:.7}
#notes{position:fixed;left:20px;right:20px;bottom:20px;max-height:38vh;overflow:auto;background:rgba(7,16,26,.96);border:1px solid var(--line);
  border-radius:16px;padding:18px 22px;font-size:18px;line-height:1.5;color:#DDE8F5;display:none;z-index:9}
#notes.on{display:block}
#notes b{color:var(--gold)}
@media (prefers-reduced-motion:reduce){.anim,.step,.slide,svg .draw{transition:none!important}.spin,.floaty,.pulse{animation:none!important}}
/* print / screenshot modes */
body.print{overflow:visible;height:auto}
body.print #viewport{position:static;display:block}
body.print #deck{transform:none!important;width:1600px;height:auto}
body.print .slide{position:relative;opacity:1;visibility:visible;transform:none;height:900px;page-break-after:always;break-after:page;background:var(--space);overflow:hidden}
body.print .anim,body.print .step{opacity:1!important;transform:none!important;transition:none!important}
body.print svg .draw{stroke-dashoffset:0!important;transition:none!important}
body.print #stars,body.print #progress,body.print #hud,body.print #notes{display:none}
body.shot #deck{transform:none!important}
body.shot .slide{transition:none!important}
body.shot .anim,body.shot .step{opacity:1!important;transform:none!important;transition:none!important}
body.shot svg .draw{stroke-dashoffset:0!important;transition:none!important}
body.shot #hud,body.shot #progress{display:none}
@page{size:1600px 900px;margin:0}
"""

JS = r"""
(function(){
const q=new URLSearchParams(location.search);
const deck=document.getElementById('deck');
const slides=[...document.querySelectorAll('.slide')];
const bar=document.querySelector('#progress i');
const hud=document.getElementById('hud');
const notes=document.getElementById('notes');
let cur=0;
// tiny python highlighter for <pre class="code">
document.querySelectorAll('pre.code').forEach(p=>{
  let t=p.textContent.replace(/&/g,'&amp;').replace(/</g,'&lt;');
  const toks=[];const enc=i=>String(i).split('').map(c=>'QWXZJKVYPU'[+c]).join('');const dec=s=>+s.split('').map(c=>'QWXZJKVYPU'.indexOf(c)).join('');
  const keep=(cls,s)=>{toks.push('<span class="'+cls+'">'+s+'</span>');return '\u0001'+enc(toks.length-1)+'\u0002'};
  t=t.replace(/#[^\n]*/g,m=>keep('c',m));
  t=t.replace(/("[^"\n]*"|'[^'\n]*')/g,m=>keep('s',m));
  t=t.replace(/\b(import|from|as|def|return|for|in|if|else|print|True|False|None)\b/g,m=>keep('k',m));
  t=t.replace(/\b(\d+(\.\d+)?)\b/g,m=>keep('n',m));
  t=t.replace(/\.(\w+)\(/g,(m,a)=>'.'+keep('f',a)+'(');
  t=t.replace(/\u0001([QWXZJKVYPU]+)\u0002/g,(m,i)=>toks[dec(i)]);
  p.innerHTML=t;
});
// prepare draw-on paths
document.querySelectorAll('svg .draw').forEach(p=>{
  const L=p.getTotalLength?p.getTotalLength():1000;
  p.style.strokeDasharray=L; p.style.strokeDashoffset=L; p.dataset.len=L;
});
function fit(){
  if(document.body.classList.contains('print')||document.body.classList.contains('shot'))return;
  const s=Math.min(innerWidth/1600,innerHeight/900);
  deck.style.transform='scale('+s+')';
}
function countUp(el){
  const to=parseFloat(el.dataset.to);const dec=(el.dataset.dec|0);const t0=performance.now();const dur=1600;
  const fmt=v=>v.toLocaleString('en-US',{minimumFractionDigits:dec,maximumFractionDigits:dec});
  (function tick(t){const k=Math.min(1,(t-t0)/dur);const e=1-Math.pow(1-k,3);el.textContent=(el.dataset.pre||'')+fmt(to*e)+(el.dataset.suf||'');if(k<1)requestAnimationFrame(tick)})(t0);
}
function finalState(s){
  s.querySelectorAll('.step').forEach(x=>x.classList.add('on'));
  s.querySelectorAll('.count').forEach(el=>{const dec=(el.dataset.dec|0);el.textContent=(el.dataset.pre||'')+parseFloat(el.dataset.to).toLocaleString('en-US',{minimumFractionDigits:dec,maximumFractionDigits:dec})+(el.dataset.suf||'')});
  s.querySelectorAll('svg .draw').forEach(p=>p.style.strokeDashoffset=0);
}
function enter(s){
  s.querySelectorAll('svg .draw').forEach(p=>{p.style.transition='none';p.style.strokeDashoffset=p.dataset.len;p.getBoundingClientRect();p.style.transition='';
    requestAnimationFrame(()=>requestAnimationFrame(()=>{p.style.strokeDashoffset=0}))});
  s.querySelectorAll('.count').forEach(el=>setTimeout(()=>countUp(el),(parseFloat(el.dataset.d||'.3'))*1000));
}
function steps(s){return [...s.querySelectorAll('.step')].sort((a,b)=>(a.dataset.step|0)-(b.dataset.step|0))}
function show(i,back){
  i=Math.max(0,Math.min(slides.length-1,i));
  slides.forEach((s,k)=>{s.classList.toggle('active',k===i);s.classList.toggle('past',k<i)});
  const s=slides[i];
  steps(s).forEach(x=>x.classList.toggle('on',!!back));
  if(i!==cur||!s.dataset.entered){enter(s);s.dataset.entered=1}
  cur=i;
  bar.style.width=((i+1)/slides.length*100)+'%';
  hud.textContent=(i+1)+' / '+slides.length+'   ·   ← →  ·  F fullscreen  ·  N notes';
  notes.innerHTML='<b>Speaker notes ('+(i+1)+'):</b> '+(s.dataset.notes||'');
  history.replaceState(null,'','#'+(i+1));
}
function next(){const st=steps(slides[cur]).filter(x=>!x.classList.contains('on'));
  if(st.length){const n=st[0].dataset.step;st.filter(x=>x.dataset.step===n).forEach(x=>x.classList.add('on'));return}
  if(cur<slides.length-1){slides[cur+1].dataset.entered='';show(cur+1)}}
function prev(){const st=steps(slides[cur]).filter(x=>x.classList.contains('on'));
  if(st.length){const n=st[st.length-1].dataset.step;st.filter(x=>x.dataset.step===n).forEach(x=>x.classList.remove('on'));return}
  if(cur>0){slides[cur-1].dataset.entered='';show(cur-1,true)}}
if(q.has('print')){document.body.classList.add('print');slides.forEach(s=>{s.classList.add('active');finalState(s)});return}
if(q.has('shot')){document.body.classList.add('shot');const n=(+q.get('shot')||1)-1;slides.forEach((s,k)=>{s.classList.toggle('active',k===n)});finalState(slides[n]);
  document.getElementById('stars').style.display='block';drawStars(true);return}
addEventListener('resize',fit);fit();
addEventListener('keydown',e=>{
  if(['ArrowRight','PageDown',' ','Enter'].includes(e.key)){e.preventDefault();next()}
  else if(['ArrowLeft','PageUp','Backspace'].includes(e.key)){e.preventDefault();prev()}
  else if(e.key==='Home'){show(0)}else if(e.key==='End'){show(slides.length-1)}
  else if(e.key==='f'||e.key==='F'){document.fullscreenElement?document.exitFullscreen():document.documentElement.requestFullscreen()}
  else if(e.key==='n'||e.key==='N'){notes.classList.toggle('on')}
});
addEventListener('click',e=>{if(e.target.closest('a,button,#notes'))return;(e.clientX>innerWidth/3)?next():prev()});
let tx=null;addEventListener('touchstart',e=>{tx=e.touches[0].clientX},{passive:true});
addEventListener('touchend',e=>{if(tx===null)return;const dx=e.changedTouches[0].clientX-tx;if(Math.abs(dx)>50)(dx<0?next():prev());tx=null});
const start=parseInt((location.hash||'#1').slice(1))||1;show(start-1);drawStars(false);
function drawStars(still){
  const c=document.getElementById('stars');const x=c.getContext('2d');let W,H,st=[];
  function init(){W=c.width=innerWidth*devicePixelRatio;H=c.height=innerHeight*devicePixelRatio;
    st=[...Array(190)].map(()=>({x:Math.random()*W,y:Math.random()*H,r:(Math.random()*1.3+.3)*devicePixelRatio,p:Math.random()*6.28,v:Math.random()*.15+.03}))}
  init();addEventListener('resize',init);
  (function loop(t){x.clearRect(0,0,W,H);for(const s of st){const a=.35+.45*Math.sin(s.p+t/900);x.globalAlpha=a;x.fillStyle='#CFE3FF';
    x.beginPath();x.arc(s.x,s.y,s.r,0,6.283);x.fill();if(!still){s.x-=s.v;if(s.x<0)s.x=W}}
    if(!still)requestAnimationFrame(loop)})(0);
}
})();
"""


def footer(code: str, title: str) -> str:
    return (f'<div class="foot"><div class="brand"><span class="lg lg-pub" role="img" aria-label="Publica Academy"></span>'
            f'<span>Publica Academy · Time-Series Programme · {html.escape(code)}</span></div>'
            f'<div class="brand">'
            f'<span>Prepared for NIGCOMSAT</span><span class="chip"><span class="lg lg-nig" role="img" aria-label="NIGCOMSAT"></span></span></div></div>')


def _small(name, width):
    import base64, io
    from PIL import Image
    from common import BRAND_DIR
    im = Image.open(BRAND_DIR / name)
    im.thumbnail((width, 10_000))
    buf = io.BytesIO()
    im.save(buf, format="PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


PUB = _small("publica-academy-logo.png", 200)
NIG = _small("nigcomsat-logo.png", 420)


def render(code: str, title: str, slides: list[dict]) -> str:
    """slides: [{"html": str, "notes": str, "cls": "center", "foot": True}]"""
    parts = []
    for s in slides:
        cls = "slide " + s.get("cls", "")
        notes = html.escape(s.get("notes", ""), quote=True)
        foot = footer(code, title) if s.get("foot", True) else ""
        parts.append(f'<section class="{cls}" data-notes="{notes}">{s["html"]}{foot}</section>')
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(code)} · {html.escape(title)}</title>
<link rel="icon" href="{PUB}">
<style>{CSS % {**B, 'pub': PUB, 'nig': NIG}}</style></head>
<body>
<div id="viewport"><canvas id="stars"></canvas><div id="deck">
{''.join(parts)}
</div></div>
<div id="progress"><i></i></div><div id="hud"></div><div id="notes"></div>
<script>{JS}</script>
</body></html>"""


def logos_title_block() -> str:
    return (f'<div style="display:flex;gap:26px;align-items:center;justify-content:center;margin-bottom:46px">'
            f'<div style="background:#fff;border-radius:22px;padding:14px 22px;height:164px;display:flex;align-items:center">'
            f'<span class="lg lg-nig" style="width:170px;height:140px" role="img" aria-label="NIGCOMSAT"></span></div>'
            f'<div style="background:#fff;border-radius:22px;padding:14px 26px;height:164px;display:flex;align-items:center;gap:16px">'
            f'<span class="lg lg-pub" style="width:100px;height:80px" role="img" aria-label="Publica Academy"></span>'
            f'<span style="color:#0B1622;font-weight:800;font-size:30px;line-height:1.05;text-align:left">Publica<br>Academy</span></div></div>')


def json_attr(obj) -> str:
    return html.escape(json.dumps(obj), quote=True)
