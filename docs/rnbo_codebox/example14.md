// stateful DSP effect operators

@state allpass = new allpass();
@state average_rms = new average_rms();
@state comb = new comb();
@state cross = new cross();
@state onepole = new onepole();
@state reson = new reson();
@state svf = new svf();

// for example:
@state bq = new biquad();
let a0 = in2;
let a1 = in3;
let a2 = in4;
let b1 = in5;
let b2 = in6;

out1 = bq.next(in1, a0, a1, a2, b1, b2);
