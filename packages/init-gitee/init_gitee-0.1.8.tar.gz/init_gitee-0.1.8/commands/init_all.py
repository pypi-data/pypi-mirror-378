import click
import os

@click.command(
    name="init-all",
    context_settings={"help_option_names": ["--help", "-h"]},
)
@click.argument("repo_name", required=True)
def init_all(repo_name):
    commands = [
        f"init-gitee create-repo -g mpypi {repo_name}",
        f"uv init {repo_name}",
    ]
    for command in commands:
        print("-" * 30)
        print(f"Executing: {command}")
        result = os.system(command)
        if result != 0:
            print(f"Command failed: {command}")
        print("+" * 30)
    os.chdir(repo_name)
    print("changed directory to:", os.getcwd())
    commands = [
        f"init-git mpypi/{repo_name}",
    ]
    for command in commands:
        print("-" * 30)
        print(f"Executing: {command}")
        result = os.system(command)
        if result != 0:
            print(f"Command failed: {command}")
        print("+" * 30)
