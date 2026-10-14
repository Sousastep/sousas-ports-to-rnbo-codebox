// audio conversions
let atodb = atodb(in1);
let dbtoa = dbtoa(atodb);
let phasewrap = phasewrap(in1);
let poltocar = poltocar(in1,in2);
let cartopol = cartopol(in1, in2);

// dsp status
let vs = vectorsize();
let sr = samplerate();

out1 = atodb;
out2 = dbtoa;