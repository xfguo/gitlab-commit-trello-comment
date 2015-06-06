# Introduction

gitlab-commit-trello-comment will monitor your gitlab commit with card number(like #234) and push a format comment to that card of your trello board.
modified from gitlab-webhook-receiver project.

gitlab-webhook-receiver is a script to receive http posts from gitlab and then
pull the latest branches from a git repo.

# Dependencies

Before getting stated you will need install [Trolly](https://github.com/plish/Trolly) and httplib2 (reqired by trolly).

    pip install trolly httplib2

or

    pip install -r requirements.txt


# License

gitlab-commit-trello-comment is released under the [GPL v2](http://www.gnu.org/licenses/gpl-2.0.html).

# Documentation

(1) Modify the script
---------------------

Copy the config.py.sample to config.py and fill your gitlab and trello info.

(2) create the gitlab webhook
-----------------------------

In gitlab, as admin, go to "Hooks" tab, create hook as: http://your.ip.goes.here:8000

or change the port on line 175 of the script.

(3) Optional init script
------------------------

remember to edit the script if any of your directories were changed.

# Trouble getting it working?

Let me know what's happening and I'll try to help. Email me at xfguo@credosemi.com.

