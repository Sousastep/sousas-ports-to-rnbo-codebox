function msg_array(a1)
{
	post(JSON.stringify(a1) + " is our converted JS array\n");
	
	// could do a shallow copy with spread operator, but not
	// necessary, because a1 is already a deep copy of input
	// let a2 = [...a1];  
	
	a1.push("five");
	
	outlet_array(0, a1);
}
