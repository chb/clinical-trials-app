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
		this.attr('canEdit', true);
		this.updateFromInfo(json.info)
		
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
		this.attr('mainTitle', (info && info.title) ? info.title : this.title);
	},
	
	edit: function() {
		this.attr('editing', !this.attr('editing'));
	},
	
	allowEditing: function(flag) {
		this.attr('canEdit', flag);
	},
	
	save: function() {
		if (!this.attr('editing')) {
			alert("Not currently editing this trial");
			return;
		}
		
		// save values
		var self = this;
		this.allowEditing(false);
		$.putJSON('trials/' + this._id + '/info', {
			'title': $('#edit_title').val(),
			'notes': $('#edit_notes').val(),
		})
		.done(function(json, status, xhr) {
			self.updateFromInfo(json ? json.trial : null);
			self.allowEditing(true);
		})
		.fail(function(xhr, status, error) {
			console.log('FAILED to save trial:', status, error);
			alert("Failed to save trial info: " + error);
			self.allowEditing(true);
		});
		this.edit();
	},
});
