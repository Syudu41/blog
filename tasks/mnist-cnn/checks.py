"""Decode and inspect CNN media; verify recorded operations and visual values."""
import hashlib
import json
from pathlib import Path

import av
import numpy as np
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parent


def main(draft=False):
    run=sorted((ROOT/'runs').glob('*/detail.json'))[-1].parent
    stages=json.loads((run/'stages.json').read_text())
    layout=json.loads((run/'layout.json').read_text())
    detail=json.loads((run/'detail.json').read_text())
    data=np.load(ROOT/'trace.npz')
    meta=json.loads((ROOT/'training.json').read_text())
    assert detail['trace_sha256']==meta['trace_sha256']
    r,c=detail['row'],detail['col']
    actual=float(np.sum(np.array(detail['patch'])*np.array(detail['kernel']))+detail['bias'])
    assert abs(actual-detail['z'])<1e-6
    assert abs(max(map(max,detail['pool_values']))-data['p1'][0,r//2,c//2])<1e-8
    assert abs(detail['sample_loss']-meta['sample_cross_entropy'])<1e-12
    for bar,p in zip(detail['probability_bars'],data['probabilities']):
        assert abs(bar['p']-p)<1e-12 and abs(bar['bar_length']-2.25*p)<1e-12
    failures=[]
    for stage,objects in layout.items():
        for obj in objects:
            left,right,bottom,top=obj['bounds']
            if left < -6.95 or right > 6.95 or bottom < -3.95 or top > 3.85:
                failures.append(dict(stage=stage,bounds=obj['bounds']))
    assert not failures,failures
    ordered=['input','patch-and-kernel','convolution-arithmetic','relu-positive','relu-negative',
             'scan-start','scan-complete','four-feature-maps','pool-window','pool-maximum',
             'second-convolution','second-pooling','flatten-and-classifier','logits',
             'probabilities','prediction-and-metrics']
    assert all(stages[a]<stages[b] for a,b in zip(ordered,ordered[1:]))
    samples=dict(stages)
    start=stages['scan-start']
    for offset in (1.,3.,5.,7.):samples[f'scan-{offset:.0f}s']=start+offset
    for label,t in list(stages.items()):
        if label in ('pool-maximum','second-convolution','probabilities'):
            samples[label+'-transition']=t-1.5
    captures={};count=0;last=0;title_reference=None;title_errors=[]
    path=run/'visualization.mp4' if draft else ROOT/'output/visualization.mp4'
    with av.open(str(path)) as video:
        stream=video.streams.video[0]
        width,height=stream.width,stream.height
        fps=float(stream.average_rate)
        assert (width,height)==((960,540) if draft else (1920,1080))
        assert stream.codec_context.name=='h264' and stream.pix_fmt=='yuv420p'
        assert fps==(15 if draft else 30)
        for frame in video.decode(video=0):
            count+=1;last=float(frame.time)
            if not draft and count % 30 == 1:
                title=np.asarray(frame.to_image())[40:110,50:1200].mean(2)>110
                if title_reference is None:title_reference=title
                title_errors.append(float(np.count_nonzero(title!=title_reference)/title_reference.sum()))
            for label,t in samples.items():
                delta=abs(last-t)
                if delta<1/fps and (label not in captures or delta<captures[label][0]):
                    captures[label]=(delta,frame.to_image())
    assert not title_errors or max(title_errors)<.02
    assert len(captures)==len(samples),(len(captures),len(samples))
    assert 60<last<120,last
    assert path.stat().st_size<30000000
    # Pure black canvas survives encoding at the four corner samples of each hold.
    for delta,img in captures.values():
        pixels=np.asarray(img)
        for x,y in [(4,4),(width-5,4),(4,height-5),(width-5,height-5)]:
            assert pixels[y,x].max()<8
    # Check actual rendered heatmaps, using every pixel's interior center.
    # Coordinates are in the scene's 14.222... x 8 frame; thumbnails retain pixel values.
    checks=[('input','x',0,-3.65,-.15,3.65,'gray'),
            ('scan-complete','a1',0,4.15,-.05,3.65,'cyan')]
    checks += [('four-feature-maps','a1',c,x,.25,2.35,'cyan') for c,x in enumerate((-4.8,-1.6,1.6,4.8))]
    checks += [('pool-maximum','p1',0,4.55,.1,2.45,'cyan')]
    checks += [('second-convolution','a2',c,.5+(c%4)*1.78,.83-(c//4)*1.8,1.28,'violet') for c in range(8)]
    checks += [('second-pooling','p2',c,.5+(c%4)*1.78,.83-(c//4)*1.8,1.28,'violet') for c in range(8)]
    color_errors={}
    for stage,key,channel,cx,cy,side,tint in checks:
        values=data[key][channel]
        scale=1 if key=='x' else float(data['a1' if key in ('a1','p1') else 'a2'].max())
        high=np.array([255,255,255] if tint=='gray' else [85,217,236] if tint=='cyan' else [181,154,255])
        base=np.array([0,0,0] if tint=='gray' else [5,11,18])
        image=np.array(captures[stage][1],float)
        errors=[];n=len(values)
        for row in range(n):
            for col in range(n):
                # Skip highlighted pool pixel and cell boundaries affected by borders.
                if stage=='pool-maximum' and (row,col)==(r//2,c//2):continue
                px=round(width/2+(cx+((col+.5)/n-.5)*side)*height/8)
                py=round(height/2-(cy+(.5-(row+.5)/n)*side)*height/8)
                expected=np.floor(base+(high-base)*values[row,col]/scale)
                errors.append(float(np.max(abs(image[py,px]-expected))))
        error=float(np.percentile(errors,95))
        # Small maps in a compressed draft have fewer than four pixels per cell.
        assert error<(45 if draft else 32),(stage,channel,error)
        color_errors[f'{stage}-{channel}']=error
    prefix='draft' if draft else 'review'
    sample_items=list(samples.items())
    for first in range(0,len(sample_items),4):
        sheet=Image.new('RGB',(1920,1120),'#18202a');draw=ImageDraw.Draw(sheet)
        for i,(label,t) in enumerate(sample_items[first:first+4]):
            x=(i%2)*960;y=(i//2)*560
            sheet.paste(captures[label][1].resize((960,540)),(x,y+20))
            draw.text((x+10,y+3),f'{label} / {t:.2f}s',fill='white')
        sheet.save(ROOT/f'{prefix}-stages-{first//4+1}.png')
    if not draft:
        thumb=captures['four-feature-maps'][1].copy();thumb.thumbnail((640,360))
        thumb.save(ROOT/'output/thumbnail.png')
        for name in ('stages.json','layout.json','detail.json'):
            (ROOT/name).write_text((run/name).read_text())
    report=dict(sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                dimensions=[width,height],frames=count,duration=round(last+1/fps,3),fps=fps,
                bytes=path.stat().st_size,inspected_samples=len(samples),
                heatmap_pixel_95th_percentile_errors=color_errors,frame_bounds_passed=True,
                title_bitmap_max_change=max(title_errors,default=0),stages=stages)
    (ROOT/f'{prefix}-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('stages',)},indent=2))


if __name__=='__main__':
    import sys
    main('--draft' in sys.argv)
