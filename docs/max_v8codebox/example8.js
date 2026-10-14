// the v8 engine supports all sorts of newer developments from the let keyword to promises to arrow functions to classes to typed arrays, multiline strings, default args, and more

// the version of v8 we are bundling at the time of this writing is 10.1.69. This is essentially the language features available in Chrome 101, and node 18 (ES2022 plus some of ES2023).

// more info on ES6 and beyond: https://www.w3schools.com/js/js_es6.asp https://compat-table.github.io/compat-table/es6/

'use strict';


this.arrow = () => outlet(0, "I am an arrow function");

function bang() {
	let promise = Promise.resolve();

	promise.then(() => outlet(0, "promise done!"));

	outlet(0, "code finished"); // this alert shows first
}

// spread operator
function spread() {
	let a = [ "one", "two" ];
	let b = [ "three", "four", ...a];
	
	// multi-line strings and ${} to interpolate values
	let text = 
`let a = [ "one", "two" ];
let b = [ "three", "four", ...a];
b is ${b}
`
	post(text);
	
}

class foo {
	constructor(v) {
		this.v = v;
	}
	square() {
		return this.v*this.v;
	}
}

function class_example()
{
	let bar = new foo(3);
	post("3x3 = " + bar.square() + "\n");
}

function typedarray_example()
{
	let a = new Int32Array(arguments.length+1);
	let sum = 0;
	let i = 0;
	
	for (i = 0; i < arguments.length; i++) {
		a[i] = arguments[arguments.length-1-i];
		sum += a[i];
	}
	a[i] = sum;
	outlet(0, a);
}

function defaultarg(arg = 74) {
	post("my arg is " + arg + "\n");
	outlet(0, arg);
}