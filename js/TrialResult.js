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
	init: function(json) {
		this.trial = new Trial(json.trial);
	}
});
