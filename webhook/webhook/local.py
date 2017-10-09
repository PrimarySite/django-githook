# Settings that you'll want to override in production
# ALLOWED_HOSTS []
# DEBUG = False

GITHUB_WEBHOOK_KEY = 'a-long-string-goes-here'
R10K_BIN = '/bin/r10k'
R10K_CONFDIR = '/etc/r10k'
R10K_USER = 'r10k'
HOOK_SCRIPT = '/usr/local/bin/hook.sh'
ENVIRONMENT_ENV = ''
PUPPET_USER = 'puppet'
ENC_DIR = '/etc/enc'