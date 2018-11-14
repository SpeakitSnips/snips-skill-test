#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import ConfigParser
from hermes_python.hermes import Hermes
from hermes_python.ontology import *
import io
from ctxmngr import ContextManager
from homein import HomeInMQTT
import pytoml


CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIG_INI = "config.ini"

class SnipsConfigParser(ConfigParser.SafeConfigParser):
    def to_dict(self):
        return {section : {option_name : option for option_name, option in self.items(section)} for section in self.sections()}


def read_configuration_file(configuration_file):
    try:
        with io.open(configuration_file, encoding=CONFIGURATION_ENCODING_FORMAT) as f:
            conf_parser = SnipsConfigParser()
            conf_parser.readfp(f)
            return conf_parser.to_dict()
    except (IOError, ConfigParser.Error) as e:
        return dict()

def subscribe_intent_callback(hermes, intentMessage):
    global context, homein
    conf = read_configuration_file(CONFIG_INI)
    action_wrapper(hermes, intentMessage, conf, context, homein)


def action_wrapper(hermes, intentMessage, conf, context, homein):
    hermes.publish_end_session(intentMessage.session_id, "Bonjour depuis Gitlab!")


if __name__ == "__main__":
    speakit_config = pytoml.loads(open("/etc/speakit.toml").read())
    ctxHost, ctxPort = speakit_config["homein"]["context"].split(":")
    ctxPort = int(ctxPort)

    homeinHost, homeinPort = speakit_config["homein"]["mqtt"].split(":")
    homeinPort = int(homeinPort)

    site = speakit_config["speakit"]["site"]

    context = ContextManager(ctxHost,ctxPort)
    homein = HomeInMQTT(homeinHost, homeinPort, site)

    with Hermes("localhost:1883") as h:
        h.subscribe_intent("Alice:TestGit", subscribe_intent_callback) \
         .start()
