/**
 *  An object encapsulating matching results for one trial.
 */
var TrialResult = can.Model.extend(
{
	/// Instantiate from an array of results
	fromJSON: function(array, finder_result) {
		if (!array) {
			return null;
		}
		
		var results = [];
		for (var i = 0; i < array.length; i++) {
			var result = new TrialResult(array[i]);
			result.finder_result = finder_result
			results.push(result);
		}
		return results;
	},
},
{
	finder_result: null,
	
	init: function(json) {
		this.attr('tests', new TrialResultTest.fromJSON(json.tests));
		this.attr('hasTests', this.tests && this.tests.length > 0);
		this.attr('canEdit', true);
		
		this.attr('suggested', this.patient_info && this.patient_info.suggested);
		this.attr('status', this.overallStatus());
		this.bind('suggested', function(ev, newVal, oldVal) {
			this.attr('status', this.overallStatus());
		});
		
		var trial = new Trial(json.trial);
		this.attr('trial', trial);
		
		this.bind('shownForStatus', function(ev, newVal, oldVal) {
			this.attr('shown', newVal && this.shownForInterventions && this.shownForPhases)
		});
		this.bind('shownForInterventions', function(ev, newVal, oldVal) {
			this.attr('shown', newVal && this.shownForStatus && this.shownForPhases);
		});
		this.bind('shownForPhases', function(ev, newVal, oldVal) {
			this.attr('shown', newVal && this.shownForStatus && this.shownForInterventions);
		});
	},
	
	setCanEdit: function(flag) {
		this.attr('canEdit', flag);
	},
	
	edit: function() {
		TrialEditor.singleton().edit(this);
	},
	
	cancel: function() {
		TrialEditor.singleton().done(this);
	},
	
	save: function() {
		TrialEditor.singleton().save(this);
	},
	
	suggest: function() {
		this.attr('suggested', !this.suggested);
		this.finder_result.updateResultCount();
		this.putSuggested(true);
	},
	
	putSuggested: function(revert_on_fail, is_retry) {
		var self = this;
		$.putJSON('trials/' + this.trial._id + '/patient/' + this.finder_result.patient_id + '/info', {
			'suggested': this.suggested
		})
		.done(function(json, status, xhr) {
			self.updateFromPatientInfo(json);
		})
		.fail(function(xhr, status, error) {
			console.error('Failed to save trial patient info:', status, error, 'will retry:', !is_retry);
			
			if (!is_retry) {
				self.putSuggested(revert_on_fail, true)
			}
			else if (revert_on_fail) {
				this.attr('suggested', !this.suggested);
				this.finder_result.updateResultCount();
				alert("Failed to save trial patient info: " + error);
			}
		});
	},
	
	updateFromPatientInfo: function(info) {
		if (info && (!info.trial_id || info.trial_id == this.trial._id) && (!info.patient_id || info.patient_id == this.finder_result.patient_id)) {
			this.attr('patient_info', info);
		}
		else {
			console.error("Cannot update from patient info because of trial_id/patient_id mismatch:", info.trial_id, this.trial._id, info.patient_id, this.finder_result.patient_id)
		}
	},
	
	/** Returns "suggested", "eligible" or "ineligible", based on trial preferences and trial test status. */
	overallStatus: function() {
		if (this.suggested) {
			return 'suggested';
		}
		if (this.tests) {
			for (var i = 0; i < this.tests.length; i++) {
				if ('fail' == this.tests[i].status) {
					return 'ineligible';
				}
			}
		}
		return 'eligible';
	},
	
	/**
		Can be used to sort an array of TrialResult instances.
		@returns -1, 0 or 1, depending on how the receiver compares to the "other" instance
	 */
	compare: function(other) {
		if (this.status != other.status) {				// 1. sort by status
			if (this.suggested) {
				return -1;
			}
			if (other.suggested) {
				return 1;
			}
			if ('eligible' == this.status) {
				return -1;
			}
			return 1;
		}
		if (this.trial.title < other.trial.title) {		// 2. sort by title
			return -1;
		}
		return 1;
	}
});


/**
 *  One trial match test.
 */
var TrialResultTest = can.Model.extend(
{
	/// Instantiate from an array of tests
	fromJSON: function(array) {
		if (!array) {
			return null;
		}
		
		var tests = [];
		for (var i = 0; i < array.length; i++) {
			tests.push(new TrialResultTest(array[i]));
		}
		return tests;
	},
},
{
});
