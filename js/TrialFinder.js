/**
 *  An object handling trial search.
 */
var TrialFinder = can.Model.extend({
},
{
	status: null,
	error: null,
	patient: null,
	
	// the result object will have `results`, `interventions` and `phases`.
	// `interventions` and `phases` needs: huid, name, num_results
	result: null,
	
	/// Search for trials for the given term
	find: function(patient, elem, evt) {
		var self = this;
		self.attr('status', "Searching...");
		self.attr('error', null);
		self.attr('result', null);
		
		var search = null;
		
		if (this.patient) {
			this.patient.save();
			search = this.patient.last_manual_search;
		}
		
		if (!search) {
			search = $('#manual_problem').val(); // element.val() || 
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
				if (json && 'results' in json) {
					self.attr('result', {
						'results': TrialResult.fromJSON(json['results']),
						'interventions': [],
						'phases': [],
					});
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
