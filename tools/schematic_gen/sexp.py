import re
class Sym(str):
    """bare atom"""
def unesc(t):
    return re.sub(r'\\(.)', lambda m: '\n' if m.group(1)=='n' else m.group(1), t)
def parse(s):
    tok = re.compile(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()"]+')
    stack=[[]]
    for m in tok.finditer(s):
        t=m.group(0)
        if t=='(':
            stack.append([])
        elif t==')':
            x=stack.pop(); stack[-1].append(x)
        elif t[0]=='"':
            stack[-1].append(unesc(t[1:-1]))
        else:
            stack[-1].append(Sym(t))
    return stack[0][0]
def q(s):
    return '"'+s.replace('\\','\\\\').replace('"','\\"').replace('\n','\\n')+'"'
def dump(x, ind=0):
    if isinstance(x, list):
        # short lists inline
        inner=[dump(e, ind+1) for e in x]
        flat='('+' '.join(inner)+')'
        if len(flat)<100 and '\n' not in flat:
            return flat
        out='('+inner[0]
        for e in inner[1:]:
            out+='\n'+'  '*(ind+1)+e
        return out+')'
    if isinstance(x, Sym): return str(x)
    if isinstance(x,(int,float)): return fmt(x)
    return q(x)
def fmt(v):
    if isinstance(v,int): return str(v)
    s=('%.4f'%v).rstrip('0').rstrip('.')
    return '0' if s=='-0' else s
def find(lst, key):
    return [e for e in lst if isinstance(e,list) and e and e[0]==key]
