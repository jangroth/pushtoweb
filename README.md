# Push2Web

## TL;DR:
*Markdown files* (git) -> *AWS* (Lambda) -> *Web page* (S3)

## Install

* Create and activate Python3 virtual environment
```
virtualenv --python=python3 venv
source venv/bin/activate
pip3 install -r requirements.lock
```

* Assume AWS role in target account

* Run playbook
```
cd ansible
ansible-playbook -v -i inventory/test main.yml
```
