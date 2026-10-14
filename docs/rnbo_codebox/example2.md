// Declare functions first 

@state modOsc = new cycle();
@state cOsc = new cycle();

function simpleFM(carrier, harmRatio, modIndex)
{
	let modFreq = carrier * harmRatio;
	let modAmp = modFreq * modIndex;
	cFreq = carrier + modOsc.next(modFreq, 0)[0] * modAmp;
	return cOsc.next(cFreq, 0)[0]; 
}

// call the function and pass ins as args
let x = simpleFM(in1, in2, in3);

// smooth the input with average()
@state avg = new average();
let gain = avg.next(in4 / 127.0, 100); // smooth 100 samples

// output the result
out1 = x * gain;