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
		this.attr('trial', new Trial(json.trial));
		this.attr('tests', new TrialResultTest.fromJSON(json.tests))
		
		this.bind('shownForInterventions', function(ev, newVal, oldVal) {
			this.attr('shown', newVal && this.shownForPhases);
		});
		this.bind('shownForPhases', function(ev, newVal, oldVal) {
			this.attr('shown', newVal && this.shownForInterventions);
		});
	},
	
	/** Returns true if at least one test's status is "fail". */
	hasFail: function() {
		var tests = this.attr('tests');
		if (tests) {
			for (var i = 0; i < tests.length; i++) {
				if ('fail' == tests[i].status) {
					return true;
				}
			}
		}
		return false;
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
