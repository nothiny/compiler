import glob, difflib, re, collections
base_p='/tmp/a100-opt3-baseline/a100c/cache/e607a35bc0f0fd1da21966b08e9b632679643ce1c0676614e20f0c4ba06eb6a7/program.S'
off='/tmp/a100-opt3-candidate/a100c/cache/989ef2872d6d25e069f12af116a7165c3a3dcdb858e4f4c76dd6a99acd9ca8c8/program.S'
def code(p): return [l.split('#')[0].rstrip() for l in open(p) if l.strip() and not l.strip().startswith(('#','.'))]
B,O=code(base_p),code(off)
diff=[d for d in difflib.unified_diff(B,O,lineterm='',n=0) if d.startswith(('+','-')) and not d.startswith(('+++','---'))]
cls=collections.Counter(); bad=[]
for d in diff:
    body=d[1:].strip()
    if d[0]=='-' and body.startswith('li'): cls['removed-li']+=1
    elif d[0]=='-' and body.startswith('vsetvli'): cls['removed-vsetvli(reg-avl)']+=1
    elif d[0]=='+' and re.match(r'vsetvli\s+\w+,\s*x0,', body): cls['added-vsetvli-x0']+=1
    elif d[0]=='+' and body.startswith('vsetvli'): cls['added-vsetvli(other)']+=1
    else:
        cls['UNEXPECTED']+=1; bad.append(d)
print(dict(cls))
for d in bad[:10]: print('  UNEXPECTED:', d)
