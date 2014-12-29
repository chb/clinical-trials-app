/**
 *  An object encapsulating matching results for one trial.
 */
var TrialResult = can.Model.extend(
{
	/// Instantiate from an array of results
	fromJSON: function(array) {
		if (!array) {
			return null;
		}
		
		var results = [];
		for (var i = 0; i < array.length; i++) {
			var result = new TrialResult(array[i]);
			results.push(result);
		}
		return results;
	},
},
{
	init: function(json) {
		this.attr('tests', new TrialResultTest.fromJSON(json.tests));
		this.attr('hasTests', this.tests && this.tests.length > 0);
		
		var trial = new Trial(json.trial);
		trial.attr('status', this.overallStatus());
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
	
	/** Returns true if at least one test's status is "fail". */
	overallStatus: function() {
		// if suggested...
		if (this.tests) {
			for (var i = 0; i < this.tests.length; i++) {
				if ('fail' == this.tests[i].status) {
					return 'ineligible';
				}
			}
		}
		return 'eligible';
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
