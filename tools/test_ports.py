"""DSP arithmetic verification, not an RNBO compiler replacement.
Runs the delivered .txt arithmetic in C++ against the checked-in original DSP.
Temporary generated C++ and executable are confined to a temporary directory.
"""
from pathlib import Path
import re
import subprocess
import tempfile
from port_airwindows import NAMES, ROOT, strip_comments


def extract_functions(text):
    functions = []
    while (m := re.search(r'function (\w+)\(([^)]*)\)(?:: (\w+))?\s*\{', text)):
        end = m.end(); depth = 1
        while depth:
            if text[end] == '{': depth += 1
            if text[end] == '}': depth -= 1
            end += 1
        functions.append((m[1], m[2], m[3], text[m.end():end-1]))
        text = text[:m.start()] + text[end:]
    return text, functions


def local_types(text):
    text = re.sub(r'\blet (\w+): Int', r'Int \1', text)
    text = re.sub(r'\blet (\w+)', r'double \1', text)
    text = re.sub(r'\bconst (\w+) =', r'const double \1 =', text)
    return text


def port_class(name):
    text, funcs = extract_functions(strip_comments(Path('RNBO', name+'.txt').read_text()))
    fields = []
    def state(m):
        var, typ, val = m.groups()
        if val.startswith('new Fixed'):
            expression = val[val.index('(')+1:-1]
            if expression.startswith('['):
                items = expression[1:-1]
                fields.append(f'Array<Int, {len(items.split(","))}> {var}{{{{{items}}}}};')
            else:
                dims = expression.split(',')
                arr = 'float' if val.startswith('new FixedFloat32Array') else 'double'
                for dim in reversed(dims): arr = f'Array<{arr}, {dim.strip()}>'
                fields.append(f'{arr} {var}{{}};')
        else:
            fields.append(f'{"Int" if typ else "double"} {var} = {val};')
        return ''
    text = re.sub(r'@state (\w+)(: Int)? = ([^;]+);', state, text)
    def param(m):
        fields.append(f'double {m[1]} = {m[2]};')
        return ''
    text = re.sub(r'@param\([^\n]*?\) (\w+) = ([^;]+);', param, text)
    def constant(m):
        fields.append(f'static constexpr Int {m[1]} = {m[2]};')
        return ''
    text = re.sub(r'const (\w+) = (\d+);', constant, text)
    methods = []
    for fun, args, ret, body in funcs:
        args = ', '.join(('Int ' + x.strip().split(':')[0]) if ':' in x else 'double ' + x.strip() for x in args.split(',') if x.strip())
        rettype = 'void' if fun in ('init', 'dspsetup') else 'Int' if ret == 'Int' else 'double'
        methods.append(f'{rettype} {fun}({args}) {{ {local_types(body)} }}')
    init = 'init();' if any(f[0] == 'init' for f in funcs) else ''
    return f'''struct Port_{name} {{
        double in1=0,in2=0,in3=0,in4=0,out1=0,out2=0,out3=0,out4=0,sr=44100;
        Int vs=64;
        double samplerate() {{return sr;}}
        Int vectorsize() {{return vs;}}
        {chr(10).join(sorted(fields, key=lambda f: not f.startswith('static constexpr')))}
        {chr(10).join(methods)}
        Port_{name}() {{{init}}}
        void run() {{ {local_types(text)} }}
    }};\n'''


def reference_class(name):
    h = strip_comments((ROOT/name/(name+'.h')).read_text().split('private:',1)[1])
    h = h[:h.rindex('};')]
    h = re.sub(r'char _programName\[[^]]+\];|std::set< std::string > _canDo;', '', h)
    if name == 'X2Buss':
        h = h.replace('intermediateL[18]', 'intermediateL[33]').replace('intermediateR[18]', 'intermediateR[33]')
        h = h.replace('slewL[34]', 'slewL[65]').replace('slewR[34]', 'slewR[65]')
    cpp = (ROOT/name/(name+'.cpp')).read_text()
    ctor = cpp.split('AudioEffectX(audioMaster, kNumPrograms, kNumParameters)\n{',1)[1].split('_canDo.insert',1)[0]
    ctor = re.sub(r'fpd[LR] = 1.0; while \(fpd[LR] < 16386\) fpd[LR] = rand\(\)\*UINT32_MAX;', '', ctor)
    proc = (ROOT/name/(name+'Proc.cpp')).read_text().split('::processDoubleReplacing',1)[1]
    proc = proc[proc.index('{')+1:proc.rindex('}')]
    if name in ('VariMu', 'ButterComp2'):
        lo = proc.index('static int noisesourceL'); hi = proc.index('double drySampleL',lo)
        proc = proc[:lo]+proc[hi:]
    params = re.findall(r'\b([A-J])\s*=\s*([\d.]+);', strip_comments(ctor))
    full_header = strip_comments((ROOT/name/(name+'.h')).read_text())
    constants = '\n'.join(re.findall(r'const int d4\w+ = \d+;', full_header)).replace('const int', 'static constexpr int')
    prime = re.search(r'static int prime\[\] = \{[^}]+\};', full_header)
    if prime: constants += '\ninline ' + prime[0]
    return f'''struct Ref_{name} {{
        {constants}
        {h}
        double sr=44100;
        double getSampleRate() {{return sr;}}
        Ref_{name}() {{ {ctor} fpdL=305419896u; fpdR=2271560481u; }}
        void process(double **inputs,double **outputs,VstInt32 sampleFrames) {{ {proc} }}
    }};\n''', params


PRELUDE = r'''
#include <array>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <algorithm>
using Int = int64_t;
using VstInt32 = int;
constexpr double PI = 3.14159265358979323846;
using std::sin; using std::cos; using std::tan; using std::asin;
using std::pow; using std::floor; using std::sqrt; using std::trunc;
using std::log1p; using std::expm1; using std::log; using std::fma;
using std::atan; using std::ceil; using std::log10;
inline double sign(double x) {return (x>0)-(x<0);}
inline double random(double lo,double hi) {static uint32_t x=1234567;x^=x<<13;x^=x>>17;x^=x<<5;return lo+(hi-lo)*(double(x)/4294967296.0);}
inline double tempo() {return 120;}
inline double minimum(double x,double y) {return std::min(x,y);}
inline double maximum(double x,double y) {return std::max(x,y);}
inline double clamp(double x,double a,double b) {return std::clamp(x,a,b);}
template<class T,size_t N> struct Array {
    std::array<T,N> a{};
    T& operator[](Int i) {if(i<0 || i>=Int(N)) throw std::runtime_error("array bounds");return a[size_t(i)];}
};
'''


def build():
    code = PRELUDE
    tests = []
    for name in NAMES:
        ref, params = reference_class(name)
        code += ref + port_class(name)
        cpp = (ROOT/name/(name+'.cpp')).read_text()
        labels = dict(re.findall(r'case kParam([A-J]): vst_strncpy\s*\(text, "([^"]+)"', cpp.split('::getParameterName',1)[1].split('::getParameterDisplay',1)[0]))
        assignments = ''
        changes = ''
        for key, default in params:
            param = 'p_'+re.sub(r'[^A-Za-z0-9_]', '', labels[key]).lower()
            assignments += f'r->{key} = setting==0 ? {default} : setting==1 ? 0.0f : setting==2 ? 1.0f : float(0.17+0.071*{ord(key)-65}); p->{param}=r->{key};\n'
            changes += f'r->{key}=float(0.8-0.063*{ord(key)-65});p->{param}=r->{key};\n'
        extra = 'r->lastDryL=0;r->lastDryR=0;' if name == 'ADClip9' else ''
        tests.append(f'''
        {{ double peakError=0;
        for(double rate: {{44100.0,48000.0,96000.0}}) for(Int vector: {{1,64,256}}) for(int setting=0;setting<4;setting++) {{
            auto r = new Ref_{name}{{}}; auto p = new Port_{name}{{}};
            {extra}
            r->sr=p->sr=rate;p->vs=vector;
            {assignments}
            double error=0;
            for(Int base=0;base<{65536 if name == 'TakeCare' else 16384};base+=vector) {{
                if(base==8192) {{ {changes} }}
                double l[256]{{}},rr[256]{{}},ol[256]{{}},orr[256]{{}};
                for(Int i=0;i<vector;i++) {{
                    Int t=base+i;
                    l[i] = t<128 ? 0.0 : (t==128 ? 3.0 : std::sin(t*0.013)*1.2 + std::sin(t*0.311)*0.3);
                    rr[i] = t<128 ? 0.0 : (t==129 ? -3.0 : std::cos(t*0.019)*0.7);
                }}
                double* inputs[2]={{l,rr}};double* outputs[2]={{ol,orr}};
                r->process(inputs,outputs,int(vector));
                for(Int i=0;i<vector;i++) {{
                    p->in1=l[i];p->in2=rr[i];p->run();
                    if(!std::isfinite(p->out1)||!std::isfinite(p->out2)) throw std::runtime_error("{name}: nonfinite");
                    error=std::max(error,std::max(std::fabs(ol[i]-p->out1),std::fabs(orr[i]-p->out2)));
                }}
            }}
            if(error>{'2e-5' if name == 'Ultralight2' else '2e-10'}) {{ std::cerr<<"FAIL {name} rate="<<rate<<" vector="<<vector<<" setting="<<setting<<" max error="<<error<<"\\n";return 1; }}
            peakError=std::max(peakError,error);
            delete r;delete p;
        }}
        std::cout<<"PASS {name}: 36 original-DSP comparisons, max error="<<peakError<<"\\n";
        }}
        ''')
    for name in ('RCInflator2_Ideal','mrelwood_BandbAss'):
        code += port_class(name)
        tests.append(f'''
        for(double rate: {{44100.0,48000.0,96000.0}}) for(Int vector: {{1,64,256}}) {{
            auto p=new Port_{name};p->sr=rate;p->vs=vector;
            for(Int t=0;t<32768;t++) {{
                p->in1=t<128 ? 0 : 0.5*std::sin(t*0.03);p->in2=t<128 ? 0 : 0.4*std::cos(t*0.023);
                p->in3= (t%4096)<256 ? 0.9*std::sin(t*0.01) : 0;p->in4=0.2*std::sin(t*0.025);
                p->run();if(!std::isfinite(p->out1)||!std::isfinite(p->out2)) throw std::runtime_error("{name}: nonfinite");
            }}
            delete p;
        }}
        std::cout<<"PASS {name}: stereo/sidechain smoke at 3 rates and 3 vectors\\n";
        ''')
    # Independently evaluate the original Inflator waveshaper / crossover equations.
    tests.append(r'''
    for(int split=0;split<2;split++) for(int clipmode=0;clipmode<2;clipmode++)
    for(double curve: {-50.0,0.0,50.0}) for(double amount: {0.0,50.0,100.0}) {
        Port_RCInflator2_Ideal p;p.band_split=split;p.clip=clipmode;p.curve=curve;p.effect=amount;p.input_db=6;p.output_db=-3;
        double ia[2]={0,0},ib[2]={0,0};
        double ca=std::tan(PI*(240.0/44100-0.25))*0.5+0.5,cb=std::tan(PI*(2400.0/44100-0.25))*0.5+0.5;
        double gain=cb*(1-ca)/(cb-ca);
        auto shape=[&](double x) {double y=std::fabs(x),a=curve*0.01+1.5,b=curve*-0.02,c=curve*0.01-0.5,d=0.0625-curve*0.0025+curve*curve*0.000025;
            double s=y<1 ? a*y+b*y*y+c*y*y*y-d*(y*y-2*y*y*y+y*y*y*y) : y<2 ? 2*y-y*y : 0;
            return s*amount*0.01*((x>0)-(x<0))+x*(1-amount*0.01);};
        for(int t=0;t<4096;t++) {
            p.in1=std::sin(t*0.23)*1.4;p.in2=std::cos(t*0.017)*0.9;p.run();
            for(int ch=0;ch<2;ch++) {double x=clamp((ch?p.in2:p.in1)*std::pow(10,0.3),clipmode?-1:-2,clipmode?1:2);
                if(split) {double l=ia[ch]+ca*(x-ia[ch]);ia[ch]=2*l-ia[ch];double r=(1-cb)*ib[ch]+cb*x;ib[ch]=2*r-ib[ch];double h=x-r;
                    x=shape(l)+shape((x-l-h)*gain)/gain+shape(h);} else x=shape(x);
                x*=std::pow(10,-0.15);if(std::fabs(x-(ch?p.out2:p.out1))>1e-12) throw std::runtime_error("Inflator reference mismatch");
            }
        }
    }
    std::cout<<"PASS Inflator: 36 independent JSFX-equation comparisons\n";
    ''')
    tests.append(r'''
    {
        Port_mrelwood_BandbAss p;
        p.vs=64;p.stereo=1;p.link_thresholds=0;
        for(Int t=0;t<300000;t++) {
            p.in1=t<4096 ? 0.7*std::sin(t*0.02) : 0;
            p.in2=t<4096 ? -p.in1 : 0;
            p.in3=t<1024 ? 0.8*std::sin(t*0.01) : 0;
            p.in4=t<4096 ? 0.4 : 0;
            if(t==8192) p.channel4=-1;
            if(t==16384) {p.channel4=1;p.attack=50;p.hold=100;p.release=300;p.depth=200;}
            p.run();if(!std::isfinite(p.out1)||!std::isfinite(p.out2)) throw std::runtime_error("BandbAss automation/silence");
            if(t==512 && p.secmode!=1) throw std::runtime_error("BandbAss ch4 auto detect");
            if(t==8256 && p.secmode!=-1) throw std::runtime_error("BandbAss ch4 disable");
        }
        if(!p.sleeping) throw std::runtime_error("BandbAss five-second sleep");
    }
    {
        Port_RCInflator2_Ideal p;p.input_db=6;p.output_db=-3;p.effect_in=0;
        p.in1=2;p.in2=-2;p.run();
        if(std::fabs(p.out1-std::pow(10,-0.15))>1e-12 || std::fabs(p.out2+p.out1)>1e-12) throw std::runtime_error("Inflator effect-in gain/clip behavior");
    }
    std::cout<<"PASS JSFX controls: Inflator partial bypass; BandbAss ch4 auto/disable, automation, long silence\n";
    ''')
    return code+'\nint main(){try{\n'+''.join(tests)+'\n}catch(const std::exception& e){std::cerr<<e.what()<<"\\n";return 1;}return 0;}\n'


if __name__ == '__main__':
    with tempfile.TemporaryDirectory(prefix='rnbo-dsp-') as tmp:
        src = Path(tmp,'tests.cpp'); src.write_text(build())
        exe = Path(tmp,'tests')
        subprocess.run(['clang++','-std=c++17','-O1','-fsanitize=address,undefined','-fno-omit-frame-pointer',str(src),'-o',str(exe)],check=True)
        subprocess.run([str(exe)],check=True)
