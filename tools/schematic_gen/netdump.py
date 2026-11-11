import re, sys
s=open(sys.argv[1]).read()
for name, body in re.findall(r'<net code="\d+" name="([^"]*)"[^>]*>(.*?)</net>', s, re.S):
    nodes=re.findall(r'<node ref="([^"]+)" pin="([^"]+)"', body)
    if name.startswith('unconnected') : continue
    print(name, ' '.join(sorted(f'{r}.{p}' for r,p in nodes)))
