function array(name)
{
	let a1 = new MaxArray();
	a1.name = name;

	let a2 = new MaxArray();
	
	for (let i = 0; i < a1.length; i++) {
		a2.append(a1.at(i));
	}
	a2.append("five");
	
	outlet(0, "array", a2.name);
}