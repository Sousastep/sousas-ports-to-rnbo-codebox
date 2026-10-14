@state phasor = new phasor();
let phasorValue = phasor.next(1);

let duty = in1;
let rampUp = in2;
let rampDn = in3;

// window / envelope / wavetable ops
let blackman = blackman(phasorValue);
let boxtotri = boxtotri(phasorValue, duty);
let hamming = hamming(phasorValue);
let hann = hann(phasorValue);
let kink = kink(phasorValue, duty);
let triangle = triangle(phasorValue, duty);
let trapezoid = trapezoid(phasorValue, rampUp, rampDn);
let welch = welch(phasorValue);

out1 = blackman;
out2 = boxtotri;
out3 = hamming; 
out4 = hann;
out5 = kink;
out6 = triangle
out7 = trapezoid
out8 = welch;