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
			result.trials = Trial.fromJSON(result.trials);
			results.push(result);
		}
		return results;
	},
},
{
	
});
