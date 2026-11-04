"""Check arithmetic, causal activation order, media, and final review frames."""
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
    hidden=[max(0,math.fsum(a*b for a,b in zip(row,data['x']))+bias)
            for row,bias in zip(data['w1'],data['b1'])]
    outputs=[1/(1+math.exp(-(math.fsum(a*b for a,b in zip(row,hidden))+bias)))
             for row,bias in zip(data['w2'],data['b2'])]
    np.testing.assert_allclose(hidden,data['h'],rtol=1e-12,atol=1e-12)
    np.testing.assert_allclose(outputs,data['y'],rtol=1e-12,atol=1e-12)
    assert [len(layer) for layer in layout['nodes']]==[3,4,2]
    assert layout['edges']==[12,8]
    # Verify vertical label clearance independently of the visual review.
    bottom=min(p[1] for layer in layout['nodes'] for p in layer)-layout['node_radius']
    assert bottom-layout['label_y']>.22
    assert stages['input-activations']<stages['input-hidden-start']<stages['signals-arrive-hidden']<stages['hidden-activations']<stages['hidden-output-start']<stages['signals-arrive-output']<stages['output-activations']
    samples=[('network-ready',stages['network-ready']),('input-activations',stages['input-activations']),
             ('input-signal-early',stages['input-hidden-start']+.6),('input-signal-late',stages['input-hidden-start']+1.2),
             ('hidden-activations',stages['hidden-activations']),
             ('hidden-signal-early',stages['hidden-output-start']+.6),('hidden-signal-late',stages['hidden-output-start']+1.2),
             ('output-activations',stages['output-activations']),
             ('completed-forward-pass',stages['completed-forward-pass']),('reset',stages['reset'])]
    captures={};times=[];first=last=None
    artifact=ROOT/'output/visualization.mp4'
    with av.open(str(artifact)) as video:
        stream=video.streams.video[0]
        assert (stream.width,stream.height)==(1920,1080)
        assert stream.codec_context.name=='h264' and str(stream.average_rate)=='30'
        assert stream.pix_fmt=='yuv420p'
        for frame in video.decode(video=0):
            time=float(frame.time);times.append(time)
            if first is None:first=frame.to_image()
            for name,target in samples:
                distance=abs(time-target)
                if name not in captures or distance<captures[name][0]:captures[name]=(distance,frame.to_image())
            last=frame.to_image()
    duration=times[-1]+1/30
    assert 13<=duration<=18 and len(times)>390
    assert artifact.stat().st_size<20000000
    seam=float(np.abs(np.array(first,float)-np.array(last,float)).mean())
    assert seam<1
    blue=np.array([23,103,166]);pixel_errors=[]
    # Sample above the LaTeX glyphs, inside each neuron's filled circle.
    for stage,active in [('network-ready',0),('input-activations',1),('hidden-activations',2),('output-activations',3),('reset',0)]:
        image=np.array(captures[stage][1],float)
        for index,points in enumerate(layout['nodes']):
            vals=data[('x','h','y')[index]] if index<active else [0]*len(points)
            for point,value in zip(points,vals):
                x=round(960+point[0]*135);y=round(540-(point[1]+layout['node_radius']*.6)*135)
                actual=np.median(image[y-1:y+2,x-1:x+2],axis=(0,1))
                expected=255*(1-.65*value)+blue*.65*value
                pixel_errors.append(float(np.max(abs(actual-expected))))
    assert max(pixel_errors)<12,max(pixel_errors)
    # A representative completed frame makes the gallery card useful.
    thumbnail=captures['completed-forward-pass'][1].copy();thumbnail.thumbnail((640,640))
    thumbnail.save(ROOT/'output/thumbnail.png')
    with Image.open(ROOT/'output/thumbnail.png') as image:
        assert image.size==(640,360);image.verify()
    for start in range(0,len(samples),4):
        sheet=Image.new('RGB',(1800,1052),'white');draw=ImageDraw.Draw(sheet)
        for i,(name,time) in enumerate(samples[start:start+4]):
            x=(i%2)*900;y=(i//2)*526
            tile=captures[name][1].resize((900,506));sheet.paste(tile,(x,y+20))
            draw.text((x+10,y+3),f'{name}: {time:.2f}s',fill='black')
        sheet.save(ROOT/f'review-stages-{start//4+1}.png')
    result=json.loads((run/'result.json').read_text())
    report=dict(sha256=hashlib.sha256(artifact.read_bytes()).hexdigest(),dimensions=[1920,1080],fps=30,
                frames=len(times),duration=round(duration,3),bytes=artifact.stat().st_size,
                seam_mean_channel_error=seam,max_activation_pixel_channel_error=max(pixel_errors),
                hidden=hidden,outputs=outputs,stages=stages,
                thumbnail_frame_seconds=stages['completed-forward-pass'],environment=result['environment'])
    (ROOT/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    for name in ['computation.json','layout.json']:(ROOT/name).write_text((run/name).read_text())
    print(json.dumps({k:v for k,v in report.items() if k not in ['stages','environment']}))


if __name__=='__main__':main()
