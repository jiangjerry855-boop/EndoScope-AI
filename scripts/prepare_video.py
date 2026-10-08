"""Burn concise English captions below the unchanged desktop recording."""
from pathlib import Path
import json, subprocess, tempfile, textwrap
ROOT=Path(__file__).resolve().parents[1]
assets=ROOT/'web/assets'
steps=json.loads((assets/'chapters.json').read_text())
def stamp(t):
    ticks=round(t*100)
    return f'{ticks//360000:01d}:{ticks//6000%60:02d}:{ticks//100%60:02d}.{ticks%100:02d}'
header='''[Script Info]
ScriptType: v4.00+
PlayResX: 1280
PlayResY: 800
WrapStyle: 2
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Caption,DejaVu Sans,26,&H00F4F6F5,&H000000FF,&H002C2B10,&H002C2B10,0,0,0,0,100,100,0,0,1,0,0,2,60,60,48,1
Style: Notice,DejaVu Sans,16,&H00BDD5CF,&H000000FF,&H002C2B10,&H002C2B10,0,0,0,0,100,100,0,0,1,0,0,2,40,40,14,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
for s in steps:
    caption=r'\N'.join(textwrap.wrap(s['caption_en'],width=82))
    header+=f'Dialogue: 0,{stamp(s["start"])},{stamp(s["end"])},Caption,,0,0,0,,{caption}\n'
header+='Dialogue: 0,0:00:00.00,0:00:32.70,Notice,,0,0,0,,EndoScope AI | Research and education only | Not a diagnostic device\n'
with tempfile.TemporaryDirectory(prefix='endoscope-captions-') as temporary:
    ass=Path(temporary)/'captions.ass'; ass.write_text(header)
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(assets/'endoscope-demo.mp4'),'-vf',f'pad=1280:800:0:0:color=0x102b2c,ass={ass}','-c:v','libx264','-preset','fast','-crf','19','-c:a','copy','-movflags','+faststart',str(assets/'endoscope-demo-en.mp4')],check=True)
print(assets/'endoscope-demo-en.mp4')
