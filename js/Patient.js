/**
 *  A patient.
 */
var Patient = can.Model.extend({
	id: '_id',
	findOne: 'GET /patients/{id}',
	update: 'PUT /patients/{_id}',
},
{
	findTrials: function(obj, element, evt) {
		this.save();
		var search = element.val() || this.last_manual_search || $('#manual_problem').val();
		Trial.searchFor(search, JSON.stringify(this._data))
		
		// TODO: hide problem list
	},
});
