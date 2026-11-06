"""Verify native ManimML layer geometry, live computations and rendered media."""
import hashlib
import json
from pathlib import Path

import av
import numpy as np
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parent
NAMES=['Input','Conv 1 + ReLU','Pool 1','Conv 2 + ReLU','Pool 2','Flatten','Dense','Softmax']
SHAPES=[[1,28,28],[4,28,28],[4,14,14],[8,14,14],[8,7,7],[392],[10],[10]]
SCANS={'convolution-1':(0,1,'a1',1,1,1,10.),'pooling-1':(1,2,'p1',1,2,0,4.5),
       'convolution-2':(2,3,'a2',4,1,1,6.),'pooling-2':(3,4,'p2',1,2,0,3.5)}


def main(draft=False):
    runs=[p.parent for p in (ROOT/'runs').glob('*/detail.json')
          if json.loads(p.read_text()).get('layer_style','').startswith('native ManimML')
          and len(json.loads(p.read_text()).get('samples',[]))>0]
    run=sorted(runs)[-1]
    stages=json.loads((run/'stages.json').read_text());layout=json.loads((run/'layout.json').read_text())
    detail=json.loads((run/'detail.json').read_text());data=np.load(ROOT/'trace.npz')
    meta=json.loads((ROOT/'training.json').read_text());assert detail['trace_sha256']==meta['trace_sha256']
    assert detail['parameter_counts']==[0,40,0,296,0,0,3930,0]
    assert sum(detail['parameter_counts'])==meta['parameter_count']==4266
    reference=layout['architecture']['layers'];assert [x['name'] for x in reference]==NAMES
    assert [x['shape'] for x in reference]==SHAPES
    assert [x['maps'] for x in reference[:5]]==[1,4,4,8,8]
    assert [x['type'] for x in reference[:5]]==['Convolutional2DLayer','Convolutional2DLayer','MaxPooling2DLayer','Convolutional2DLayer','MaxPooling2DLayer']
    assert reference[6]['type']=='FeedForwardLayer' and len(reference[6]['nodes'])==10
    plane_lengths=[]
    for i,layer in enumerate(reference[:5]):
        for corners in layer['map_corners']:
            width=np.linalg.norm(np.array(corners['top_right'])-corners['top_left'])
            height=np.linalg.norm(np.array(corners['bottom_left'])-corners['top_left'])
            assert abs(width-SHAPES[i][1]*.102)<1e-9 and abs(height-width)<1e-9
        plane_lengths.append(width)
    assert abs(plane_lengths[2]/plane_lengths[1]-.5)<1e-9
    assert abs(plane_lengths[4]/plane_lengths[3]-.5)<1e-9
    centers=np.array([x['center'] for x in reference])
    for stage,record in layout.items():
        np.testing.assert_allclose([x['center'] for x in record['layers']],centers,atol=1e-8)
        for l,r,b,t in record['bounds']:
            if l==r and b==t:continue  # Nonrendering ValueTracker point in the draft record.
            assert l>=-7.0 and r<=7.0 and b>=-3.95 and t<=3.95,(stage,[l,r,b,t])
    geometric_errors=[];scalar_errors=[]
    for sample in detail['samples']:
        source,target,key,arity,stride,padding,seconds=SCANS[sample['scan']]
        assert sample['key']==key and len(sample['input_centers'])==arity and len(sample['output_centers'])==1
        assert sample['stride']==stride and sample['padding']==padding
        scalar_errors.append(abs(sample['value']-float(data[key][sample['channel'],sample['row'],sample['col']])))
        for corners in sample['input_corners']:
            a=np.array(corners['top_left'])
            for corner in ('top_right','bottom_left'):assert abs(np.linalg.norm(np.array(corners[corner])-a)-(2 if stride==2 else 3)*.102)<1e-9
        for corners in sample['output_corners']:
            a=np.array(corners['top_left'])
            for corner in ('top_right','bottom_left'):assert abs(np.linalg.norm(np.array(corners[corner])-a)-.102)<1e-9
        r,c=sample['position'];size=2 if padding==0 else 3
        for j,actual in enumerate(sample['input_centers']):
            corners=reference[source]['map_corners'][sample['channel'] if stride==2 else j]
            tl=np.array(corners['top_left']);right=(np.array(corners['top_right'])-tl)/SHAPES[source][1]
            down=(np.array(corners['bottom_left'])-tl)/SHAPES[source][1]
            expected=tl+(stride*r-padding+size/2)*down+(stride*c-padding+size/2)*right
            geometric_errors.append(float(np.max(abs(np.array(actual)-expected))))
        corners=reference[target]['map_corners'][sample['channel']]
        tl=np.array(corners['top_left']);right=(np.array(corners['top_right'])-tl)/SHAPES[target][1]
        down=(np.array(corners['bottom_left'])-tl)/SHAPES[target][1]
        expected=tl+(r+.5)*down+(c+.5)*right
        geometric_errors.append(float(np.max(abs(np.array(sample['output_centers'][0])-expected))))
    assert max(scalar_errors)==0
    assert max(geometric_errors)<1e-8,max(geometric_errors)
    for k,record in enumerate(detail['probabilities']):
        assert abs(record['p']-data['probabilities'][k])<1e-12
        assert abs(record['width']-max(.002,.88*record['p']))<1e-9
    samples={name:t for name,t in stages.items() if name in ('architecture','four-channels','eight-channels','flatten','dense','complete-network') or name.endswith('-origin') or name in SCANS}
    selected={}
    for scan,values in SCANS.items():
        for fraction in (.25,.7):
            key=f'{scan}-motion-{fraction}';time=stages[scan+'-start']+values[-1]*fraction
            sample=min((s for s in detail['samples'] if s['scan']==scan),key=lambda s:abs(s['time']-time))
            samples[key]=sample['time'];selected[key]=sample
    for stage in ('four-channels','eight-channels','flatten','dense','complete-network'):
        samples[stage+'-transition']=stages[stage]-(1 if stage!='complete-network' else 2.4)
    captures={};count=0;last=0;header_reference=None;header_errors=[]
    path=run/'visualization.mp4' if draft else ROOT/'output/visualization.mp4'
    with av.open(str(path)) as video:
        stream=video.streams.video[0];width,height=stream.width,stream.height;fps=float(stream.average_rate)
        assert (width,height)==((960,540) if draft else (1920,1080))
        assert stream.codec_context.name=='h264' and stream.pix_fmt=='yuv420p' and fps==(15 if draft else 30)
        for frame in video.decode(video=0):
            count+=1;last=float(frame.time)
            if count%int(fps)==1:
                image=np.asarray(frame.to_image())
                region=image[round(height*185/1080):round(height*332/1080)].mean(2)>80
                if header_reference is None:header_reference=region
                header_errors.append(float(np.count_nonzero(region!=header_reference)/header_reference.sum()))
            for label,t in samples.items():
                distance=abs(last-t)
                if distance<1/fps and (label not in captures or distance<captures[label][0]):captures[label]=(distance,frame.to_image())
    assert len(captures)==len(samples),(len(captures),len(samples))
    assert max(header_errors)<.08,max(header_errors)
    assert 45<last<100 and path.stat().st_size<30000000
    for _,im in captures.values():
        pixels=np.asarray(im)
        assert all(pixels[y,x].max()<8 for x,y in [(4,4),(width-5,4),(4,height-5),(width-5,height-5)])
    # Compare actual orange receptive-field corner pixels with projected runtime geometry.
    camera=detail['camera'];rotation=np.array(camera['rotation_matrix']);focal=camera['focal_distance']
    def project(point):
        p=np.array(point)@rotation.T
        return p[:2]*focal/(focal-p[2])
    pixel_distances={}
    for name,sample in selected.items():
        pixels=np.asarray(captures[name][1],float);distances=[]
        for corners in (sample['input_corners'][0],sample['output_corners'][0]):
            local=[]
            for key in ('top_left','bottom_right'):
                point=project(corners[key]);px=round(width/2+point[0]*height/8);py=round(height/2-point[1]*height/8)
                radius=4 if draft else 6
                y0=max(0,py-radius);x0=max(0,px-radius)
                patch=pixels[y0:py+radius+1,x0:px+radius+1]
                # Native 3D lighting changes intensity; test the orange hue and position.
                red,green,blue=patch[:,:,0],patch[:,:,1],patch[:,:,2]
                mask=(red>100)&(green>45)&(red>1.2*green)&(red>1.7*blue)
                ys,xs=np.nonzero(mask)
                local.append(float(np.min(np.hypot(xs+x0-px,ys+y0-py))) if len(xs) else 999.)
            assert min(local)<=(5 if draft else 7),(name,local)
            distances.append(min(local))
        pixel_distances[name]=distances
    # Native dense nodes must be visible, and the winning logit node must be filled.
    nodes=sorted(reference[6]['nodes'],key=lambda p:-p[1]);winner=int(data['logits'].argmax())
    point=project(nodes[winner]);px=round(width/2+point[0]*height/8);py=round(height/2-point[1]*height/8)
    final=np.asarray(captures['complete-network'][1],float)
    dense_error=float(np.min(np.max(abs(final[py-2:py+3,px-2:px+3]-np.array([88,196,221])*.85),axis=2)))
    assert dense_error<30,dense_error
    prefix='draft' if draft else 'review';items=list(samples.items())
    for first in range(0,len(items),4):
        sheet=Image.new('RGB',(1920,1120),'#18202a');draw=ImageDraw.Draw(sheet)
        for i,(label,t) in enumerate(items[first:first+4]):
            x=(i%2)*960;y=(i//2)*560;sheet.paste(captures[label][1].resize((960,540)),(x,y+20))
            draw.text((x+8,y+3),f'{label} / {t:.2f}s',fill='white')
        sheet.save(ROOT/f'{prefix}-stages-{first//4+1}.png')
    if not draft:
        thumb=captures['convolution-1-motion-0.7'][1].copy();thumb.thumbnail((640,360));thumb.save(ROOT/'output/thumbnail.png')
        for name in ('stages.json','layout.json','detail.json'):(ROOT/name).write_text((run/name).read_text())
    report=dict(run=run.name,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),dimensions=[width,height],fps=fps,
        frames=count,duration=round(last+1/fps,3),bytes=path.stat().st_size,inspected_samples=len(samples),
        native_layer_types=[x['type'] for x in reference],native_channel_counts=[x['maps'] for x in reference[:5]],
        physical_plane_sides=plane_lengths,window_geometry_max_error=max(geometric_errors),live_readout_max_error=max(scalar_errors),
        header_bitmap_max_change=max(header_errors),projected_filter_corner_pixel_distances=pixel_distances,
        dense_winner_max_channel_error=dense_error,projected_bounds_passed=True,stages=stages)
    (ROOT/f'{prefix}-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='stages'},indent=2))


if __name__=='__main__':
    import sys
    main('--draft' in sys.argv)
