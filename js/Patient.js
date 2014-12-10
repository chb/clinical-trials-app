/**
 *  A patient.
 */
var Patient = can.Model.extend({
	id: '_id',
	findOne: 'GET /patients/{id}',
	update: 'PUT /patients/{_id}',
},
{
	init: function(json) {
		this.attr('hasConditions', this.conditions && this.conditions.length > 0);
	}
});
