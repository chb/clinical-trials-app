/**
 *  An object encapsulating trial search results.
 */
var TrialResult = can.Model.extend({
	
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
	reason: null,
	
	shown: false,
	shownForInterventions: false,
	shownForPhases: false,
	
	init: function(json) {
		this.trial = new Trial(json.trial);
		
		this.bind('shownForInterventions', function(ev, newVal, oldVal) {
			this.attr('shown', newVal && this.shownForPhases);
		});
		this.bind('shownForPhases', function(ev, newVal, oldVal) {
			this.attr('shown', newVal && this.shownForInterventions);
		});
	}
});
