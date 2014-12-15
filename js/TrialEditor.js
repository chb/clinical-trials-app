/**
 *  Handles editing trial information.
 */
var TrialEditor = can.Construct.extend({
	singleton: function() {
		if (null === this._instance) {
			this._instance = new TrialEditor();
		}
		return this._instance;
	},
	_instance: null,
},
{
	trial: null,
	
	edit: function(trial) {
		this.done(this.trial);
		this.trial = trial;
		this.trial.attr('editing', true);
	},
	
	done: function(trial) {
		if (null !== this.trial && trial === this.trial) {
			this.trial.attr('editing', false);
			this.trial = null;
		}
	},
	
	save: function(saveTrial) {
		if (!this.trial || saveTrial !== this.trial || !this.trial.attr('editing')) {
			alert("Not currently editing this trial");
			return;
		}
		
		// save values
		var trial = this.trial;
		trial.allowEditing(false);
		$.putJSON('trials/' + this.trial._id + '/info', {
			'title': $('#edit_title').val(),
			'notes': $('#edit_notes').val(),
		})
		.done(function(json, status, xhr) {
			trial.updateFromInfo(json ? json.trial : null);
			trial.allowEditing(true);
		})
		.fail(function(xhr, status, error) {
			console.log('FAILED to save trial:', status, error);
			alert("Failed to save trial info: " + error);
			trial.allowEditing(true);
		});
		this.done(trial);
	}
});
