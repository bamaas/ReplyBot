## Description

ReplyBot for Huawei 4G wifi router

### Installation
``` 
pip install -r requirements.txt
```

### Running
```
 python DataRunner.py -u <username> -p <password> --action "check" 
```
**Note:** the client and router must have the same time to make this script work.

### Usage
Give username and password through cli arguments or set them in the config.ini

| Argument         | Value                | Description                     |
| :-----------     | -------------        | --------------------------------|
| -u, --username   | "\<your username>"   | Your username between " "
| -p, --password   | "\<your password>"   | Your password between " "
| -a, --action     | "\<an action>"       | One of the actions as listed below.
| --no-log         |                      | Disable printing to console     |


### Actions
| Value             | Description                                                                             |
| :---------------- | :---------------------------------------------------------------------------------------|
| check             |   Check if expected message is received. |
| send            |      Send one message to the recipient.                                                |
| clean             |       Delete all messages in the inbox, outbox and drafts.                                          |
| auto             |       Replies if expected message is received                                   |
| random             |                                 |

### Dependency
This script makes use of of [huawei-lte-api](https://pypi.org/project/huawei-lte-api/).

### Developer
contact me @ [basmaas.nl](https://basmaas.nl/)