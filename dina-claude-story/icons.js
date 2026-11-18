const I={
wb:'<rect x="5" y="7" width="38" height="26" rx="4"/><path d="M16 41l4-8M32 41l-4-8"/><rect x="11" y="13" width="9" height="7" rx="1.5"/><rect x="25" y="13" width="11" height="5" rx="1.5"/><path d="M25 24h12"/>',
sheet:'<rect x="7" y="7" width="34" height="34" rx="4"/><path d="M7 18h34M7 29h34M18 7v34M29 7v34"/>',
chart:'<path d="M8 40h32"/><rect x="11" y="26" width="6" height="12" rx="1"/><rect x="21" y="18" width="6" height="20" rx="1"/><rect x="31" y="10" width="6" height="28" rx="1"/>',
plug:'<rect x="4" y="17" width="14" height="14" rx="4"/><rect x="30" y="17" width="14" height="14" rx="4"/><path d="M18 24h12M11 21v6M37 21v6"/>',
db:'<ellipse cx="24" cy="11" rx="14" ry="5"/><path d="M10 11v26c0 3 6 5 14 5s14-2 14-5V11M10 24c0 3 6 5 14 5s14-2 14-5"/>',
q:'<circle cx="24" cy="24" r="17"/><path d="M19 19a5 5 0 1 1 7 4.6c-1.4.6-2 1.6-2 3V29"/><circle cx="24" cy="34" r="1.2" fill="currentColor"/>',
users:'<circle cx="18" cy="17" r="6"/><path d="M7 38c0-7 5-11 11-11s11 4 11 11"/><circle cx="33" cy="15" r="5"/><path d="M31 25c6 0 10 4 10 10"/>',
time:'<path d="M5 30h38"/><circle cx="10" cy="30" r="3" fill="currentColor"/><circle cx="24" cy="30" r="3" fill="currentColor"/><circle cx="38" cy="30" r="3" fill="currentColor"/><rect x="6" y="12" width="10" height="8" rx="2"/><rect x="28" y="10" width="12" height="9" rx="2"/>',
sel:'<rect x="8" y="8" width="32" height="32" rx="3" stroke-dasharray="5 4"/><path d="M28 28l10 4-4 2-2 4z" fill="currentColor"/>',
edit:'<path d="M10 38l3-10 18-18 7 7-18 18z"/><path d="M27 14l7 7"/>',
fx:'<text x="24" y="33" font-size="24" text-anchor="middle" fill="currentColor" stroke="none" font-style="italic" font-weight="bold">fx</text>',
check:'<circle cx="24" cy="24" r="17"/><path d="M16 24l6 6 11-12"/>',
chat:'<path d="M8 10h32v22H20l-8 7v-7H8z"/><path d="M15 19h18M15 25h12"/>',
globe:'<circle cx="24" cy="24" r="17"/><path d="M7 24h34M24 7c-6 6-6 28 0 34M24 7c6 6 6 28 0 34"/>',
laptop:'<rect x="10" y="10" width="28" height="19" rx="2"/><path d="M5 37h38l-4-6H9z"/>',
clock:'<circle cx="24" cy="24" r="17"/><path d="M24 14v10l7 5"/>',
warn:'<path d="M24 6L44 40H4z" stroke-linejoin="round"/><path d="M24 18v11"/><circle cx="24" cy="34" r="1.6" fill="currentColor"/>',
crown:'<path d="M7 36l-2-20 11 9 8-14 8 14 11-9-2 20z" stroke-linejoin="round"/><path d="M8 41h32"/>',
eye:'<path d="M4 24s7-12 20-12 20 12 20 12-7 12-20 12S4 24 4 24z"/><circle cx="24" cy="24" r="5"/>',
doc:'<path d="M12 6h16l9 9v27H12z"/><path d="M28 6v9h9M18 24h13M18 31h13"/>',
img:'<rect x="6" y="9" width="36" height="30" rx="4"/><circle cx="17" cy="19" r="4"/><path d="M6 34l11-9 8 7 6-5 11 9"/>',
mail:'<rect x="6" y="11" width="36" height="26" rx="4"/><path d="M7 13l17 13 17-13"/>',
link:'<path d="M20 28l8-8"/><path d="M22 14l3-3a8 8 0 0 1 12 12l-3 3M26 34l-3 3a8 8 0 0 1-12-12l3-3"/>',
bell:'<path d="M12 33V22a12 12 0 0 1 24 0v11l3 4H9z"/><path d="M20 41a4 4 0 0 0 8 0"/>',
scan:'<path d="M6 16V6h10M32 6h10v10M42 32v10H32M16 42H6V32"/><path d="M12 24h24"/>'
};
var ic=(k,extra='')=>`<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="3.2" stroke-linecap="round" ${extra}>${I[k]}</svg>`;
var spark=(s,x,y,d,fx='pop')=>{let r='';for(let i=0;i<12;i++){const a=i*30*Math.PI/180,l=i%2?.30:.38;r+=`<line x1="${50+Math.cos(a)*8}" y1="${50+Math.sin(a)*8}" x2="${50+Math.cos(a)*l*100}" y2="${50+Math.sin(a)*l*100}"/>`}
 return `<div class="a spark" data-fx="${fx}" data-d="${d}" style="left:${x}px;top:${y}px;width:${s}px;height:${s}px"><svg viewBox="0 0 100 100" width="${s*.8}" height="${s*.8}" stroke="#fff" stroke-width="7" stroke-linecap="round">${r}</svg></div>`};
var shot=(src,x,y,w,d=0,fx='shot')=>`<div class="a shot" data-fx="${fx}" data-d="${d}" style="left:${x}px;top:${y}px;width:${w}px"><img src="img/${src}.png" class="kb"></div>`;
var chip=(k,t,x,y,d,cls='')=>`<div class="a chip ${cls}" data-fx="right" data-d="${d}" style="right:${x}px;top:${y}px">${k?ic(k):''}<span>${t}</span></div>`;
var card=(k,t,x,y,d,n='',sz=240)=>`<div class="a card" data-fx="pop" data-d="${d}" style="left:${x}px;top:${y}px;width:${sz}px;height:${sz}px">${n?`<div class="num">${n}</div>`:''}${ic(k)}<b>${t}</b></div>`;
var box=(x,y,w,h,d,extra='')=>`<div class="a" data-fx="pop" data-d="${d}" style="left:${x}px;top:${y}px;width:${w}px;height:${h}px;border:5px solid var(--ac);border-radius:10px;box-shadow:0 0 0 6px rgba(217,119,90,.18);${extra}"></div>`;

