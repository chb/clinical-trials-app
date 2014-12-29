
var _intervention_map = {
	"Biological": "Drug/Biological",
	"Drug": "Drug/Biological",
	"Behavioral": "Behavioral/Other",
	"Other": "Behavioral/Other",
};


/**
 *  An object handling the overall trial search result.
 */
var TrialFinderResult = can.Model.extend({
},
{
	results: null,
	showSuggested: true,
	numSuggested: "~",
	showEligible: true,
	numEligible: "~",
	showIneligible: false,
	numIneligible: "~",
	numShown: 0,
	numShownTitle: null,		// cannot check for "numShown == 1" in Mustache
	
	// `interventions` and `phases` are TrialGroupable subclasses
	interventions: null,
	phases: null,
	
	/** Instantiate from an array of results. */
	init: function(json) {
		if (!json) {
			return null;
		}
		
		// fill properties
		this.attr('results', TrialResult.fromJSON(json['results']));
		this.countResults();
		this.collectInterventions();
		this.collectPhases();
		this.updateTrialShownState();
	},
	
	countResults: function() {
		var sugg = 0;
		var elig = 0;
		var inelig = 0;
		for (var i = 0; i < this.results.length; i++) {
			if ('ineligible' == this.results[i].overallStatus()) {
				inelig++;
			}
			else {
				elig++;
			}
		}
		this.attr('numSuggested', sugg);
		this.attr('numEligible', elig);
		this.attr('numIneligible', inelig);
	},
	
	/** Collect interventions from all the trials into a unique Array. */
	collectInterventions: function() {
		if (this.interventions && this.interventions.length > 0) {
			return;
		}
		
		var arr = [];
		var assoc = {};
		for (var i = 0; i < this.results.length; i++) {
			var trial = this.results[i].trial;
			if (trial && trial.interventions) {
				var did_count = [];			// collect counted interventions because we map, avoiding double counts
				for (var j = 0; j < trial.interventions.length; j++) {
					var inter = trial.interventions[j];
					if (inter in _intervention_map) {
						inter = _intervention_map[inter];
					}
					if (did_count.contains(inter)) {
						continue;
					}
					did_count.push(inter);
					
					var exist = assoc[inter];
					if (!exist) {
						exist = new TrialIntervention(null, inter);		// cannot supply "this" in a constructor??
						exist.parent = this;							// workaround
						assoc[inter] = exist;
						arr.push(exist);
					}
				}
			}
		}
		
		if (arr.length > 0) {
			this.attr('interventions', arr.sort(TrialGroupable.sortByName));
		}
	},
	
	/** Collect trial phases from all the trials into a unique Array. */
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
					if (!exist) {
						exist = new TrialPhase(null, phase);
						exist.parent = this;
						assoc[phase] = exist;
						arr.push(exist);
					}
				}
			}
		}
		
		this.attr('phases', arr.sort(TrialGroupable.sortByName));
	},
	
	
	toggleShowSuggested: function() {
		this.attr('showSuggested', !this.showSuggested);
		this.updateTrialShownState();
	},
	
	toggleShowEligible: function() {
		this.attr('showEligible', !this.showEligible);
		this.updateTrialShownState();
	},
	
	toggleShowIneligible: function() {
		this.attr('showIneligible', !this.showIneligible);
		this.updateTrialShownState();
	},
	
	/** Updates the `shownForXY` property on the result instances. */
	updateTrialShownState: function() {
		var shownIntv = $.map(this.interventions, function(item, idx) {
			return item.active ? item.name : null;
		});
		var shownPhs = $.map(this.phases, function(item, idx) {
			return item.active ? item.name : null;
		});
		
		var numInterventions = {};
		var numPhases = {};
		var showPhases = false;
		var shown = 0;
		for (var i = 0; i < this.results.length; i++) {
			var result = this.results[i];
			result.attr('shownForInterventions', false);
			result.attr('shownForPhases', false);
			var trial = result.trial;
			
			// update shown status based on eligibility status
			if (trial && trial.status) {
				if ('suggested' == trial.status) {
					result.attr('shownForStatus', this.showSuggested);
				}
				else if ('eligible' == trial.status) {
					result.attr('shownForStatus', this.showEligible);
				}
				else if ('ineligible' == trial.status) {
					result.attr('shownForStatus', this.showIneligible);
				}
				else {
					console.warn('Trial has an unknown status:', trial.status);
					result.attr('shownForStatus', true);
				}
			}
			else {
				console.error('No trial status, or worse: no trial', trial, trial ? trial.status : undefined);
			}
			
			// update shown status based on interventions 
			if (trial && trial.interventions) {
				for (var j = 0; j < trial.interventions.length; j++) {
					var inter = trial.interventions[j];
					inter = inter in _intervention_map ? _intervention_map[inter] : inter;
					result.attr('shownForInterventions', result.shownForInterventions || shownIntv.indexOf(inter) >= 0);
					
					if (result.shownForStatus) {
						var exist = numInterventions[inter] || 0;
						numInterventions[inter] = exist + 1;
					}
				}
			}
			
			// update shown status based on phase
			if (trial && trial.phases) {
				for (var j = 0; j < trial.phases.length; j++) {
					var phase = trial.phases[j];
					result.attr('shownForPhases', result.shownForPhases || shownPhs.indexOf(phase) >= 0);
					
					if (result.shownForStatus && result.shownForInterventions) {
						var exist = numPhases[phase] || 0;
						numPhases[phase] = exist + 1;
						showPhases = true;
					}
				}
			}
			
			// count
			if (result.shown) {
				shown++;
			}
		}
		this.attr('numShown', shown);
		if (shown > 1) {
			this.attr('numShownTitle', shown + " Trials");
		}
		else {
			this.attr('numShownTitle', (shown > 0) ? "1 Trial" : null);
		}
		
		// update intervention and phase counts
		for (var i = 0; i < this.interventions.length; i++) {
			var intervention = this.interventions[i];
			intervention.attr('numMatches', numInterventions[intervention.name] || 0);
		}
		for (var i = 0; i < this.phases.length; i++) {
			var phase = this.phases[i];
			phase.attr('numMatches', numPhases[phase.name] || 0);
		}
		
		this.attr('showPhases', showPhases);
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
	parent: null,
	name: null,
	huid: null,
	active: false,
	numMatches: 0,
	
	addMatch: function() {
		this.attr('numMatches', this.numMatches + 1);
	},
});

var TrialIntervention = TrialGroupable.extend({},
{
	init: function(parent, name) {
		//this.attr('parent', parent);		// supplying `this` in a constructor trips up Can.js
		this.attr('name', name);
		this.attr('huid', 'intervention_' + this.name.replace(/\W\D/, '_'));
	},
});

var TrialPhase = TrialGroupable.extend({},
{
	init: function(parent, name) {
		//this.attr('parent', parent);
		this.attr('name', name);
		this.attr('huid', 'phase_' + this.name.replace(/\W\D/, '_'));
		this.attr('active', true);
	},
});
