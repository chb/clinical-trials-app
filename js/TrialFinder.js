/**
 *  An object encapsulating trial search results.
 */
var TrialFinder = can.Model.extend({
},
{
	status: null,
	patient: null,
	
	trials: [],
	interventions: [],
	phases: [],
	// `interventions` and `phases` needs: huid, name, num_results
	
	/// Search for trials for the given term
	find: function(patient, elem, evt) {
		var self = this;
		self.attr('status', "Searching...");
		
		var search = null;
		
		if (this.patient) {
			this.patient.save();
			search = this.patient.last_manual_search;
		}
		
		if (!search) {
			search = $('#manual_problem').val(); // element.val() || 
		}
		var url = '/trials?term=' + encodeURIComponent(search);
		console.log(url);
		
		$.ajax({url: url, type: 'GET', dataType: 'json'})
		.done(function(json, message, req) {
			self.attr('status', "Sorting...");
			if (json && 'trials' in json) {
				self.attr('trials', json['trials']);
			}
			
			self.attr('status', null);
		});
		
		// TODO: hide problem list
	},
});
