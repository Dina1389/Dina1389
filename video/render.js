// Renders index.html frame-by-frame into MP4 segments, then muxes with the voice-over.
// usage: node render.js [workers] [fps]
const {chromium}=require('playwright');const {spawn,execFileSync}=require('child_process');const path=require('path');const fs=require('fs');
const W=+(process.argv[2]||4),FPS=+(process.argv[3]||30),DUR=344.27;
const N=Math.ceil(DUR*FPS),dir=path.join(__dirname,'build');fs.mkdirSync(dir,{recursive:true});
async function worker(i,b){
  const a=Math.floor(N*i/W),e=Math.floor(N*(i+1)/W);
  const ff=spawn('ffmpeg',['-v','error','-y','-f','image2pipe','-framerate',FPS,'-c:v','mjpeg','-i','-','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p',`${dir}/seg${i}.mp4`],{stdio:['pipe','inherit','inherit']});
  const p=await b.newPage({viewport:{width:1080,height:1920}});
  await p.goto('file://'+path.join(__dirname,'index.html'));await p.evaluate(()=>document.fonts.ready);
  for(let f=a;f<e;f++){await p.evaluate(t=>setTime(t),f/FPS);const buf=await p.screenshot({type:'jpeg',quality:95});
    if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));
    if(i===0&&(f-a)%300===0)console.log(`w0 ${f-a}/${e-a}`);}
  ff.stdin.end();await new Promise(r=>ff.on('close',r));
}
(async()=>{const b=await chromium.launch({args:['--allow-file-access-from-files']});
  await Promise.all([...Array(W)].map((_,i)=>worker(i,b)));await b.close();
  fs.writeFileSync(`${dir}/list.txt`,[...Array(W)].map((_,i)=>`file 'seg${i}.mp4'`).join('\n'));
  execFileSync('ffmpeg',['-v','error','-y','-f','concat','-safe','0','-i',`${dir}/list.txt`,'-i',path.join(__dirname,'audio/voiceover.mp3'),'-c:v','copy','-c:a','aac','-b:a','192k','-shortest','-movflags','+faststart',path.join(__dirname,'install-as-app-tiktok.mp4')]);
  console.log('done');})();
