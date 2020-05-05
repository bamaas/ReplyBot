from huawei_lte_api.Client import Client
from huawei_lte_api.AuthorizedConnection import AuthorizedConnection
from huawei_lte_api.enums.sms import BoxTypeEnum
from time import sleep
from datetime import datetime


class ConnectionManager:

    def __init__(self, username, password, ip):
        self.client = None
        self.username = username
        self.password = password
        self.ip = ip

    def __enter__(self):
        connection = AuthorizedConnection('http://{}:{}@{}/'.format(self.username, self.password, self.ip))
        self.client = Client(connection)
        return self.client

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.user.logout()


class Router:

    boxtypes = {
        'inbox': BoxTypeEnum.LOCAL_INBOX,
        'outbox': BoxTypeEnum.LOCAL_SENT,
        'drafts': BoxTypeEnum.LOCAL_DRAFT
    }

    def __init__(self, username, password, ip='192.168.8.1'):
        self.ip = ip
        self.username = username
        self.password = password

    def get_boxtype(self, boxtype):
        if isinstance(boxtype, BoxTypeEnum):
            return boxtype
        else:
            boxtype = self.boxtypes.get(boxtype.lower(), "{} is an incorrect boxtype. Please choose between: {}."
                                        .format(boxtype, self.boxtypes.keys()))
            return boxtype

    def send_msg(self, recipient, content, send_date=None):
        with ConnectionManager(self.username, self.password, self.ip) as client:
            recipient = int(recipient)
            if send_date is None:
                send_date = datetime.today().replace(microsecond=0)
            resp = client.sms.send_sms([recipient], content, from_date=send_date)
            if resp != 'OK':
                raise Exception("Failed to sent message to '{}' with content '{}'. Response: '{}'."\
                                .format(recipient, content, resp))
            # poll outbox to be sure that it is sent
            success = False
            for i in range(4):
                msg_outbox = self.get_latest_msg("outbox")
                if msg_outbox is not None:
                    msg_outbox_date = datetime.strptime(msg_outbox['Date'], "%Y-%m-%d %H:%M:%S")
                    if msg_outbox_date == send_date:
                        success = True
                        break
                sleep(1)
            if success is False:
                raise Exception(
                    "Message to '{}' with content '{}' isn't appearing in the outbox after sent it. Response: '{}'.".format(
                        recipient, content, resp))

    def get_msgs(self, boxtype):
        """ Returns None if there are no messages.
            Always returns a list type object """
        boxtype = self.get_boxtype(boxtype)
        with ConnectionManager(self.username, self.password, self.ip) as client:
            sms_list = client.sms.get_sms_list(1, boxtype)
            count = int(sms_list['Count'])
            if count == 0:
                return
            elif count == 1:
                return [sms_list['Messages']['Message']]    # put the single dict in a list
            else:
                return sms_list['Messages']['Message']

    def get_unread_messages_from_inbox(self):
        messages = self.get_msgs('inbox')
        if messages is not None:
            unread_messages = [msg for msg in messages if (msg['Smstat'] == '0')]
            return unread_messages

    def get_latest_msg(self, boxtypes):
        messages = self.get_msgs(boxtypes)
        if messages is not None:
            # when there is only one message a dict is returned
            # if there are multiple, the dicts are returned in a list
            # we always want to return only a dictionary
            if isinstance(messages, list):
                return messages[0]
            else:
                return messages

    def clean_box(self, boxtype):
        messages = self.get_msgs(boxtype)
        if messages is not None:
            with ConnectionManager(self.username, self.password, self.ip) as client:
                for msg in messages:
                    id = msg['Index']
                    content = msg['Content']
                    resp = client.sms.delete_sms(id)
                    if resp != 'OK':
                        raise Exception(
                            "Failed to delete message with ID '{}' and content '{}'. Response: '{}'."\
                                .format(id, content, resp))

    def read_msg(self, index):
        # simple 'wrapper' function to have all the connections happening in the Router class
        with ConnectionManager(self.username, self.password, self.ip) as client:
            client.sms.set_read(index)


    # def verify_client_router_sync(self):
    #     client_date = datetime.today().replace(microsecond=0)
    #     self.client.save_sms([0000], "automatic test message to verify the client date and the router date is equal.")
    #     msg = self.get_latest_msg('drafts')
    #     router_date = datetime.strptime(msg['Date'], "%Y-%m-%d %H:%M:%S")
    #     self.client.sms.delete_sms(msg['Index'])