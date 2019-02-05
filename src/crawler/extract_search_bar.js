// Attempts to identify a search form in the page
let getSearchForm = function(regex) {
	let forms = Array.from(document.getElementsByTagName("form"));

	for (let i=0; i<forms.length; i++) {
		let form = forms[i];
		// If the regex matches any of these attributes, we found the search form
		if (form.id.match(regex) != null || form.className.match(regex) != null || form.action.match(regex) != null || form.name.match(regex) != null || (form.hasAttribute("role") && form.attributes.role.value.match(regex) != null))
			return form;
	}

	return null;
}

// Attempts to identify a search form from the elements in the form
// This function is called when forms do not provide enough info to be identified as search forms
let getSearchHandlesFromChildren = function(regex) {
	let textBox = null;
	let button = null;
	let form = null;

	let forms = Array.from(document.getElementsByTagName("form"));

	for (let i=0; i<forms.length; i++) {
		// Check each element in each form individually
		for (let j=0; j<forms[i].length; j++) {
			let field = forms[i][j];
			// If the regex matches any of these attributes, we found the search text box
			if ((field.type == "text" || field.type == "search") && (field.id.match(regex) != null || field.className.match(regex) != null || field.title.match(regex) || field.value.match(regex) || field.placeholder.match(regex))) {
				textBox = field;
				form = forms[i];
				break;
			}
		}
	}

	if (form == null)
		return null;

	// TODO: this might fail in case of multiple buttons in the same form, since it returns the first one it finds
	for (let i=0; i<form.length; i++) {
		// Within the same form, get the search button
		if (form[i].tagName == "BUTTON" || (form[i].tagName == "INPUT" && form[i].type == "submit")) {
			button = form[i];
			break;
		}
	}

	// TODO: button is a 'a' element (doesn't appear in the form array)

	if (textBox != null && button != null)
		return [textBox.element, button.element];
	else if (textBox != null)
		// There are normal cases where there is no search button (the interface expects the user to click return)
		return textBox.element;
	else
		return null;

}

// Attempts to find a search text and button
// Returns an array [textBox, button]
let getSearchHandles = function() {
	let textBox = null;
	let button = null;
	let regex = /(.*search.*|.*srch.*|.*query.*)/i;
	// Get search form
	let searchForm = getSearchForm(regex);
	
	if (searchForm == null) {
		// We could not identify a search form
		// This code attempts to find information in the forms' children
		return getSearchHandlesFromChildren(regex);
	}
	// TODO: searchForm still null because the search box is not enclosed in a form element
	// In the meantime, return null
	if (searchForm == null)
		return null;

	// Found search form. Now extract text box and search button
	for (let i=0; i<searchForm.length; i++) {
		if (searchForm[i].type == "text" || searchForm[i].type == "search") {
			textBox = searchForm[i];
		}
		// TODO: this might fail in case of multiple buttons in the same form, since it returns the first one it finds
		if (searchForm[i].tagName == "BUTTON" || (searchForm[i].tagName == "INPUT" && searchForm[i].type == "submit")) {
			button = searchForm[i];
		}
	}

	// TODO: button is a 'a' element (doesn't appear in the form array)

	if (textBox != null && button != null)
		return [textBox.element, button.element];
	else if (textBox != null)
		// There are normal cases where there is no search button (the interface expects the user to click return)
		return textBox.element;
	else
		return null;
}

/** PSEUDO CODE **/
/*

keywords = {search, srch, query}

	get all forms in page
	for each form:
		search attributes for keywords: id, class, action, name, role
		if successful:
			get input of type text or search
			get button
	// we're here if nothing found
	for each form:
		get all inputs of type text or search
		for each input of type text or search:
			search attributes for keywords: id, class, value, title, placeholder
			if successful:
				get input
				get button within form


	special cases to consider:
		- searchbox not in a form
		- more than one button in the search form
		x form not identified by intuitive attribute values
		- form's children with no intuitive attribute values
		- button is an A element (doesn't appear in the form array)

*/