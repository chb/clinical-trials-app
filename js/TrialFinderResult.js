/**
 *  An object handling the overall trial search result.
 */
var TrialFinderResult = can.Model.extend({
},
{
	// `interventions` and `phases` needs: huid, name, num_matches
	interventions: [],
	phases: [],
	
	/// Instantiate from an array of results
	init: function(json) {
		if (!json) {
			return null;
		}
		
		// fill properties
		var array = ('results' in json) ? json['results'] : [];
		this.results = TrialResult.fromJSON(array);
		this.collectInterventions();
		this.collectPhases();
	},
	
	/// Collect interventions from all the trials into a unique Array
	collectInterventions: function() {
		if (this.interventions && this.interventions.length > 0) {
			return;
		}
		
		var assoc = {};
		for (var i = 0; i < this.results.length; i++) {
			var trial = this.results[i].trial;
			if (trial && trial.interventions) {
				for (var j = 0; j < trial.interventions.length; j++) {
					var inter = trial.interventions[j];
					var exist = assoc[inter];
					
					if (exist) {
						exist.num_matches += 1;
					}
					else {
						var dict = {
							name: inter,
							huid: 'intervention_' + inter.replace(/\W\D/, '_'),
							num_matches: 0,
						};
						assoc[inter] = dict;
					}
				}
			}
		}
		
		// create array and sort by name
		var arr = [];
		for (var p in assoc) {
			arr.push(assoc[p]);
		}
		
		this.attr('interventions', arr.sort(function(a, b) {
			if (a.name > b.name)
				return 1;
			if (a.name < b.name)
				return -1;
			return 0;
		}));
	},
	
	/// Collect trial phases from all the trials into a unique Array
	collectPhases: function() {
		if (this.phases && this.phases.length > 0) {
			return;
		}
		
		var assoc = [];
		for (var i = 0; i < this.results.length; i++) {
			var trial = this.results[i].trial;
			if (trial && trial.phases) {
				for (var j = 0; j < trial.phases.length; j++) {
					assoc.push(trial.phases[j]);
				}
			}
		}
	},
});
