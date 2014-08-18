
var _intervention_map = {
	"Biological": "Drug/Biological",
	"Drug": "Drug/Biological",
};

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
		
		var arr = [];
		var assoc = {};
		for (var i = 0; i < this.results.length; i++) {
			var trial = this.results[i].trial;
			if (trial && trial.interventions) {
				for (var j = 0; j < trial.interventions.length; j++) {
					var inter = trial.interventions[j];
					if (inter in _intervention_map) {
						inter = _intervention_map[inter];
					}
					
					var exist = assoc[inter];
					if (exist) {
						exist.addMatch();
					}
					else {
						var ti = new TrialIntervention(inter);
						assoc[inter] = ti;
						arr.push(ti);
					}
				}
			}
		}
		
		this.attr('interventions', arr.sort(TrialGroupable.sortByName));
	},
	
	/// Collect trial phases from all the trials into a unique Array
	collectPhases: function() {
		if (this.phases && this.phases.length > 0) {
			return;
		}
		
		var arr = [];
		var assoc = {};
		for (var i = 0; i < this.results.length; i++) {
			var trial = this.results[i].trial;
			if (trial && trial.phases) {
				for (var j = 0; j < trial.phases.length; j++) {
					var phase = trial.phases[j];
					
					var exist = assoc[phase];
					if (exist) {
						exist.addMatch();
					}
					else {
						var ph = new TrialPhase(phase);
						assoc[phase] = ph;
						arr.push(ph);
					}
				}
			}
		}
		
		this.attr('phases', arr.sort(TrialGroupable.sortByName));
	},
});


var TrialGroupable = can.Model.extend({
	sortByName: function(a, b) {
		if (a.name > b.name)
			return 1;
		if (a.name < b.name)
			return -1;
		return 0;
	},
},
{
	name: null,
	huid: null,
	num_matches: 1,
	
	addMatch: function() {
		this.attr('num_matches', this.num_matches + 1);
	},
	
	toggle: function(self, elem, evt) {
	},
});

var TrialIntervention = TrialGroupable.extend({},
{
	init: function(name) {
		this.attr('name', name);
		this.attr('huid', 'intervention_' + this.name.replace(/\W\D/, '_'));
	},
	
	toggle: function(self, elem, evt) {
		console.log("Toggle intervention", this.name);
	},
});

var TrialPhase = TrialGroupable.extend({},
{
	init: function(name) {
		this.attr('name', name);
		this.attr('huid', 'phase_' + this.name.replace(/\W\D/, '_'));
	},
	
	toggle: function(self, elem, evt) {
		console.log("Toggle phase", this.name);
	},
});
