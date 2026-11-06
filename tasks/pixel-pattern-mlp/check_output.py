"""Check recorded scene states and decode actual review frames and motion samples."""
import argparse,json,hashlib,subprocess
from pathlib import Path
import av
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('run',type=Path);args=p.parse_args();run=args.run
trace=json.loads((ROOT/'trace.json').read_text());stages=json.loads((run/'stages.json').read_text())
layout=json.loads((run/'layout.json').read_text());signals=json.loads((run/'signals.json').read_text())
video=run/'visualization.mp4'
container=av.open(str(video));stream=container.streams.video[0];frames=0
width,height,fps=stream.codec_context.width,stream.codec_context.height,float(stream.average_rate)
for f in container.decode(video=0):frames+=1
container.close()
assert frames>0
violations=[]
for stage,info in layout.items():
 for obj in info['objects']:
  l,r,b,t=obj['bounds']
  if l < -7.1112 or r>7.1112 or b < -4 or t >4:violations.append((stage,obj))
assert not violations,violations
# This also catches a display that keeps old parameters when its metrics advance.
for step in [1,32,128,512,1024,2048]:
 s=next(s for s in trace['snapshots'] if s['step']==step)
 for key in ['params','h','p','loss','test_correct']:
  expected=s[key] if key in s else s['example'][key]
  if key=='params':
   for a,b in zip(layout[f'training-{step}']['values'][key],expected):np.testing.assert_allclose(a,b,atol=1e-14,rtol=0)
  else:np.testing.assert_allclose(layout[f'training-{step}']['values'][key],expected,atol=1e-14,rtol=0)
for stage,info in layout.items():
 if 'rendered' not in info or not info['rendered']:continue
 actual=info['rendered'];assert actual['minimum_entry_gap']>.025,(stage,actual['minimum_entry_gap'])
 assert actual['brackets']==['#FFFFFF','#FFFFFF']
 assert actual['native_layer_types']==['FeedForwardLayer']*3
 if stage.startswith('training-') or stage in ['sgd-update','same-image-after-update','complete-network']:
  state=info['values']
  for k in range(2):
   expected=[f'{v:.2f}' if abs(v)>=.005 else '0.00' for row in state['params'][2*k] for v in row]
   assert actual['matrix_entries'][k]==expected,(stage,k,actual['matrix_entries'][k],expected)
 if stage.startswith('training-') or stage in ['same-image-after-update','complete-network']:
  np.testing.assert_allclose(actual['probability_bar_values'],np.maximum(.002/1.55,info['values']['p']),atol=1e-9,rtol=0)
  for k,key in enumerate(['x','h','p']):
   digits=3 if k==2 else 2
   expected=[f'{v:.{digits}f}' if abs(v)>=.5*10**(-digits) else f'{0:.{digits}f}' for v in info['values'][key]]
   assert actual['node_labels'][k]==expected,(stage,k)
assert next(s['count'] for s in signals if s['key']=='hidden-gradient-backward')==12
assert any(s['reverse'] for s in signals) and any(not s['reverse'] for s in signals)
review=ROOT/'review-frames';review.mkdir(exist_ok=True)
def frame_at(time):
 c=av.open(str(video));st=c.streams.video[0];c.seek(int(time/float(st.time_base)),stream=st,backward=True)
 result=None
 for frame in c.decode(video=0):
  if frame.time>=time:result=frame.to_image();break
 c.close();assert result is not None
 return result
names=['problem','architecture-and-weights','selected-weight-vector','hidden-activations','initial-prediction','cross-entropy','backpropagation','selected-gradient','sgd-update','same-image-after-update','training-128','complete-network']
for i in range(0,len(names),3):
 sheet=Image.new('RGB',(960,3*565),'#171717');draw=ImageDraw.Draw(sheet)
 for row,name in enumerate(names[i:i+3]):
  im=frame_at(stages[name]);im.save(review/f'{name}.png');im.thumbnail((960,540));sheet.paste(im,(0,row*565+25));draw.text((15,row*565+6),f'{name} @ {stages[name]:.2f}s',fill='white')
 sheet.save(review/f'sheet-{i//3}.jpg',quality=93)
# Sparse full-duration motion review (actual decoded frames, never a replacement artifact).
ims=[]
for sec in np.arange(0,stages['complete-network']+1,.7):
 im=frame_at(float(sec));im.thumbnail((640,360));ims.append(im)
ims[0].save(review/'motion.webp',save_all=True,append_images=ims[1:],duration=140,loop=0,quality=65)
report=dict(status='passed',frames_decoded=frames,width=width,height=height,
 duration=frames/fps,fps=fps,stage_frames=names,
 out_of_frame_objects=violations,signals=signals,artifact_sha256=hashlib.sha256(video.read_bytes()).hexdigest(),
 font_evidence='All prose uses Tex; all arithmetic, matrix entries and labels use MathTex. Default LaTeX article Computer Modern; no Text objects in scene.py.',
 layout_scope='Recorded object bounds and explicit state checks plus separate human frame/motion review; bounds alone do not certify readability.')
(ROOT/'output-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['signals','stage_frames']},indent=2))
