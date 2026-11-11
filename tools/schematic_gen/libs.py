import copy, re
from sexp import parse, dump, Sym, find
import os
SRC=os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../kicad_files/AATV/AATV_backup_v5.kicad_sch')
V7='/usr/share/kicad/symbols/'
_cache={}
def v7lib(lib):
    if lib not in _cache:
        _cache[lib]=parse(open(V7+lib+'.kicad_sym').read())
    return _cache[lib]
DROP={'exclude_from_sim','in_pos_files','duplicate_pin_numbers_are_jumpers','show_name','do_not_autoplace','embedded_fonts','embedded_files','jumper_pin_groups'}
def conv(x, parent=None):
    if not isinstance(x,list): return x
    out=[]
    hideflag=False
    for e in x:
        if isinstance(e,list) and e:
            if e[0] in DROP: continue
            if e[0]=='hide' and len(e)==2:
                if e[1]=='yes': hideflag=True
                continue
            if e[0] in ('bold','italic') and len(e)==2:
                if e[1]=='yes': out.append(Sym(e[0]))
                continue
        out.append(conv(e,x))
    if hideflag:
        if x[0]=='property':
            eff=[e for e in out if isinstance(e,list) and e and e[0]=='effects']
            if eff: eff[0].append(Sym('hide'))
            else: out.append([Sym('effects'),[Sym('font'),[Sym('size'),1.27,1.27]],Sym('hide')])
        elif x[0]=='pin':
            # insert after length
            idx=[i for i,e in enumerate(out) if isinstance(e,list) and e and e[0]=='length'][0]
            out.insert(idx+1,Sym('hide'))
        else:
            out.append(Sym('hide'))
    return out
def from_src(name):
    s=open(SRC).read()
    root=parse(s)
    ls=find(root,'lib_symbols')[0]
    for sy in ls[1:]:
        if sy[1]==name: return conv(copy.deepcopy(sy))
    raise KeyError(name)
def from_v7(lib,name):
    L=v7lib(lib)
    for sy in L[1:]:
        if isinstance(sy,list) and sy[0]=='symbol' and sy[1]==name:
            sy=copy.deepcopy(sy); sy[1]=lib+':'+name; return sy
    raise KeyError(name)
def pins(sym):
    res=[]
    def walk(x):
        for e in x:
            if isinstance(e,list) and e:
                if e[0]=='pin':
                    at=find(e,'at')[0]; ln=find(e,'length')[0][1]
                    nm=find(e,'name')[0][1]; num=find(e,'number')[0][1]
                    res.append(dict(type=str(e[1]),x=float(at[1]),y=float(at[2]),rot=float(at[3]) if len(at)>3 else 0,len=float(ln),name=nm,num=num))
                elif e[0]=='symbol': walk(e)
    walk(sym)
    return res
