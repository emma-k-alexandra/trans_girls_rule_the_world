# Trans Girls Rule The World

A tumblr bot to reblog trans girl's selfies

## Install
```bash
git clone https://github.com/Deafjams/trans_girls_rule_the_world.git
cd trans_girls_rule_the_world
python setup.py install
```

## Configure
```bash
export TRANS_GIRLS_CONSUMER_KEY={{Your tumblr consumer key}}
export TRANS_GIRLS_CONSUMER_SECRET={{Your tumblr consumer secret key}}
export TRANS_GIRLS_OAUTH_TOKEN={{Your tumblr oauth token}}
export TRANS_GIRLS_OAUTH_SECRET={{Your tumblr oauth secret}}
```

## Run
```bash
nohup python3 server.py &
python3 cron.py
```
Note: This is incredibly fragile and will be strengthened in future releases
