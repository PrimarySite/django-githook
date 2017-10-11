# Django Githook

This is a quick implementation of a django webhook, for R10K, almost exclusively based upon the work
by Vitor Freitas at his blog **[here](https://simpleisbetterthancomplex.com/tutorial/2016/10/31/how-to-handle-github-webhooks-using-django.html)**; just a couple of light touches to make it a little more python3 friendly.

Normally you'll create a virtualenv (`python3 -m venv .venv`) to install your python packages for this app into.
The prerequisite python package requirements are in the requirements.txt file (`pip install -r requirements.txt`).

Clone this repository and change the variable settings in the `local.py` in `webhook/webhook` to suit your environment.

You then need to set up a way to run your app and to handle the incoming request; usually I use nginx paired with uwsgi.

The user account will need the permissions to execute commands with sudo, so you'll need to `visudo`, in my case I created a `Cmnd_Alias` with the commands you can execute as the root user.
E.g.

```
Cmnd_Alias  USER_CMDS = /usr/local/bin/git, /usr/local/bin/ssh, /usr/local/bin/hook.sh
user ALL=(root) NOPASSWD:USER_CMDS
```
