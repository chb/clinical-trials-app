/**
 *  Handles editing trial/trial-patient information.
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
	result: null,
	
	edit: function(result) {
		this.done(this.result);
		this.result = result;
		this.result.attr('editing', true);
	},
	
	done: function(result) {
		if (null !== this.result && result === this.result) {
			this.result.attr('editing', false);
			this.result = null;
		}
	},
	
	save: function(saveResult) {
		if (!this.result || saveResult !== this.result || !this.result.attr('editing')) {
			alert("Not currently editing this trial");
			return;
		}
		
		var result = this.result;
		result.setCanEdit(false);
		var trial = result.trial;
		
		// grab DOM data now because we'll be setting "editing" to false during this run-loop
		var trial_info = {
			'title': $('#edit_title').val(),
			'notes': $('#edit_notes').val(),
		};
		var patient_info = {
			'notes': $('#edit_patient_notes').val(),
		};
		
		$.when(
			
			// save trial info data
			$.putJSON('trials/' + trial._id + '/info', trial_info)
			.done(function(json, status, xhr) {
				trial.updateFromInfo(json ? json.trial : null);
			})
			.fail(function(xhr, status, error) {
				console.error('Failed to save trial info:', status, error);
				alert("Failed to save trial info: " + error);
			}),
			
			// save trial patient info data
			$.putJSON('trials/' + trial._id + '/patient/' + result.finder_result.patient_id + '/info', patient_info)
			.done(function(json, status, xhr) {
				result.updateFromPatientInfo(json);
			})
			.fail(function(xhr, status, error) {
				console.error('Failed to save trial patient info:', status, error);
				alert("Failed to save trial patient info: " + error);
			})
		).done(function() {
			result.setCanEdit(true);
		})
		this.done(result);
	}
});
