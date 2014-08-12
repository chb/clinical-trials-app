function initApp(){window!=window.top&&$("#back_to_patient").hide(),Patient.findOne({id:"x"}).then(function(t){var i=TrialFinder();i.attr("patient",t),$("#app").html(can.view("trialresult_tmpl",{finder:i}))})}function loadJSON(t,i,n){$.ajax({url:t,dataType:"json"}).always(function(a,e,o){"success"==e?i?i(a,e,o):console.warn("Successfully loaded",t,"but no success func is set"):(console.error("ERROR loading URL:",t,"RETURNED",a,e,o),i&&n(a,e,o))})}function sortedKeysFromDict(t){var i=[];for(var n in t)i[i.length]=n;return i.sort(),i}function sortChildren(t,i,n){var a=t.children(i).get();a.sort(n),$.each(a,function(i,n){t.append(n)})}function newUUID(){return"xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g,function(t){var i=16*Math.random()|0,n="x"==t?i:3&i|8;return n.toString(16)})}function hideTooManyCategoryTags(t){var i=$(t),n=i.parent(),a=n.height();i.siblings().show().filter(".over_limit").hide(),i.hide();var e=n.height()-a;window.scrollBy(0,e)}function _toggleTrialLocationContact(t){var i=$(t),n=i.siblings(".loc_contact");n.is(":visible")?n.fadeOut("fast"):(n.show(),n.css("left",(i.outerWidth()-n.outerWidth())/2+i.position().left))}Array.prototype.contains=function(t){return this.indexOf(t)>=0},"indexOf"in Array.prototype||(Array.prototype.indexOf=function(t){for(var i=0;i<this.length;i++)if(this[i]==t)return i;return-1}),Array.prototype.uniqueArray=function(){for(var t={},i=[],n=0,a=this.length;a>n;++n)t.hasOwnProperty(this[n])||(i.push(this[n]),t[this[n]]=1);return i},window.console||!function(){var t=["log","debug","info","warn","error","assert","dir","dirxml","group","groupEnd","time","timeEnd","count","trace","profile","profileEnd"],i=t.length;window.console={};for(var n=0;i>n;n++)window.console[t[n]]=function(){}}();var Patient=can.Model.extend({id:"_id",findOne:"GET /patients/{id}",update:"PUT /patients/{_id}"},{}),TrialFinder=can.Model.extend({},{status:null,error:null,patient:null,result:null,find:function(t,i,n){var a=this;a.attr("status","Searching..."),a.attr("error",null),a.attr("result",null);var e=null;this.patient&&(this.patient.save(),e=this.patient.last_manual_search),e||(e=$("#manual_problem").val()),$.ajax({url:"/find?term="+encodeURIComponent(e),type:this.patient?"PUT":"GET",data:this.patient?this.patient._data:null,dataType:"json"}).always(function(t,i,n){"success"==i?(a.attr("status","Sorting..."),t&&"results"in t&&(a.attr("result",{results:TrialResult.fromJSON(t.results),interventions:[],phases:[]}),a.attr("complete",!0))):a.attr("error","Error: "+n.toString()),a.attr("status",null)})}}),TrialResult=can.Model.extend({fromJSON:function(t){if(!t)return null;for(var i=[],n=0;n<t.length;n++){var a=new TrialResult(t[n]);a.trials=Trial.fromJSON(a.trials),i.push(a)}return i}},{}),Trial=can.Model.extend({findAll:"GET /trials",eligibilityCriteria:"GET /trials/{id}/criteria",geocode:function(t,i){for(var n=0;n<t.length;n++)t[n].geocode(i)},fromJSON:function(t){if(!t)return null;for(var i=[],n=0;n<t.length;n++)i.push(new Trial(t[n]));return i}},{intervention_types:null,trial_phases:null,trial_locations:null,did_add_pins:!1,last_loc_distances:null,closest:null,interventionTypes:function(){if(null==this.intervention_types){var t=[];if("intervention"in this&&this.intervention){for(var i=0;i<this.intervention.length;i++)"intervention_type"in this.intervention[i]&&t.push(this.intervention[i].intervention_type);t=t.uniqueArray()}t.length<1&&(t=["Observational"]),this.intervention_types=t}return this.intervention_types},trialPhases:function(){if(null==this.trial_phases){(!1 in this||!this.phase)&&(this.phase="N/A");var t=["N/A"];"N/A"!=this.phase&&(t=this.phase.split("/")),this.trial_phases=t}return this.trial_phases},locations:function(){if(null===this.trial_locations&&"location"in this&&this.location){for(var t=[],i=0;i<this.location.length;i++){var n=this.location[i],a="formatted"in n.geodata&&n.geodata.formatted&&n.geodata.formatted.length>0?n.geodata.formatted.split(/,\s+/):["Unknown"],e=a.pop(),o=n.status?n.status.match(/recruiting/i):null,r=n.status?n.status.match(/not\s+[\w\s]*\s+recruiting/i):null,l={trial:this,name:"facility"in n&&n.facility.name?n.facility.name:"",city:a.length>0?a.join(", "):"",country:e,geodata:"geodata"in n?n.geodata:null,status:n.status,status_color:r?"orange":o?"green":"red",contact:"contact"in n&&n.contact?n.contact:null};t.push(new TrialLocation(l))}this.trial_locations=t}return this.trial_locations},locationsByDistance:function(t){if(!t&&null!==this.last_loc_distances)return this.last_loc_distances;var i=[],n=this.locations();if(n){for(var a=0;a<n.length;a++){var e=n[a];i.push([e.kmDistanceTo(t),e])}i.sort(function(t,i){return t[0]-i[0]}),this.last_loc_distances=i}return i},geocode:function(t){var i=this.locationsByDistance(t),n=i&&i.length>0?i[0]:[99999,null];this.closest=n[0]},showClosestLocations:function(t,i,n,a,e){var o=i.find(".trial_locations"),r=this.locations();if(r&&r.length>0){o.find(".show_more_locations").remove();var l=Math.min(r.length-n,a);r.length-n-l<3&&(l=r.length-n),l+=n;for(var s=n;l>s;s++){var c=r[s];c.kmDistanceTo(t);var h=can.view("templates/trial_location.ejs",{loc:c});o.append(h)}if(s<r.length){var u=this,d=10,f=r.length-s-d<3?r.length-s:d,p=$("<a/>",{href:"javascript:void(0)"}).text("Show "+(f<r.length-s?"next "+f:" all")).click(function(n){u?u.showClosestLocations(t,i,s,f,!0):console.error("The trial object is undefined")}),g=$("<div/>").addClass("trial_location").addClass("show_more_locations"),v=$("<h3/>").html("There are "+(r.length-s)+" more locations<br />");v.append(p),g.append(v),e?(g.hide(),o.append(g),g.fadeIn("fast")):o.append(g)}}else{var g=$('<div class="trial_location"><h3>No trial locations available</h3></div>');o.append(g)}},showLocation:function(t,i){var n=can.view("templates/trial_location.ejs",{loc:i});t.find(".trial_locations").append(n)},locationPins:function(){var t=this.locations(),i=[];if(t&&t.length>0)for(var n=0;n<t.length;n++)if("geodata"in t[n]){var a={lat:t[n].geodata.latitude,lng:t[n].geodata.longitude,location:t[n],trial:this};i.push(a)}return i},toggleEligibilityCriteria:function(t,i,n,a){console.log(t,i,n,a);var e=$(t),o=e.closest(".trial"),r=o.find(".formatted_criteria").first();r.is(":visible")?(r.hide(),e.text("Show eligibility criteria")):(r.show(),e.text("Hide eligibility criteria"),0==r.text().length&&_loadEligibilityCriteria(r,i))},loadEligibilityCriteria:function(t,i){var n=$(t);n.text("Loading..."),loadJSON("trials/"+i+"/criteria_html",function(t,i,a){"criteria"in t?n.html(t.criteria):(console.log('Expected JSON response with a "criteria" dictionary, but got these: ',t,i,a),n.text("(unknown criteria)"))},function(t,a,e){n.html("Error getting criteria: "+e+'.<br /><a href="javascript:void();" onclick="_loadEligibilityCriteria(this.parentNode, \''+i+"')\">Try again</a>.")})}}),TrialLocation=can.Model.extend({},{distance:null,init:function(t){for(var i in t)t.hasOwnProperty(i)&&(this[i]=t[i])},kmDistanceTo:function(t){return t&&"geodata"in this?this.distance=kmDistanceBetweenLocationsLatLng(t.lat(),t.lng(),this.geodata.latitude,this.geodata.longitude):t&&(console.warn("No geodata for trial location: ",this),this.distance=null),this.distance}});