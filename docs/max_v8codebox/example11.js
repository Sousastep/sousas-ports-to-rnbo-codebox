// declaring attributes in Javascript code.
// for any attribute that uses default getters and/or setters,
// it is important to declare the attribute using 'var' insetad of 'let'

var fluffy = 0;
declareattribute("fluffy", { style: "onoff", embed: 1, label: "Enable Fluffiness" });
	
var bunny = 74;
declareattribute("bunny", { setter : "setbunny", min: -3, max: 101, default: 74, type: "long" });

var bingo = "One";
declareattribute({ name: "bingo", style: "enum", enumvals: ["One", "Two", "Three"] });

// alternate enum index (use symbols in menu for setting an integer)
var bingoindex = 0;
declareattribute({ name: "bingoindex", style: "enumindex", enumvals: ["One", "Two", "Three"] });

var bongo = [ 1, 0, 0, 1];
declareattribute({ name: "bongo", style: "rgba" });

var boppy = [ 74 , 75 ];
declareattribute("boppy", { min: -3, max: 101, default: [ 74, 75 ], type: "long" });

// custom setter
function setbunny(v)
{
	bunny = v;
	post("I am setting bunny to: " + v + "\n");
}

// possible properties to pass in are:
// name : string
// getter : string
// setter : string
// embed : number/bool
// type: string ("long", "float", "symbol", "atom")
// size : number (for arrays...also implicit if default is an array)
// style : string ("onoff" for toggle display style, "enum" or "enumindex" for menu list, "rgba" for color)
// label : string
// category : string
// min : number
// max : number
// default : number, string, array
// invisible : number/bool
// steps : number
// enumvals : array of strings
// paint : number/bool