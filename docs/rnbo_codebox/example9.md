let trigger = in1;
let offset = in2;
let quantum = in3;
// transport
let beattime = beattime();
let currenttime = currenttime();
let currentsampletime = currentsampletime();

let transport = transport();
let tempo = tempo();
let timesignature = timesignature();

let beattimeatsample = beattimeatsample(offset);
let tempoatsample = tempoatsample(offset);
let transportatsample = transportatsample(offset);
let timesignatureatsample = timesignatureatsample(offset);

let lockedphase = lockedphase(quantum);
let quantize = quantize(in1, quantum);

out1 = transport; 
out2 = tempo;
out3 = timesignature[0]; 
out4 = timesignature[1];
out5 = beattime;
out6 = currenttime;
out7 = currentsampletime;
out8 = lockedphase;
out9 = quantize;