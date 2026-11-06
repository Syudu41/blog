"""Independent scalar reconstruction, finite differences, update and test metrics."""
import json
import math
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent
trace=json.loads((ROOT/'trace.json').read_text()); data=np.load(ROOT/'dataset.npz')

def scalar(params,x,target):
    w,b,v,c=params
    z=[sum(w[j][i]*x[i] for i in range(4))+b[j] for j in range(4)]
    h=[max(0,a) for a in z]
    logits=[sum(v[k][j]*h[j] for j in range(4))+c[k] for k in range(4)]
    m=max(logits); e=[math.exp(a-m) for a in logits];p=[a/sum(e) for a in e]
    return z,h,logits,p,math.log(sum(e))+m-logits[target]
max_forward=0.; max_grad=0.
for snap in trace['snapshots']:
    case=snap['example'];actual=scalar(snap['params'],case['x'],case['target'])
    for key,value in zip(['z','h','logits','p','loss'],actual):
        max_forward=max(max_forward,float(np.max(np.abs(np.array(case[key])-value))))
    predicted=[np.argmax(scalar(snap['params'],x,int(y))[3]) for x,y in zip(data['test_x'],data['test_y'])]
    assert sum(predicted==data['test_y'])==snap['test_correct']
first,after=trace['snapshots'][:2];eps=1e-6
np.testing.assert_array_equal(data['train_x'][0],first['example']['x'])
assert data['train_y'][0]==first['example']['target']
for index,param in enumerate(first['params']):
    original=np.array(param);analytic=np.array(first['example']['gradients'][index]);fd=np.zeros_like(original)
    for ij in np.ndindex(original.shape):
        plus=[np.array(p) for p in first['params']];minus=[p.copy() for p in plus]
        plus[index][ij]+=eps;minus[index][ij]-=eps
        fd[ij]=(scalar(plus,first['example']['x'],0)[4]-scalar(minus,first['example']['x'],0)[4])/(2*eps)
    max_grad=max(max_grad,float(np.max(np.abs(fd-analytic))))
    np.testing.assert_allclose(after['params'][index],original-trace['learning_rate']*analytic,atol=1e-14,rtol=0)
assert max_forward<1e-12 and max_grad<1e-8
assert after['example']['loss']<first['example']['loss']
# Fully replay every update and compare all recorded parameter snapshots.
from train import main
old=(ROOT/'trace.json').read_bytes();main();assert (ROOT/'trace.json').read_bytes()==old
report=dict(status='passed',scalar_forward_max_error=max_forward,finite_difference_max_error=max_grad,
    gradient_parameters_checked=40,updates_replayed=2048,test_metrics_recomputed=7,
    initial_hidden=first['example']['h'],first_loss=first['example']['loss'],after_loss=after['example']['loss'],
    final_test_correct=trace['snapshots'][-1]['test_correct'],test_total=64,
    scope='Synthetic 2x2 patterns; test accuracy is not evidence about natural images.')
(ROOT/'numerical-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
