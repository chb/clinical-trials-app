/**
 *  An object encapsulating trial search results.
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
	trial: null,
	tests: null,
	
	shown: false,
	shownForInterventions: false,
	shownForPhases: false,
	
	init: function(json) {
		this.attr('trial', new Trial(json.trial));
		this.attr('tests', new TrialResultTest.fromJSON(json.tests))
		
		this.bind('shownForInterventions', function(ev, newVal, oldVal) {
			this.attr('shown', newVal && this.shownForPhases);
		});
		this.bind('shownForPhases', function(ev, newVal, oldVal) {
			this.attr('shown', newVal && this.shownForInterventions);
		});
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
