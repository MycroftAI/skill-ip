# Copyright 2017 Mycroft AI Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import time
from os.path import dirname, join
from ifaddr import get_adapters, IP

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill, intent_handler
import mycroft.audio
from mycroft.util.log import LOG


def get_ifaces(ignore_list=None):
    """ Build a dict with device names and their associated ip address.

    Arguments:
        ignore_list(list): list of devices to ignore. Defaults to "lo"

    Returns:
        (dict) with device names as keys and ip addresses as value.
    """
    ignore_list = ignore_list or ['lo']
    res = {}
    for iface in get_adapters():
        # ignore "lo" (the local loopback)
        if iface.ips and iface.name not in ignore_list:
            for addr in iface.ips:
                if addr.is_IPv4:
                    res[iface.nice_name] = addr.ip
                    break
    return res


class IPSkill(MycroftSkill):
    SEC_PER_LETTER = 0.65  # timing based on Mark 1 screen
    LETTERS_PER_SCREEN = 9.0

    def __init__(self):
        super(IPSkill, self).__init__(name="IPSkill")

    @intent_handler(IntentBuilder("IPIntent").require("query").require("IP"))
    def handle_query_IP(self, message):
        addr = get_ifaces()
        dot = self.dialog_renderer.render("dot")

        if len(addr) == 0:
            self.speak_dialog("no network connection")
            return
        elif len(addr) == 1:
            self.enclosure.deactivate_mouth_events()
            iface, ip = addr.popitem()
            self.enclosure.mouth_text(ip)
            ip_spoken = ip.replace(".", " "+dot+" ")
            self.speak_dialog("my address is",
                              {'ip': ip_spoken})
            time.sleep((self.LETTERS_PER_SCREEN + len(ip)) *
                           self.SEC_PER_LETTER)
        else:
            self.enclosure.deactivate_mouth_events()
            for iface in addr:
                ip = addr[iface]
                self.enclosure.mouth_text(ip)
                ip_spoken = ip.replace(".", " " + dot + " ")
                self.speak_dialog("my address on X is Y",
                                 {'interface': iface, 'ip': ip_spoken})
                time.sleep((self.LETTERS_PER_SCREEN + len(ip)) *
                               self.SEC_PER_LETTER)

        mycroft.audio.wait_while_speaking()
        self.enclosure.activate_mouth_events()
        self.enclosure.mouth_reset()

    @intent_handler(IntentBuilder("").require("query").require("IP")
            .require("last").require("digits"))
    def handle_query_last_part_IP(self, message):
        addr = get_ifaces()
        if len(addr) == 0:
            self.speak_dialog("no network connection")
            return

        self.enclosure.deactivate_mouth_events()
        if "wlan0" in addr:
            ip_end = addr['wlan0'].split(".")[-1]
            self.speak_dialog("last digits", data={"digits": ip_end})
        elif "eth0" in addr:
            ip_end = addr['eth0'].split(".")[-1]
            self.speak_dialog("last digits", data={"digits": ip_end})
        self.enclosure.mouth_text(ip_end)
        time.sleep(3) # Show for at least 3 seconds

        mycroft.audio.wait_while_speaking()
        self.enclosure.activate_mouth_events()
        self.enclosure.mouth_reset()


def create_skill():
    return IPSkill()
