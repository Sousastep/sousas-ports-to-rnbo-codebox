function init()
{
	// init is a special function which is called once
	post("init the codebox");
}

function dspsetup() 
{	
	// dspsetup is called whenever audio is turned on
	var vs = vectorsize();
	var sr = samplerate();
	post("DSP on");
	post("Vectorsize: ", vs);
	post("Samplerate: ", sr);
}

// Generator operators are stateful
// we instantiate these like so:
@state cycle = new cycle();

// Get the next calculated value
// cycle~ has two inlets:
let wave = cycle.next(in1, 0);

// cycle~ has two outlets
out1 = wave[0] * in2;
out2 = wave[1];
out3 = pi; // pi is a constant
