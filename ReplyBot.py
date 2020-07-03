from Router import Router
from datetime import datetime, timedelta
from time import sleep
import argparse
import configparser
from random import randrange

class ReplyBot(Router):

    def __init__(self, username, password, no_log=False):
        super().__init__(username, password)
        self.log = lambda x: print(x) if not no_log else None   # If true, no logging happens on the functions.
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')

    def check(self):
        msg = self.get_latest_msg('inbox')
        if msg is not None:
            actual_sender = msg['Phone']
            actual_content = msg['Content']
            expected_sender = self.config['expected-msg']['sender']
            expected_content = self.config['expected-msg']['sender']
            if expected_content in actual_content and expected_sender == actual_sender:
                self.read_msg(msg['Index'])
                self.log("Expected message received!")
                return True
        else:
            self.log("Expected message not received.")
            return False

    def send(self):
        send_date = datetime.today().replace(microsecond=0)
        date_limit = send_date + timedelta(minutes=1)
        recipient = self.config['reply-msg']['recipient']
        content = self.config['reply-msg']['content']
        self.send_msg(recipient, content)
        # poll inbox for success message
        success = False
        for i in range(20):
            msg = self.get_latest_msg("inbox")
            if msg is not None:
                id = msg['Index']
                actual_sender = msg['Phone']
                actual_content = msg['Content']
                expected_sender = self.config['success-msg']['sender']
                expected_content = self.config['success-msg']['contains']
                if expected_content in actual_content and actual_sender == expected_sender:
                    msg_date = datetime.strptime(msg['Date'], "%Y-%m-%d %H:%M:%S")
                    # If the response msg is received within one minute from the send_date
                    if send_date <= msg_date <= date_limit:
                        success = True
                        self.read_msg(id)
                        self.log("Message successfully delivered.")
                        break
            sleep(1)
        if success is False:
            raise Exception("Failed to send message, success message not received.")

    def clean(self):
        self.clean_box('inbox')
        self.log('Inbox cleaned.')
        self.clean_box('outbox')
        self.log('Outbox cleaned.')
        self.clean_box('drafts')
        self.log('Drafts cleaned.')

    def auto(self):
        received = self.check()
        if received:
            self.send()

    def random(self):
        received = self.check()
        if received:
            self.clean()
            count = randrange(2, 5)
            self.log("Sending {} messages...".format(count))
            for i in range(count):
                self.send()
                wait = randrange(15, 45)
                self.log("Pausing for " + str(wait) + " seconds...")
                if i == count-1:
                    break
                sleep(wait)
            self.clean()


if __name__ == '__main__':

    # Example
    # ----------------
    # DataRunner.py -u <username> -p <password> --action "smart"

    actions = {
        "check",    # Check if expected message is received.
        "send",     # Send one message to the recipient
        "clean",    # Delete all messages in the inbox, outbox and drafts.
        "auto",     # Replies if expected message is received
        "random"
    }

    # Parse config
    config = configparser.ConfigParser()
    config.read('config.ini')
    config_username = config['router']['username']
    config_password = config['router']['password']

    # Parse cli arguments
    required = lambda conf: True if conf == '' else False
    parser = argparse.ArgumentParser(description="Data manager for Huawei 4G wifi router")
    parser.add_argument('-u', '--username', type=str, help="Your username", required=required(config_username), default=config_username)
    parser.add_argument('-p', '--password', type=str, help="Your password", required=required(config_password), default=config_password)
    parser.add_argument('-a', '--action', type=str, help="The action you want to perform", choices=actions, required=True)
    parser.add_argument('--no-log', default=False, action="store_true", help="Disable logging of script info.")
    args = vars(parser.parse_args())
    action = args['action']
    no_log = args['no_log']  # not given == False

    # Run bot action
    if no_log is False:
        print("Action: " + action + "\n-------------------------")
    bot = ReplyBot(args['username'], args['password'], no_log)
    run_action = bot.__getattribute__(action.replace(" ", "_"))
    run_action()



