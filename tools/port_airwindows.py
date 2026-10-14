"""Generate RNBO codebox~ text artifacts from the checked-in Airwindows sources.
Run from project root: python3 tools/port_airwindows.py
No third-party dependencies. Original sources are never modified.
"""
from pathlib import Path
import re

ROOT = Path('airwindows/plugins/LinuxVST/src')
NAMES = 'ClipOnly3 ADClip9 PaulWide Dynamics3 VariMu Density3 ZAcidLowpass X2Buss TakeCare TapeHack2 ToTape9 VerbTiny VerbThic Ultralight2 ButterComp2 PurestSquish ChannelX ZOutputStage'.split()
LICENSE = Path('airwindows/LICENSE').read_text()


def strip_comments(s):
    return re.sub(r'/\*.*?\*/|//[^\n]*', '', s, flags=re.S)


def translate(s):
    s = s.replace('long double', 'double')
    s = re.sub(r'\bgetSampleRate\(\)', 'samplerate()', s)
    s = s.replace('M_PI_2', '(PI*0.5)').replace('M_PI', 'PI').replace('UINT32_MAX', '4294967295.0')
    s = re.sub(r'\b(?:double|float)\(([^()]*)\)', r'(\1)', s)
    s = re.sub(r'\((?:double|float)\)', '', s)
    # Casts may contain nested parentheses: translate using balanced scanning.
    while re.search(r'\((?:int|VstInt32)\)\s*\(', s):
        m = re.search(r'\((?:int|VstInt32)\)\s*\(', s)
        begin = m.end(); end = begin; depth = 1
        while depth:
            if s[end] == '(': depth += 1
            if s[end] == ')': depth -= 1
            end += 1
        s = s[:m.start()] + 'toIndex(' + s[begin:end-1] + ')' + s[end:]
    s = re.sub(r'\((?:int|VstInt32)\)\s*(floor|ceil|trunc)\(([^()]*)\)', r'toIndex(\1(\2))', s)
    s = re.sub(r'\((?:int|VstInt32)\)\s*(\w+)', r'toIndex(\1)', s)
    s = re.sub(r'\bconst\s+(?:double|float)\s+', 'let ', s)
    s = re.sub(r'\b(?:double|float|bool)\s+', 'let ', s)
    s = re.sub(r'\b(?:int|VstInt32)\s+(\w+)', r'let \1: Int', s)
    s = s.replace('fabs(', 'abs(').replace('fmax(', 'maximum(').replace('fmin(', 'minimum(')
    s = re.sub(r'(\d(?:[\d.eE+-]*\d)?)[lf]\b', r'\1', s)
    # uint32 wrapping, including the unsigned subtraction in the decorrelation test.
    s = re.sub(r'(fpd[LR]) \^= \1 << 13; \1 \^= \1 >> 17; \1 \^= \1 << 5;', r'\1 = advanceRandom(\1);', s)
    s = s.replace('fpdL-fpdR <', 'unsigned32(fpdL-fpdR) <').replace('fpdR-fpdL <', 'unsigned32(fpdR-fpdL) <')
    # Every variable used as an array index is explicitly Int.
    return s

RNG = '''// Xorshift32 with explicit unsigned wrapping (fixed, reproducible seeds).
function unsigned32(x) {
    return x - floor(x / 4294967296.0) * 4294967296.0;
}
function advanceRandom(x) {
    let a: Int = x;
    let left: Int = unsigned32(x * 8192.0);
    let b: Int = unsigned32(a ^ left);
    let shifted: Int = floor(b / 131072.0);
    let c: Int = unsigned32(b ^ shifted);
    left = unsigned32(c * 32.0);
    return unsigned32(c ^ left);
}
function toIndex(x) {
    let result: Int = trunc(x);
    return result;
}
'''


def generate(name):
    h = (ROOT/name/(name+'.h')).read_text()
    cpp = (ROOT/name/(name+'.cpp')).read_text()
    proc = (ROOT/name/(name+'Proc.cpp')).read_text().split('::processDoubleReplacing', 1)[1]
    ctor = strip_comments(cpp.split('AudioEffectX(audioMaster, kNumPrograms, kNumParameters)\n{', 1)[1].split('_canDo.insert', 1)[0])
    defaults = dict(re.findall(r'\b([A-J])\s*=\s*([\d.]+);', ctor))
    labels = dict(re.findall(r'case kParam([A-J]): vst_strncpy\s*\(text, "([^"]+)"', cpp.split('::getParameterName', 1)[1].split('::getParameterDisplay', 1)[0]))
    mapping = {key: 'p_' + re.sub(r'[^A-Za-z0-9_]', '', labels[key]).lower() for key in defaults}
    states = []
    constants = [f'const {var} = {value};' for var, value in re.findall(r'const int (d4\w+) = (\d+);', h)]
    prime = re.search(r'static int prime\[\] = \{([^}]+)\}', h)
    if prime:
        states.append('''@state prime = new FixedIntArray([''' + prime[1] + ''']);''')
    private = strip_comments(h.split('private:', 1)[1])
    for enum in re.findall(r'enum\s*\{(.*?)\};', private, re.S):
        for i, item in enumerate(enum.split(',')):
            item = item.strip()
            if item:
                constants.append(f'const {item} = {i};')
    private = re.sub(r'enum\s*\{.*?\};', '', private, flags=re.S)
    for kind, decl in re.findall(r'\b(double|float|bool|int|uint32_t)\s+([^;]+);', private):
        for part in decl.split(','):
            part = part.strip()
            arr = re.fullmatch(r'(\w+)\[([^]]+)\]', part)
            if arr:
                var, size = arr.groups()
                if name == 'X2Buss' and var.startswith('intermediate'): size = '33'
                if name == 'X2Buss' and var.startswith('slew'): size = '65'
                array_type = 'FixedFloat32Array' if kind == 'float' else 'FixedFloat64Array'
                states.append(f'@state {var} = new {array_type}({size});')
            else:
                if re.fullmatch('[A-J]', part): continue
                value = '305419896.0' if part == 'fpdL' else '2271560481.0' if part == 'fpdR' else '0'
                typ = ': Int' if kind == 'int' else ''
                states.append(f'@state {part}{typ} = {value};')
    ctor = re.sub(r'\b[A-J]\s*=\s*[\d.]+;', '', ctor)
    ctor = re.sub(r'fpd[LR] = 1.0; while \(fpd[LR] < 16386\) fpd[LR] = rand\(\)\*UINT32_MAX;', '', ctor)
    # ADClip9's original constructor leaves lastDry uninitialized: initialize to zero above.
    proc = strip_comments(proc)
    start = proc.index('int processing') if name == 'PaulWide' else re.search(r'(?:double|float) overallscale', proc).start()
    setup, body = proc[start:].split('while (--sampleFrames >= 0)', 1)
    body = body[body.index('{')+1:body.index('*out1 = inputSampleL;')]
    body = body.replace('*in1', 'in1').replace('*in2', 'in2')
    if name in ('VariMu', 'ButterComp2'):
        lo = body.index('static int noisesourceL')
        hi = body.index('double drySampleL')
        body = body[:lo] + '// Legacy ~1e-16 residue noise omitted; compression is unchanged.\n' + body[hi:]
    # Source double dither is disabled, but its random sequence updates are active.
    setup = translate(setup)
    if name == 'ToTape9':
        setup = setup.replace('(H*H)', 'asFloat32(H*H)')
    if name == 'ChannelX':
        # Use a typed selector; custom function returns infer as number in RNBO.
        setup = setup.replace('switch (toIndex( A * 4.999 ))', 'let consoleType: Int = trunc(A * 4.999);\n switch (consoleType)')
    if name == 'PaulWide':
        # The original double DSP deliberately uses float scale variables.
        setup = setup.replace('scaleFactor *= pow(1.0-derez,6);', 'scaleFactor = asFloat32(scaleFactor * pow(1.0-derez,6));')
        setup = setup.replace('scaleFactor = 0.0001;', 'scaleFactor = asFloat32(0.0001);')
    body = translate(body)
    ctor = translate(ctor)
    # Preserve Ultralight2's float storage and intermediate assignment rounding.
    float_vars = set()
    if name == 'Ultralight2':
        for decl in re.findall(r'\bfloat\s+([^;]+);', private):
            float_vars.update(p.strip() for p in decl.split(',') if '[' not in p and not re.fullmatch('[A-J]', p.strip()))
        for fragment in (strip_comments(proc),):
            float_vars.update(re.findall(r'\bfloat\s+(\w+)', fragment))
        def round_assignments(fragment):
            # Scalar assignment statements, including chained constructor assignments.
            pattern = r'(?<![\w.])(' + '|'.join(sorted(float_vars, key=len, reverse=True)) + r')\s*(=|\+=|-=|\*=|/=)\s*([^;]+);'
            def cast(m):
                var, op, rhs = m.groups()
                if op != '=': rhs = var + ' ' + op[0] + ' (' + rhs + ')'
                return var + ' = asFloat32(' + rhs + ');'
            fragment = re.sub(pattern, cast, fragment)
            # Chained assignments inside asFloat32 must round every target.
            return fragment
        setup = round_assignments(setup)
        body = round_assignments(body)
        ctor = round_assignments(ctor)
    # Lift vector-level temporaries to state so they survive between samples.
    block_states = []
    def lift(m):
        var, typ, value = m.groups()
        block_states.append(f'@state {var}{typ or ""} = 0;')
        return f'{var} = {value};'
    setup = re.sub(r'let (\w+)(: Int)? = ([^;]+);', lift, setup)
    setup = re.sub(r'let (\w+)(: Int)?;', lambda m: block_states.append(f'@state {m[1]}{m[2] or ""} = 0;') or '', setup)
    for key, param in mapping.items():
        setup = re.sub(r'\b'+key+r'\b', param, setup)
        body = re.sub(r'\b'+key+r'\b', param, body)
    # TakeCare shadows inputSampleL/R inside the undersampled stage in C++.
    # Preserve that scope with differently named locals in RNBO as well.
    if name == 'TakeCare':
        lo = body.index('let inputSampleL = (o3GL')
        hi = body.index('bez[bez_SampR] = 0.0;', lo) + len('bez[bez_SampR] = 0.0;')
        segment = body[lo:hi].replace('inputSampleL', 'reverbSampleL').replace('inputSampleR', 'reverbSampleR')
        body = body[:lo] + segment + body[hi:]
    text = f'/* {name} — standalone RNBO codebox~ port\n * in1/in2: left/right; out1/out2: left/right.\n * Controls use original normalized VST values (0..1).\n * Double-precision DSP path; no added output dither.\n * Paste this entire file into codebox~ inside rnbo~.\n * '+LICENSE.replace('\n', '\n * ')+'\n */\n\n'
    for key, value in defaults.items():
        text += f'// VST {key}: {labels[key]}\n@param({{ min: 0, max: 1 }}) {mapping[key]} = {value};\n'
    text += '\n'+'\n'.join(constants+states+block_states)+'\n@state frame: Int = 0;\n'+RNG
    if 'fma(' in text + body + setup:
        text += '\n// RNBO has no fused multiply-add operator; preserve the equation.\nfunction multiplyAdd(a, b, c) { return a * b + c; }\n'
        body = body.replace('fma(', 'multiplyAdd(')
        setup = setup.replace('fma(', 'multiplyAdd(')
    if name in ('PaulWide', 'Ultralight2', 'ToTape9'):
        text += '\n@state floatCast = new FixedFloat32Array(1);\nfunction asFloat32(x) { floatCast[0] = x; return floatCast[0]; }\n'
    text += '\nfunction init() {\n'+ctor+'\n}\nfunction dspsetup() { frame = 0; }\n'
    text += '\nif (frame == 0) {\n'+setup+'\n}\nlet sampleFrames = vectorsize() - frame - 1;\nlet inFramesToProcess = vectorsize();\n'+body
    text += '\nout1 = inputSampleL;\nout2 = inputSampleR;\nframe++;\nif (frame >= vectorsize()) frame = 0;\n'
    text = re.sub(r'\btrue\b', '1', text)
    text = re.sub(r'\bfalse\b', '0', text)
    # Custom functions return numbers in RNBO; fixed-array indices require Int.
    lines = []
    index_count = 0
    for line in text.splitlines():
        while '[toIndex(' in line:
            begin = line.index('[toIndex(')
            end = begin + len('[toIndex('); depth = 1; pos = end
            while depth:
                if line[pos] == '(': depth += 1
                if line[pos] == ')': depth -= 1
                pos += 1
            expression = line[end:pos-1]
            index_count += 1
            var = f'readIndex{index_count}'
            lines.append(f'let {var}: Int = trunc({expression});')
            line = line[:begin] + '[' + var + line[pos:]
        lines.append(line)
    text = '\n'.join(lines) + '\n'
    text = re.sub(r'\n[ \t]*\n(?:[ \t]*\n)+', '\n\n', text)
    Path('RNBO', name+'.txt').write_text(text)

if __name__ == '__main__':
    Path('RNBO').mkdir(exist_ok=True)
    import sys
    for name in (sys.argv[1:] or NAMES):
        generate(name)
        print('Generated', name)
