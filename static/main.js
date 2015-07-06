function initApp(){window!=window.top&&$("#back_to_patient").hide(),Patient.findOne({id:"x"}).then(function(t){var i=TrialFinder();i.attr("patient",t),$("#app").html(can.view("app_tmpl",{finder:i})),i.find(t)},function(t,i,e){$("#app").empty().append("<h3>"+i+"</h3>").append('<h1 class="red">'+e+"</h1>").append("<p>As an administrator, check the app log for more information</p>")})}function sortedKeysFromDict(t){var i=[];for(var e in t)i[i.length]=e;return i.sort(),i}function sortChildren(t,i,e){var n=t.children(i).get();n.sort(e),$.each(n,function(i,e){t.append(e)})}function newUUID(){return"xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g,function(t){var i=16*Math.random()|0,e="x"==t?i:3&i|8;return e.toString(16)})}jQuery.extend({putJSON:function(t,i){return $.ajax({type:"PUT",url:t,contentType:"application/json",data:JSON.stringify(i),dataType:"json"})}}),Array.prototype.contains=function(t){return this.indexOf(t)>=0},"indexOf"in Array.prototype||(Array.prototype.indexOf=function(t){for(var i=0;i<this.length;i++)if(this[i]==t)return i;return-1}),Array.prototype.uniqueArray=function(){for(var t={},i=[],e=0,n=this.length;n>e;++e)t.hasOwnProperty(this[e])||(i.push(this[e]),t[this[e]]=1);return i},window.console||!function(){var t=["log","debug","info","warn","error","assert","dir","dirxml","group","groupEnd","time","timeEnd","count","trace","profile","profileEnd"],i=t.length;window.console={};for(var e=0;i>e;e++)window.console[t[e]]=function(){}}();var Patient=can.Model.extend({id:"_id",findOne:"GET /patient",update:"PUT /patients/{_id}"},{init:function(t){this.attr("hasConditions",this.conditions&&this.conditions.length>0)}}),TrialFinder=can.Model.extend({},{patient:null,result:null,find:function(t,i,e){var n=this;n.attr("status","Searching..."),n.attr("error",null),n.attr("result",null),$.getJSON("/find",{condition:"Breast Cancer"}).always(function(t,i,e){if("success"==i){if(n.attr("status","Sorting..."),t){var s=new TrialFinderResult(t);n.attr("result",s),n.attr("complete",!0)}}else n.attr("error","Error: "+e.toString());n.attr("status",null)})}}),_intervention_map={Biological:"Drug/Biological",Drug:"Drug/Biological",Behavioral:"Behavioral/Other",Other:"Behavioral/Other"},TrialFinderResult=can.Model.extend({},{patient_id:null,results:null,showSuggested:!0,numSuggested:"~",showEligible:!0,numEligible:"~",showIneligible:!1,numIneligible:"~",numShown:0,numShownTitle:null,interventions:null,phases:null,init:function(t){return t?(this.attr("results",TrialResult.fromJSON(t.results,this)),this.updateResultOrder(),this.updateResultCount(),this.collectInterventions(),this.collectPhases(),void this.updateTrialShownState()):null},updateResultOrder:function(){this.results&&this.results.length>0&&Array.prototype.sort.apply(this.results,[function(t,i){return t.compare(i)}])},updateResultCount:function(){for(var t=0,i=0,e=0,n=0;n<this.results.length;n++)switch(this.results[n].status){case"suggested":t++;break;case"eligible":i++;break;default:e++}this.attr("numSuggested",t),this.attr("numEligible",i),this.attr("numIneligible",e)},collectInterventions:function(){if(!(this.interventions&&this.interventions.length>0)){for(var t=[],i={},e=0;e<this.results.length;e++){var n=this.results[e].trial;if(n&&n.interventions)for(var s=[],r=0;r<n.interventions.length;r++){var a=n.interventions[r];if(a in _intervention_map&&(a=_intervention_map[a]),!s.contains(a)){s.push(a);var o=i[a];o||(o=new TrialIntervention(null,a),o.parent=this,i[a]=o,t.push(o))}}}t.length>0&&this.attr("interventions",t.sort(TrialGroupable.sortByName))}},collectPhases:function(){if(!(this.phases&&this.phases.length>0)){for(var t=[],i={},e=0;e<this.results.length;e++){var n=this.results[e].trial;if(n&&n.phases)for(var s=0;s<n.phases.length;s++){var r=n.phases[s],a=i[r];a||(a=new TrialPhase(null,r),a.parent=this,i[r]=a,t.push(a))}}this.attr("phases",t.sort(TrialGroupable.sortByName))}},toggleShowSuggested:function(){this.attr("showSuggested",!this.showSuggested),this.updateTrialShownState()},toggleShowEligible:function(){this.attr("showEligible",!this.showEligible),this.updateTrialShownState()},toggleShowIneligible:function(){this.attr("showIneligible",!this.showIneligible),this.updateTrialShownState()},updateTrialShownState:function(){for(var t=this.interventions?$.map(this.interventions,function(t,i){return t.active?t.name:null}):[],i=this.phases?$.map(this.phases,function(t,i){return t.active?t.name:null}):[],e={},n={},s=!1,r=0,a=0;a<this.results.length;a++){var o=this.results[a];o.attr("shownForInterventions",!1),o.attr("shownForPhases",!1);var l=o.trial;switch(o.status){case"suggested":o.attr("shownForStatus",this.showSuggested);break;case"eligible":o.attr("shownForStatus",this.showEligible);break;case"ineligible":o.attr("shownForStatus",this.showIneligible);break;default:console.warn("Trial has an unknown status:",o.status),o.attr("shownForStatus",!0)}if(l&&l.interventions)for(var h=0;h<l.interventions.length;h++){var u=l.interventions[h];if(u=u in _intervention_map?_intervention_map[u]:u,o.attr("shownForInterventions",o.shownForInterventions||t.indexOf(u)>=0),o.shownForStatus){var d=e[u]||0;e[u]=d+1}}if(l&&l.phases)for(var h=0;h<l.phases.length;h++){var f=l.phases[h];if(o.attr("shownForPhases",o.shownForPhases||i.indexOf(f)>=0),o.shownForStatus&&o.shownForInterventions){var d=n[f]||0;n[f]=d+1,s=!0}}o.shown&&r++}if(this.attr("numShown",r),r>1?this.attr("numShownTitle",r+" Trials"):this.attr("numShownTitle",r>0?"1 Trial":null),this.interventions)for(var a=0;a<this.interventions.length;a++){var c=this.interventions[a];c.attr("numMatches",e[c.name]||0)}if(this.phases)for(var a=0;a<this.phases.length;a++){var f=this.phases[a];f.attr("numMatches",n[f.name]||0)}this.attr("showPhases",s)}}),TrialGroupable=can.Model.extend({sortByName:function(t,i){return t.name>i.name?1:t.name<i.name?-1:0}},{parent:null,name:null,huid:null,active:!1,numMatches:0,addMatch:function(){this.attr("numMatches",this.numMatches+1)}}),TrialIntervention=TrialGroupable.extend({},{init:function(t,i){this.attr("name",i),this.attr("huid","intervention_"+this.name.replace(/\W\D/,"_"))}}),TrialPhase=TrialGroupable.extend({},{init:function(t,i){this.attr("name",i),this.attr("huid","phase_"+this.name.replace(/\W\D/,"_")),this.attr("active",!0)}}),TrialResult=can.Model.extend({fromJSON:function(t,i){if(!t)return null;for(var e=[],n=0;n<t.length;n++){var s=new TrialResult(t[n]);s.finder_result=i,e.push(s)}return e}},{finder_result:null,init:function(t){this.attr("tests",new TrialResultTest.fromJSON(t.tests)),this.attr("hasTests",this.tests&&this.tests.length>0),this.attr("canEdit",!0),this.attr("suggested",this.patient_info&&this.patient_info.suggested),this.attr("status",this.overallStatus()),this.bind("suggested",function(t,i,e){this.attr("status",this.overallStatus())});var i=new Trial(t.trial);this.attr("trial",i),this.bind("shownForStatus",function(t,i,e){this.attr("shown",i&&this.shownForInterventions&&this.shownForPhases)}),this.bind("shownForInterventions",function(t,i,e){this.attr("shown",i&&this.shownForStatus&&this.shownForPhases)}),this.bind("shownForPhases",function(t,i,e){this.attr("shown",i&&this.shownForStatus&&this.shownForInterventions)})},setCanEdit:function(t){this.attr("canEdit",t)},edit:function(){TrialEditor.singleton().edit(this)},cancel:function(){TrialEditor.singleton().done(this)},save:function(){TrialEditor.singleton().save(this)},suggest:function(){this.attr("suggested",!this.suggested),this.finder_result.updateResultCount(),this.putSuggested(!0)},putSuggested:function(t,i){var e=this;$.putJSON("trials/"+this.trial._id+"/patient/"+this.finder_result.patient_id+"/info",{suggested:this.suggested}).done(function(t,i,n){e.updateFromPatientInfo(t)}).fail(function(n,s,r){console.error("Failed to save trial patient info:",s,r,"will retry:",!i),i?t&&(this.attr("suggested",!this.suggested),this.finder_result.updateResultCount(),alert("Failed to save trial patient info: "+r)):e.putSuggested(t,!0)})},updateFromPatientInfo:function(t){!t||t.trial_id&&t.trial_id!=this.trial._id||t.patient_id&&t.patient_id!=this.finder_result.patient_id?console.error("Cannot update from patient info because of trial_id/patient_id mismatch:",t.trial_id,this.trial._id,t.patient_id,this.finder_result.patient_id):this.attr("patient_info",t)},overallStatus:function(){if(this.suggested)return"suggested";if(this.tests)for(var t=0;t<this.tests.length;t++)if("fail"==this.tests[t].status)return"ineligible";return"eligible"},compare:function(t){return this.status!=t.status?this.suggested?-1:t.suggested?1:"eligible"==this.status?-1:1:this.trial.title<t.trial.title?-1:1}}),TrialResultTest=can.Model.extend({fromJSON:function(t){if(!t)return null;for(var i=[],e=0;e<t.length;e++)i.push(new TrialResultTest(t[e]));return i}},{}),Trial=can.Model.extend({findAll:"GET /trials",geocode:function(t,i){for(var e=0;e<t.length;e++)t[e].geocode(i)},fromJSON:function(t){if(!t)return null;for(var i=[],e=0;e<t.length;e++)i.push(new Trial(t[e]));return i}},{interventions:null,phases:null,init:function(t){if(this.updateFromInfo(),this.phases&&this.attr("phasesFormatted",$.makeArray(this.phases).sort().join(", ")),this.attr("primary_outcome"))for(var i=0;i<this.attr("primary_outcome").length;i++){var e=this.attr("primary_outcome")[i];"safety_issue"in e&&e.attr("safety_issue","Yes"==e.safety_issue)}if(this.attr("secondary_outcome"))for(var i=0;i<this.attr("secondary_outcome").length;i++){var e=this.attr("secondary_outcome")[i];"safety_issue"in e&&e.attr("safety_issue","Yes"==e.safety_issue)}},updateFromInfo:function(t){t&&(t.notes&&!t.notes.html&&(t=$.extend({},t),t.notes=this.info?this.info.notes:null),this.attr("info",t)),this.attr("mainTitle",this.info&&this.info.title?this.info.title:this.title)},previewTitle:function(t,i,e){var n=$("#edit_title");n.val()==this.title?n.val(this.attr("previousTitle")):(this.attr("previousTitle",n.val()),n.val(this.title))}}),TrialEditor=can.Construct.extend({singleton:function(){return null===this._instance&&(this._instance=new TrialEditor),this._instance},_instance:null},{result:null,edit:function(t){this.done(this.result),this.result=t,this.result.attr("editing",!0)},done:function(t){null!==this.result&&t===this.result&&(this.result.attr("editing",!1),this.result=null)},save:function(t){if(!this.result||t!==this.result||!this.result.attr("editing"))return void alert("Not currently editing this trial");var i=this.result;i.setCanEdit(!1);var e=i.trial,n={title:$("#edit_title").val(),notes:$("#edit_notes").val()},s={notes:$("#edit_patient_notes").val()};$.when($.putJSON("trials/"+e._id+"/info",n).done(function(t,i,n){e.updateFromInfo(t?t.trial:null)}).fail(function(t,i,e){console.error("Failed to save trial info:",i,e),alert("Failed to save trial info: "+e)}),$.putJSON("trials/"+e._id+"/patient/"+i.finder_result.patient_id+"/info",s).done(function(t,e,n){i.updateFromPatientInfo(t)}).fail(function(t,i,e){console.error("Failed to save trial patient info:",i,e),alert("Failed to save trial patient info: "+e)})).done(function(){i.setCanEdit(!0)}),this.done(i)}});