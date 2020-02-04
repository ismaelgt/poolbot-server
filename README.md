# Poolbot Server

This is a djangae project which provides persistent storage, a RESTful API and leaderboard interface for the [poolbot slack client](https://github.com/dannymilsom/poolbot).

## Getting Started

First install all the dependencies:

```
  mkvirtualenv poolbot-server
  ./install_deps
  npm install
  gulp
  ./src/manage.py collectstatic
```

To finish the leaderboard config run `cp src/app/extra_settings.py.base src/app/extra_settings.py` and add the IPs granted access to AUTHORISED_LEADERBOARD_IPS. The reason for IP whitelisting is that the leaderboard is designed to be used on a public computer where user level authentication would be a security issue.
