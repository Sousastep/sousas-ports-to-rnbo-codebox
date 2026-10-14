// Generator operators are stateful
// we instantiate these like so:
@state cycle = new cycle();
@state phasor = new phasor();
@state train = new train();
@state noise = new noise();
@state pink = new pink();
@state rand = new rand();
// antialiased generators: 
@state rect = new rect();
@state saw = new saw();
@state tri = new tri();

// Get the next calculated value
out1 = cycle.next(in1,0)[0];
out2 = phasor.next(in1);
out3 = train.next(in1, 0.5, 0.5);
out4 = noise.next();
out5 = pink.next();
out6 = rand.next(in1);
out7 = rect.next(in1, 0.5, 0)[0];
out8 = saw.next(in1, 0)[0];
out9 = tri.next(in1, 0.5, 0)[0];