// These operators are drawn from objects released in Max 8.3
@state what = new what()
@state updown = new updown()
@state where = new where()
@state swing = new swing()
@state subdiv = new subdiv()

let what_out = what.next(in1, [0.0, 0.5], 0, 0)
let what_trigger = what_out[0]
let what_index = what_out[1]
out1 = what_trigger
out2 = what_index

out3 = updown.next(in1, 30, 30, 0.717)

let where_out = where.next(in1)
let where_elapsed = where_out[0]
let where_remaining = where_out[1]
out4 = where_elapsed
out5 = where_remaining

let swing_out = swing.next(in1, 0.7, 0)
let swing_sig = swing_out[0]
let swing_step = swing_out[1]
out6 = swing_sig
out7 = swing_step

subdiv.setPattern([0.5, 1.0]);
subdiv.setProb([6, 1]);
let subdivision = subdiv.next(in1, 6, 0, 1, 0)

out8 = subdivision[0] // phasor output is the first
out9 = subdivision[1] // step number is the second
