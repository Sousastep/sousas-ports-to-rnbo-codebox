// old way: using names and Dict objects

function bang()
{
	let testy = {};
	testy.bubble = "tea";
	testy.age = 74;
	testy.more = { status : "on", pending : 0 };
	

	let d = new Dict();
	d.parse(JSON.stringify(testy));

	outlet(0, "dictionary", d.name);
}

function dictionary(name)
{
	let d1 = new Dict(name);
	let d2 = new Dict();
	
	d2.set("a", d1.get("a"));
	d2.set("b", d1.get("b"));
	d2.set("x", "marks the spot");	
	
	outlet(0, "dictionary", d2.name);
}