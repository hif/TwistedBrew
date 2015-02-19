#!/usr/bin python

import json


class MessageEnvelope:

    def __init__(self, receiver="", command="", subject_id=0, status=0, data=""):
        self.receiver = receiver
        self.command = command
        self.subject_id = subject_id
        self.status = status
        self.data = data

    def seal(self):
        json_dict = {"receiver": self.receiver,
                     "command": self.command,
                     "subject_id": self.subject_id,
                     "status": self.status,
                     "data": self.data}
        return json.dumps(json_dict, sort_keys=True)

    @staticmethod
    def open(json_str):
        json_obj = json.loads(json_str)
        sealed_msg = MessageEnvelope()
        sealed_msg.receiver = json_obj['receiver']
        sealed_msg.command = json_obj['command']
        sealed_msg.subject_id = json_obj['subject_id']
        sealed_msg.status = json_obj['status']
        sealed_msg.data = json_obj['data']
        return sealed_msg

    def __str__(self):
        fmt = "{{\"receiver\":\"{0}\",\"command\":\"{1}\",\"subject_id\":{2},\"status\":{3},\"data\":\"{4}\"}}"
        return fmt.format(self.receiver, self.command, self.subject_id, self.status, self.data)



