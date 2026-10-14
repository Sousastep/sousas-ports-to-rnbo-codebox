inlets = 2;
let values = [ 0., 0.];

function bang()
{
	outlet(0, values[0] + values[1]);
}

function msg_float(val)
{
	values[inlet] = val;
	
	// could instead always call bang 
	// to output on any input
	if (inlet == 0) {
		bang();
	} 
}