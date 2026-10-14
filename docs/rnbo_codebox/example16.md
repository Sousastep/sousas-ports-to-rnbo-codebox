// buffers are stateful
// codebox can reference a Max buffer
@state maxbuf = new buffer("jongly");
// or a rnbo buffer
@state rnbobuf = new data("internal");
// or create a buffer
@state codebuf = new buffer(512);
// add a param to morph buffers
@param() morph = 0;

for (var i = 0; i < dim(codebuf); i += 1)
{
	let x = peek(rnbobuf, i);
	let y = peek(maxbuf, in1 * dim(maxbuf));
	let val = interp(morph, x[0], y[0]);
	poke(codebuf, val, i);
}

out1 = codebuf[in1 * dim(codebuf)];