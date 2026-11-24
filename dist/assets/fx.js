/* Interactive pieces ported from Framer components to plain JS (styles in tools/odoo_site/fx.css).
   The markup is static HTML from tools/odoo_site/gen.py; this file only adds behaviour, so
   every button stays a working link without JavaScript.
   - .fx-metal      Liquid Metal Button+ by Matthias Ölschlegel (its WebGL chrome ring shader)
   - .fx-glass      Liquid Glass Buttons (its displacement/highlight maps and pointer optics)
   - .fx-eye        Eye Follow Button
   - .fx-aperture   Aperture (Alloy) Accordion
   - .fx-preloader  opening scene (pure CSS), once per visit, skipped by any input
   Reduced motion: no animation loops; everything is shown in its resting state. */
(() => {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const finePointer = matchMedia('(hover: hover) and (pointer: fine)').matches;
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));

  /* ---------------- Preloader ---------------- */
  const pre = document.querySelector('.fx-preloader');
  if (pre) {
    let seen = false;
    try { seen = sessionStorage.getItem('fx-intro') === '1'; sessionStorage.setItem('fx-intro', '1'); } catch (_) {}
    if (seen || reduce) pre.remove();
    else {
      const end = () => pre.remove();
      setTimeout(end, 3250);
      ['pointerdown', 'keydown', 'wheel', 'touchmove'].forEach(e => addEventListener(e, end, { once: true, passive: true }));
    }
  }

  /* ---------------- Eye Follow button ---------------- */
  const eyes = [...document.querySelectorAll('.fx-eye')];
  if (eyes.length) {
    const pupils = eyes.map(btn => [...btn.querySelectorAll('.fx-eye-pupil')]);
    const RANGE = 0.9, MAX = (40 - 12) / 2 * RANGE;
    if (finePointer && !reduce) {
      let raf = 0, mx = 0, my = 0;
      const update = () => {
        raf = 0;
        pupils.forEach(list => list.forEach(p => {
          const r = p.parentElement.getBoundingClientRect();
          const dx = mx - (r.left + r.width / 2), dy = my - (r.top + r.height / 2);
          const d = Math.hypot(dx, dy) || 1, k = Math.min(d, MAX) / d;
          p.style.transform = `translate(${dx * k}px, ${dy * k}px)`;
        }));
      };
      addEventListener('mousemove', e => { mx = e.clientX; my = e.clientY; if (!raf) raf = requestAnimationFrame(update); }, { passive: true });
    }
    if (!reduce) {
      setInterval(() => {
        if (document.hidden) return;
        eyes.forEach(b => b.classList.add('is-blinking'));
        setTimeout(() => eyes.forEach(b => b.classList.remove('is-blinking')), 200);
      }, 2000);
    }
  }

  /* ---------------- Aperture accordion ---------------- */
  document.querySelectorAll('.fx-aperture').forEach(root => {
    const panels = [...root.querySelectorAll('.fx-ap-panel')];
    const open = target => panels.forEach(p => {
      const on = p === target;
      p.classList.toggle('is-open', on);
      p.querySelector('.fx-ap-trigger').setAttribute('aria-expanded', String(on));
      const body = p.querySelector('.fx-ap-body');
      if (on) body.removeAttribute('inert'); else body.setAttribute('inert', '');
    });
    panels.forEach((p, i) => {
      const trigger = p.querySelector('.fx-ap-trigger');
      trigger.addEventListener('click', () => open(p));
      if (finePointer) p.addEventListener('pointerenter', () => { if (!p.classList.contains('is-open')) open(p); });
      trigger.addEventListener('keydown', e => {
        const step = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 }[e.key];
        if (!step) return;
        e.preventDefault();
        const next = panels[(i + step + panels.length) % panels.length];
        next.querySelector('.fx-ap-trigger').focus();
        open(next);
      });
    });
    open(panels.find(p => p.classList.contains('is-open')) || panels[0]);
  });

  // The glass maps and the metal shader are built once the page is idle, so they never compete with first paint.
  const idle = fn => {
    const run = () => ('requestIdleCallback' in window ? requestIdleCallback(fn, { timeout: 2500 }) : setTimeout(fn, 400));
    if (document.readyState === 'complete') run(); else addEventListener('load', run, { once: true });
  };

  /* ---------------- Liquid Glass button ---------------- */
  // makeGlassMaps and its helpers are copied unchanged from the component
  function normalizeGlassRadii(width,height,radius){const values=typeof radius==="number"?[radius,radius,radius,radius]:radius;const radii=values.map(value=>Number.isFinite(value)?Math.max(0,value):0);// Avoid rounding changes to the existing uniform-radius map.
if(radii.every(value=>value===radii[0])){const r=Math.min(radii[0],width/2,height/2);return[r,r,r,r];}const[tl,tr,br,bl]=radii;const scale=Math.min(1,width/(tl+tr),width/(bl+br),height/(tl+bl),height/(tr+br));return[tl*scale,tr*scale,br*scale,bl*scale];}/**
 * Exact inward distance and outward normal for four independently rounded corners.
 * A radius can exceed half an axis; selecting a radius by the rectangle's quadrant
 * is therefore insufficient. Instead compare all straight segments and quarter arcs.
 * Returns a reused record: consume it before calling the sampler again.
 */function createGlassBoundarySampler(width,height,radii){const[tl,tr,br,bl]=radii;const segments=[[tl,0,width-tr,0],[width,tr,width,height-br],[bl,height,width-br,height],[0,tl,0,height-bl]];const arcs=[{x:tl,y:tl,r:tl,sx:-1,sy:-1},{x:width-tr,y:tr,r:tr,sx:1,sy:-1},{x:width-br,y:height-br,r:br,sx:1,sy:1},{x:bl,y:height-bl,r:bl,sx:-1,sy:1}].filter(arc=>arc.r>0);const result={distance:0,nx:0,ny:0};return(x,y)=>{if(x<0||x>width||y<0||y>height)return null;for(const arc of arcs){const dx=x-arc.x;const dy=y-arc.y;if(dx*arc.sx>=0&&dy*arc.sy>=0&&dx*dx+dy*dy>arc.r*arc.r)return null;}let bestSquared=Infinity;let normalX=0;let normalY=0;const consider=(bx,by)=>{const dx=bx-x;const dy=by-y;const squared=dx*dx+dy*dy;const epsilon=1e-10*Math.max(1,squared,Number.isFinite(bestSquared)?bestSquared:0);if(squared<bestSquared-epsilon){bestSquared=squared;normalX=dx;normalY=dy;}else if(Math.abs(squared-bestSquared)<=epsilon){// Equal closest points meet on a medial axis. Blend their normals
// rather than introducing an arbitrary left/right discontinuity.
normalX+=dx;normalY+=dy;}};for(const[ax,ay,bx,by]of segments){const dx=bx-ax;const dy=by-ay;const lengthSquared=dx*dx+dy*dy;const t=lengthSquared>0?Math.max(0,Math.min(1,((x-ax)*dx+(y-ay)*dy)/lengthSquared)):0;consider(ax+t*dx,ay+t*dy);}for(const arc of arcs){const dx=x-arc.x;const dy=y-arc.y;// A point outside the arc's quadrant projects to one of its endpoints;
// both endpoints were already considered by their adjoining segments.
if(dx*arc.sx<0||dy*arc.sy<0)continue;const length=Math.hypot(dx,dy);const nx=length>1e-12?dx/length:arc.sx*Math.SQRT1_2;const ny=length>1e-12?dy/length:arc.sy*Math.SQRT1_2;consider(arc.x+nx*arc.r,arc.y+ny*arc.r);}result.distance=Math.sqrt(bestSquared);const normalLength=Math.hypot(normalX,normalY);result.nx=normalLength>1e-12?normalX/normalLength:0;result.ny=normalLength>1e-12?normalY/normalLength:0;return result;};}/**
 * Static, procedural PNGs for a glass surface. Call after measuring in an effect;
 * regenerate only when width, height, radius, or shoulder changes.
 *
 * SVG: use colorInterpolationFilters="sRGB", explicit CSS-pixel filter/image
 * dimensions, preserveAspectRatio="none", R for X, G for Y, and
 * feDisplacementMap scale={2 * shoulder}. Its offset is scale * (channel - .5):
 * the field peaks at 0.58 of the half-range, hence a 6px shoulder bends ~3.48px.
 * RGB 128 is the requested neutral center; 8-bit quantization leaves at most
 * shoulder / 255 px of center offset (~0.024px for a 6px shoulder).
 *
 * The shape is a lens approximation, not a full optical ray tracer. The inner
 * center stays undistorted; only the shoulder samples toward the button center.
 * Up to 1.5 samples/CSS px, 768px/axis, and 98,304 pixels per map. Both RGBA
 * buffers together are at most 768KiB; no network images or animation loops.
 */function makeGlassMaps(width,height,radius,shoulder){const empty={displacement:"",highlight:""};if(typeof document==="undefined")return empty;const finitePositive=(value,fallback)=>Number.isFinite(value)&&value>0?value:fallback;const w=finitePositive(width,1);const h=finitePositive(height,1);const halfW=w/2;const halfH=h/2;const radii=normalizeGlassRadii(w,h,radius);const uniform=radii.every(value=>value===radii[0]);const r=radii[0];const sampleBoundary=uniform?null:createGlassBoundarySampler(w,h,radii);const requestedShoulder=finitePositive(shoulder,6);const rim=Math.min(requestedShoulder,halfW,halfH);const limitPixels=98304;const factor=Math.min(1.5,768/w,768/h,Math.sqrt(limitPixels/w/h));const mapW=Math.max(1,Math.floor(w*factor));const mapH=Math.max(1,Math.floor(h*factor));const sampleW=w/mapW;const sampleH=h/mapH;const footprint=Math.max(sampleW,sampleH);const clamp01=value=>Math.max(0,Math.min(1,value));try{const canvas=document.createElement("canvas");canvas.width=mapW;canvas.height=mapH;const context=canvas.getContext("2d");if(!context)return empty;const field=context.createImageData(mapW,mapH);const light=context.createImageData(mapW,mapH);const a=field.data;const b=light.data;const lightX=-.5547;const lightY=-.83205;for(let y=0;y<mapH;y++){const py=(y+.5)*sampleH-halfH;for(let x=0;x<mapW;x++){const index=(y*mapW+x)*4;a[index]=128;a[index+1]=128;a[index+2]=128;a[index+3]=255;const px=(x+.5)*sampleW-halfW;let inwardDistance;let nx;let ny;if(uniform){// Preserve the original analytic field exactly for equal corners.
const qx=Math.abs(px)-(halfW-r);const qy=Math.abs(py)-(halfH-r);const ox=Math.max(qx,0);const oy=Math.max(qy,0);const outerDistance=Math.hypot(ox,oy);inwardDistance=-(outerDistance+Math.min(Math.max(qx,qy),0)-r);if(inwardDistance<=0||inwardDistance>=rim)continue;const sx=px<0?-1:1;const sy=py<0?-1:1;if(outerDistance>1e-6){nx=ox/outerDistance*sx;ny=oy/outerDistance*sy;}else if(qx>qy){nx=sx;ny=0;}else if(qy>qx){nx=0;ny=sy;}else{nx=sx*Math.SQRT1_2;ny=sy*Math.SQRT1_2;}}else{const boundary=sampleBoundary(px+halfW,py+halfH);if(!boundary||boundary.distance<=0||boundary.distance>=rim)continue;inwardDistance=boundary.distance;nx=boundary.nx;ny=boundary.ny;}const u=inwardDistance/rim;const bell=Math.sin(Math.PI*u)**2;const magnitude=.58*bell*rim/requestedShoulder;a[index]=Math.round(127.5-127.5*nx*magnitude);a[index+1]=Math.round(127.5-127.5*ny*magnitude);// Two broad directional lobes, never a uniform bright ring.
// Strong specular light stays narrow; the center remains clear.
const facing=nx*lightX+ny*lightY;const bright=Math.max(0,facing)**1.7;const dark=Math.max(0,-facing)**1.6;const narrowBand=Math.exp(-Math.pow((u-.16)/.19,2));const softBand=Math.exp(-Math.pow((u-.34)/.34,2));const coverage=clamp01(inwardDistance/footprint+.5);const fade=(1-u)**1.2;const signedLight=(.72*bright*narrowBand-.14*dark*softBand)*fade;const tone=signedLight>=0?255:0;b[index]=tone;b[index+1]=tone;b[index+2]=tone;b[index+3]=Math.round(255*Math.abs(signedLight)*coverage);}}context.putImageData(field,0,0);const displacement=canvas.toDataURL("image/png");context.putImageData(light,0,0);const highlight=canvas.toDataURL("image/png");// Return backing-store memory promptly after the PNG strings are made.
canvas.width=1;canvas.height=1;return{displacement,highlight};}catch{// A restricted/unavailable canvas leaves the component's CSS fallback.
return empty;}}
  const refraction = /(?:Chrome|Chromium|Edg)\//.test(navigator.userAgent) && !/iPhone|iPad|iPod/.test(navigator.userAgent)
    && !(navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
  let glassId = 0;
  idle(() => document.querySelectorAll('.fx-glass').forEach(btn => {
    const q = s => btn.querySelector(s);
    const face = q('.ml-optical-face'), body = q('.ml-optical-body'), surface = q('.ml-optical-surface');
    const tint = q('.ml-optical-tint'), shoulderEl = q('.ml-optical-shoulder'), reflection = q('.ml-optical-reflection');
    const caustic = q('.ml-optical-caustic'), pointerLight = q('.ml-optical-pointer-light'), rim = q('.ml-optical-rim');
    const edgeLight = q('.ml-optical-edge-light'), counterLight = q('.ml-optical-counter-light');
    const SHOULDER = 10, BLUR = 2.5, REFRACT = 0.65, id = `fx-glass-${++glassId}`;
    let useFilter = false;
    const measure = () => {
      const w = Math.round(btn.offsetWidth), h = Math.round(btn.offsetHeight);
      if (!w || !h) return;
      const radius = Math.min(h / 2, parseFloat(getComputedStyle(btn).borderTopLeftRadius) || h / 2);
      const maps = makeGlassMaps(w, h, [radius, radius, radius, radius], SHOULDER);
      if (!maps.displacement) return;
      let img = q('.ml-optical-normal');
      if (!img) {
        img = document.createElement('img');
        img.className = 'ml-optical-normal';
        img.alt = '';
        img.draggable = false;
        shoulderEl.after(img);
      }
      img.src = maps.highlight;
      if (refraction) {
        const NS = 'http://www.w3.org/2000/svg';
        let svg = q('svg.fx-defs');
        if (!svg) { svg = document.createElementNS(NS, 'svg'); svg.setAttribute('class', 'fx-defs'); svg.setAttribute('aria-hidden', 'true'); btn.prepend(svg); }
        svg.innerHTML = '';
        const defs = document.createElementNS(NS, 'defs'), filter = document.createElementNS(NS, 'filter');
        Object.entries({ id, x: 0, y: 0, width: w, height: h, filterUnits: 'userSpaceOnUse', 'color-interpolation-filters': 'sRGB' })
          .forEach(([k, v]) => filter.setAttribute(k, v));
        const fe = document.createElementNS(NS, 'feImage');
        Object.entries({ href: maps.displacement, x: 0, y: 0, width: w, height: h, preserveAspectRatio: 'none', result: 'map' })
          .forEach(([k, v]) => fe.setAttribute(k, v));
        const dm = document.createElementNS(NS, 'feDisplacementMap');
        Object.entries({ in: 'SourceGraphic', in2: 'map', scale: 2 * SHOULDER * REFRACT, xChannelSelector: 'R', yChannelSelector: 'G' })
          .forEach(([k, v]) => dm.setAttribute(k, v));
        filter.append(fe, dm);
        defs.append(filter);
        svg.append(defs);
        useFilter = true;
      }
      paint();
    };
    // optics state; springs approximated by critically damped easing per frame
    const s = { x: 0, y: 0, tx: 0, ty: 0, h: 0, th: 0, p: 0, tp: 0 };
    let raf = 0, last = 0;
    const paint = () => {
      const { x, y, h, p } = s, hp = clamp(h, 0, 1);
      face.style.transform = `perspective(900px) rotateX(${-y * h * 0.45 + p * 2.4}deg) rotateY(${x * h * 0.75}deg) translateY(${-0.65 * h + 1.8 * p}px) scale(${1 - 0.009 * p}, ${1 - 0.026 * p})`;
      const lift = hp * (1 - p);
      body.style.boxShadow = `0 1px 1px #00000028,0 ${4 + lift * 1.5 - p * 2}px ${5 + lift * 1.5 - p * 2}px -3px #00000038,0 ${12 + lift * 2 - p * 8}px ${20 + lift * 3 - p * 11}px -10px #00000035`;
      const blur = BLUR + (BLUR * 0.12 - BLUR) * hp;
      const f = `${useFilter ? `url(#${id}) ` : ''}blur(${blur}px) saturate(1.08)`;
      surface.style.backdropFilter = f;
      surface.style.webkitBackdropFilter = refraction ? f : `blur(${blur}px) saturate(1.08)`;
      tint.style.opacity = 0.045 - 0.025 * hp;
      const v = hp * (1 - p * 0.4);
      shoulderEl.style.boxShadow = `inset 0 ${9 - v * 2.5}px ${12 - v * 2}px -8px #00000070,inset 0 ${-9 + v * 2}px 9px -7px #ffffffed,inset 5px 0 8px -7px #0000006b,inset -5px 0 8px -7px #0000004d`;
      reflection.style.transform = `translate(${-30 + h * 36 + x * h * 9}%, ${y * h * 5}px)`;
      reflection.style.opacity = 0.16 + 0.18 * hp + 0.08 * Math.sin(Math.PI * hp);
      caustic.style.transform = `translateX(${h * 75 + x * h * 55}%)`;
      caustic.style.opacity = 0.1 + 0.62 * h;
      const lx = 50 + x * 44, ly = 50 + y * 38, local = hp * 0.75 * (1 - p * 0.18);
      pointerLight.style.background = `radial-gradient(ellipse 76px 44px at ${lx}% ${ly}%, #ffffff2b 0%, #ffffff12 36%, #ffffff00 78%)`;
      pointerLight.style.opacity = local;
      edgeLight.style.background = `radial-gradient(ellipse 90px 48px at ${lx}% ${ly}%, #ffffffff 0%, #ffffffb8 32%, #ffffff00 82%)`;
      edgeLight.style.opacity = local;
      counterLight.style.background = `radial-gradient(ellipse 70px 36px at ${100 - lx}% ${100 - ly}%, #ffffffa6 0%, #ffffff35 35%, #ffffff00 82%)`;
      counterLight.style.opacity = local;
      const angle = 180 + x * h * 12 - h * 24;
      rim.style.background = `conic-gradient(from ${angle}deg at 50% 50%, #ffffffdf 0deg, #ffffff60 36deg, #ffffff05 68deg, #00000021 112deg, #ffffff18 155deg, #ffffff 190deg, #ffffffb3 217deg, #ffffff06 256deg, #0000000f 300deg, #ffffff15 335deg, #ffffffdf 360deg)`;
    };
    const tick = now => {
      const dt = last ? Math.min(0.05, (now - last) / 1000) : 1 / 60;
      last = now;
      const k = 1 - Math.exp(-dt * 16), kh = 1 - Math.exp(-dt * 9), kp = 1 - Math.exp(-dt * 22);
      s.x += (s.tx - s.x) * k; s.y += (s.ty - s.y) * k; s.h += (s.th - s.h) * kh; s.p += (s.tp - s.p) * kp;
      paint();
      const moving = Math.abs(s.tx - s.x) + Math.abs(s.ty - s.y) + Math.abs(s.th - s.h) + Math.abs(s.tp - s.p) > 0.002;
      raf = moving ? requestAnimationFrame(tick) : 0;
      if (!moving) last = 0;
    };
    const wake = () => { if (!raf) raf = requestAnimationFrame(tick); };
    if (!reduce) {
      const move = e => {
        if (e.pointerType !== 'mouse') return;
        const r = btn.getBoundingClientRect();
        s.tx = clamp((e.clientX - r.left) / r.width * 2 - 1, -1, 1);
        s.ty = clamp((e.clientY - r.top) / r.height * 2 - 1, -1, 1);
        s.th = 1;
        wake();
      };
      btn.addEventListener('pointerenter', move);
      btn.addEventListener('pointermove', move);
      btn.addEventListener('pointerleave', () => { s.th = 0; s.tp = 0; wake(); });
      btn.addEventListener('pointerdown', e => { if (e.button === 0) { s.tp = 1; wake(); } });
      addEventListener('pointerup', () => { if (s.tp) { s.tp = 0; wake(); } });
    }
    measure();
    let timer = 0;
    new ResizeObserver(() => { clearTimeout(timer); timer = setTimeout(measure, 90); }).observe(btn);
  }));

  /* ---------------- Liquid Metal button ---------------- */
  const METAL_VERTEX = 'attribute vec2 position;varying vec2 uv;void main(){uv=position*.5+.5;gl_Position=vec4(position,0.,1.);}';
  const METAL_FRAGMENT = `
precision highp float;
varying vec2 uv;
uniform float time, pixels, tube, flow, dispersion, glow, warmth, hover, hoverTone, hoverIntensity, press, response, release;
uniform vec2 pointer;
const float PI=3.14159265;
float pool(float a,float b,float sharp){return exp((cos(a-b)-1.)*sharp);}
float studio(vec3 r,float a,float q,float shift){
    float f=sin(a*2.-time*.53)+.28*sin(3.*a+time*.31)+q*.52+r.z*.12+shift;
    float main=smoothstep(-.5,-.28,f)-smoothstep(.37,.57,f);
    float strip=smoothstep(.84,.95,f);
    float curve=.5+.5*r.z;
    return .12+.75*main+.65*strip+.12*curve;
}
void main(){
    vec2 p=(vec2(uv.x,1.-uv.y)*2.-1.)*1.2;
    float r=max(length(p),.0001);
    float a=atan(p.y,p.x);
    float phase=time*.65;
    float aim=atan(pointer.y+.0001,pointer.x+.0001);
    float attraction=pool(a,aim,2.8)*hover;
    float wave=sin(3.*a-release*11.)*sin(PI*release)*exp(-release*2.7);
    float rip=flow*(.010*sin(3.*a-phase*1.3)+.006*sin(5.*a+phase*.8));
    float radius=.81+rip+attraction*.018*response-press*.012*response+wave*.035*response;
    float width=tube*(1.+flow*.16*sin(2.*a-phase)+attraction*.19*response+press*.24*response);
    float q=(r-radius)/max(width,.018);
    float aa=2.64/max(pixels,1.);
    float coverage=1.-smoothstep(width-aa,width+aa,abs(r-radius));
    float z=sqrt(max(.0001,1.-clamp(q*q,0.,1.)));
    vec2 tangent=vec2(-p.y,p.x)/r;
    vec3 normal=normalize(vec3(p/r*clamp(q,-1.,1.)+tangent*(.10*flow*sin(3.*a-phase)+wave*.35),z));
    vec3 reflected=reflect(vec3(0.,0.,-1.),normal);
    float shift=dispersion*(.08+.13*pool(a,phase+.7,2.));
    vec3 chrome=vec3(studio(reflected,a,q,shift),studio(reflected,a,q,0.),studio(reflected,a,q,-shift));
    float hot=pool(a,phase-1.9,12.)+pool(a,-phase*.71+1.2,20.)*.7;
    chrome+=vec3(.75,.87,1.)*hot*pow(z,2.)*.72;
    float hoverCore=attraction*pow(z,4.)*hoverIntensity;
    vec3 hoverTarget=mix(vec3(.08,.12,.19),vec3(1.),step(0.,hoverTone));
    chrome=mix(chrome,hoverTarget,hoverCore*mix(.50,.46,step(0.,hoverTone)));
    chrome*=mix(vec3(1.),vec3(1.14,.96,.72),max(0.,warmth));
    chrome*=mix(vec3(1.),vec3(.78,.93,1.13),max(0.,-warmth));
    chrome=mix(chrome,vec3(.94,.98,1.),pow(abs(clamp(q,-1.,1.)),14.)*.38);
    float halo=exp(-pow((r-radius)/(width*2.8),2.))*hot*glow*.21*(1.-smoothstep(1.08,1.2,r));
    vec3 haloColor=mix(vec3(.65,.79,1.),vec3(1.,.88,.65),.5+.5*sin(a+phase));
    float alpha=coverage+(1.-coverage)*halo;
    vec3 col=clamp(chrome,0.,1.)*coverage+haloColor*(1.-coverage)*halo;
    gl_FragColor=vec4(col,alpha);
}`;
  const METAL = { thickness: 5.2, flow: 0.65, dispersion: 0.65, glow: 0.5, warmth: 0 };
  const MOTION = { speed: 0.8, attraction: 0.7, response: 0.65 };
  const EDGE = { width: 3.2, speed: 1, flow: 0.75 }, ICON_SIZE = 52, ICON_ANGLE = 135, HOVER_INTENSITY = 0.72;
  idle(() => document.querySelectorAll('.fx-metal').forEach(root => {
    const canvas = root.querySelector('.fx-metal-canvas');
    const gradient = root.querySelector('linearGradient');
    const input = { x: -0.5, y: -0.5, sx: 0.5, sy: 0.5, hovering: false, focused: false, pressed: false, release: 1 };
    let gl = null;
    try { gl = canvas.getContext('webgl', { alpha: true, premultipliedAlpha: true, antialias: false, depth: false, stencil: false, powerPreference: 'low-power' }); } catch (_) {}
    if (!gl) return;  // the CSS chrome ring stays as the fallback
    const compile = (type, src) => { const sh = gl.createShader(type); gl.shaderSource(sh, src); gl.compileShader(sh); return gl.getShaderParameter(sh, gl.COMPILE_STATUS) ? sh : null; };
    const vs = compile(gl.VERTEX_SHADER, METAL_VERTEX), fs = compile(gl.FRAGMENT_SHADER, METAL_FRAGMENT);
    if (!vs || !fs) return;
    const program = gl.createProgram();
    gl.attachShader(program, vs); gl.attachShader(program, fs); gl.linkProgram(program);
    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) return;
    gl.useProgram(program);
    gl.bindBuffer(gl.ARRAY_BUFFER, gl.createBuffer());
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, -1, 1, 1, -1, 1, 1]), gl.STATIC_DRAW);
    const position = gl.getAttribLocation(program, 'position');
    gl.enableVertexAttribArray(position);
    gl.vertexAttribPointer(position, 2, gl.FLOAT, false, 0, 0);
    const u = {};
    ['time', 'pixels', 'tube', 'flow', 'dispersion', 'glow', 'warmth', 'hover', 'hoverTone', 'hoverIntensity', 'press', 'response', 'release', 'pointer']
      .forEach(n => { u[n] = gl.getUniformLocation(program, n); });
    const set = (n, v) => gl.uniform1f(u[n], v);
    set('tube', Math.min(0.16, Math.max(0.022, METAL.thickness / ICON_SIZE)));
    set('flow', METAL.flow); set('dispersion', METAL.dispersion); set('glow', METAL.glow); set('warmth', METAL.warmth);
    set('response', MOTION.response); set('hoverTone', 1); set('hoverIntensity', HOVER_INTENSITY);
    let phase = 1.4, frame = 0, last = 0, visible = true, hover = 0, press = 0, x = -0.5, y = -0.5, sx = 0.5, sy = 0.5;
    const draw = () => {
      gl.viewport(0, 0, canvas.width, canvas.height);
      set('pixels', canvas.width); set('time', phase); set('hover', hover * MOTION.attraction); set('press', press);
      set('release', reduce ? 1 : input.release);
      gl.uniform2f(u.pointer, x, y);
      gl.drawArrays(gl.TRIANGLES, 0, 6);
      canvas.style.opacity = '1';
      root.setAttribute('data-renderer', 'webgl');
      const ep = phase * EDGE.speed, st = root.style;
      st.setProperty('--orb-phase', `${ep * 46 - 85}deg`);
      st.setProperty('--orb-counter', `${-ep * 31 + 75}deg`);
      st.setProperty('--orb-pool-x', `${50 + Math.sin(ep * 0.73) * 16 * EDGE.flow}%`);
      st.setProperty('--orb-pool-y', `${50 + Math.cos(ep * 0.57) * 22 * EDGE.flow}%`);
      const pull = hover * MOTION.attraction * HOVER_INTENSITY;
      const lx = 50 + Math.cos(ep * 0.91) * 48, ly = 50 + Math.sin(ep * 0.91) * 48;
      st.setProperty('--orb-light-x', `${lx + (sx * 100 - lx) * pull}%`);
      st.setProperty('--orb-light-y', `${ly + (sy * 100 - ly) * pull}%`);
      st.setProperty('--orb-wake-x', `${sx * 100}%`);
      st.setProperty('--orb-wake-y', `${sy * 100}%`);
      ['top', 'right', 'bottom', 'left'].forEach((side, i) => st.setProperty(`--orb-edge-${side}`, `${EDGE.width * (1 + Math.sin(ep * 1.13 + i * Math.PI * 0.5) * 0.28 * EDGE.flow)}px`));
      const shift = Math.sin(phase * 0.8) * 35;
      if (gradient) gradient.setAttribute('gradientTransform', `rotate(${ICON_ANGLE - 90 + shift * 0.45} .5 .5)`);
    };
    const tick = now => {
      frame = 0;
      if (!visible || document.hidden || reduce) { last = 0; return; }
      const dt = last ? Math.min(0.05, (now - last) / 1000) : 1 / 60;
      last = now;
      const active = input.hovering || input.focused, k = 1 - Math.exp(-dt * 10);
      hover += ((active ? 1 : 0) - hover) * k;
      press += ((input.pressed ? 1 : 0) - press) * (1 - Math.exp(-dt * 18));
      x += (input.x - x) * k; y += (input.y - y) * k; sx += (input.sx - sx) * k; sy += (input.sy - sy) * k;
      input.release = Math.min(1, input.release + dt * 1.35);
      phase += dt * MOTION.speed;  // "ambient" mode: always flowing while visible
      draw();
      frame = requestAnimationFrame(tick);
    };
    const wake = () => { if (!frame && visible && !document.hidden && !reduce) frame = requestAnimationFrame(tick); };
    const resize = () => {
      const box = canvas.getBoundingClientRect(), dpr = Math.min(devicePixelRatio || 1, 2);
      canvas.width = Math.max(1, Math.min(512, Math.round(box.width * dpr)));
      canvas.height = canvas.width;
      draw();
      wake();
    };
    new ResizeObserver(resize).observe(canvas);
    new IntersectionObserver(([e]) => { visible = e.isIntersecting; if (visible) wake(); else { cancelAnimationFrame(frame); frame = 0; last = 0; } }).observe(root);
    document.addEventListener('visibilitychange', () => { if (!document.hidden) wake(); });
    const activeAttr = () => { root.setAttribute('data-active', String(input.hovering || input.focused)); wake(); };
    const pressed = v => { input.pressed = v; root.setAttribute('data-pressed', String(v)); wake(); };
    const pointer = e => {
      const b = canvas.getBoundingClientRect();
      const px = (e.clientX - b.left) / Math.max(1, b.width) * 2 - 1, py = (e.clientY - b.top) / Math.max(1, b.height) * 2 - 1;
      const len = Math.max(1, Math.hypot(px, py));
      input.x = px / len; input.y = py / len;
      const f = root.getBoundingClientRect();
      input.sx = clamp((e.clientX - f.left) / Math.max(1, f.width), 0, 1);
      input.sy = clamp((e.clientY - f.top) / Math.max(1, f.height), 0, 1);
      wake();
    };
    if (!reduce) {
      root.addEventListener('pointerenter', e => { if (e.pointerType !== 'touch') { input.hovering = true; pointer(e); activeAttr(); } });
      root.addEventListener('pointermove', pointer);
      root.addEventListener('pointerleave', () => { input.hovering = false; pressed(false); activeAttr(); });
      root.addEventListener('pointerdown', e => { if (e.button === 0) { pointer(e); pressed(true); } });
      root.addEventListener('pointerup', () => { if (input.pressed) { pressed(false); input.release = 0; wake(); } });
      root.addEventListener('focus', () => { if (root.matches(':focus-visible')) { input.focused = true; input.sx = input.sy = 0.5; activeAttr(); } });
      root.addEventListener('blur', () => { input.focused = false; pressed(false); activeAttr(); });
    } else {
      root.setAttribute('data-reduced', 'true');
    }
    resize();
  }));
})();
