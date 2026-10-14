// v8 has some new fast paths to set and get values in a Jitter Matrix using TypedArrays. 
// The typed array passed into the copyarraytomatrix or copymatrixtoarray function must match 
// the type and match the dimensions multiplied by planecount of the matrix. 

const mplanecount = 2;
const mwidth = 2000;
const mheight = 2000;


let fluffy = new JitterMatrix(mplanecount, "float32", mwidth, mheight);
let bunny = new Float32Array(mplanecount * mwidth * mheight); 

function oldschool()
{
	fluffy.clear();
	
	post("starting benchmark\n");
  	let starttime = Date.now();
 	for (let i = 0; i < mwidth; i++) {
		for (let j = 0; j < mheight; j++) {
			fluffy.setcell2d(i, j, i, j);
		}
	}

	let elapsedtime = Date.now() - starttime;
 	post("oldschool results: " + elapsedtime + " ms\n");
	
	outlet(0, "jit_matrix", fluffy.name);
}

function newschool()
{
	let k=0;
	
	fluffy.clear();

	post("starting benchmark\n");
  	let starttime = Date.now();
 	for (let i = 0; i < mwidth; i++) {
		for (let j = 0; j < mheight; j++) {
			bunny[k++] = i;
			bunny[k++] = j;
		}
	}
	fluffy.copyarraytomatrix(bunny);
	
	let elapsedtime = Date.now() - starttime;
 	post("newschool results: " + elapsedtime + " ms\n");
	
	outlet(0, "jit_matrix", fluffy.name);
 
}