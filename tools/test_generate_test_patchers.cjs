// Node-hosted Max API simulation; not a Max/RNBO integration or compile test.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '..');
const sourceDirectory = path.join(root, 'RNBO');
const script = fs.readFileSync(path.join(sourceDirectory, 'generate_test_patchers.js'), 'utf8');
let jobs = [], messages = [], errors = [];
class Box {
    constructor(patcher, x, y, type, args) {
        this.patcher = patcher; this.rect = [x, y, x + 70, y + 23];
        this.type = type; this.args = args; this.valid = true; this.varname = '';
        this.attrs = {}; this.boxattrs = {}; this.source = '';
        if (type === 'rnbo~') {
            this.inner = new Patch();
            this.inner.parentBox = this;
            this.inner.newdefault(10, 10, 'in~', 1); // Simulate a user default template.
            this.inner.newdefault(10, 60, 'out~', 1);
        }
    }
    get nextobject() { return this.patcher.boxes[this.patcher.boxes.indexOf(this) + 1]; }
    subpatcher() { return this.inner; }
    getattrnames() { return []; }
    getboxattrnames() { return []; }
    setattr(name, value) { this.attrs[name] = value; }
    setboxattr(name, value) { this.boxattrs[name] = value; }
    getattr(name) { return this.attrs[name]; }
    message(name, value) { assert.equal(name, 'set'); this.value = value; }
}
class Patch {
    constructor() { this.boxes = []; this.lines = []; }
    get firstobject() { return this.boxes[0]; }
    newdefault(x, y, type, ...args) {
        assert(['rnbo~', 'codebox~', 'in~', 'out~', 'number', 'setparam', 'comment', 'loadmess'].includes(type));
        const box = new Box(this, x, y, type, args); this.boxes.push(box); return box;
    }
    connect(from, output, to, input) {
        assert(this.boxes.includes(from) && this.boxes.includes(to));
        if (from.type === 'codebox~') assert(output < oracle(codeboxSource(from)).outputs);
        if (to.type === 'codebox~') assert(input < oracle(codeboxSource(to)).inputs);
        this.lines.push({ from, output, to, input });
    }
    remove(box) { box.valid = false; this.boxes.splice(this.boxes.indexOf(box), 1); }
}
// RNBO does not expose code as a writable attribute through v8, so generated
// codebox~ boxes stay empty; port checks read the checked-in source instead.
function codeboxSource(box) {
    const host = box.patcher.parentBox;
    assert(/^rnbo_test_/.test(host.varname), 'codebox outside a generated host');
    return fs.readFileSync(path.join(sourceDirectory, host.varname.slice(10) + '.txt'), 'utf8');
}
function oracle(source) {
    const stripped = source.replace(/\/\*[\s\S]*?\*\/|\/\/[^\n]*/g, '');
    return {
        inputs: Math.max(1, ...[...stripped.matchAll(/\bin(\d+)\b/g)].map(m => +m[1])),
        outputs: Math.max(0, ...[...stripped.matchAll(/\bout(\d+)\b/g)].map(m => +m[1])),
        params: [...stripped.matchAll(/@param(?:\([^\n]*\))?\s+(\w+)\s*=/g)].map(m => m[1]),
        // Literal numeric defaults are auto-sent via loadmess; others null.
        defaults: [...stripped.matchAll(/@param(?:\([^\n]*\))?\s+(\w+)\s*=\s*([^;\n]*)/g)].map(m => {
            const e = m[2].trim();
            return /^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$/.test(e) ? Number(e) : null;
        })
    };
}
class Folder {
    constructor(directory) {
        this.pathname = directory;
        this.files = fs.existsSync(directory) ? fs.readdirSync(directory) : [];
        this.index = 0;
    }
    get end() { return this.index >= this.files.length; }
    get filename() { return this.files[this.index]; }
    get filetype() { return fs.statSync(path.join(this.pathname, this.filename)).isDirectory() ? 'fold' : 'TEXT'; }
    next() { this.index++; }
    close() { this.closed = true; }
}
class File {
    constructor(filename, mode) {
        assert.equal(mode, 'read');
        this.isopen = fs.existsSync(filename);
        if (this.isopen) { this.data = fs.readFileSync(filename); this.eof = this.data.length; }
        this.position = 0;
    }
    readbytes(n) { const data = [...this.data.subarray(this.position, this.position + n)]; this.position += data.length; return data; }
    close() { this.isopen = false; }
}
class Task {
    constructor(fn, context) { this.fn = fn; this.context = context; }
    schedule(ms) { assert(ms >= 0); jobs.push(this); }
    cancel() { this.canceled = true; }
}
const parent = new Patch();
const context = vm.createContext({
    File, Folder, Task, patcher: parent,
    post: text => messages.push(text), error: text => errors.push(text),
    outlet: (...args) => messages.push(args)
});
vm.runInContext(script, context, { filename: 'generate_test_patchers.js' });
assert.equal(vm.runInContext('typeof TextDecoder', context), 'undefined');
// UTF-8 must work in Max runtimes without browser/Node decoding globals.
for (const value of ['', 'ASCII\r\n', '© — µ −', '日本語', '🎛️ 🎵', 'x'.repeat(16383) + '🎵']) {
    const bytes = [...Buffer.from(value, 'utf8')];
    assert.equal(context.decodeUTF8(bytes), value);
    assert.equal(context.decodeUTF8(bytes.map(b => b > 127 ? b - 256 : b)), value);
}
assert.equal(context.decodeUTF8([0xEF, 0xBB, 0xBF, 65]), 'A');
for (const bytes of [[0x80], [0xC0, 0xAF], [0xC2], [0xC2, 65],
    [0xE0, 0x80, 0x80], [0xED, 0xA0, 0x80], [0xF0, 0x80, 0x80, 0x80],
    [0xF4, 0x90, 0x80, 0x80], [0xF5, 0x80, 0x80, 0x80]]) {
    assert.throws(() => context.decodeUTF8(bytes), /UTF-8/);
}
context.bang();
assert(errors.pop().includes('Set SOURCE_DIRECTORY'));
context.SOURCE_DIRECTORY = sourceDirectory;
context.bang();
function drain() {
    let count = 0;
    while (jobs.length) {
        assert(++count < 1000, 'Task queue did not terminate');
        const task = jobs.shift(); if (!task.canceled) task.fn.call(task.context);
    }
}
drain();
assert.deepEqual(errors, []);
const files = fs.readdirSync(sourceDirectory).filter(f => /\.txt$/i.test(f)).sort();
assert.equal(parent.boxes.length, files.length);
for (let i = 0; i < files.length; i++) {
    const filename = files[i], rnbo = parent.boxes[i];
    const original = fs.readFileSync(path.join(sourceDirectory, filename), 'utf8');
    const expected = oracle(original), p = rnbo.inner;
    assert.equal(rnbo.varname, 'rnbo_test_' + filename.slice(0, -4));
    assert.deepEqual(rnbo.args, ['@autobuild', 0, '@annotation_name', filename.slice(0, -4)]);
    assert.equal(rnbo.attrs.autobuild, 0);
    const code = p.boxes.find(b => b.type === 'codebox~');
    assert.equal(code.attrs.code, undefined, filename + ' attempted the unwritable v8 code attribute');
    assert.equal(code.source, '');
    assert.equal(p.boxes.filter(b => b.type === 'in~').length, expected.inputs, filename);
    assert.equal(p.boxes.filter(b => b.type === 'out~').length, expected.outputs, filename);
    assert.equal(p.boxes.filter(b => b.type === 'setparam').length, expected.params.length, filename);
    for (const name of expected.params) {
        const number = p.boxes.find(b => b.varname === 'value_' + name);
        const setter = p.boxes.find(b => b.varname === 'set_' + name);
        assert.equal(number.attrs.format, 6);
        assert.equal(number.args[1], 'float');
        assert.deepEqual(setter.args, [name]);
        assert(p.lines.some(l => l.from === number && l.to === setter && l.input === 0));
        assert(p.lines.some(l => l.from === setter && l.to === code && l.input === 0));
        const index = expected.params.indexOf(name);
        const defaultValue = expected.defaults[index];
        const loader = p.boxes.find(b => b.varname === 'load_' + name);
        if (defaultValue === null) {
            assert(!loader, filename + ' loadmess for nonliteral default ' + name);
        } else {
            assert(loader, filename + ' missing loadmess for ' + name);
            assert.deepEqual(loader.type, 'loadmess');
            assert.deepEqual(loader.args, [defaultValue], filename + ' loadmess value for ' + name);
            assert(p.lines.some(l => l.from === loader && l.to === number && l.input === 0));
        }
    }
    assert.equal(p.lines.length, expected.inputs + expected.outputs + 2 * expected.params.length +
        expected.defaults.filter(d => d !== null).length, filename);
    // All boxes stay disjoint; patchcord crossings are permitted.
    for (let a = 0; a < p.boxes.length; a++) for (let b = a + 1; b < p.boxes.length; b++) {
        const r = p.boxes[a].rect, s = p.boxes[b].rect;
        assert(!(r[0] < s[2] && s[0] < r[2] && r[1] < s[3] && s[1] < r[3]), filename + ' overlapping boxes');
    }
}
context.bang(); drain(); assert.equal(parent.boxes.length, files.length, 'rerun duplicated effects');
const meta = context.analyzeSource(`// in99 out99 @param bogus = 1;
/* in88 out88 */ @param({ enum: ["in77", "out66", "@param fake"] }) choice = 1;
@param gain = -2e-3; @param() computed = PI / 2;
let text = "escaped \\\" in55"; out4 = in3;`);
assert.equal(meta.inputs, 3); assert.equal(meta.outputs, 4);
assert.deepEqual(Array.from(meta.params, p => p.name), ['choice', 'gain', 'computed']);
assert.equal(meta.params[1].defaultValue, -.002); assert.equal(meta.params[2].defaultValue, null);
assert.throws(() => context.analyzeSource('@param x = 1; @param x = 2; out1=in1;'), /Duplicate/);
assert.throws(() => context.analyzeSource('listout1 = [];'), /List ports/);
// Failure must remove only its partially created host and continue the batch.
const first = parent.boxes[0]; parent.remove(first);
const create = parent.newdefault;
parent.newdefault = function (...args) {
    const box = create.apply(this, args);
    if (box.type === 'rnbo~') box.inner.newdefault = () => { throw new Error('simulated Max creation error'); };
    return box;
};
context.bang(); drain();
assert.equal(parent.boxes.length, files.length - 1);
assert(errors.pop().includes('simulated Max creation error'));
parent.newdefault = create;
context.bang();
const one = jobs.shift(); one.fn.call(one.context); // Create host/source but don't finish wiring.
assert.equal(parent.boxes.length, files.length);
context.cancel(); drain();
assert.equal(parent.boxes.length, files.length - 1, 'cancel retained unfinished host');
assert.deepEqual(errors, []);
console.log(`PASS bang interface: ${files.length} real sources; empty codebox~, annotation_name set, ports, Decimal controls with loadmess defaults, wiring, layout/no-overlap incl. loadmess, rerun, cancel, failure cleanup and lexer edge cases; UTF-8 Unicode/invalid-byte checks without TextDecoder.`);
