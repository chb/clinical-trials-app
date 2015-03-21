Clinical Trials App
===================

A Python 3/Flask web app that screens a patient's eligibility for certain clinical trials.
App state is stored in a local MongoDB NoSQL database.
Trial data is obtained via [TrialReach's][trialreachapi] trial API, which enhances trial data registered on [ClinicalTrials.gov][ctg].

[trialreachapi]: http://developer.trialreach.com
[ctg]: http://www.clinicaltrials.gov


User Flow
---------

The app is used in context of a patient.
Patient data (age, gender, zip, problems, meds, labs, ...) is obtained via the [SMART on FHIR][smart] API.
This involves logging in to the SMART container, either explicitly through a  login page or implicitly by launching the app from within the EHR.

The patient's demographics (gender, age, location and picture, if available) are shown atop.
> Need to determine how/if to show problems, meds, ...

A query for all trials being performed in the area is then performed against TrialReach's API with the respective restrictions.
Each trial's target profile is compared against patient data to determine her preliminary eligibility.

Trials are then listed, along with their matching and failing criteria, below the patient overview, ordered first by status (suggested first, then eligible, then ineligible) and then by trial title.
> Need to figure out best trial sort order

The list provides a quick glance at the trials, with trial title, intervention, phase and keywords visible.
> Display other trial information that is important.

Textual eligibility criteria can be expanded and a link to the original ClinicalTrials.gov website is provided.

[smart]: http://smartplatforms.org


Technical Flow
==============

The app performs most logic server-side and exposes this functionality via a REST-like API used by the web frontend.


Backend Server
--------------

### Patient Data

Patient data is fetched via the SMART on FHIR API (currently using DSTU-1), which populates a `TrialPatient` instance.
To avoid making a round-trip to the SMART server three times within a few seconds, patient data is cached to our Mongo database.
Cache data is discarded if it's older than 5 minutes, requiring a new round-trip to the SMART API server.

### Trial Data

To find trials matching the search query, a `TrialFinder` instance is created with a handle to a `TrialServer` subclass:

- Initially a `LocalTrialServer` instance that reads target profile JSON from disk
- Later a `TrialReachServer` instance that queries and retrieves data via TrialReach's API

Each trial is represented in a `TargetTrial` instance, holding on to trial and target profile data.

    TODO: Figure out
      a) which data is local
      b) if it should be cached to Mongo on app-install

### Trial Matching

The list of _Trial_ instances and the _Patient_ object are then handed to a `TrialPatientMatcher` instance.
This object compares each trial's criteria to the available patient data.
**Logic modules** exist that are capable of comparing specific patient data to eligibility criteria (e.g. a module to determine if a lab value is in range).
Trial data is then complemented with the corresponding matching metadata (TBD) and returned as JSON via API for the web frontend to consume.


Web Frontend
------------

The web frontend is built as an HTML5 app (using [can.js][canjs]) and is included in this repository.

[canjs]: http://canjs.com/


Installation
============

This is a Python 3 app running on the [Flask][] framework.
App state is stored into a (local) [MongoDB][] database.
Manual setup involves installing _Python 3_, _pip_ and _MongoDB_, then using a virtual environment, which requires `virtualenv`, as follows:

```bash
git clone --recursive https://github.com/chb/clinical-trials-app.git
cd clinical-trials-app
virtualenv -p python3 env
. env/bin/activate
pip install -r requirements.txt
```

A Vagrant/Ansible [installation script suite is available][app-install] that configures a VM as needed, including reverse-proxying.

[app-install]: https://github.com/chb/clinical-trials-app-installer

Configuration
-------------

You should now copy `config.default.py` to `config.py` and adjust the settings.
When done the app is ready to be run, best via _gunicorn_ or manually:

```bash
python wsgi.py
```

The app checks for the presence of `config.py`, if it is not present it looks at environment variables of the same name.
This can be exploited when running on Heroku, all configuration variables can be set as environment vars in the Heroku dashboard.


[flask]: http://flask.pocoo.org
[mongodb]: http://www.mongodb.org
