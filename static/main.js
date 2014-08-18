function initApp(){window!=window.top&&$("#back_to_patient").hide(),Patient.findOne({id:"x"}).then(function(t){var n=TrialFinder();n.attr("patient",t),$("#app").html(can.view("app_tmpl",{finder:n}))})}function loadJSON(t,n,e){$.ajax({url:t,dataType:"json"}).always(function(i,r,a){"success"==r?n?n(i,r,a):console.warn("Successfully loaded",t,"but no success func is set"):(console.error("ERROR loading URL:",t,"RETURNED",i,r,a),n&&e(i,r,a))})}function sortedKeysFromDict(t){var n=[];for(var e in t)n[n.length]=e;return n.sort(),n}function sortChildren(t,n,e){var i=t.children(n).get();i.sort(e),$.each(i,function(n,e){t.append(e)})}function newUUID(){return"xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g,function(t){var n=16*Math.random()|0,e="x"==t?n:3&n|8;return e.toString(16)})}function _toggleTrialLocationContact(t){var n=$(t),e=n.siblings(".loc_contact");e.is(":visible")?e.fadeOut("fast"):(e.show(),e.css("left",(n.outerWidth()-e.outerWidth())/2+n.position().left))}Array.prototype.contains=function(t){return this.indexOf(t)>=0},"indexOf"in Array.prototype||(Array.prototype.indexOf=function(t){for(var n=0;n<this.length;n++)if(this[n]==t)return n;return-1}),Array.prototype.uniqueArray=function(){for(var t={},n=[],e=0,i=this.length;i>e;++e)t.hasOwnProperty(this[e])||(n.push(this[e]),t[this[e]]=1);return n},window.console||!function(){var t=["log","debug","info","warn","error","assert","dir","dirxml","group","groupEnd","time","timeEnd","count","trace","profile","profileEnd"],n=t.length;window.console={};for(var e=0;n>e;e++)window.console[t[e]]=function(){}}();var Patient=can.Model.extend({id:"_id",findOne:"GET /patients/{id}",update:"PUT /patients/{_id}"},{}),TrialFinder=can.Model.extend({},{status:null,error:null,patient:null,result:null,find:function(t,n,e){var i=this;i.attr("status","Searching..."),i.attr("error",null),i.attr("result",null);var r=this.patient?this.patient.last_manual_search:null;r||(r=$("#manual_problem").val()),this.patient&&(this.patient.attr("last_manual_search",r),this.patient.save()),$.ajax({url:"/find?term="+encodeURIComponent(r),type:this.patient?"PUT":"GET",data:this.patient?this.patient._data:null,dataType:"json"}).always(function(t,n,e){"success"==n?(i.attr("status","Sorting..."),t&&(i.attr("result",new TrialFinderResult(t)),i.attr("complete",!0))):i.attr("error","Error: "+e.toString()),i.attr("status",null)})}}),_intervention_map={Biological:"Drug/Biological",Drug:"Drug/Biological"},TrialFinderResult=can.Model.extend({},{interventions:[],phases:[],init:function(t){if(!t)return null;var n="results"in t?t.results:[];this.results=TrialResult.fromJSON(n),this.collectInterventions(),this.collectPhases()},collectInterventions:function(){if(!(this.interventions&&this.interventions.length>0)){for(var t=[],n={},e=0;e<this.results.length;e++){var i=this.results[e].trial;if(i&&i.interventions)for(var r=0;r<i.interventions.length;r++){var a=i.interventions[r];a in _intervention_map&&(a=_intervention_map[a]);var o=n[a];if(o)o.addMatch();else{var s=new TrialIntervention(a);n[a]=s,t.push(s)}}}this.attr("interventions",t.sort(TrialGroupable.sortByName))}},collectPhases:function(){if(!(this.phases&&this.phases.length>0)){for(var t=[],n={},e=0;e<this.results.length;e++){var i=this.results[e].trial;if(i&&i.phases)for(var r=0;r<i.phases.length;r++){var a=i.phases[r],o=n[a];if(o)o.addMatch();else{var s=new TrialPhase(a);n[a]=s,t.push(s)}}}this.attr("phases",t.sort(TrialGroupable.sortByName))}}}),TrialGroupable=can.Model.extend({sortByName:function(t,n){return t.name>n.name?1:t.name<n.name?-1:0}},{name:null,huid:null,num_matches:1,addMatch:function(){this.attr("num_matches",this.num_matches+1)},toggle:function(t,n,e){}}),TrialIntervention=TrialGroupable.extend({},{init:function(t){this.attr("name",t),this.attr("huid","intervention_"+this.name.replace(/\W\D/,"_"))},toggle:function(t,n,e){console.log("Toggle intervention",this.name)}}),TrialPhase=TrialGroupable.extend({},{init:function(t){this.attr("name",t),this.attr("huid","phase_"+this.name.replace(/\W\D/,"_"))},toggle:function(t,n,e){console.log("Toggle phase",this.name)}}),TrialResult=can.Model.extend({fromJSON:function(t){if(!t)return null;for(var n=[],e=0;e<t.length;e++){var i=new TrialResult(t[e]);n.push(i)}return n}},{init:function(t){this.trial=new Trial(t.trial)}}),Trial=can.Model.extend({findAll:"GET /trials",eligibilityCriteria:"GET /trials/{id}/criteria",geocode:function(t,n){for(var e=0;e<t.length;e++)t[e].geocode(n)},fromJSON:function(t){if(!t)return null;for(var n=[],e=0;e<t.length;e++)n.push(new Trial(t[e]));return n}},{}),TrialLocation=can.Model.extend({},{distance:null,init:function(t){for(var n in t)t.hasOwnProperty(n)&&(this[n]=t[n])},kmDistanceTo:function(t){return t&&"geodata"in this?this.distance=kmDistanceBetweenLocationsLatLng(t.lat(),t.lng(),this.geodata.latitude,this.geodata.longitude):t&&(console.warn("No geodata for trial location: ",this),this.distance=null),this.distance}});