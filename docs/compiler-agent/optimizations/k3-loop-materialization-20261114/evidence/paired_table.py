import json, glob, os
rows=[]
for d in sorted(glob.glob('/tmp/a100-opt3/candidate-metrics/*-t1')):
    name=os.path.basename(d)[:-3]
    f=d+'/metrics.json'
    if not os.path.exists(f): continue
    m=json.load(open(f))
    ss=m.get('steady_state') or {}
    tot=ss.get('per_call_total') or ss.get('total_per_call')
    rows.append((name, tot))
print('%-28s %14s %14s %9s' % ('case','baseline','candidate','change'))
base={}
for d in sorted(glob.glob('/tmp/a100-opt3/baseline-metrics/*-t1')):
    name=os.path.basename(d)[:-3]
    f=d+'/metrics.json'
    if not os.path.exists(f): continue
    m=json.load(open(f)); ss=m.get('steady_state') or {}
    base[name]=ss.get('per_call_total') or ss.get('total_per_call')
for name, cand in rows:
    b=base.get(name)
    if b is None:
        print('%-28s %14s %14s' % (name, 'NO-BASE', f'{cand:.0f}')); continue
    print('%-28s %14.0f %14.0f %8.2f%%' % (name, b, cand, 100*(cand-b)/b))
