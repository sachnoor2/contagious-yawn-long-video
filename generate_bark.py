import re, subprocess, pathlib, numpy as np, torch
from transformers import AutoProcessor, BarkModel
from scipy.io import wavfile
text=pathlib.Path('script_hinglish.txt').read_text(); text=text.split('HOOK:',1)[-1]
parts=[p.strip() for p in re.split(r'\n\s*\n',text) if p.strip() and not p.startswith(('TITLE:','END CARD:'))]
out=pathlib.Path('audio_parts');out.mkdir(exist_ok=True)
proc=AutoProcessor.from_pretrained('suno/bark'); model=BarkModel.from_pretrained('suno/bark'); model.eval()
for i,p in enumerate(parts):
 x=proc(p,voice_preset='v2/hi_speaker_2',return_tensors='pt')
 with torch.no_grad(): y=model.generate(**x,do_sample=True)
 y=y.cpu().numpy().squeeze(); sr=model.generation_config.sample_rate
 wavfile.write(out/f'{i:02}.wav',sr,(np.clip(y,-1,1)*32767).astype(np.int16))
# cap internal silence gaps at 500ms, fade 8ms per part, 18ms crossfades
files=sorted(out.glob('*.wav')); norm=pathlib.Path('audio_norm');norm.mkdir(exist_ok=True)
for p in files:
 q=norm/p.name; subprocess.run(['ffmpeg','-y','-i',str(p),'-af','silenceremove=stop_periods=-1:stop_duration=0.5:stop_threshold=-42dB,afade=t=in:d=0.008,afade=t=out:d=0.008',str(q)],check=True)
inputs=[]
for p in sorted(norm.glob('*.wav')): inputs += ['-i',str(p)]
# concat with 18ms crossfades
cmd=['ffmpeg','-y',*inputs,'-filter_complex']
if len(files)==1: filt='[0:a]anull[out]'
else:
 filt='[0:a][1:a]acrossfade=d=0.018:c1=tri:c2=tri[x1]'
 for i in range(2,len(files)): filt+=f';[x{i-1}][{i}:a]acrossfade=d=0.018:c1=tri:c2=tri[x{i}]'
 filt=filt.replace(f'[x{len(files)-1}]','')+'[out]'
cmd += [filt,'-map','[out]','-af','atempo=1.08,aresample=async=1:first_pts=0','-ar','24000','-ac','1','public/audio/voiceover.wav']
subprocess.run(cmd,check=True)
subprocess.run(['ffprobe','-v','error','-show_streams','-of','json','public/audio/voiceover.wav'],check=True)
