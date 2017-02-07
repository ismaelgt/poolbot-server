# Poolbot Server

This is a djangae project which provides persistent storage and an API for the [poolbot slack client](https://github.com/dannymilsom/poolbot).


# Leaderboard


## Install dependencies

```
  mkvirtualenv poolbot-server
  pip install nodeenv
  nodeenv -p --prebuilt
  npm install
  gulp  # transpiles JSX -> JS
  ./src/manage.py collectstatic
```

## Setting up

The following two steps must be completed to enable the leaderboard:

1. Create `src/leaderboard/slack_user_list.json` and paste in the contents of the response from https://api.slack.com/methods/users.list/test (this is a temporary work around)
2. Run `cp src/app/extra_settings.py.base src/app/extra_settings.py` and add the IPs granted access to AUTHORISED_LEADERBOARD_IPS.  The reason for IP whitelisting is that the leaderboard is designed to be used on a public computer where user level authentication would be a security issue.
