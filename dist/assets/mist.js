/* Animated "Mist" background for sections marked .s_nv_mist.
   The warp shader comes from Paper Shaders (@paper-design/shaders, MIT), used
   with the "Mist" preset of the AnimatedLiquidBackground Framer component and
   recoloured from pink to the brand green. Plain WebGL2, no libraries.
   Drawn at half resolution; paused off screen; with reduced motion or
   Save-Data a single still frame is drawn instead of the animation. */
(() => {
  const hosts = document.querySelectorAll('.s_nv_mist');
  if (!hosts.length) return;
  const still = matchMedia('(prefers-reduced-motion: reduce)').matches
    || (navigator.connection && navigator.connection.saveData);

  // "Mist" preset, mapped exactly as the component maps its controls to uniforms
  const MIST = {
    color1: [0.043, 0.122, 0.090, 1], color2: [0.118, 0.541, 0.376, 1], color3: [0.043, 0.122, 0.090, 1],  // #0B1F17 / #1E8A60 / #0B1F17
    rotation: 0, proportion: 0.33, scale: 0.48, distortion: 4 / 50, swirl: 0.65, swirlIterations: 5,
    softness: 1, shape: 2 /* Edge */, shapeScale: 0.48, speed: 0.5446, seedMs: -2350 * 1000 / 120,
  };

  const VERT = `#version 300 es
layout(location=0) in vec4 a_position;void main(){gl_Position=a_position;}`;
  const FRAG = `#version 300 es
precision highp float;
uniform float u_time;uniform float u_pixelRatio;uniform vec2 u_resolution;
uniform float u_scale;uniform float u_rotation;uniform vec4 u_color1;uniform vec4 u_color2;uniform vec4 u_color3;
uniform float u_proportion;uniform float u_softness;uniform float u_shape;uniform float u_shapeScale;
uniform float u_distortion;uniform float u_swirl;uniform float u_swirlIterations;
out vec4 fragColor;
#define TWO_PI 6.28318530718
#define PI 3.14159265358979323846
vec2 rotate(vec2 uv,float th){return mat2(cos(th),sin(th),-sin(th),cos(th))*uv;}
float random(vec2 st){return fract(sin(dot(st.xy,vec2(12.9898,78.233)))*43758.5453123);}
float noise(vec2 st){vec2 i=floor(st),f=fract(st);
  float a=random(i),b=random(i+vec2(1.,0.)),c=random(i+vec2(0.,1.)),d=random(i+vec2(1.,1.));
  vec2 u=f*f*(3.-2.*f);return mix(mix(a,b,u.x),mix(c,d,u.x),u.y);}
vec4 blend_colors(vec4 c1,vec4 c2,vec4 c3,float mixer,float edgesWidth,float edge_blur){
  vec3 color1=c1.rgb*c1.a,color2=c2.rgb*c2.a,color3=c3.rgb*c3.a;
  float r1=smoothstep(.0+.35*edgesWidth,.7-.35*edgesWidth+.5*edge_blur,mixer);
  float r2=smoothstep(.3+.35*edgesWidth,1.-.35*edgesWidth+edge_blur,mixer);
  vec3 c=mix(mix(color1,color2,r1),color3,r2);float o=mix(mix(c1.a,c2.a,r1),c3.a,r2);return vec4(c,o);}
void main(){
  vec2 uv=gl_FragCoord.xy/u_resolution.xy;float t=.5*u_time;float noise_scale=.0005+.006*u_scale;
  uv-=.5;uv*=(noise_scale*u_resolution);uv=rotate(uv,u_rotation*.5*PI);uv/=u_pixelRatio;uv+=.5;
  float n1=noise(uv*1.+t),n2=noise(uv*2.-t),angle=n1*TWO_PI;
  uv.x+=4.*u_distortion*n2*cos(angle);uv.y+=4.*u_distortion*n2*sin(angle);
  float iterations_number=ceil(clamp(u_swirlIterations,1.,30.));
  for(float i=1.;i<=iterations_number;i++){
    uv.x+=clamp(u_swirl,0.,2.)/i*cos(t+i*1.5*uv.y);uv.y+=clamp(u_swirl,0.,2.)/i*cos(t+i*1.*uv.x);}
  float proportion=clamp(u_proportion,0.,1.),shape=0.,mixer=0.;
  if(u_shape<.5){vec2 s=uv*(.5+3.5*u_shapeScale);shape=.5+.5*sin(s.x)*cos(s.y);
    mixer=shape+.48*sign(proportion-.5)*pow(abs(proportion-.5),.5);}
  else if(u_shape<1.5){vec2 s=uv*(.25+3.*u_shapeScale);float f=fract(s.y);
    shape=smoothstep(.0,.55,f)*smoothstep(1.,.45,f);mixer=shape+.48*sign(proportion-.5)*pow(abs(proportion-.5),.5);}
  else{float sh=1.-uv.y;sh-=.5;sh/=(noise_scale*u_resolution.y);sh+=.5;
    float shape_scaling=.2*(1.-u_shapeScale);shape=smoothstep(.45-shape_scaling,.55+shape_scaling,sh+.3*(proportion-.5));mixer=shape;}
  vec4 color_mix=blend_colors(u_color1,u_color2,u_color3,mixer,1.-clamp(u_softness,0.,1.),.01+.01*u_scale);
  fragColor=vec4(color_mix.rgb,color_mix.a);
}`;

  const mount = host => {
    const canvas = document.createElement('canvas');
    canvas.className = 's_nv_fx_canvas';
    canvas.setAttribute('aria-hidden', 'true');
    const gl = canvas.getContext('webgl2', { antialias: false, premultipliedAlpha: true, powerPreference: 'low-power' });
    if (!gl) return;
    const compile = (type, src) => {
      const s = gl.createShader(type);
      gl.shaderSource(s, src);
      gl.compileShader(s);
      return gl.getShaderParameter(s, gl.COMPILE_STATUS) ? s : null;
    };
    const vs = compile(gl.VERTEX_SHADER, VERT), fs = compile(gl.FRAGMENT_SHADER, FRAG);
    if (!vs || !fs) return;
    const prog = gl.createProgram();
    gl.attachShader(prog, vs);
    gl.attachShader(prog, fs);
    gl.linkProgram(prog);
    if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) return;
    gl.useProgram(prog);
    gl.bindBuffer(gl.ARRAY_BUFFER, gl.createBuffer());
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, -1, 1, 1, -1, 1, 1]), gl.STATIC_DRAW);
    gl.enableVertexAttribArray(0);
    gl.vertexAttribPointer(0, 2, gl.FLOAT, false, 0, 0);
    const u = name => gl.getUniformLocation(prog, name);
    gl.uniform1f(u('u_scale'), MIST.scale);
    gl.uniform1f(u('u_rotation'), MIST.rotation * Math.PI / 180);
    gl.uniform4fv(u('u_color1'), MIST.color1);
    gl.uniform4fv(u('u_color2'), MIST.color2);
    gl.uniform4fv(u('u_color3'), MIST.color3);
    gl.uniform1f(u('u_proportion'), MIST.proportion);
    gl.uniform1f(u('u_softness'), MIST.softness);
    gl.uniform1f(u('u_shape'), MIST.shape);
    gl.uniform1f(u('u_shapeScale'), MIST.shapeScale);
    gl.uniform1f(u('u_distortion'), MIST.distortion);
    gl.uniform1f(u('u_swirl'), MIST.swirl);
    gl.uniform1f(u('u_swirlIterations'), MIST.swirlIterations);
    const uTime = u('u_time'), uRes = u('u_resolution'), uRatio = u('u_pixelRatio');

    // The pattern is soft, so half resolution looks the same; u_pixelRatio keeps its scale.
    const K = 0.5;
    const resize = () => {
      const r = host.getBoundingClientRect();
      canvas.width = Math.max(1, Math.round(r.width * K));
      canvas.height = Math.max(1, Math.round(r.height * K));
      gl.viewport(0, 0, canvas.width, canvas.height);
      gl.uniform2f(uRes, canvas.width, canvas.height);
      gl.uniform1f(uRatio, K);
      if (still) draw(0);
    };
    let elapsed = MIST.seedMs, last = 0, visible = false, frame = 0;
    const draw = dt => {
      elapsed += dt * MIST.speed;
      gl.uniform1f(uTime, elapsed * 0.001);
      gl.drawArrays(gl.TRIANGLES, 0, 6);
      canvas.classList.add('is-ready');
    };
    host.prepend(canvas);
    resize();
    new ResizeObserver(resize).observe(host);
    if (still) return;

    const loop = now => {
      if (!visible || document.hidden) { frame = 0; return; }
      draw(last ? Math.min(now - last, 50) : 0);
      last = now;
      frame = requestAnimationFrame(loop);
    };
    const resume = () => { if (!frame && visible && !document.hidden) { last = 0; frame = requestAnimationFrame(loop); } };
    new IntersectionObserver(([e]) => { visible = e.isIntersecting; resume(); }, { rootMargin: '100px' }).observe(host);
    document.addEventListener('visibilitychange', resume);
  };

  const start = () => hosts.forEach(mount);
  if (document.readyState === 'complete') start(); else addEventListener('load', start, { once: true });
})();
