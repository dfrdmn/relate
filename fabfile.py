"""Deployment scripts for www.mylabmanual.com."""
from fabric.api import cd, env, prefix, run


env.hosts = ['www.mylabmanual.com']
env.use_ssh_config = True


def deploy():
    """Main deployment script."""
    code_dir = '/home/ubuntu/repos/relate'
    with cd(code_dir), prefix('. /usr/local/bin/virtualenvwrapper.sh; workon relate'):
        git_pull()
        migrate()
        reload()


def git_pull():
    """Run 'git pull'."""
    run("git pull")


def migrate():
    """Run any database migrations needed."""
    run("./manage.py migrate")


def reload():
    """Reload apache2."""
    run("sudo systemctl reload apache2")
