# Clean up old files from your team's Slack account

Install the code:
```
pip install https://github.com/wreckah/slack-cleaner/archive/master.zip
```

Obtain an access token:
  * Open `https://slack.com/oauth/authorize?client_id=<client_id>&scope=admin+files%3Aread+groups%3Aread+channels%3Aread+users%3Aread&redirect_uri=https%3A%2F%2F127.0.0.1%2Foauth%2Fcallback&team=swiftgift` in your browser (`admin` account required to delete files of all users).
  * Allow access
  * Get code from redirected URL (https://127.0.0.1/oauth/callback?code=<code>&state=) and put it into request:
  ```
    curl -i 'https://slack.com/api/oauth.access' -d'client_id=<client_id>&client_secret=<client_secret>&code=<code>&redirect_uri=https%3A%2F%2F127.0.0.1%2Foauth%2Fcallback'
  ```
  * Get token from the response
  ```json
{
  "ok": true,
  "access_token": "<token>",
  "scope": "admin,files:read,groups:read,channels:read,users:read",
  "user_id": "U03J507JV",
  "team_name": "<team>",
  "team_id": "<id>"
}
  ```

Now let's go:
```
slack_cleaner <team> <token> -d<days> -s<backup_dir>
```
