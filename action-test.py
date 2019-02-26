#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import ConfigParser
from hermes_python.hermes import Hermes
from hermes_python.ffi.utils import MqttOptions
from hermes_python.ontology import *
import io
from ctxmngr import ContextManager
from homein import HomeInMQTT
import pytoml
import random
import string
import json


CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIG_INI = "config.ini"

class SnipsConfigParser(ConfigParser.SafeConfigParser):
    def to_dict(self):
        return {section : {option_name : option for option_name, option in self.items(section)} for section in self.sections()}

def _random_id():
    return "".join(
        [random.choice(string.ascii_uppercase + string.digits) for i in range(16)]
    )

def _get_speakit_conf(key, default_value):
    global speakit_config
    return speakit_config["speakit"].get(key, default_value)

def read_configuration_file(configuration_file):
    try:
        with io.open(configuration_file, encoding=CONFIGURATION_ENCODING_FORMAT) as f:
            conf_parser = SnipsConfigParser()
            conf_parser.readfp(f)
            return conf_parser.to_dict()
    except (IOError, ConfigParser.Error) as e:
        return dict()

def subscribe_intent_callback(hermes, intentMessage):
    global homein
    conf = read_configuration_file(CONFIG_INI)
    action_wrapper(hermes, intentMessage, conf, homein)


def action_wrapper(hermes, intentMessage, conf, homein):
    hermes.publish_end_session(intentMessage.session_id, "Bonjour depuis Gitlab!")

if __name__ == "__main__":
    mqtt_opts = MqttOptions()
    
    speakit_config = pytoml.loads(open("/etc/speakit.toml").read())
    ctxHost, ctxPort = speakit_config["homein"]["context"].split(":")
    ctxPort = int(ctxPort)
    
    homeinHost, homeinPort = speakit_config["homein"]["mqtt"].split(":")
    homeinPort = int(homeinPort)

    context = ContextManager(ctxHost,ctxPort)
    homein = HomeInMQTT(homeinHost, homeinPort, speakit_config, context)

    with Hermes(mqtt_options=mqtt_opts) as h:
        h.subscribe_intent("Alice:TestGit", subscribe_intent_callback) \
         .start()