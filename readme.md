# Clean up old files from your team's Slack account

The free team account in Slack allows to store 5GB only. When it's exceeded,
Slack starts to show warnings asking you to remove large files.
This tool allows to make a backup and delete files older than X days.

Unfortunately I haven't implemented this tool as service, so you should obtain OAuth access
tokens for Slack API manually :(

1. Create an app here: https://api.slack.com/apps/new
2. You can use http://requestb.in/ to create `Redirect URI` for your app. It helps you to collect all codes from your users.
3. Get `client_id` and `client_secret` from your new app.
4. Ask your Slack users to visit URL:
  `https://slack.com/oauth/authorize?client_id=<client_id>&scope=files%3Aread+files%3Awrite%3Auser+groups%3Aread+channels%3Aread+users%3Aread&redirect_uri=<requestb_url>&team=<team>` and grant the access.
5. Visit your requestb.in page and collect all granted codes.
6. Obtain OAuth access tokens from codes by request:
  `curl -i 'https://slack.com/api/oauth.access' -d'client_id=<client_id>&client_secret=<client_secret>&code=<code>&redirect_uri=<requestb_url>`


Now you have access tokens and are ready to use the tool:
```
pip install https://github.com/wreckah/slack-cleaner/archive/master.zip
slack_cleaner <access_token> -d<days> -s<backup_dir>
```

If you want to delete files for ex-users, you can add `admin` to token's
requested scopes for your admin user and use this token.
