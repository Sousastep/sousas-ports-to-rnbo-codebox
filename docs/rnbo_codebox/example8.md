@state phasor = new phasor();
let phasorValue = phasor.next(in1);

let w = in2;
let x = in3;
let y = in4;
let z = in5;

// interpolation
let cosinterp = cosineinterp(phasorValue, x, y);
let cubeinterp = cubicinterp(phasorValue, w, x, y, z);
let lerp = linearinterp(phasorValue, x, y);
let splerp = splineinterp(phasorValue, w, x, y, z);

// or using the interp operator, set the method using the option
// linear | cubic | spline | cosine | step | none (linear)
let interp_op = interp(phasorValue, w, x, y, z, {interp: "spline"});
out1 = phasorValue;
out2 = interp_op;
out3 = cosinterp;
out4 = cubeinterp;
out5 = lerp;