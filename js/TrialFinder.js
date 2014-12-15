/**
 *  An object handling trial search.
 */
var TrialFinder = can.Model.extend({
},
{
	patient: null,
	
	// the result object is a `TrialFinderResult` instance
	result: null,
	
	/// Search for trials for the given term
	find: function(patient, elem, evt) {
		var self = this;
		self.attr('status', "Searching...");
		self.attr('error', null);
		self.attr('result', null);
		
		$.getJSON('/find', {'condition': 'Breast Cancer'})
		.always(function(json, message, req) {
			
			// success: instantiate TrialResult objects
			if ('success' == message) {
				self.attr('status', "Sorting...");
				if (json) {
					var result = new TrialFinderResult(json);
					self.attr('result', result);
					self.attr('complete', true);
				}
			}
			else {
				self.attr('error', "Error: " + req.toString());
			}
			self.attr('status', null);
		});
	},
});
