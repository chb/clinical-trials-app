/**
 *  Called when the DOM is ready, this function starts loading patient data.
 */
function initApp() {
	// hide the patient selector if in an iframe
	if (window != window.top) {
		$('#back_to_patient').hide();
	}
	
	// launch the app
	Patient.findOne({id: 'x'})
	.then(function(patient) {
		var finder = TrialFinder();
		finder.attr('patient', patient);
		
		// render the finder into the template
		$('#app').html(can.view('app_tmpl', {
			finder: finder,
		}));
		
		// search trials
		finder.find(patient);
	});
}


/*
 *  ----------------------------
 *  Extending Array capabilities
 *  ----------------------------
 */

Array.prototype.contains = function(obj) {
	return (this.indexOf(obj) >= 0);
};

if ( ! ('indexOf' in Array.prototype)) {
	Array.prototype.indexOf = function(obj) {
		for (var i = 0; i < this.length; i++) {
			if (this[i] == obj) {
				return i;
			}
		}
		
		return -1;
	};
}

Array.prototype.uniqueArray = function() {
	var uniq = {};
	var new_arr = [];
	for (var i = 0, l = this.length; i < l; ++i){
		if (uniq.hasOwnProperty(this[i])) {
			continue;
		}
		new_arr.push(this[i]);
		uniq[this[i]] = 1;
	}
	
	return new_arr;
};

function sortedKeysFromDict(dict) {
	var sorted = [];
	for (var key in dict) {
	    sorted[sorted.length] = key;
	}
	sorted.sort();
	return sorted;
}



/*
 *	-------------
 *	DOM Utilities
 *	-------------
 */
function sortChildren(parent, selector, sortFunc) {
	var items = parent.children(selector).get();
	items.sort(sortFunc);
	
	$.each(items, function(idx, itm) {
		parent.append(itm);
	});
}


function newUUID() {
	return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
		var r = Math.random()*16|0;
		var v = c == 'x' ? r : (r&0x3|0x8);
		return v.toString(16);
	});
}



/**
 *  Thanks Twitter, with this we can use console.xy without fear.
 */
if (!window.console) {
	(function() {
		var names = ["log", "debug", "info", "warn", "error", "assert", "dir", "dirxml", "group", "groupEnd", "time", "timeEnd", "count", "trace", "profile", "profileEnd"];
		var l = names.length;
		
		window.console = {};
		for (var i = 0; i < l; i++) {
			window.console[names[i]] = function() {};
		}
	}());
}

