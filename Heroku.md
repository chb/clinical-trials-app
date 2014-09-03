Heroku Setup
============

These are the steps necessary to setup the app on Heroku and get it running.

1. Install/update the [Herokup Toolbelt](https://toolbelt.heroku.com)
2. Create the app in Heroku dashboard and add the remote to the git checkout:
    ```
    git remote add heroku git@heroku.com:clinical-trials-app.git
    ```

3. Login to Heroku from command-line with `heroku login`
4. Run `heroku.sh` to set our configuration variables
5. Push to heroku:
    ```
    git push heroku master
    ```

