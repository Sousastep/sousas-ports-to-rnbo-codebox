// v8 has some impressive optimizations as compared with our older engine (2/2)

'use strict';

var LOOP_ITERATIONS = 1000;
var ARRAY_SIZE = 4096;

function bang() {
 const input = new Array(ARRAY_SIZE);
  for (var i=0; i<ARRAY_SIZE; i++) {
    input[i] = 74.;
  }
  
  post("starting benchmark\n");
  var starttime = Date.now();
  var val = 0;
  for (var i=0; i<LOOP_ITERATIONS; i++) {
    for (var j=0; j<ARRAY_SIZE; j++) {
      val += input[j];
    }
  }
  var elapsedtime = Date.now() - starttime;
  post("benchmark results: " + LOOP_ITERATIONS + " iterations in " + elapsedtime + " ms\n");
  post("arrray accumulation is: " + val +"\n")
}