/**
 *  A trial.
 */
var Trial = can.Model.extend({
	findAll: 'GET /trials',
	eligibilityCriteria: 'GET /trials/{id}/criteria',
	
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
	
});
