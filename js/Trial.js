/**
 *  A trial.
 */
var Trial = can.Model.extend({
	findAll: 'GET /trials',
	
	/// Geocode an array of trials.
	geocode: function(trials, to_location) {
		for (var i = 0; i < trials.length; i++) {
			trials[i].geocode(to_location);
		}
	},
	
	fromJSON: function(array) {
		if (!array) {
			return null;
		}
		
		var trials = [];
		for (var i = 0; i < array.length; i++) {
			trials.push(new Trial(array[i]));
		}
		return trials;
	},
},
{
	interventions: null,
	phases: null,
	
	init: function(json) {
		this.updateFromInfo()
		
		if (this.phases) {
			this.attr('phasesFormatted', $.makeArray(this.phases).sort().join(', '));
		}
		
		// "fix" outcomes
		if (this.attr('primary_outcome')) {
			for (var i = 0; i < this.attr('primary_outcome').length; i++) {
				var out = this.attr('primary_outcome')[i];
				if ('safety_issue' in out) {
					out.attr('safety_issue', ('Yes' == out['safety_issue']));
				}
			}
		}
		if (this.attr('secondary_outcome')) {
			for (var i = 0; i < this.attr('secondary_outcome').length; i++) {
				var out = this.attr('secondary_outcome')[i];
				if ('safety_issue' in out) {
					out.attr('safety_issue', ('Yes' == out['safety_issue']));
				}
			}
		}
	},
	
	
	// MARK: Local Trial Info
	
	updateFromInfo: function(info) {
		if (info) {
			this.attr('info', info);
		}
		this.attr('mainTitle', (this.info && this.info.title) ? this.info.title : this.title);
	},
	
	/** Toggles "edit_title" content with the original title and whatever was in there before. */
	previewTitle: function(ctx, elem, event) {
		var field = $('#edit_title');
		if (field.val() == this.title) {
			field.val(this.attr('previousTitle'));
		}
		else {
			this.attr('previousTitle', field.val());
			field.val(this.title);
		}
	},
});
