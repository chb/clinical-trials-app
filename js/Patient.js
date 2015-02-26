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
	}
});
