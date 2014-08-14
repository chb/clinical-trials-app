/**
 *  An object handling trial search.
 */
var TrialFinder = can.Model.extend({
},
{
	status: null,
	error: null,
	patient: null,
	
	// the result object is a `TrialFinderResult` instance
	result: null,
	
	/// Search for trials for the given term
	find: function(patient, elem, evt) {
		var self = this;
		self.attr('status', "Searching...");
		self.attr('error', null);
		self.attr('result', null);
		
		var search = this.patient ? this.patient.last_manual_search: null;
		if (!search) {
			search = $('#manual_problem').val(); // element.val() || 
		}
		
		if (this.patient) {
			this.patient.attr('last_manual_search', search);
			this.patient.save();
		}
		
		$.ajax({
			url: '/find?term=' + encodeURIComponent(search),
			type: this.patient ? 'PUT' : 'GET',
			data: this.patient ? this.patient._data : null,
			dataType: 'json'
		})
		.always(function(json, message, req) {
			
			// success: instantiate TrialResult objects
			if ('success' == message) {
				self.attr('status', "Sorting...");
				if (json) {
					self.attr('result', new TrialFinderResult(json));
					self.attr('complete', true);
				}
			}
			else {
				self.attr('error', "Error: " + req.toString());
			}
			self.attr('status', null);
		});
		
		// TODO: hide problem list
	},
});
