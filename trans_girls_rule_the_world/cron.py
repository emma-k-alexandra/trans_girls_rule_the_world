"""
Cronjob for trans girls bot
"""
import os
import plan

def trans_girls_cron():
    """
    Config for trans girls cron
    """
    cron = plan.Plan('trans_girls_rule_the_world')

    cron.script('rule.py', every='5.minutes', path=os.getcwd())

    #update cron if crontab exists, write new cron if crontab doesn't exist
    try:
        cron.run('update')

    except plan.PlanError:
        cron.run('write')

if __name__ == '__main__':
    trans_girls_cron()
