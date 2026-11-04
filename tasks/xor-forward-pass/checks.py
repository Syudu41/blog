"""Independently verify XOR, activation-curve markers, and rendered media."""
import hashlib
import json
import math
from pathlib import Path

import av
import numpy as np
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parent


def main():
    run=sorted((ROOT/'runs').glob('*/layout.json'))[-1].parent
    data=json.loads((run/'computation.json').read_text())
    layout=json.loads((run/'layout.json').read_text())
    stages=json.loads((run/'stages.json').read_text())
    assert data["w1"]==[[1,-1],[-1,1]] and data["b1"]==[0,0]
    assert data["w2"]==[[10,10]] and data["b2"]==-5
    errors=[]
    for case in data['cases']:
        a,b=case['x'];z=[a-b,b-a];h=[max(0,v) for v in z]
        logit=10*sum(h)-5;p=1/(1+math.exp(-logit));y=int(a!=b)
        loss=math.log1p(math.exp(-abs(logit)))
        assert case['y']==y and int(p>=.5)==y
        for name,expected in [('z',z),('h',h),('logit',logit),('p',p),('loss',loss)]:
            np.testing.assert_allclose(case[name],expected,atol=1e-12,rtol=1e-12)
            errors.append(float(np.max(np.abs(np.array(case[name])-expected))))
    assert [len(layer) for layer in layout['nodes']]==[2,2,1] and layout['edges']==[4,2]
    for g,result in zip(layout['graphs'],[1,0,1/(1+math.exp(-5))]):assert abs(g['activation']-result)<1e-12
    assert stages['hidden-weighted-sums']<stages['relu-positive-neuron-value']<stages['relu-negative-neuron-value']<stages['hidden-output-start']<stages['output-logit']<stages['sigmoid-neuron-value']<stages['prediction']<stages['completed-forward-pass']
    samples=[(k,t) for k,t in stages.items() if not k.endswith('-start')]
    motion=[('input-flow-early',stages['input-hidden-start']+.45),('input-flow-late',stages['input-hidden-start']+1.25),
            ('output-flow-early',stages['hidden-output-start']+.45),('output-flow-late',stages['hidden-output-start']+1.25)]
    samples+=motion;captures={};frames=0;duration=0
    path=ROOT/'output/visualization.mp4'
    with av.open(str(path)) as video:
        stream=video.streams.video[0]
        assert (stream.width,stream.height)==(1920,1080)
        assert stream.codec_context.name=='h264' and stream.pix_fmt=='yuv420p' and stream.average_rate==30
        for frame in video.decode(video=0):
            frames+=1;time=float(frame.time);duration=time+1/30
            for name,target in samples:
                distance=abs(time-target)
                if distance<=.04 and (name not in captures or distance<captures[name][0]):captures[name]=(distance,frame.to_image())
    assert 25<=duration<=65 and frames>750 and path.stat().st_size<20000000
    # The evaluated graph cursor must lie at the function's correct output.
    orange=np.array([212,98,23]);marker_errors=[]
    for graph,name in zip(layout['graphs'],['relu-positive','relu-negative','sigmoid']):
        image=np.array(captures[name+'-on-curve'][1],float)
        px=round(960+135*graph['on_curve'][0]);py=round(540-135*graph['on_curve'][1])
        patch=image[py-3:py+4,px-3:px+4]
        error=float(np.min(np.max(np.abs(patch-orange),axis=2)))
        assert error<25,(name,error)
        marker_errors.append(error)
    # Activation fills must reflect the actual hidden and output values.
    image=np.array(captures['completed-forward-pass'][1],float)
    color_errors=[];case=data['cases'][2];values=[case['x'],case['h'],[case['p']]]
    for points,vals in zip(layout['nodes'],values):
        for point,value in zip(points,vals):
            px=round(960+point[0]*135);py=round(540-(point[1]+.18)*135)
            actual=np.median(image[py-1:py+2,px-1:px+2],axis=(0,1))
            expected=255*(1-.55*value)+np.array([18,107,145])*.55*value
            color_errors.append(float(np.max(abs(actual-expected))))
    assert max(color_errors)<15,max(color_errors)
    for start in range(0,len(samples),4):
        sheet=Image.new('RGB',(1800,1052),'white');draw=ImageDraw.Draw(sheet)
        for i,(name,time) in enumerate(samples[start:start+4]):
            x=(i%2)*900;y=(i//2)*526
            sheet.paste(captures[name][1].resize((900,506)),(x,y+20))
            draw.text((x+8,y+3),f'{name}: {time:.2f}s',fill='black')
        sheet.save(ROOT/f'review-stages-{start//4+1}.png')
    thumb=captures['completed-forward-pass'][1].copy();thumb.thumbnail((640,640));thumb.save(ROOT/'output/thumbnail.png')
    with Image.open(ROOT/'output/thumbnail.png') as image:assert image.size==(640,360);image.verify()
    environment=json.loads((run/'result.json').read_text())['environment']
    report=dict(sha256=hashlib.sha256(path.read_bytes()).hexdigest(),dimensions=[1920,1080],frames=frames,
                duration=round(duration,3),fps=30,bytes=path.stat().st_size,
                arithmetic_max_error=max(errors),curve_marker_pixel_errors=marker_errors,
                activation_color_max_channel_error=max(color_errors),stages=stages,environment=environment)
    (ROOT/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    for name in ['computation.json','layout.json']:(ROOT/name).write_text((run/name).read_text())
    print(json.dumps({k:v for k,v in report.items() if k not in ['stages','environment']}))


if __name__=='__main__':main()
