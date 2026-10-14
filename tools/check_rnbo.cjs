// Uses the RNBO grammar installed with Max; does not modify that installation.
const fs = require('fs');
const path = require('path');
const rnbo = process.env.RNBO_DIR || '/Applications/Max.app/Contents/Resources/C74/packages/RNBO';
process.env.RNBO_DIR = rnbo;
const modules = path.join(rnbo, 'server/node_modules');
const xam = path.join(modules, '@rnbo/xam/lib');
const peg = require(path.join(modules, 'pegjs'));
const parser = peg.generate(fs.readFileSync(path.join(xam, 'expression.pegjs'), 'utf8'), {cache: true, allowedStartRules: ['Start']});
const semantic = process.argv.includes('--semantic') ? require(path.join(xam, 'expression.js')) : null;
let failed = false;
for (const file of fs.readdirSync('RNBO').filter(f => f.endsWith('.txt')).sort()) {
    try {
        const text = fs.readFileSync(path.join('RNBO', file), 'utf8');
        const ast = parser.parse(text);
        if (semantic) semantic.parse(text, {props: {classname: 'codebox~'}, patchPath: file}, true);
        console.log(`PASS ${file}: RNBO ${semantic ? 'grammar and name/operator checks' : 'grammar'} (${ast.body.length} statements)`);
    } catch (e) {
        failed = true;
        console.error(`FAIL ${file}: ${e.message} ${JSON.stringify(e.location || e.loc || '')}`);
    }
}
if (failed) process.exitCode = 1;
