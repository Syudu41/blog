"""Independently check CNN arithmetic and export final-media review evidence."""
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parent


def reference_conv(x,k,bias):
    out=np.zeros((len(k),x.shape[1]-2,x.shape[2]-2))
    for o in range(len(k)):
        for r in range(out.shape[1]):
            for c in range(out.shape[2]):
                total=float(bias[o])
                for channel in range(x.shape[0]):
                    for i in range(3):
                        for j in range(3):total+=x[channel,r+i,c+j]*k[o,channel,i,j]
                out[o,r,c]=max(total,0)
    return out


def main():
    run=sorted((ROOT/'runs').glob('*/computation.json'))[-1].parent
    d={k:np.array(v) for k,v in json.loads((run/'computation.json').read_text()).items()}
    first=reference_conv(d['x'],d['k1'],np.array([.12,.12,.15]))
    second=reference_conv(first,d['k2'],np.full(4,.2))
    hidden=np.maximum(np.array([sum(w*x for w,x in zip(row,second.flatten()))+b
                                for row,b in zip(d['w'],d['bias'])]),0)
    logits=np.array([sum(w*x for w,x in zip(row,hidden))+b for row,b in zip(d['v'],d['ob'])])
    probabilities=np.exp(logits-max(logits));probabilities/=sum(probabilities)
    errors={}
    for name,expected in [('a',first),('b',second),('h',hidden),('p',probabilities)]:
        np.testing.assert_allclose(d[name],expected,rtol=1e-12,atol=1e-12)
        errors[name]=float(np.max(np.abs(d[name]-expected)))
    assert [d[k].shape for k in ['x','a','b','h','p']]==[(1,7,7),(3,5,5),(4,3,3),(5,),(3,)]
    path=ROOT/'output/visualization.gif';times=[];elapsed=0
    stages=json.loads((run/'stages.json').read_text())
    targets=list(stages.values())+[1.85,1.95,2.05,2.15,9.1,9.5,10.95,11.35]
    captures={}
    first_frame=last_frame=None
    with Image.open(path) as image:
        assert image.size==(1200,600) and image.info['loop']==0
        for i in range(image.n_frames):
            image.seek(i);times.append(elapsed)
            for target in targets:
                error=abs(elapsed-target)
                if target not in captures or error<captures[target][0]:
                    captures[target]=(error,image.convert('RGB'))
            if i==0:first_frame=image.convert('RGB')
            if i==image.n_frames-1:last_frame=image.convert('RGB')
            elapsed+=image.info['duration']/1000
    assert 12<=elapsed<=20
    assert abs(len(times)/elapsed-30)<.5
    assert path.stat().st_size<12000000
    with Image.open(ROOT/'output/thumbnail.png') as thumb:
        assert thumb.size==(640,320);thumb.verify()
    seam=float(np.abs(np.array(first_frame,float)-np.array(last_frame,float)).mean())
    assert seam<1
    stages=json.loads((run/'stages.json').read_text())
    sheets=[]
    items=list(stages.items())
    for start in range(0,len(items),4):
        sheet=Image.new('RGB',(1800,940),'white');draw=ImageDraw.Draw(sheet)
        for i,(name,t) in enumerate(items[start:start+4]):
            f=min(range(len(times)),key=lambda j:abs(times[j]-t))
            tile=captures[t][1].resize((900,450));x=(i%2)*900;y=(i//2)*470
            sheet.paste(tile,(x,y+20));draw.text((x+10,y+3),f'{name}: {t:.2f}s',fill='black')
        name=f'review-stages-{start//4+1}.png';sheet.save(ROOT/name);sheets.append(name)
    # Consecutive frames across the first scan, at native display width.
    sheet=Image.new('RGB',(1800,940),'white');draw=ImageDraw.Draw(sheet)
    for i,t in enumerate([1.85,1.95,2.05,2.15]):
        f=min(range(len(times)),key=lambda j:abs(times[j]-t))
        x=(i%2)*900;y=(i//2)*470
        sheet.paste(captures[t][1].resize((900,450)),(x,y+20));draw.text((x+10,y+3),f'convolution motion: {times[f]:.2f}s',fill='black')
    sheet.save(ROOT/'review-motion.png')
    sheet=Image.new('RGB',(1800,940),'white');draw=ImageDraw.Draw(sheet)
    for i,t in enumerate([9.1,9.5,10.95,11.35]):
        x=(i%2)*900;y=(i//2)*470
        sheet.paste(captures[t][1].resize((900,450)),(x,y+20))
        draw.text((x+10,y+3),f'dense flow: {t:.2f}s',fill='black')
    sheet.save(ROOT/'review-flow.png')
    # Check final cell colors against independently calculated activations.
    image=np.array(captures[stages['prediction']][1],float)
    color_errors=[]
    for key,center in [('x',(-5.6,0)),('a',(-2.5,0)),('b',(.3,0))]:
        values=d[key][0];n=len(values);scale=max(float(d[key].max()),1e-8)
        for row in range(n):
            for col in range(n):
                point=np.array(center)+(col+.5-n/2)*np.array([.31,.025])+(n/2-row-.5)*np.array([-.105,.31])
                px=round((point[0]+8)*75);py=round((4-point[1])*75)
                measured=np.median(image[py-1:py+2,px-1:px+2],axis=(0,1))
                alpha=.1+.85*values[row,col]/scale
                expected=255*(1-alpha)+np.array([23,103,166])*alpha
                color_errors.append(float(np.max(np.abs(measured-expected))))
    assert max(color_errors)<18, max(color_errors)
    result=json.loads((run/'result.json').read_text())
    report=dict(sha256=hashlib.sha256(path.read_bytes()).hexdigest(),dimensions=[1200,600],
                frames=len(times),duration=round(elapsed,3),average_fps=len(times)/elapsed,
                bytes=path.stat().st_size,loop=0,seam_mean_channel_error=seam,
                arithmetic_max_errors=errors,visible_cell_color_max_channel_error=max(color_errors),
                probabilities=probabilities.tolist(),
                stages=stages,render_environment=result['environment'])
    (ROOT/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    (ROOT/'computation.json').write_text((run/'computation.json').read_text())
    print(json.dumps({k:v for k,v in report.items() if k not in ['render_environment','stages']}))


if __name__=='__main__':main()
