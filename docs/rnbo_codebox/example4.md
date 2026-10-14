// stateless operators are simple functions
let vs = vectorsize();
let sr = samplerate();

// that can have parameters:
let rand = random(5, 15);
let scaled = scale(rand, 5, 15, 0, 127, 4);

// and some can take options:
let interp = interp(in1, 0, 0.5, {interp: "linear"});

out1 = vs;
out2 = sr;
out3 = rand;
out4 = scaled;
out5 = interp;