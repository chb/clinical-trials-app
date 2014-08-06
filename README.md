Clinical Trials App
===================

A Python/Flask web app that screens a patient's eligibility for certain clinical trials.
Trial data is obtained via [LillyCOI's][lilly] trial API, which enhances trial data registered on [ClinicalTrials.gov][ctg].

[lilly]: http://www.lillycoi.com
[ctg]: http://www.clinicaltrials.gov


User Flow
---------

The app is used in context of a patient.
Patient data (age, gender, zip, problems, meds, labs) is obtained via the [SMART on FHIR][smart] API to prepopulate a form.
This involves logging in to the SMART container, either explicitly through a web login page if the app is a standalone app or implicitly by launching the app from within the EHR and passing the correct context.

A query for trials is then performed against Lilly's API, which retrieves all trials matching a certain search condition.
For trials that have a **target profile**, the trial's target profile is compared against the patient data to determine the patient's preliminary eligibility.

Trials are then listed alongside indicators on why a patient is (in)eligible for a trial.
There will be a possibility to add or remove patient criteria to narrow down or broaden the breadth of potential trials.

[smart]: http://smartplatforms.org


Technical Flow
==============

The app provides most logic server-side and exposes this functionality via a REST-like API.
The main endpoint is `/trials`, which handles search parameters in the URL, where one can `PUT` a patient JSON dictionary to receive trials pre-scanned for the given patient.

### Preliminary Example

Given you are looking for _Rheumatoid Arthritis_ trials for your patient, you would:

```
PUT /trials?term=Rheumatoid+Arthritis
```

```json
{
    "age_years": 6,
    "gender": "male",
    "location": "Boston, MA",
    "problems": [
        ...
    ]
}
```

The server creates a `Patient` instance to represent the patient, which it keeps in memory.
To find trials matching the search query, a `TrialFinder` instance is created with a handle to a `TrialServer` subclass, which represents Lilly's v2 trial server.
The trial finder proceeds to query Lilly's API to retrieve trial data.
Search results are paged, so the trial finder will likely have to repeatedly query the API until all trials have arrived.
Each trial is represented in a `Trial` instance and downloads its corresponding target profile, if one is available.

The list of _Trial_ instances and the _Patient_ object are then handed to a `TrialPatientMatcher` instance.
This object compares each trial's criteria to the available patient data.
**Logic modules** will exist that are capable of comparing specific patient data to eligibility criteria (e.g. a module to determine if a lab value is in range).
Trial data is then complemented with the corresponding matching metadata (TBD) and returned as JSON via the API.


Web Frontend
============

The web frontend is built as an HTML5 app (using [can.js][canjs]) and is included in this repository.
It stores patient data in the session object, ultimately using the server's standard API, as described above.
(...)

[canjs]: http://canjs.com/
