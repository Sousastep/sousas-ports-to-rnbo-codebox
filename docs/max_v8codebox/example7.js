// new way: using msg_dictionary and outlet_dictionary with automatic object conversion. similar approaches can be done with Max array and string objects

function bang()
{
	let testy = {};
	testy.bubble = "tea";
	testy.age = 74;
	testy.more = { status : "on", pending : 0 };
	
	outlet_dictionary(0, testy);
}

function msg_dictionary(o1)
{
	let o2 = {};
		
	o2.a = o1.a;
	o2.b = o1.b;	
	o2.x = "marks the spot";	
	
	outlet_dictionary(0, o2);
}

function msg_array(a)
{
	post(a + "is our converted JS array\n");
}

function msg_string(s)
{
	post(s + "is our converted JS string\n");
}