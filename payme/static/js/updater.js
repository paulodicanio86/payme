function output_text()
{
    var amount = document.getElementById('amount_id').value
    if (isNumber(amount))
    {
	amount = parseFloat(amount)
	if (isInt(amount*10.0) || isInt(amount))
	{
	    
	}
	else if (isInt(amount*100.0))
	{
	    amount = amount.toFixed(2)
	    //amount = calculate_charge(amount)
	    text = 'You will be charged: <i class="fa fa-gbp">'  + amount
	}
	else
	{
	    text = ' '
	}
    }
    else if (amount=='')
    {
	text = ' '
    }
    else
    {
	text = ' '
    }
    document.getElementById('amount_output_text').innerHTML = text

}

function isNumber(n) {
    return !isNaN(parseFloat(n)) && isFinite(n)
}

function calculate_charge(n)
{
    if (n < 100.0)
    {
	return (n + 3.50).toFixed(2)
    }
    else
    {
	n = n + (n * 0.035)
	return n.toFixed(2)
    }
}

function isInt(n) {
   return n % 1 === 0
}
