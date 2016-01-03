"""
Cronjob for trans girls bot
"""
import os
import plan
import trans_girls_rule_the_world

def trans_girls_cron():
    """
    Config for trans girls cron
    """
    cron = plan.Plan('trans_girls_rule_the_world')
    path = trans_girls_rule_the_world.__path__[0]

    cron.script('rule.py', every='5.minutes', path=path)

    #update cron if crontab exists, write new cron if crontab doesn't exist
    try:
        cron.run('update')

    except plan.PlanError:
        cron.run('write')

if __name__ == '__main__':
    trans_girls_cron()
