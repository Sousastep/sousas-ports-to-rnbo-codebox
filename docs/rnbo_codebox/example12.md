// stateful operators need to be instantiated 
// using the @state decorator and the 'new' keyword
@state allpass = new allpass();
@state gatetotrig = new gatetotrig();
@state cycle = new cycle();

// then each state is processed 
// using the .next() method
var trig = gatetotrig.next(in1) * cycle.next(1, 0)[0];

// arguments can also be passed in to the .next() method
out1 = allpass.next({x: trig, delayTime: 100, gain: 0.95});
