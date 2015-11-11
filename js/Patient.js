/**
 *  A patient.
 */
var Patient = can.Model.extend({
	id: '_id',
	findOne: 'GET /patient',
	update: 'PUT /patients/{_id}',
},
{
	init: function(json) {
		this.attr('hasConditions', this.conditions && this.conditions.length > 0);
		if (this.conditions) {
			for (var i = 0; i < this.conditions.length; i++) {
				if (this.conditions[i].mutations) {
					for (var j = 0; j < this.conditions[0].mutations.length; j++) {
						var display = "Unknown Mutation";
						switch (this.conditions[0].mutations[j].hgnc) {
							case 'HGNC:3430':   display = "HER-2";   break;
							case 'HGNC:3467':   display = "ESR1";    break;
							case 'HGNC:8910':   display = "PGR";     break;
						}
						this.conditions[0].mutations[j].attr('display', display);
					};
				}
			};
		}
	}
});
