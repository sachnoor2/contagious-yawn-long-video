import subprocess, pathlib
chunks=sorted(pathlib.Path('out/chunks').glob('chunk-*.mp4'))
assert len(chunks)==5, f'expected 5 chunks, found {len(chunks)}'
with open('out/concat.txt','w') as f:
 for p in chunks:f.write(f"file '{p.resolve()}'\n")
subprocess.run(['ffmpeg','-y','-f','concat','-safe','0','-i','out/concat.txt','-c','copy','out/contagious-yawn-final.mp4'],check=True)
