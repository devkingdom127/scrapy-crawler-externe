# .bashrc

# Source global definitions
if [ -f /etc/bashrc ]; then
        . /etc/bashrc
fi

# User specific aliases and functions
alias lsl="ls -ltah"
alias LSL="lsl"

alias edit-aliases="nano /home/ec2-user/.bashrc"

alias goto-app="cd /opt/python/current/"
alias goto-eb-hooks="cd /opt/elasticbeanstalk/hooks/appdeploy"
alias goto-logs="cd /opt/python/log"
alias goto-home="cd /home/ec2-user"

alias show-log-eb="lnav /var/log/eb-activity.log"