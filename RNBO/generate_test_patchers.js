/* Max 9 v8.codebox: RNBO effect test-patcher generator.
 * 1. Set SOURCE_DIRECTORY below to your RNBO folder (absolute Max/POSIX path).
 * 2. Paste this entire script into a v8.codebox in a normal, unlocked Max patch.
 * 3. Send bang (or generate). Progress/errors appear in the Max console/outlet.
 * 4. Each rnbo~'s inner codebox~ is left empty (the v8 engine cannot write the
 *    code attribute): paste the matching .txt contents into it yourself.
 * 5. Open each generated rnbo~, inspect the patch, then build it manually.
 *
 * Creates objects in THIS patch; does not save files, enable DSP, connect a DAC,
 * clear your patch, or automatically build effects. Repeated bangs skip names
 * already present. "cancel" stops generation and removes only unfinished work.
 * Numbers use Decimal (Floating-Point), format 6, NOT integer Decimal (format 0).
 * Uses Max File/Folder/Task/Patcher APIs, not Node's fs or npm packages.
 */

var SOURCE_DIRECTORY = "/REPLACE/WITH/YOUR/RNBO";
var HOST_COLUMNS = 3;
var CONTROL_COLUMNS = 4;
var DEFER_MS = 100; // Allow codebox parsing/port updates before connecting.
inlets = 1;
outlets = 1;

var generatorContext = this;
var batch = null;
var scheduledTask = null;

function bang() { generate(); }

function generate() {
    if (batch) {
        error("RNBO generator: already running; send cancel first.\n");
        return;
    }
    try {
        const directory = SOURCE_DIRECTORY.replace(/\/+$/, "");
        if (!directory || directory.indexOf("/REPLACE/") === 0) {
            throw new Error("Set SOURCE_DIRECTORY at the top of this script first.");
        }
        const folder = new Folder(directory);
        const files = [];
        let resolvedDirectory;
        try {
            resolvedDirectory = folder.pathname || directory;
            while (!folder.end) {
                if (/\.txt$/i.test(folder.filename) && folder.filetype !== "fold") {
                    files.push(folder.filename);
                }
                folder.next();
            }
        } finally { folder.close(); }
        files.sort();
        if (!files.length) throw new Error("No .txt files found in " + directory);
        batch = {
            directory: resolvedDirectory, files: files, index: 0,
            created: 0, skipped: 0, failed: 0, pending: null,
            parent: generatorContext.patcher, baseY: nextHostY(generatorContext.patcher)
        };
        post("RNBO generator: found " + files.length + " text files.\n");
        schedule(nextEffect);
    } catch (e) { reportError("directory", e); }
}

function cancel() {
    if (scheduledTask) scheduledTask.cancel();
    scheduledTask = null;
    if (!batch) return;
    discardPending();
    post("RNBO generator: canceled; completed objects retained.\n");
    outlet(0, "canceled", batch.created, batch.failed);
    batch = null;
}

function schedule(fn) {
    scheduledTask = new Task(fn, generatorContext);
    scheduledTask.schedule(DEFER_MS);
}

function nextEffect() {
    if (!batch) return;
    if (batch.index >= batch.files.length) {
        post("RNBO generator: done — " + batch.created + " created, " +
            batch.skipped + " skipped, " + batch.failed + " failed. Autobuild remains OFF.\n");
        outlet(0, "done", batch.created, batch.skipped, batch.failed);
        batch = null;
        scheduledTask = null;
        return;
    }
    const filename = batch.files[batch.index++];
    const effectName = filename.replace(/\.txt$/i, "");
    // Preserve punctuation in filenames to avoid collisions between e.g. a-b/a_b.
    const scriptingName = "rnbo_test_" + effectName;
    if (findNamed(batch.parent, scriptingName)) {
        batch.skipped++;
        post("RNBO generator: skip existing " + scriptingName + "\n");
        schedule(nextEffect);
        return;
    }
    try {
        const source = readSource(joinPath(batch.directory, filename));
        const metadata = analyzeSource(source);
        const column = batch.created % HOST_COLUMNS;
        const row = Math.floor(batch.created / HOST_COLUMNS);
        const x = 30 + column * 480;
        const y = batch.baseY + row * 90;
        const rnbo = batch.parent.newdefault(x, y, "rnbo~",
            "@autobuild", 0, "@annotation_name", effectName);
        if (!rnbo || !rnbo.valid) throw new Error("Could not create rnbo~.");
        batch.pending = { rnbo: rnbo, filename: filename, effectName: effectName,
            source: source, metadata: metadata };
        rnbo.varname = scriptingName;
        rnbo.rect = [x, y, x + 450, y + 24];
        preventOverlap(batch.parent, rnbo);
        rnbo.setattr("autobuild", 0);
        const inner = rnbo.subpatcher();
        if (!inner) throw new Error("rnbo~ did not expose its subpatcher.");
        batch.pending.inner = inner;
        // A user's RNBO default template may already contain in~/out~ objects.
        // Clear only this newly created patch, never an existing user's patch.
        const templateObjects = [];
        for (let obj = inner.firstobject; obj; obj = obj.nextobject) templateObjects.push(obj);
        templateObjects.forEach(obj => inner.remove(obj));
        const codebox = inner.newdefault(30, 110, "codebox~");
        if (!codebox || !codebox.valid) throw new Error("Could not create RNBO codebox~.");
        codebox.varname = "effect_code";
        codebox.rect = [30, 110, 650, 470];
        preventOverlap(inner, codebox);
        batch.pending.codebox = codebox;
        // RNBO does not expose code as a writable attribute via v8; the codebox~
        // stays empty. Paste the matching .txt contents manually afterwards.
        schedule(finishEffect);
    } catch (e) { failEffect(filename, e); }
}

function finishEffect() {
    if (!batch || !batch.pending) return;
    const pending = batch.pending;
    try {
        const p = pending.inner;
        const code = pending.codebox;
        comment(p, 30, 20, 620, pending.effectName);
        const info = pending.metadata;
        for (let i = 1; i <= info.inputs; i++) {
            const x = portX(i, info.inputs);
            const input = p.newdefault(x, 70, "in~", i);
            input.varname = "audio_in_" + i;
            input.rect = [x, 70, x + 70, 94];
            preventOverlap(p, input);
            p.connect(input, 0, code, i - 1);
        }
        for (let i = 1; i <= info.outputs; i++) {
            const x = portX(i, info.outputs);
            const output = p.newdefault(x, 520, "out~", i);
            output.varname = "audio_out_" + i;
            output.rect = [x, 520, x + 70, 544];
            preventOverlap(p, output);
            p.connect(code, i - 1, output, 0);
        }
        const cellWidth = Math.max(190, ...info.params.map(param =>
            ("setparam " + param.name).length * 7 + 24));
        info.params.forEach((param, index) => {
            const x = 700 + (index % CONTROL_COLUMNS) * cellWidth;
            const y = 65 + Math.floor(index / CONTROL_COLUMNS) * 115;
            // Cell, top to bottom: name comment, loadmess, number, setparam.
            // 22 + 18 + 23 + 23 = 96px, inside the 115px row stride.
            comment(p, x, y, cellWidth - 15, param.name);
            const number = p.newdefault(x, y + 50, "number", "@initialFormat", "float");
            number.varname = "value_" + param.name;
            number.setattr("format", 6); // Decimal floating-point display/output.
            number.rect = [x, y + 50, x + 100, y + 73];
            preventOverlap(p, number);
            const setter = p.newdefault(x, y + 78, "setparam", param.name);
            setter.varname = "set_" + param.name;
            setter.rect = [x, y + 78, x + cellWidth - 15, y + 101];
            preventOverlap(p, setter);
            p.connect(number, 0, setter, 0);
            p.connect(setter, 0, code, 0);
            if (param.defaultValue !== null) {
                // Numeric atom arg renders as e.g. "loadmess 0.5" / "loadmess -0.1".
                const loader = p.newdefault(x, y + 27, "loadmess", param.defaultValue);
                loader.varname = "load_" + param.name;
                loader.rect = [x, y + 27, x + cellWidth - 15, y + 45];
                preventOverlap(p, loader);
                p.connect(loader, 0, number, 0);
                number.message("set", param.defaultValue);
            }
        });
        pending.rnbo.setattr("autobuild", 0);
        post("RNBO generator: created " + pending.filename + " (" + info.inputs +
            " in, " + info.outputs + " out, " + info.params.length + " params).\n");
        outlet(0, "created", pending.effectName, info.inputs, info.outputs, info.params.length);
        batch.created++;
        batch.pending = null;
        schedule(nextEffect);
    } catch (e) { failEffect(pending.filename, e); }
}

function failEffect(filename, e) {
    reportError(filename, e);
    discardPending();
    batch.failed++;
    schedule(nextEffect);
}

function discardPending() {
    if (batch.pending && batch.pending.rnbo.valid) batch.parent.remove(batch.pending.rnbo);
    batch.pending = null;
}

function reportError(filename, e) {
    error("RNBO generator: " + filename + ": " + String(e.message || e) + "\n");
    outlet(0, "failed", filename, String(e.message || e));
}

function findNamed(p, name) {
    for (let obj = p.firstobject; obj; obj = obj.nextobject) {
        if (obj.varname === name) return obj;
    }
    return null;
}

function nextHostY(p) {
    let bottom = 20;
    for (let obj = p.firstobject; obj; obj = obj.nextobject) {
        bottom = Math.max(bottom, obj.rect[3]);
    }
    return bottom + 50;
}

function portX(index, count) {
    return 30 + (count <= 1 ? 0 : (index - 1) * 575 / (count - 1));
}

// Runtime double-check of the arithmetic layout. If a freshly placed box
// (host, codebox~, in~/out~, comment, number, setparam or loadmess) would
// overlap anything already placed in the same patcher, drop it below the
// lowest overlapping bottom and re-check until it fits.
function preventOverlap(p, box) {
    for (let attempt = 0; attempt < 128; attempt++) {
        const r = box.rect;
        if (!r) return;
        let bottom = null;
        for (let obj = p.firstobject; obj; obj = obj.nextobject) {
            if (obj === box) continue;
            const s = obj.rect;
            if (!s) continue;
            if (r[0] < s[2] && s[0] < r[2] && r[1] < s[3] && s[1] < r[3]) {
                bottom = bottom === null ? s[3] : Math.max(bottom, s[3]);
            }
        }
        if (bottom === null) return;
        const height = r[3] - r[1];
        box.rect = [r[0], bottom + 8, r[2], bottom + 8 + height];
    }
}

function comment(p, x, y, width, text) {
    const obj = p.newdefault(x, y, "comment");
    obj.message("set", text);
    obj.rect = [x, y, x + width, y + 22];
    preventOverlap(p, obj);
    return obj;
}

function joinPath(directory, filename) {
    return directory.replace(/\/+$/, "") + "/" + filename;
}

function readSource(path) {
    const file = new File(path, "read");
    if (!file.isopen) throw new Error("Cannot read " + path);
    try {
        // Decode UTF-8 as bytes, preserving Unicode license notices and long lines.
        const chunks = [];
        while (file.position < file.eof) {
            const before = file.position;
            chunks.push(...file.readbytes(Math.min(16384, file.eof - file.position)));
            if (file.position <= before) throw new Error("Read stalled: " + path);
        }
        const source = decodeUTF8(chunks);
        if (!source.trim()) throw new Error("Empty source: " + path);
        return source;
    } finally { file.close(); }
}

// Max v8 versions differ in their browser globals. Decode File.readbytes()
// directly instead of requiring TextDecoder, Buffer, or a Node module.
function decodeUTF8(bytes) {
    const text = [];
    for (let i = 0; i < bytes.length;) {
        const start = i;
        const first = bytes[i++] & 255;
        let value;
        let remaining;
        let minimum;
        if (first < 0x80) {
            value = first; remaining = 0; minimum = 0;
        } else if (first >= 0xC2 && first <= 0xDF) {
            value = first & 0x1F; remaining = 1; minimum = 0x80;
        } else if (first >= 0xE0 && first <= 0xEF) {
            value = first & 0x0F; remaining = 2; minimum = 0x800;
        } else if (first >= 0xF0 && first <= 0xF4) {
            value = first & 7; remaining = 3; minimum = 0x10000;
        } else {
            throw new Error("Invalid UTF-8 at byte " + start);
        }
        if (i + remaining > bytes.length) throw new Error("Truncated UTF-8 at byte " + start);
        for (let j = 0; j < remaining; j++) {
            const next = bytes[i++] & 255;
            if ((next & 0xC0) !== 0x80) throw new Error("Invalid UTF-8 continuation at byte " + (i - 1));
            value = value * 64 + (next & 0x3F);
        }
        if (value < minimum || value > 0x10FFFF || (value >= 0xD800 && value <= 0xDFFF)) {
            throw new Error("Invalid UTF-8 code point at byte " + start);
        }
        if (value <= 0xFFFF) text.push(String.fromCharCode(value));
        else {
            value -= 0x10000;
            text.push(String.fromCharCode(0xD800 + (value >> 10), 0xDC00 + (value & 0x3FF)));
        }
    }
    // Match conventional UTF-8 text reading: discard an optional leading BOM.
    if (text[0] === "\uFEFF") text.shift();
    return text.join("");
}

// Small lexer, not a DSP compiler. Ignore comments/string contents when counting
// ports. Keep strings as atomic tokens so enum labels cannot invent ports/params.
function sourceTokens(source) {
    const tokens = [];
    let i = source.charCodeAt(0) === 0xFEFF ? 1 : 0;
    while (i < source.length) {
        const c = source[i];
        if (/\s/.test(c)) { i++; continue; }
        if (source.slice(i, i + 2) === "//") {
            const end = source.indexOf("\n", i + 2);
            i = end < 0 ? source.length : end + 1;
        } else if (source.slice(i, i + 2) === "/*") {
            const end = source.indexOf("*/", i + 2);
            if (end < 0) throw new Error("Unterminated block comment.");
            i = end + 2;
        } else if (c === '"' || c === "'") {
            const start = i++;
            let closed = false;
            while (i < source.length) {
                if (source[i] === "\\") i += 2;
                else if (source[i++] === c) { closed = true; break; }
            }
            if (!closed) throw new Error("Unterminated string.");
            tokens.push(source.slice(start, i));
        } else {
            const match = /^(?:[A-Za-z_$][\w$]*|(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)/.exec(source.slice(i));
            if (match) { tokens.push(match[0]); i += match[0].length; }
            else { tokens.push(c); i++; }
        }
    }
    return tokens;
}

function analyzeSource(source) {
    const tokens = sourceTokens(source);
    let inputs = 1; // RNBO codebox always has its first inlet.
    let outputs = 0;
    const params = [];
    const names = new Set();
    for (let i = 0; i < tokens.length; i++) {
        const port = /^(in|out)([1-9]\d*)$/.exec(tokens[i]);
        if (port && tokens[i - 1] !== ".") {
            if (port[1] === "in") inputs = Math.max(inputs, Number(port[2]));
            else outputs = Math.max(outputs, Number(port[2]));
        }
        if (/^(?:listin|listout)\d+$/.test(tokens[i])) {
            throw new Error("List ports are not supported by this signal-effect generator.");
        }
        if (tokens[i] !== "@" || tokens[i + 1] !== "param") continue;
        let cursor = i + 2;
        if (tokens[cursor] === "(") {
            let depth = 1;
            while (++cursor < tokens.length && depth) {
                if (tokens[cursor] === "(") depth++;
                if (tokens[cursor] === ")") depth--;
            }
            if (depth) throw new Error("Unbalanced @param declaration.");
        }
        const name = tokens[cursor++];
        if (!/^[A-Za-z_$][\w$]*$/.test(name || "")) throw new Error("Invalid @param name.");
        if (tokens[cursor] === ":") cursor += 2; // Optional type annotation.
        if (tokens[cursor++] !== "=") throw new Error("Missing @param default for " + name);
        const start = cursor;
        while (cursor < tokens.length && tokens[cursor] !== ";") cursor++;
        if (cursor === tokens.length) throw new Error("Unterminated @param " + name);
        if (names.has(name)) throw new Error("Duplicate @param " + name);
        names.add(name);
        const expression = tokens.slice(start, cursor).join("");
        // No eval: nonliteral defaults remain in codebox; UI stays unset/zero.
        const defaultValue = /^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$/.test(expression)
            ? Number(expression) : null;
        params.push({ name: name, defaultValue: defaultValue });
    }
    if (!outputs) throw new Error("No signal outputs found in the source.");
    return { inputs: inputs, outputs: outputs, params: params };
}
