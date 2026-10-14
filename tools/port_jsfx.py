"""Source-driven EEL subset translator for the six requested mrelwood effects.
No GUI/serialization translation. Namespace functions are specialized per instance;
EEL RAM uses a private fixed array. Run from the repository root.
"""
from pathlib import Path
import re
from port_airwindows import strip_comments

NAMES = ['mrelwood_GoldComp4', 'mrelwood_Sky_is_the_limit_3v2_BETA',
         'mrelwood_DubStep_Wob-Wob', 'mrelwood_Chmahastic_Reverb_2',
         'mrelwood_GateIQ', 'mrelwood_HP-LP_LR4_Filters']

class Parser:
    def __init__(self, text):
        pattern = r'\s*(\d+(?:\.\d*)?(?:[eE][+-]?\d+)?|\.\d+(?:[eE][+-]?\d+)?|\$pi|[A-Za-z_][\w.]*|==|!=|<=|>=|\+=|-=|\*=|/=|\^=|&&|\|\||[()+*/%^?:;,\[\]=<>!|&-])'
        self.tokens=[]; pos=0
        while pos<len(text):
            if not text[pos:].strip(): break
            m=re.match(pattern,text[pos:])
            if not m: raise ValueError('Unexpected EEL: '+text[pos:pos+100])
            self.tokens.append(m[1]);pos+=m.end()
        self.tokens.append('EOF');self.i=0
    def pop(self):
        t=self.tokens[self.i];self.i+=1;return t
    def peek(self):return self.tokens[self.i]
    def expect(self,t):
        actual=self.pop()
        if actual!=t:raise ValueError(f'Expected {t}, got {actual}: {self.tokens[max(0,self.i-8):self.i+8]}')
    def sequence(self,end='EOF'):
        a=[]
        while self.peek()!=end:
            if self.peek()==';':self.pop();continue
            a.append(self.expr())
            if self.peek()==';':self.pop()
        return ('seq',a)
    def expr(self, level=0):
        t=self.pop()
        if t=='(':
            left=self.sequence(')');self.expect(')')
        elif t in ('-','+','!'):left=('un',t,self.expr(10))
        elif re.match(r'^(?:\d|\.\d)',t):left=('num',t)
        else:left=('var',t)
        prec={'=':1,'+=':1,'-=':1,'*=':1,'/=':1,'^=':1,'?':2,'||':3,'&&':4,'|':5,'&':5,'==':6,'!=':6,'<':7,'>':7,'<=':7,'>=':7,'+':8,'-':8,'*':9,'/':9,'%':9,'^':11}
        while True:
            op=self.peek()
            if op=='(':
                self.pop();args=[]
                if self.peek()!=')':
                    args.append(self.expr())
                    while self.peek()==',':
                        self.pop()
                        args.append(self.sequence(')') if left == ('var','loop') else self.expr())
                self.expect(')');left=('call',left,args);continue
            if op=='[':
                self.pop();idx=self.expr();self.expect(']');left=('index',left,idx);continue
            p=prec.get(op,0)
            if p<=level:break
            self.pop()
            if op=='?':
                yes=self.expr()
                no=('num','0')
                if self.peek()==':':self.pop();no=self.expr()
                left=('if',left,yes,no)
            else:left=('bin',op,left,self.expr(p-1 if p==1 or op=='^' else p))
        return left

class Compiler:
    def __init__(self,functions):
        self.functions=functions;self.states=set();self.methods={};self.counter=0
    def temp(self):self.counter+=1;return 'tmp'+str(self.counter)
    def variable(self,name,ns,instances,args):
        if name in args:return 'arg_'+name
        if name=='$pi':return 'PI'
        if name=='srate':return 'samplerate()'
        if name=='tempo':return 'tempo()'
        if name=='beat_position':return 'in3'
        if name.startswith('this.'):
            m=re.match(r'this(\.+)(.*)',name); dots=len(m[1]);parts=ns.split('.') if ns else []
            prefix='.'.join(parts[:len(parts)-dots+1])
            name=(prefix+'.' if prefix else '')+m[2]
        elif name.split('.')[0] in instances:name=(ns+'.' if ns else '')+name
        v='s_'+name.replace('.','_');self.states.add(v);return v
    def emit(self,node,ns='',instances=(),args=()):
        k=node[0]
        if k=='num':return '',node[1]
        if k=='var':return '',self.variable(node[1],ns,instances,args)
        if k=='seq':
            if len(node[1]) == 1: return self.emit(node[1][0],ns,instances,args)
            code='';value='0'
            for index,n in enumerate(node[1]):
                c,value=self.emit(n,ns,instances,args);code+=c
                # Calls before the last expression must execute even if their result is ignored.
                if n[0]=='call' and index < len(node[1])-1:code+=value+';\n';value='0'
            return code,value
        if k=='un':
            c,x=self.emit(node[2],ns,instances,args)
            return c,(f'(0 - {x})' if node[1]=='-' else f'({node[1]}{x})')
        if k=='index':
            c,b=self.emit(node[1],ns,instances,args);d,i=self.emit(node[2],ns,instances,args);t=self.temp()
            return c+d+f'let {t}: Int = trunc({b}+({i}));\n',f'ram[{t}]'
        if k=='if':
            c,x=self.emit(node[1],ns,instances,args);a,y=self.emit(node[2],ns,instances,args);b,z=self.emit(node[3],ns,instances,args);t=self.temp()
            return c+f'let {t} = 0;\nif ({x}) {{\n{a}{t} = {y};\n}} else {{\n{b}{t} = {z};\n}}\n',t
        if k=='bin':
            op=node[1];a,x=self.emit(node[2],ns,instances,args);b,y=self.emit(node[3],ns,instances,args)
            if op in ('=','+=','-=','*=','/=','^='):
                rhs=f'pow({x},{y})' if op=='^=' else y
                return a+b+f'{x} {"=" if op=="^=" else op} {rhs};\n',x
            if op=='^':return a+b,f'pow({x},{y})'
            if op in ('|','&'):
                t=self.temp();u=self.temp();return a+b+f'let {t}: Int = trunc({x});\nlet {u}: Int = trunc({y});\n',f'({t} {op} {u})'
            if op=='/':return a+b,f'eelDivide({x},{y})'
            return a+b,f'({x} {op} {y})'
        if k=='call':
            target=node[1][1];raw=node[2]
            if target in ('loop','while'):
                t=self.temp()
                if target=='loop':
                    c,n=self.emit(raw[0],ns,instances,args);body,v=self.emit(raw[1],ns,instances,args)
                    return c+f'for (let {t}: Int = 0; {t} < {n}; {t}++) {{\n{body}{v};\n}}\n','0'
                body,v=self.emit(raw[0],ns,instances,args)
                return f'let {t} = 1;\nwhile ({t}) {{\n{body}{t} = {v};\n}}\n','0'
            if target=='memset':
                ca,base=self.emit(raw[0],ns,instances,args);cb,val=self.emit(raw[1],ns,instances,args);cc,count=self.emit(raw[2],ns,instances,args);t=self.temp();u=self.temp()
                return ca+cb+cc+f'for (let {t}: Int = 0; {t} < {count}; {t}++) {{ let {u}: Int = trunc({base}+{t}); ram[{u}] = {val}; }}\n','0'
            fun=target.split('.')[-1]
            code='';values=[]
            for n in raw:
                c,v=self.emit(n,ns,instances,args);t=self.temp();code+=c+f'let {t} = {v};\n';values.append(t)
            if fun in self.functions:
                prefix=target[:-len(fun)].rstrip('.')
                if prefix=='this':prefix=ns
                elif prefix.startswith('this.'):
                    m=re.match(r'this(\.+)(.*)',prefix);parts=ns.split('.') if ns else [];prefix='.'.join(parts[:len(parts)-len(m[1])+1]+[m[2]])
                elif prefix.split('.')[0] in instances:prefix=(ns+'.' if ns else '')+prefix
                key=(fun,prefix)
                method='fn_'+(prefix+'_'+fun).replace('.','_')
                if key not in self.methods:
                    self.methods[key]=''
                    params,inst,ast=self.functions[fun]
                    body,v=self.emit(ast,prefix,inst,params)
                    self.methods[key]=f'function {method}('+', '.join('arg_'+p for p in params)+f') {{\n{body}return {v};\n}}\n'
                return code,method+'('+', '.join(values)+')'
            builtins={'min':'minimum','max':'maximum','rand':'random','sign':'sign','log':'ln'}
            if target=='rand':
                return code,('random(0, '+values[0]+')' if values else 'random(0, 1)')
            if target=='log10':
                # EEL treats log(0) as a very negative value. Keep detector silence finite.
                return code,'log10(maximum(1e-30, '+values[0]+'))'
            return code,builtins.get(target,target)+'('+', '.join(values)+')'
        raise ValueError(node)

def extract(text):
    functions={}
    pattern=r'function\s+(\w+)\s*\(([^)]*)\)\s*(?:instance\s*\(([^)]*)\)\s*)?\('
    while (m:=re.search(pattern,text)):
        pos=m.end();depth=1
        while depth:
            if text[pos]=='(':depth+=1
            elif text[pos]==')':depth-=1
            pos+=1
        body=text[m.end():pos-1]
        functions[m[1]]=(re.findall(r'\w+',m[2]),set(re.findall(r'\w+',m[3] or '')),Parser(body).sequence())
        text=text[:m.start()]+text[pos:]
    return text,functions

def generate(name):
    source=Path('mrelwood',name+('.jsfx' if name.endswith('Reverb_2') else '')).read_text()
    clean=strip_comments(source)
    header=clean.split('@init')[0]
    params=[]
    for m in re.finditer(r'^slider(\d+):([\d.-]+)<([^,]+),([^,>]+)[^>]*>([^\n]*)',header,re.M):
        number,default,lo,hi,label=m.groups()
        if number in ({'14'} if name.endswith('GoldComp4') else {'10','11','12','13'} if name.endswith('GateIQ') else set()):continue
        params.append((number,default,lo,hi,label))
    text=clean.split('@init',1)[1].split('@gfx',1)[0]
    # Remove GUI-only helpers and stale alternate algorithms by parsing, then specializing only reachable functions.
    text,functions=extract(text)
    sections=re.split(r'(@slider|@block|@sample)',text)
    chunks={'init':sections[0]};key='init'
    for item in sections[1:]:
        if item.startswith('@'):key=item[1:]
        else:chunks[key]=item
    preamble=''
    if name.endswith('GoldComp4'):
        # RMS and meters feed only the removed GUI, not the gain computation.
        chunks['sample']=chunks['sample'][chunks['sample'].index('schpf > 20'):]
        chunks['sample']=re.sub(r'\w+\.meterspl\([^;]*;', '', chunks['sample'])
        chunks['sample']=re.sub(r'slider14\s*=.*?;', '', chunks['sample'],flags=re.S)
        chunks['init']='dbmin=-192; pi=$pi; volout=0; in1.y0.pk=in1.y0.flt=in2.y0.pk=in2.y0.flt=in3.y0.pk=in3.y0.flt=in4.y0.pk=in4.y0.flt=-192;'
        chunks['sample']='clnL=spl0;clnR=spl1;'+chunks['sample']
        chunks['block']=''
    if 'Sky_is' in name:
        # Source bufsz() mixes GUI memory offsets into audio allocation; reserve its six audio buffers only.
        args,inst,ast=functions['bufsz']
        fbody='bufsz = srate>150000 ? 32 : srate>75000 ? 64 : srate>40000 ? 128 : 256; limL.buf=0;limR.buf=bufsz;limM.buf=bufsz*2;limS.buf=bufsz*3;lim2L.buf=bufsz*4;lim2R.buf=bufsz*5;memset(0,0,bufsz*6);'
        functions['bufsz']=(args,inst,Parser(fbody).sequence())
    if 'DubStep' in name:
        chunks['slider']='fmin=slider1; fmax=max(slider1+10,slider2);fran=fmax-fmin;offs=slider3;steep=slider4;'
        preamble='// in3: continuous beat position (quarter notes). Pattern buttons default off.\n'
        for i in range(1,57):
            params.append(('step'+str(i),'0','0','1','Pattern button '+str(i)))
        chunks['slider']+=''.join(f'bufena[{i}]=sliderstep{i};' for i in range(1,57))
    if 'Chmahastic' in name:
        chunks['init']=re.sub(r'[LR]\.fpd = 1.0; while .*?;', '', chunks['init'])
        # Right-hand lengths can be 8% larger than left. Give each line its own safe region.
        chunks['init']=re.sub(r'freemem \+=\s*(\d+);',lambda m:f'freemem += {int(int(m[1])*1.09)+2};',chunks['init'])
        chunks['init']+='L.fpd=305419896;R.fpd=2271560481;'
        args,inst,ast=functions['upsli']
        # Strip GUI slider clamping and volume-position display, which do not affect DSP.
        raw=clean[clean.index('function upsli()'):clean.index('function sli(')]
        body=raw[raw.index('(')+1:];body=body[body.index('(')+1:body.rfind(')')]
        body=body[body.index('roomsize ='):]
        body=re.sub(r'volposi = volpos\(voldb\);','',body)
        functions['upsli']=(args,inst,Parser(body).sequence())
    c=Compiler(functions)
    init,iv=c.emit(Parser(chunks.get('init','')).sequence())
    init += iv+';\n'
    setup,sv=c.emit(Parser(chunks.get('slider','')).sequence())
    setup += sv+';\n'
    block,bv=c.emit(Parser(chunks.get('block','')).sequence())
    block += bv+';\n'
    sample,ov=c.emit(Parser(chunks['sample']).sequence())
    sample += ov+';\n'
    text='/* '+name+' — RNBO codebox~ port of mrelwood source.\n * Stereo in1/in2 -> out1/out2; original slider units and defaults.\n * Graphics and GUI meters omitted. See RNBO/README.md and VALIDATION.md.\n'
    # Retain all author/license comments preceding the first slider.
    notice=source[:source.index('slider')]
    text+=' * '+notice.replace('/*','/ *').replace('*/','* /').replace('\n','\n * ')+'\n */\n'+preamble
    for num,default,lo,hi,label in params:
        text+=f'// {label.strip()}\n@param({{ min: {lo}, max: {hi} }}) slider{num} = {default};\n'
    ram_size = 160000 if 'Chmahastic' in name else 1536 if 'Sky_is' in name else 57 if 'DubStep' in name else 1
    if 'ram[' in init+setup+block+sample+''.join(c.methods.values()):
        text+=f'@state ram = new FixedFloat64Array({ram_size});\n'
    text+='@state frame: Int = 0;\n@state prepared = 0;\n'
    paramnames={'s_slider'+p[0]:'slider'+p[0] for p in params}
    text+='\n'.join('@state '+v+' = 0;' for v in sorted(c.states) if v not in paramnames)+'\n'
    text+='// EEL division by zero returns zero; RNBO arithmetic does not.\nfunction eelDivide(a,b) { return b == 0 ? 0 : a/b; }\n'
    text+='\n'.join(c.methods.values())
    dsp_reset='frame = 0; prepared = 0;'
    if name.endswith('GateIQ'):
        for band,freq in [('HI',5000),('MID',1500),('LOW',200)]:
            dsp_reset+=f's_inx{band}=exp(-2*PI*{freq}/samplerate());s_ina0{band}=1-s_inx{band};s_inb1{band}=0-s_inx{band};'
    text+='function dspsetup() { '+dsp_reset+' }\n'
    # Run EEL @init once after DSP rate is known, not before samplerate is available.
    text+='if (prepared == 0) {\nif (prepared == 0 && s_initialized == 0) {\n'+init+'s_initialized = 1;\n}\nprepared = 1;\n}\n'
    # @slider runs on control changes, not every vector (Sky and Chmahastic have side effects).
    text+='@state previousControls = new FixedFloat64Array('+str(len(params))+');\n@state controlsReady = 0;\n'
    text+='if (frame == 0) {\nlet changed = controlsReady == 0;\n'
    for i,(num,default,lo,hi,label) in enumerate(params):
        text+=f'if (previousControls[{i}] != slider{num}) changed = 1;\npreviousControls[{i}] = slider{num};\n'
    text+='if (changed) {\n'+setup+'controlsReady = 1;\n}\n'+block+'}\n'
    text=text.replace('prepared = 0; }', 'prepared = 0; controlsReady = 0; }')
    text+='s_spl0 = in1;\ns_spl1 = in2;\n'+sample+'\nout1 = s_spl0;\nout2 = s_spl1;\n'
    if name.endswith('Filters'):text+='out3 = s_spl2;\nout4 = s_spl3;\n'
    text+='frame++;\nif (frame >= vectorsize()) frame = 0;\n'
    text=text.replace('@state frame: Int', '@state s_initialized = 0;\n@state frame: Int')
    # Drop unused expression statements, retaining calls and all state updates.
    text=re.sub(r'^\s*(?:0|s_\w+|tmp\d+);\s*$', '', text, flags=re.M)
    text=re.sub(r'if \(\(([^()]+(?:==|!=|<=|>=|<|>)[^()]+)\)\)', r'if (\1)', text)
    for var,param in paramnames.items():text=re.sub(r'\b'+var+r'\b',param,text)
    Path('RNBO',name+'.txt').write_text(text)
    print('Generated',name,len(c.methods),'namespace functions',len(c.states),'states')

if __name__=='__main__':
    import sys
    for name in (sys.argv[1:] or NAMES):generate(name)
