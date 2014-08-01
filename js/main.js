/**
 *  Called when the DOM is ready, this function starts loading patient data.
 */
function initApp() {
	// hide the patient selector if in an iframe
	if (window != window.top) {
		$('#back_to_patient').hide();
	}
	
	// launch the app
	can.view('patient_tmpl', {
		patient: Patient.findOne({id: 'x'}),
		last_manual_search: "Rheumatoid Arthritis",
	})
	.then(function(frag) {
		$("#app").html(frag);
	});
}



/**
 *  Generic AJAX loader.
 */
 function loadJSON(url, success_func, error_func) {
	$.ajax({
		'url': url,
		'dataType': 'json'
	})
	.always(function(obj1, status, obj2) {
		if ('success' == status) {
			if (success_func) {
				success_func(obj1, status, obj2);
			}
			else {
				console.warn('Successfully loaded', url, 'but no success func is set')
			}
		}
		else {
			console.error('ERROR loading URL:', url, 'RETURNED', obj1, status, obj2);
			if (success_func) {
				error_func(obj1, status, obj2);
			}
		}
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
		for(var i = 0; i < this.length; i++) {
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

