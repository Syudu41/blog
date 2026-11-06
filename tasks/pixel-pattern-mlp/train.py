"""Deterministic float64 toy-pattern SGD; no model API or external dataset."""
import hashlib
import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent
PROTOTYPES = np.array([[0,1,0,1], [0,0,1,1], [1,0,0,1], [0,1,1,0]], dtype=float)
CLASSES = ['Vertical', 'Horizontal', 'Diagonal', 'Anti-diagonal']

def forward(params, x, target):
    w1,b1,w2,b2 = params
    z=w1@x+b1; h=np.maximum(z,0); logits=w2@h+b2
    shifted=logits-logits.max(); p=np.exp(shifted); p/=p.sum()
    loss=float(np.log(np.exp(shifted).sum())-shifted[target])
    d= p.copy(); d[target]-=1
    dh=(w2.T@d)*(z>0)
    gradients=[np.outer(dh,x),dh,np.outer(d,h),d]
    return dict(x=x.tolist(),target=int(target),z=z.tolist(),h=h.tolist(),logits=logits.tolist(),p=p.tolist(),loss=loss,
                gradients=[g.tolist() for g in gradients],delta_hidden=dh.tolist())

def main():
    rng=np.random.default_rng(2026)
    y=np.tile(np.arange(4),32)
    x=np.clip(PROTOTYPES[y]+rng.normal(0,.13,(128,4)),0,1)
    test_y=np.tile(np.arange(4),16)
    test_x=np.clip(PROTOTYPES[test_y]+rng.normal(0,.13,(64,4)),0,1)
    # Independent fixed initialization RNG, unaffected by dataset split sizes.
    init=np.random.default_rng(42)
    params=[init.normal(0,.6,(4,4)),np.full(4,.2),init.normal(0,.5,(4,4)),np.zeros(4)]
    example=np.array([.1,.9,.1,.9]); lr=.08
    snapshots=[]
    first=forward(params,example,0)
    # First update is the explained sample; later updates use shuffled training images.
    samples=[(example,0)]
    for _ in range(16):
        samples.extend((x[i],int(y[i])) for i in rng.permutation(len(y)))
    for step in range(2049):
        if step in [0,1,32,128,512,1024,2048]:
            case=forward(params,example,0)
            predictions=[int(np.argmax(forward(params,a,int(b))['p'])) for a,b in zip(test_x,test_y)]
            snapshots.append(dict(step=step,params=[a.tolist() for a in params],example=case,
                test_correct=int(np.sum(np.array(predictions)==test_y)),test_total=64))
        if step==2048: break
        sample,target=samples[step]
        result=forward(params,sample,target)
        params=[a-lr*np.array(g) for a,g in zip(params,result['gradients'])]
    trace=dict(seed=2026,initialization_seed=42,learning_rate=lr,dtype='float64',classes=CLASSES,
        prototypes=PROTOTYPES.tolist(),training_count=128,test_count=64,optimizer='single-example SGD',
        dataset_sha256=hashlib.sha256(x.tobytes()+y.tobytes()+test_x.tobytes()+test_y.tobytes()).hexdigest(),
        snapshots=snapshots)
    (ROOT/'trace.json').write_text(json.dumps(trace,indent=2)+'\n')
    np.savez_compressed(ROOT/'dataset.npz',train_x=x,train_y=y,test_x=test_x,test_y=test_y)
    for s in snapshots: print(s['step'],np.round(s['example']['p'],4),s['test_correct'])

if __name__=='__main__':main()
