// state is useful for preserving initial values
// and keeping values in memory (similar to history in gen)
@state freq = 110;
// param can be used to create a named parameter,
// just like the rnbo param object, with arguments
@param({ min: 1, max: 4, steps: 4 }) mode = 4;
@param gain = 0; // or without
	
// rnbo codebox supports switch statements
switch(mode)
{
    case 1:
		freq += in1 / samplerate(); // increment
        break;
    case 2:
		freq -= in1 / samplerate(); // decrement
        break;
    case 3:
        freq += pow(in1 / samplerate(), 2); // increment slowly
		break;
    case 4:
        freq += 0; // freeze the value
        break;
    default:
        break;
}
freq = clamp(freq, 33, 600);
@state saw = new saw();
@state filt = new reson();

out1 = filt.next(saw.next(freq, 0)[0], freq * 4, 0.5) * gain; 
out2 = freq;
out3 = mode;