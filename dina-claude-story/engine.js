// ---------- engine ----------
const root=document.getElementById('scenes');
S.forEach((sc,i)=>{const d=document.createElement('div');d.className='scene';d.innerHTML=sc.h;root.appendChild(d);sc.el=d});
// Latin runs -> IBM Plex Mono, Arabic stays in Tajawal (keeps Arabic word spacing tight)
const LAT=/[=A-Za-z0-9][\w.:=()\/\-]*(?: [A-Za-z][\w.:=()\/\-]*)*\??/g;
const wrapEn=t=>t.replace(LAT,m=>`<span class="en">${m}</span>`);
(function walk(n){[...n.childNodes].forEach(c=>{
 if(c.nodeType===3){if(LAT.test(c.textContent)&&!c.parentElement.closest('svg,.en')){const s=document.createElement('span');s.innerHTML=wrapEn(c.textContent);c.replaceWith(...s.childNodes)}LAT.lastIndex=0}
 else if(c.nodeType===1)walk(c)})})(root);
const cl=(v)=>Math.max(0,Math.min(1,v));
const eo=p=>1-Math.pow(1-p,3);
const eb=p=>{const c1=1.9,c3=c1+1;return 1+c3*Math.pow(p-1,3)+c1*Math.pow(p-1,2)};
const ar=n=>String(n);
const capEl=document.getElementById('cap'),ttl=document.getElementById('ttl');
let lastCap=-2,lastT='';
function render(t){
 S.forEach(sc=>{
  const L=t-sc.s,dur=sc.e-sc.s;
  const on=t>=sc.s-0.001&&(t<sc.e||sc.end);
  sc.el.style.opacity=on?1:0; if(!on)return;
  let so=cl(L/0.18); sc.el.style.opacity=so;
  sc.el.querySelectorAll('.a').forEach(el=>{
   const d=+el.dataset.d||0,fx=el.dataset.fx,p=cl((L-d)/0.5);
   let tr='',op=cl((L-d)/0.25);
   if(fx==='pop'){tr=`scale(${0.5+0.5*eb(p)})`;}
   else if(fx==='up'){tr=`translateY(${50*(1-eo(p))}px)`;}
   else if(fx==='right'){tr=`translateX(${-60*(1-eo(p))}px)`;}
   else if(fx==='shot'){const q=cl((L-d)/0.6);tr=`translateY(${60*(1-eo(q))}px) scale(${0.94+0.06*eo(q)})`;op=cl((L-d)/0.3);
     const im=el.querySelector('img');if(im)im.style.transform=`scale(${1+0.06*cl(L/Math.max(dur,3))})`;}
   else if(fx==='shake'){const q=cl(L/0.4);tr=`scale(${0.4+0.6*eb(q)}) rotate(${L>0.35&&L<1.0?Math.sin(L*40)*6*(1-(L-0.35)/0.65):0}deg)`;}
   else if(fx==='draw'){op=L>=d?1:0;const path=el.querySelector('path'),q=eo(cl((L-d)/0.45));path.style.clipPath=`inset(0 0 ${100-100*q}% 0)`;const dot=el.querySelector('.dot');dot.setAttribute('cy',10+200*q);}
   el.style.opacity=op;el.style.transform=tr;
  });
  sc.el.querySelectorAll('.cnt').forEach(el=>{const d=+el.dataset.d,q=eo(cl((L-d)/1.0));el.textContent=ar(Math.round(q*+el.dataset.to))});
  sc.el.querySelectorAll('.bar').forEach(el=>{const d=+el.dataset.d,q=eo(cl((L-d)/1.0));el.style.width=(q*100*+el.dataset.w)+'%'});
  sc.el.querySelectorAll('.scanl').forEach(el=>{const d=+el.dataset.d;if(L<d){el.style.opacity=0;return}el.style.opacity=1;const ph=((L-d)/1.6)%2;const y=ph<1?ph:2-ph;el.style.top=(20+y*380)+'px'});
  if(sc.t!==lastT){ttl.innerHTML=wrapEn(sc.t);lastT=sc.t;}
  const hp=cl(L/0.35);ttl.style.opacity=hp;ttl.style.transform=`translateY(${(1-eo(hp))*-24}px)`;
  if(sc.s>0 && S[S.indexOf(sc)-1].t===sc.t){ttl.style.opacity=1;ttl.style.transform='none';}
 });
 let ci=C.findIndex(c=>t>=c[0]&&t<c[1]);
 if(ci!==lastCap){capEl.innerHTML=ci<0?'':('>'+C[ci][2].replace(/<b>(.*?)<\/b>/g,'<span class="hl">$1</span>')+'<').replace(/>([^<]*)</g,(m,t)=>'>'+wrapEn(t)+'<').slice(1,-1);lastCap=ci;
  capEl.style.fontSize='88px';const w=capEl.scrollWidth,mw=capEl.clientWidth;if(w>mw)capEl.style.fontSize=Math.floor(88*mw/w)+'px';}
 if(ci>=0){const q=cl((t-C[ci][0])/0.22);capEl.style.opacity=cl((t-C[ci][0])/0.12);capEl.style.transform=`scale(${0.85+0.15*eb(q)})`;}
}
render(+(location.hash.slice(1)||0));
