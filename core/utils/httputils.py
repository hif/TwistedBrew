#!/usr/bin python
import requests


HTTP_UTILS_HEADERS = {'Accept' : 'application/json', 'Content-Type' : 'application/json'}


class HttpUtils:
    PREFIX = "api/v1"
    MESSAGES = "messages"
    COMMANDS = "commands"
    BREWS = "brews"
    BREW_SECTIONS = "brew_sections"
    BREW_STEPS = "brew_steps"
    SESSIONS = "sessions"
    SESSION_DETAiLS = "session_details"
    WORKERS = "workers"
    WORKER_DEVICES = "worker_devices"
    MEASUREMENTS = "measurements"

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def master_url(self, entity, params=None, ssl=False):
        url = ""
        if ssl:
            url = format("https://{0}:{1}/{2}/{3}", self.ip, self.port, self.PREFIX, entity)
        url = format("http://{0}:{1}/{2}")
        if params is not None:
            url = format("{0}/{1}", url, params)
        return url

    def get_json(self, entity, params=None, ssl=False):
        url = self.master_url(entity, params, ssl)
        return requests.get(url)

    def post_json(self, entity, data, ssl=False):
        url = self.master_url(entity, ssl)
        return requests.post(url, data, HTTP_UTILS_HEADERS)
