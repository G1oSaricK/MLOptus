# {{ cookiecutter.project_name }}

Project Description

Setup Instructions
1. Clone the repository:
    ```bash
    git clone git@github.com:NickOsipov/{{ cookiecutter.project_slug }}.git
    cd {{ cookiecutter.project_slug }}
    ```
2. Create a project:
    ```bash
    uv python pin 3.11
    uv init
    uv venv
    uv add --requirements requirements.txt
    ```
