[![Image](Codebox%20and%20Codebox~%20Reference%20_%20Cycling%20'74_files/c74-logo-fff_VQJR.svg)](https://rnbo.cycling74.com/)

#### Codebox

[#### Codebox Guides](https://rnbo.cycling74.com/learn/getting-started-with-codebox)

Constants

Operators

Stateful Operators

[Learn](https://rnbo.cycling74.com/learn)

[Explore](https://rnbo.cycling74.com/explore)

Reference

#### Object Reference

[Objects & Operators](https://rnbo.cycling74.com/objects)

[Codebox Operators](https://rnbo.cycling74.com/codebox)

#### API Reference

[C++ API Reference](https://rnbo.cycling74.com/cpp)

[JavaScript API Reference](https://rnbo.cycling74.com/js)

[Codebox](https://rnbo.cycling74.com/codebox)

[Codebox](https://rnbo.cycling74.com/codebox)

[### Codebox Guides](https://rnbo.cycling74.com/learn/getting-started-with-codebox)

Constants

Operators

Stateful Operators

# Codebox and Codebox~ Reference

codebox and codebox~ enable you to use rnboscript, a JavaScript-like scripting language, to implement DSP and event code directly inside of RNBO.

The`codebox` and `codebox~`objects use a JavaScript-like scripting language to implement DSP and event code directly inside of RNBO. The syntax is similar to the`codebox` in Gen, with some important differences.

Unline Gen, variables must be declared with *var, let,*or *const,*and functions must be declared with the *function* keyword. While this makes the RNBO codebox language *look* very similar to JavaScript, not all JavaScript features are supported. Overall, `codebox` is most like a super-powered `expr` object, rather than a replacement for the Max `js` object.

## [Basic Functionality](https://rnbo.cycling74.com/codebox?v=1.3.3#basic-functionality)

You can create and reference inlets and outlets using `in1`, `in2`, `out1`, `out2`, etc.

Image![basic.png](Codebox%20and%20Codebox~%20Reference%20_%20Cycling%20'74_files/basic_VQJR.png)

or in codebox~

Imagebascic-dsp.png

Referring to `in2` is sufficent to create a second inlet. When using`codebox` and not `codebox~`, any assignment to an outlet will cause an output on that outlet.

ImageScreen Shot 2022-06-27 at 2.57.49 PM.png

This will print 4 and then 5 whenever the codebox receives input at its first inlet. The codebox will always have a first inlet. As is often the case in Max, only the leftmost inlet is "hot". Sending a value to the first inlet will trigger output, while sending a value to the other inlets will instead simply update the internal value of `in2`, `in3`, etc. When working with `codebox~`, all outlets are always signals, and will output a signal vector every audio frame.

List are supported as well:

Imagelist-basic.png

You will have to use *listout* and *listin* identifiers to get accordingly typed inlets and outlets.

## [Declaring Variables](https://rnbo.cycling74.com/codebox?v=1.3.3#declaring-variables)

As mentioned, use *var*, *let*, and *const* to declare local variables. While you can re-assign the value of *var* and *let* variables, these updates will not persist between codebox calls—see `@state` below for more.

```rnbo
var myVar = 3;
var myLet = 4;
var myConst = 5;
```

You can use *const* values in parameter declarations. This includes globally-defined *const* values, like `PI`.

```rnbo
// User-defined constant
const myConst = 74;
@param({ min: 0, max : myConst}) myParam = 0;

// You can also use globally-defined params
@param({ min: 0, max : PI }) myOtherParam = 0;
```

## [Built-in Functions and Objects](https://rnbo.cycling74.com/codebox?v=1.3.3#built-in-functions-and-objects)

Codebox supports a subset of RNBO objects. Very simple objects, the ones that just wrap a stateless function call, are exposed as built-in functions in codebox. So one can write:

```rnbo
let car = cartopol(x, y);
```

This will have the same output as the `cartopol` object in RNBO. Some built-in functions return a number:

Imageoperators.png

Others return multiple values as an array:

Imageoperators-multi-return.png

RNBO objects with some internal state, like a `phasor` or a `cycle`, are exposed as codebox-supported objects. These must be created with `new` and given the `@state` decorator.

```javascript
@state myPhasor = new phasor();
```

These objects all have a `next` method, which returns the object's output while advancing its internal state by one sample. So calling `.next` repeatedly on a `phasor` will advance its internal phase.

```gen
// Passing a 1 to the next method is the same as setting the phasor's frequency to 1
// At 44.1 kHz, this advances the internal phase by 0.000022675736961
myPhasor.next(1); // 0.000022675736961
myPhasor.next(1); // 0.000045351473923
myPhasor.next(1); // 0.000068027210884
```

The cycle and phasor objects are very common:

Imagephasor_cycle_02.png

More complex RNBO objects like `granulator~` are not currently supported. Built-in functions and codebox-supported RNBO objects are listed on this page's lefthand sidebar as operators and stateful operators.

## [Looping and Branching](https://rnbo.cycling74.com/codebox?v=1.3.3#looping-and-branching)

Most of the control flow keywords from C++ and JavaScript are supported. The looping constructs `for` and `while` can be used in the basic way:

```rnbo
for (let i = 0; i < 10; i++) {
  post(i);
}

let j = 1;
while (j) {
  post(j);
  j = 0;
}
```

However, language-specific paradigms like `for..in` are not currently supported. You can also use branching constructs like `if..else` and `switch`.

```rnbo
let i = 1;
if (i) {
  post("I was right!");
} else {
  post("I was wrong...");
}

const a = 0;
switch (a) {
  case 0:
    post("a was zero");
    break;
  default:
    post("a was something else");
}
```

These keywords should follow the C++ and JavaScript specification, so refer to the documentation for those languages for a more thorough discussion of how to use these keywords.

## [Functions](https://rnbo.cycling74.com/codebox?v=1.3.3#functions)

Function declarations are supported using the `function` keyword.

Imagefunction.png

A function can return multiple values by returning an array.

Imagefunctions.png

You could also write:

```rnbo
function bla(foo)
⁠{
⁠    return [foo + 1, 2];
⁠}
⁠out1 = bla(1)[0] + in1;
```

The return type of a function is automatically deduced (it will be a list, if you use an array expression as a return type). Anonymous functions, like you might create with big-arrow notation in JavaScript or C++ lambdas, are not currently available.

## [Special Functions](https://rnbo.cycling74.com/codebox?v=1.3.3#special-functions)

There are currently three special functions:

- *init* is called once, on object creation (either manual or by loading it with a patcher) - you can use it to initialize state variables but you **must not** access buffer or data objects at this state, they might not yet be allocated
- *startup* is called once after all objects are created and data and buffer objects are allocated
- *dspsetup* is only available in `codebox~` where it will be called each time audio is turned on in Max (which is basically every time the audio state is toggled, or the sample rate or vector size is changed).
- *post* prints to the Max console. It can print numbers or constant strings.

ImageScreenshot 2022-05-31 at 19.15.14.png

## [Inlet Functions](https://rnbo.cycling74.com/codebox?v=1.3.3#inlet-functions)

Sometimes you want a function to be called whenever data comes into one of the inlets that is not the first one. This can be achieved through an inlet function. In this example, the function is called whenever a list is received at the second inlet:

ImageScreenshot 2022-05-31 at 19.28.30.png

This will run the function called `listin2` whenever the second inlet receives any input. This function will run in addition to setting the value of `listin2`, so you can think of the function as a side effect of setting `listin2`.

## [State and Params](https://rnbo.cycling74.com/codebox?v=1.3.3#state-and-params)

In order to re-use state after codebox has triggered some output, use the `@state` decorator. This will create state that persists across the lifetime of the codebox object.

Imagestate2.png

While you can use the `let` keyword to declare variables that can be used during codebox execution, these are not reusable state variables. For example, something like this will not work:

ImageScreen Shot 2022-06-27 at 3.50.57 PM.png

Finally, you can use the `@param` decorator to introduce a state variable that can be set via a message:

ImageScreen Shot 2022-06-28 at 2.05.51 PM.png

The `@param` decorator function is the only place in the codebox language that you can use a JavaScript-style object. The function takes as its one and only argument an object describing how the parameter should behave. It can take the keys `min` and `max` to define a range, or it can take the key `enum`, followed by a list of enumerated values. Enumerated parameters always start at index 0.

```rnbo
@param({ enum: [ "saw", "sine", "square", "triangle"] }) myParam = 0;
```

Following the decorator function, the parameter must be given a name and an initial value.

## [Buffers](https://rnbo.cycling74.com/codebox?v=1.3.3#buffers)

A codebox's state can also hold a reference to a buffer. This may be sized, unsized, named, or anonymous. For example, this creates a reference to a buffer "mybuf" defined outside of the codebox.

Imagebuffers.png

This will create an internal, anonymous buffer, that will always be twice the sample rate in size:

Imagebuffers2.png

**note:** the only two supported operators in size expressions are *samplerate()* and *vectorsize()*.

This will create a named buffer (which will also be available in Max) of size 44100:

Imagebuffers3.png

You can see too how we use `poke` and `peek` to set and get sample values. Reading and writing in buffers does bound checking, so you cannot read or write out of bounds. As you can see, some built-in functions take a buffer as their argument. The list of operators in the left sidebar includes such functions.

## [Types](https://rnbo.cycling74.com/codebox?v=1.3.3#types)

It is possible to give a codebox variable an explicit type.

Imagetypes.png

This is usually unnecessary, but sometimes necessary (for example) when strict typing requires that a number have an integer type.

```rnbo
@state myarray = new FixedIntArray(100);

let a = 0;
out1 = myarray[a]; // throws an error--a must be an integer

let b: Int = 0;
out1 = myarray[b]; // no error
```

Explicit types also allow you to declare a variable without setting it, if you want to. For example:

```rnbo
let x: list;
x = [];
out1 = x.concat([3]);
```

Without the explicit `list` type, codebox will assume that `x` is a number and will throw an error. Valid types include `number`, `list`, and `Int`.

Finally, you may find that your codebox fails to compile sometimes in cases where you're using a custom function that returns a list. Sometimes the compiler can infer the return type of a function, and the explicit `list` type is unnecessary. However, you can always add the explicit return type to clear up the error if you're seeing a problem.

```rnbo
// You may find that functions like this fail to compile
function myListFunc() {
   return [1, 2];
}

// Make the return type explicit to clear the error
function myListFunc(): list {
   return [1, 2];
}
```

## [Fixed Arrays](https://rnbo.cycling74.com/codebox?v=1.3.3#fixed-arrays)

Lists defined with square brackets like `[]` do not have a fixed size. Adding and removing elements from the list changes the size of the list. Sometimes it's convenient to work with fixed size arrays. These arrays are highly efficient, especially when it comes to setting and getting values from the array at a particular index.

You can initialize a **fixed size array** using the `new` keyword. A single argument will create a one-dimensional array. You can also initialize the array using a list.

```rnbo
// Create a fixed array of integers with size 100
@state a = new FixedIntArray(100);

// Create a fixed array of floats with initial values 0.0, 1.0, 2.0
@state a = new FixedFloat32Array([0.0, 1.0, 2.0]);
```

One thing that's particularly useful is that with fixed arrays, you can create multidimensional arrays that you can index along multiple dimensions. For example:

```rnbo
// Create a fixed array of integers with size 100
@state a = new FixedIntArray(100);

// Create a fixed array of 32-bit floats with width 10 and height 20 for total size 200
@state b = new FixedFloat32Array(10, 20);

// Create a fixed array of samples (float or double depending on export and host configuration)
//   with width 10, height 5, and depth 12 for total size 600
@state c = new FixedSampleArray(10, 5, 12);

// Fill each array with random values
@state n = new noise();

// If you don't put this in the init function, then it will be called once per audio frame
function init() {
  for (let i = 0; i < 100; i++) {
    a[i] = n.next();
  }

  for (let i = 0; i < 10; i++) {
    for (let j = 0; j < 20; j++) {
      b[i][j] = n.next();
    }
  }

  for (let i = 0; i < 10; i++) {
    for (let j = 0; j < 5; j++) {
      for (let k = 0; k < 12; k++) {
        c[i][j][k] = n.next();
      }
    }
  }
}
```

Here's another example, creating a `codebox~` that fills up an array with a sinusoid, 180 degrees out of phase in each channel.

```rnbo
const arrayLength = 2048;

@state x = new FixedSampleArray(2, arrayLength);
@state index: Int = 0;

function init() {
	for (let c = 0; c < 2; c++) {
		for (let i = 0; i < arrayLength; i++) {
			let f: number = arrayLength;
			x[c][i] = sin(PI * (2 * i / arrayLength + c));
		}
	}
}

index++;
if (index > arrayLength) index = 0;
out1 = x[0][index];
out2 = x[1][index];
```

The following types are supported for fixed size arrays:

```
Name ------------------ C Type --------------- Description
FixedInt8Array -------- int8_t --------------- Signed 8-bit integer
FixedUint8Array ------- uint8_t -------------- Unsigned 8-bit integer
FixedInt16Array ------- int16_t -------------- Signed 16-bit integer
FixedUint16Array ------ uint16_t ------------- Unsigned 16-bit integer
FixedInt32Array ------- int32_t -------------- Signed 32-bit integer
FixedUint32Array ------ uint32_t ------------- Unsigned 32-bit integer
FixedFloat32Array ----- float ---------------- 32-bit float
FixedFloat64Array ----- double --------------- 64-bit float
FixedBigInt64Array ---- int64_t -------------- Signed 64-bit integer
FixedBigUint64Array --- uint64_t ------------- Unsigned 64-bit integer
FixedSampleArray ------ float or double ------ The same type as an audio sample
FixedNumberArray ------ multiple ------------- Value may change depending on the
                                               circumstances in which code is generated
                                               and used. Use this if you don't need a
                                               particular number type.
FixedIntArray --------- int ------------------ Signed integer, equivalent to C int
FixedFloatArray ------- float ---------------- Equivalent to C float
FixedDoubleArray ------ double --------------- Equivalent to C double
```

## [Sample Accuracy](https://rnbo.cycling74.com/codebox?v=1.3.3#sample-accuracy)

A `codebox~` object can also accept a number message at any of its inlets.

Imageoperators.png

If only messages and no signals are connected to the inlet of a `codebox~`, then the inlet value (in1, in2, etc.) will only update once every signal vector. This is much more efficient, though it does mean that the value cannot change during the computation of an audio block.

## [List Functions](https://rnbo.cycling74.com/codebox?v=1.3.3#list-functions)

List functions in RNBO fall into two categories: global list functions and methods on a list object.

```rnbo
// Global list function listrot -- this works
let mylist = [1, 2, 3];
let rotated_list = listrot(mylist, 1); // output [3, 1, 2]

// This does not work
let a = [];
let b = concat(a, [4, 5]); // no global built-in function concat

// Function concat is a method on a list object
let c = [];
let d = c.concat([4, 5]); // does not modify c, returns a new list
```

Global list functions all have a RNBO object equivalent. For example, the object [**list.delace**](https://rnbo.cycling74.com/objects/ref/list.delace) is equivalent to the global codebox function **listdelace**. For all of these objects, the function inside codebox is simply the name of the RNBO object without the period after the word "list".

The following is a list of methods on a list object. Some of these have a RNBO object equivalent, for example the `slice` method is equivalent to the RNBO object [**list.slice**](https://rnbo.cycling74.com/objects/ref/list.slice). Many of the list functions that are currently supported are modeled after their JavaScript equivalent. Where possible, these are identical. For a full discussion of the behavior of each function, see the JavaScript documentation of that function.

- [**push**](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/push) - Adds an element to a list, returning the length of the list.
- [**pop**](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/pop) - Removes the last element from a list and returns that element.
- [**shift**](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/shift) - Removes the first element from a list and returns that element
- [**concat**](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/concat) - Merges two lists. Does not modify either list, but returns a new list.
- [**fill**](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/fill) - Changes all list elements to a static value. Returns the modified list.
- [**unshift**](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/unshift) - Adds one or more elements to the beginning of a list, returning the length of the new list.
- [**splice**](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/splice) - Changes a list by removing or replacing elements, or adding new element
- [**slice**](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/slice) - Returns a copy of part of a list.
- [**includes**](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/includes) - Determines if a list includes a certain value among its entries.
- [**indexOf**](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/indexOf) - Returns the first index at which a given element can be found in a list, or -1 if the element cannot be found.
- [**reverse**](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/reverse) - Reverses a list in place, modifying the list.

Quick Links

[Resources](https://rnbo.cycling74.com/resources)

[Versions](https://rnbo.cycling74.com/versions)

Other Resources

[cycling74.com](https://cycling74.com/)

[RNBO FAQ](https://support.cycling74.com/hc/en-us/sections/360009052113-RNBO)

[Beta Forum](http://beta.cycling74.com/)

[https://www.facebook.com/cycling74/](https://www.facebook.com/cycling74/)

[https://twitter.com/cycling74](https://twitter.com/cycling74)

[https://www.instagram.com/c74connect/](https://www.instagram.com/c74connect/)

[https://www.youtube.com/channel/UCqSNdDNH1Iq25ucNmqaGvig](https://www.youtube.com/channel/UCqSNdDNH1Iq25ucNmqaGvig)

[Terms and Conditions](https://cycling74.com/terms-and-conditions)

[Privacy Policy](https://cycling74.com/privacy-policy)

[© 2022 Cycling '74](http://cycling74.com/)