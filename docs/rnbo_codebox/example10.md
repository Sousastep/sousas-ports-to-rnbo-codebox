// the buffer itself is stateful
@state rnbobuf = new buffer("codebox.helpbuffer");
@state readPhasor = new phasor();
let readIndex = readPhasor.next(in1) * dim(rnbobuf);

// these operations we can perform on it are stateless
let channels = channels(rnbobuf);
let dim = dim(rnbobuf);
let channel = 0;
// write to a buffer with poke or splat
poke(rnbobuf, (in2 * 2 - 1), readIndex, channel, 0.5);

out1 = readIndex;
// read from a buffer (peek returns 2 values, like the object)
out2 = peek(rnbobuf, readIndex, channel)[0];
// second value in the array is the index
out3 = peek(rnbobuf, readIndex, channel)[1];
// other operators to read from a buffer
out4 = lookup(rnbobuf, readIndex, channel)[0];
out5 = wave(rnbobuf, readIndex, 0, 1, channel)[0];
out6 = sample(rnbobuf, readIndex, channel, { boundmode: "fold", channelmode: "clamp" })[0];
out7 = nearest(rnbobuf, readIndex, channel, { indexmode: "samples", interp: "cubic" })[0];