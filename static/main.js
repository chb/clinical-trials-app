function initApp(){window!=window.top&&$("#back_to_patient").hide(),Patient.findOne({id:"x"}).then(function(t){var n=TrialFinder();n.attr("patient",t),$("#app").html(can.view("app_tmpl",{finder:n})),n.find(t)})}function sortedKeysFromDict(t){var n=[];for(var i in t)n[n.length]=i;return n.sort(),n}function sortChildren(t,n,i){var e=t.children(n).get();e.sort(i),$.each(e,function(n,i){t.append(i)})}function newUUID(){return"xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g,function(t){var n=16*Math.random()|0,i="x"==t?n:3&n|8;return i.toString(16)})}jQuery.extend({putJSON:function(t,n){return $.ajax({type:"PUT",url:t,contentType:"application/json",data:JSON.stringify(n),dataType:"json"})}}),Array.prototype.contains=function(t){return this.indexOf(t)>=0},"indexOf"in Array.prototype||(Array.prototype.indexOf=function(t){for(var n=0;n<this.length;n++)if(this[n]==t)return n;return-1}),Array.prototype.uniqueArray=function(){for(var t={},n=[],i=0,e=this.length;e>i;++i)t.hasOwnProperty(this[i])||(n.push(this[i]),t[this[i]]=1);return n},window.console||!function(){var t=["log","debug","info","warn","error","assert","dir","dirxml","group","groupEnd","time","timeEnd","count","trace","profile","profileEnd"],n=t.length;window.console={};for(var i=0;n>i;i++)window.console[t[i]]=function(){}}();var Patient=can.Model.extend({id:"_id",findOne:"GET /patients/{id}",update:"PUT /patients/{_id}"},{init:function(t){this.attr("hasConditions",this.conditions&&this.conditions.length>0)}}),TrialFinder=can.Model.extend({},{patient:null,result:null,find:function(t,n,i){var e=this;e.attr("status","Searching..."),e.attr("error",null),e.attr("result",null),$.getJSON("/find",{condition:"Breast Cancer"}).always(function(t,n,i){if("success"==n){if(e.attr("status","Sorting..."),t){var r=new TrialFinderResult(t);e.attr("result",r),e.attr("complete",!0)}}else e.attr("error","Error: "+i.toString());e.attr("status",null)})}}),_intervention_map={Biological:"Drug/Biological",Drug:"Drug/Biological",Behavioral:"Behavioral/Other",Other:"Behavioral/Other"},TrialFinderResult=can.Model.extend({},{results:null,numSuggested:"~",numEligible:"~",numIneligible:"~",numShown:0,numShownTitle:null,interventions:null,phases:null,init:function(t){return t?(this.attr("results",TrialResult.fromJSON(t.results)),this.countResults(),this.collectInterventions(),void this.collectPhases()):null},countResults:function(){for(var t=0,n=0,i=0,e=0;e<this.results.length;e++)this.results[e].hasFail()?i++:n++;this.attr("numSuggested",t),this.attr("numEligible",n),this.attr("numIneligible",i)},updateTrialShownState:function(){for(var t=$.map(this.interventions,function(t,n){return t.active?t.name:null}),n=$.map(this.phases,function(t,n){return t.active?t.name:null}),i={},e=0,r=0;r<this.results.length;r++){var a=this.results[r];a.attr("shownForInterventions",!1),a.attr("shownForPhases",!1);var s=a.trial;if(s&&s.interventions)for(var o=0;o<s.interventions.length;o++){var l=s.interventions[o];l=l in _intervention_map?_intervention_map[l]:l,t.indexOf(l)>=0&&a.attr("shownForInterventions",!0)}if(s&&s.phases)for(var o=0;o<s.phases.length;o++){var h=s.phases[o];if(a.attr("shownForPhases",a.shownForPhases||n.indexOf(h)>=0),a.shownForInterventions){var u=i[h]||0;i[h]=u+1}}a.attr("shown")&&e++}this.attr("numShown",e),e>1?this.attr("numShownTitle",e+" Trials"):this.attr("numShownTitle",e>0?"1 Trial":null);for(var r=0;r<this.phases.length;r++){var h=this.phases[r];h.attr("numMatches",i[h.name]||0)}this.attr("showPhases",t.length>0)},collectInterventions:function(){if(!(this.interventions&&this.interventions.length>0)){for(var t=[],n={},i=0;i<this.results.length;i++){var e=this.results[i].trial;if(e&&e.interventions)for(var r=[],a=0;a<e.interventions.length;a++){var s=e.interventions[a];if(s in _intervention_map&&(s=_intervention_map[s]),!r.contains(s)){r.push(s);var o=n[s];o||(o=new TrialIntervention(null,s),o.parent=this,n[s]=o,t.push(o)),o.addMatch()}}}t.length>0&&this.attr("interventions",t.sort(TrialGroupable.sortByName))}},collectPhases:function(){if(!(this.phases&&this.phases.length>0)){for(var t=[],n={},i=0;i<this.results.length;i++){var e=this.results[i].trial;if(e&&e.phases)for(var r=0;r<e.phases.length;r++){var a=e.phases[r],s=n[a];s||(s=new TrialPhase(null,a),s.parent=this,n[a]=s,t.push(s))}}this.attr("phases",t.sort(TrialGroupable.sortByName))}}}),TrialGroupable=can.Model.extend({sortByName:function(t,n){return t.name>n.name?1:t.name<n.name?-1:0}},{parent:null,name:null,huid:null,active:!1,numMatches:0,addMatch:function(){this.attr("numMatches",this.numMatches+1)}}),TrialIntervention=TrialGroupable.extend({},{init:function(t,n){this.attr("name",n),this.attr("huid","intervention_"+this.name.replace(/\W\D/,"_"))}}),TrialPhase=TrialGroupable.extend({},{init:function(t,n){this.attr("name",n),this.attr("huid","phase_"+this.name.replace(/\W\D/,"_")),this.attr("active",!0)}}),TrialResult=can.Model.extend({fromJSON:function(t){if(!t)return null;for(var n=[],i=0;i<t.length;i++){var e=new TrialResult(t[i]);n.push(e)}return n}},{init:function(t){this.attr("trial",new Trial(t.trial)),this.attr("tests",new TrialResultTest.fromJSON(t.tests)),this.bind("shownForInterventions",function(t,n,i){this.attr("shown",n&&this.shownForPhases)}),this.bind("shownForPhases",function(t,n,i){this.attr("shown",n&&this.shownForInterventions)})},hasFail:function(){var t=this.attr("tests");if(t)for(var n=0;n<t.length;n++)if("fail"==t[n].status)return!0;return!1}}),TrialResultTest=can.Model.extend({fromJSON:function(t){if(!t)return null;for(var n=[],i=0;i<t.length;i++)n.push(new TrialResultTest(t[i]));return n}},{}),Trial=can.Model.extend({findAll:"GET /trials",geocode:function(t,n){for(var i=0;i<t.length;i++)t[i].geocode(n)},fromJSON:function(t){if(!t)return null;for(var n=[],i=0;i<t.length;i++)n.push(new Trial(t[i]));return n}},{interventions:null,phases:null,init:function(t){if(this.attr("canEdit",!0),this.updateFromInfo(),this.phases&&this.attr("phasesFormatted",$.makeArray(this.phases).sort().join(", ")),this.attr("primary_outcome"))for(var n=0;n<this.attr("primary_outcome").length;n++){var i=this.attr("primary_outcome")[n];"safety_issue"in i&&i.attr("safety_issue","Yes"==i.safety_issue)}if(this.attr("secondary_outcome"))for(var n=0;n<this.attr("secondary_outcome").length;n++){var i=this.attr("secondary_outcome")[n];"safety_issue"in i&&i.attr("safety_issue","Yes"==i.safety_issue)}},updateFromInfo:function(t){t&&this.attr("info",t),this.attr("mainTitle",this.info&&this.info.title?this.info.title:this.title)},allowEditing:function(t){this.attr("canEdit",t)},edit:function(){TrialEditor.singleton().edit(this)},cancel:function(){TrialEditor.singleton().done(this)},save:function(){TrialEditor.singleton().save(this)},previewTitle:function(t,n,i){var e=$("#edit_title");e.val()==this.title?e.val(this.attr("previousTitle")):(this.attr("previousTitle",e.val()),e.val(this.title))}}),TrialEditor=can.Construct.extend({singleton:function(){return null===this._instance&&(this._instance=new TrialEditor),this._instance},_instance:null},{trial:null,edit:function(t){this.done(this.trial),this.trial=t,this.trial.attr("editing",!0)},done:function(t){null!==this.trial&&t===this.trial&&(this.trial.attr("editing",!1),this.trial=null)},save:function(t){if(!this.trial||t!==this.trial||!this.trial.attr("editing"))return void alert("Not currently editing this trial");var n=this.trial;n.allowEditing(!1),$.putJSON("trials/"+this.trial._id+"/info",{title:$("#edit_title").val(),notes:$("#edit_notes").val()}).done(function(t,i,e){n.updateFromInfo(t?t.trial:null),n.allowEditing(!0)}).fail(function(t,i,e){console.log("FAILED to save trial:",i,e),alert("Failed to save trial info: "+e),n.allowEditing(!0)}),this.done(n)}});