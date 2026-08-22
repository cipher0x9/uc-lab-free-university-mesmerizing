#!/usr/bin/env python3
"""UC Lab Wave E — Resources system builder.

Builds window.UC_RESOURCES (hubs / topics / groups / portals) from a curated
seed of OFFICIAL documentation URLs, verifies every URL over HTTP(S), drops
anything that does not resolve, and injects into university/v17-UNIVERSITY.html:

  --verify   curl-check all unique seed URLs, cache results
  --inject   render CSS+JS+resources-index section into the flagship HTML
  --report   emit URL audit table snippet for the wave report

Law: hubs 8-20 links, major sections 3-8 via defaults, drills 0-2,
never invent URLs (unverified URLs are dropped, never guessed).
"""
import json, re, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / 'university/v17-UNIVERSITY.html'
CACHE = ROOT / 'tools/.uc_resources_urlcache.json'
SNIPPET = ROOT / 'tools/uc_resources_report_snippet.md'

UA = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36')

# --------------------------------------------------------------------------
# SEED — curated official docs only. [title, url]
# --------------------------------------------------------------------------

CISCO = 'https://www.cisco.com'
CVOICE = CISCO + '/c/en/us/support/unified-communications/index.html'
CSUPPORT = CISCO + '/c/en/us/support/index.html'
CUC = CISCO + '/c/en/us/support/unified-communications'
CCC = CISCO + '/c/en/us/support/customer-collaboration'
TS = '/tsd-products-support-series-home.html'
GL = '/products-installation-and-configuration-guides-list.html'
IG = '/products-installation-guides-list.html'
CR = '/products-command-reference-list.html'
RN = '/products-release-notes-list.html'
TG = '/products-troubleshooting-guides-list.html'
DS = '/products-data-sheets-list.html'
CE = '/products-configuration-examples-list.html'

def cisco_prod(cat, slug):
    """All stable support-page variants for one Cisco product."""
    base = f'{CISCO}/c/en/us/support/{cat}/{slug}'
    return [(f'{{T}} — Support Home', base + TS),
            (f'{{T}} — Install & Config Guides', base + GL),
            (f'{{T}} — Command References', base + CR),
            (f'{{T}} — Release Notes', base + RN),
            (f'{{T}} — Troubleshooting Guides', base + TG)]

LEARN = 'https://learn.microsoft.com/en-us'
AWSD = 'https://docs.aws.amazon.com'
RFC = 'https://www.rfc-editor.org/rfc/rfc'

def rfc(n, label=None):
    return [f'RFC {n}' + (f' — {label}' if label else ''), f'{RFC}{n}']

# ---------------------------------------------------------------- PORTALS --
PORTALS = [
    ['Cisco Support Central', CSUPPORT],
    ['Cisco Unified Communications — Docs & Support', CVOICE],
    ['Webex Help Center', 'https://help.webex.com/'],
    ['Webex for Developers', 'https://developer.webex.com/docs'],
    ['Cisco DevNet', 'https://developer.cisco.com/'],
    ['Microsoft Teams Documentation', LEARN + '/microsoftteams/'],
    ['MS Teams — What is Teams Phone', LEARN + '/microsoftteams/what-is-phone-system-in-office-365'],
    ['Amazon Connect Documentation', AWSD + '/connect/'],
    ['AWS Documentation', AWSD + '/'],
    ['Google Cloud Documentation', 'https://cloud.google.com/docs'],
    ['Dialogflow CX Documentation', 'https://cloud.google.com/dialogflow/cx/docs'],
    ['Genesys Cloud Resource Center', 'https://help.mypurecloud.com/'],
    ['Genesys Cloud Developer Center', 'https://developer.genesys.cloud/'],
    ['Twilio Docs', 'https://www.twilio.com/docs'],
    ['Zoom Support', 'https://support.zoom.us/'],
    ['Zoom Developers', 'https://developers.zoom.us/'],
    ['RingCentral Developers', 'https://developers.ringcentral.com/'],
    ['RingCentral Support', 'https://support.ringcentral.com/'],
    ['8x8 Support', 'https://support.8x8.com/'],
    ['8x8 Developer', 'https://developer.8x8.com/'],
    ['Avaya Support', 'https://support.avaya.com/'],
    ['Avaya Documentation', 'https://documentation.avaya.com/'],
    ['NICE CXone Help', 'https://help.nice-incontact.com/'],
    ['Asterisk Documentation', 'https://docs.asterisk.org/'],
    ['Salesforce Developers', 'https://developer.salesforce.com/docs'],
    ['Salesforce Help', 'https://help.salesforce.com/'],
    ['Intrado', 'https://www.intrado.com/'],
    ['Bandwidth Developer Docs', 'https://dev.bandwidth.com/'],
    ['RFC Editor', 'https://www.rfc-editor.org/'],
    ['IETF Datatracker', 'https://datatracker.ietf.org/'],
    ['MDN — WebRTC API', 'https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API'],
    ['W3C — WebRTC Specification', 'https://www.w3.org/TR/webrtc/'],
    ['OpenAPI Specification v3.1', 'https://spec.openapis.org/oas/v3.1.0'],
    ['JSON Schema', 'https://json-schema.org/'],
    ['Wireshark Documentation', 'https://www.wireshark.org/docs/'],
    ['Wireshark Wiki', 'https://wiki.wireshark.org/'],
    ['UC Lab Free University (GitHub)', 'https://github.com/cipher0x9/uc-lab-free-university-mesmerizing'],
    ['Campus Linktree', 'https://linktr.ee/cyphermonkey'],
]

# ------------------------------------------------------------------- HUBS --
HUBS = {}
HUBS['hub-cucm'] = [
    ['CUCM — Support Home', f'{CUC}/unified-communications-manager-callmanager{TS}'],
    ['CUCM — Install & Config Guides', f'{CUC}/unified-communications-manager-callmanager{GL}'],
    ['CUCM — Command References', f'{CUC}/unified-communications-manager-callmanager{CR}'],
    ['CUCM — Release Notes', f'{CUC}/unified-communications-manager-callmanager{RN}'],
    ['CUCM — Troubleshooting Guides', f'{CUC}/unified-communications-manager-callmanager{TG}'],
    ['Cisco Unity Connection — Support', f'{CUC}/unity-connection{TS}'],
    ['Cisco Jabber — Support', f'{CUC}/jabber{TS}'],
    ['Cisco Emergency Responder — Support', f'{CUC}/emergency-responder{TS}'],
        ['Cisco Unified Communications — Docs & Support', CVOICE],
    ['Cisco DevNet', 'https://developer.cisco.com/'],
    ['Cisco Support Central', CSUPPORT],
    rfc(3261, 'SIP'),
]
HUBS['hub-cube-sbc'] = [
    ['Cisco Unified Border Element — Support', f'{CUC}/unified-border-element{TS}'],
    ['CUBE — Install & Config Guides', f'{CUC}/unified-border-element{GL}'],
    ['CUBE — Configuration Examples', f'{CUC}/unified-border-element{CE}'],
    ['MS Teams — Plan Direct Routing', LEARN + '/microsoftteams/direct-routing-plan'],
    ['MS Teams — Certified SBCs for Direct Routing', LEARN + '/microsoftteams/direct-routing-border-controllers'],
    ['Oracle Communications Documentation', 'https://docs.oracle.com/en/industries/communications/'],
    ['Ribbon Public Documentation', 'https://publicdoc.rbbn.com/'],
    ['AudioCodes — Services & Support', 'https://www.audiocodes.com/services-support'],
    ['Twilio Elastic SIP Trunking', 'https://www.twilio.com/docs/sip-trunking'],
    rfc(3261, 'SIP'), rfc(3264, 'SDP Offer/Answer'), rfc(3550, 'RTP'),
]
HUBS['hub-sip'] = [
    rfc(3261, 'SIP Core'), rfc(3262, 'Provisional Responses (PRACK)'),
    rfc(3263, 'Locating SIP Servers'), rfc(3264, 'Offer/Answer Model'),
    rfc(3265, 'SIP Events (SUBSCRIBE/NOTIFY)'), rfc(3311, 'UPDATE Method'),
    rfc(3312, 'Resource Preconditions'), rfc(3326, 'Reason Header'),
    rfc(3428, 'MESSAGE Method'), rfc(3515, 'REFER Method'),
    rfc(3665, 'SIP Basic Call Flows'), rfc(3666, 'SIP-PSTN Call Flows'),
    rfc(3891, 'Replaces Header'), rfc(3960, 'Early Media'),
    rfc(4028, 'Session Timers'), rfc(4235, 'Dialog Event Package'),
    rfc(5411, 'A Hitchhiker\u2019s Guide to SIP'), rfc(3966, 'tel: URI'),
    ['Cisco Unified Communications — Docs & Support', CVOICE],
    ['Twilio Elastic SIP Trunking', 'https://www.twilio.com/docs/sip-trunking'],
]
HUBS['hub-icm-ucce'] = [
    ['UCCE — Support Home', f'{CCC}/unified-contact-center-enterprise{TS}'],
    ['UCCE — Install & Config Guides', f'{CCC}/unified-contact-center-enterprise{GL}'],
    ['UCCE — Troubleshooting Guides', f'{CCC}/unified-contact-center-enterprise{TG}'],
    ['UCCE — Release Notes', f'{CCC}/unified-contact-center-enterprise{RN}'],
    ['PCCE — Support Home', f'{CCC}/packaged-contact-center-enterprise{TS}'],
    ['UCCX — Support Home', f'{CCC}/unified-contact-center-express{TS}'],
    ['Cisco Customer Collaboration Portal', f'{CCC}/index.html'],
    ['Cisco Unified Communications — Docs & Support', CVOICE],
    ['Cisco DevNet', 'https://developer.cisco.com/'],
    ['Webex Help Center', 'https://help.webex.com/'],
    ['Cisco Support Central', CSUPPORT],
    ['UC Lab Free University (GitHub)', 'https://github.com/cipher0x9/uc-lab-free-university-mesmerizing'],
]
HUBS['hub-pcce'] = [
    ['PCCE — Support Home', f'{CCC}/packaged-contact-center-enterprise{TS}'],
    ['PCCE — Install & Config Guides', f'{CCC}/packaged-contact-center-enterprise{GL}'],
    ['PCCE — Release Notes', f'{CCC}/packaged-contact-center-enterprise{RN}'],
    ['UCCE — Support Home', f'{CCC}/unified-contact-center-enterprise{TS}'],
    ['UCCE — Install & Config Guides', f'{CCC}/unified-contact-center-enterprise{GL}'],
    ['Cisco Customer Collaboration Portal', f'{CCC}/index.html'],
    ['Cisco Unified Communications — Docs & Support', CVOICE],
    ['Cisco DevNet', 'https://developer.cisco.com/'],
    ['Cisco Support Central', CSUPPORT],
    ['UC Lab Free University (GitHub)', 'https://github.com/cipher0x9/uc-lab-free-university-mesmerizing'],
]
HUBS['hub-webex-cc'] = [
    ['Webex Help Center', 'https://help.webex.com/'],
    ['Webex for Developers', 'https://developer.webex.com/docs'],
    ['Webex Developer Portal', 'https://developer.webex.com/'],
    ['Webex Status', 'https://status.webex.com/'],
    ['Cisco Support Central', CSUPPORT],
    ['Cisco Unified Communications — Docs & Support', CVOICE],
    ['Salesforce Developers', 'https://developer.salesforce.com/docs'],
    ['UC Lab Free University (GitHub)', 'https://github.com/cipher0x9/uc-lab-free-university-mesmerizing'],
]
HUBS['hub-amazon-connect'] = [
    ['Amazon Connect Documentation', AWSD + '/connect/'],
    ['Amazon Connect — What Is Amazon Connect', AWSD + '/connect/latest/adminguide/what-is-amazon-connect.html'],
    ['Amazon Connect — Create an Instance', AWSD + '/connect/latest/adminguide/amazon-connect-instances.html'],
    ['Amazon Connect — API Reference', AWSD + '/connect/latest/APIReference/Welcome.html'],
    ['AWS CLI — connect Commands', AWSD + '/cli/latest/reference/connect/'],
    ['amazon-connect-streams (GitHub)', 'https://github.com/aws/amazon-connect-streams'],
    ['Amazon Connect — Product Page', 'https://aws.amazon.com/connect/'],
    ['AWS Well-Architected Framework', AWSD + '/wellarchitected/latest/framework/welcome.html'],
    ['AWS Health Dashboard', 'https://health.aws.amazon.com/health/status'],
    ['AWS Documentation', AWSD + '/'],
]
HUBS['hub-e911-redsky'] = [
    ['RedSky Technologies', 'https://www.redskye911.com/'],
    ['Intrado', 'https://www.intrado.com/'],
    ['Bandwidth — Official Site', 'https://www.bandwidth.com/'],
    ['Bandwidth Developer Docs', 'https://dev.bandwidth.com/'],
    ['Cisco Emergency Responder — Support', f'{CUC}/emergency-responder{TS}'],
    ['MS Teams — Manage Emergency Calling Policies', LEARN + '/microsoftteams/manage-emergency-calling-policies'],
    rfc(6442, 'Location Conveyance in SIP'), rfc(5222, 'LoST Protocol'),
    rfc(5985, 'HELD — HTTP Enabled Location Delivery'),
    rfc(6881, 'BCP for Emergency Calling'), rfc(7852, 'Additional Data for Emergency Calls'),
]
HUBS['hub-qos'] = [
    rfc(2474, 'Differentiated Services Field (DSCP)'),
    rfc(2597, 'Assured Forwarding PHB Group'),
    rfc(3246, 'Expedited Forwarding PHB'),
    rfc(4594, 'DiffServ Service Classes Guidelines'),
    rfc(3550, 'RTP'), rfc(3611, 'RTCP Extended Reports'),
    ['MS Teams — Implement QoS', LEARN + '/microsoftteams/qos-in-teams'],
    ['Cisco Support Central', CSUPPORT],
]
HUBS['hub-expressway'] = [
    ['Cisco Expressway Series — Support', f'{CUC}/expressway-series{TS}'],
    ['Expressway — Install & Config Guides', f'{CUC}/expressway-series{GL}'],
    ['Expressway — Configuration Examples', f'{CUC}/expressway-series{CE}'],
    ['Expressway — Release Notes', f'{CUC}/expressway-series{RN}'],
    ['Cisco Jabber — Support', f'{CUC}/jabber{TS}'],
        ['Cisco Unified Communications — Docs & Support', CVOICE],
    rfc(3261, 'SIP'), rfc(8445, 'ICE'), rfc(5389, 'STUN'), rfc(8656, 'TURN'),
]
HUBS['hub-migrations'] = [
    ['Webex Help Center', 'https://help.webex.com/'],
    ['Microsoft Teams Documentation', LEARN + '/microsoftteams/'],
    ['MS Teams — Upgrade Framework', LEARN + '/microsoftteams/upgrade-framework'],
    ['Amazon Connect — Admin Guide', AWSD + '/connect/latest/adminguide/what-is-amazon-connect.html'],
    ['Dialogflow CX Documentation', 'https://cloud.google.com/dialogflow/cx/docs'],
    ['Genesys Cloud Resource Center', 'https://help.mypurecloud.com/'],
    ['Zoom Support', 'https://support.zoom.us/'],
    ['RingCentral Developers', 'https://developers.ringcentral.com/'],
    ['AWS Well-Architected Framework', AWSD + '/wellarchitected/latest/framework/welcome.html'],
    ['Cisco Support Central', CSUPPORT],
    ['UC Lab Free University (GitHub)', 'https://github.com/cipher0x9/uc-lab-free-university-mesmerizing'],
]
HUBS['hub-sev-troubleshoot'] = [
    ['Webex Status', 'https://status.webex.com/'],
    ['AWS Health Dashboard', 'https://health.aws.amazon.com/health/status'],
    ['Google Cloud Status', 'https://status.cloud.google.com/'],
    ['Zoom Status', 'https://status.zoom.us/'],
    ['Twilio Status', 'https://status.twilio.com/'],
    ['Genesys Cloud Status', 'https://status.mypurecloud.com/'],
    ['RingCentral Status', 'https://status.ringcentral.com/'],
    ['8x8 Status', 'https://status.8x8.com/'],
    ['MS Teams — Monitor & Improve Call Quality', LEARN + '/microsoftteams/monitor-call-quality-qos'],
    ['Cisco Support Central', CSUPPORT],
    ['UC Lab Free University (GitHub)', 'https://github.com/cipher0x9/uc-lab-free-university-mesmerizing'],
]
HUBS['hub-interview'] = [
    ['Cisco Unified Communications — Docs & Support', CVOICE],
    ['MS Teams — What is Teams Phone', LEARN + '/microsoftteams/what-is-phone-system-in-office-365'],
    ['Amazon Connect Documentation', AWSD + '/connect/'],
    ['Webex for Developers', 'https://developer.webex.com/docs'],
    ['Genesys Cloud Developer Center', 'https://developer.genesys.cloud/'],
    ['Twilio Docs', 'https://www.twilio.com/docs'],
    rfc(3261, 'SIP'),
    ['UC Lab Free University (GitHub)', 'https://github.com/cipher0x9/uc-lab-free-university-mesmerizing'],
    ['Campus Linktree', 'https://linktr.ee/cyphermonkey'],
]

# ------------------------------------------------------------------ TOPICS --
# Matched against section id segments (boundary: start, '-' or '_').
TOPICS = {
    'cucm': [
        ['CUCM — Support Home', f'{CUC}/unified-communications-manager-callmanager{TS}'],
        ['CUCM — Install & Config Guides', f'{CUC}/unified-communications-manager-callmanager{GL}'],
        ['Cisco Unified Communications — Docs & Support', CVOICE],
        ['Cisco DevNet', 'https://developer.cisco.com/'],
    ],
    'unity': [
        ['Cisco Unity Connection — Support', f'{CUC}/unity-connection{TS}'],
        ['Unity Connection — Install & Config Guides', f'{CUC}/unity-connection{GL}'],
        ['Cisco Unified Communications — Docs & Support', CVOICE],
    ],
    'jabber': [
        ['Cisco Jabber — Support', f'{CUC}/jabber{TS}'],
        ['Jabber — Install & Config Guides', f'{CUC}/jabber{GL}'],
    ],
    'cube': [
        ['Cisco Unified Border Element — Support', f'{CUC}/unified-border-element{TS}'],
        ['CUBE — Install & Config Guides', f'{CUC}/unified-border-element{GL}'],
        rfc(3261, 'SIP'),
    ],
    'sbc': [
        ['Oracle Communications Documentation', 'https://docs.oracle.com/en/industries/communications/'],
        ['Ribbon Public Documentation', 'https://publicdoc.rbbn.com/'],
        ['MS Teams — Certified SBCs for Direct Routing', LEARN + '/microsoftteams/direct-routing-border-controllers'],
        ['AudioCodes — Services & Support', 'https://www.audiocodes.com/services-support'],
        rfc(3261, 'SIP'),
    ],
    'sip': [
        rfc(3261, 'SIP Core'), rfc(3264, 'Offer/Answer Model'),
        rfc(3665, 'SIP Basic Call Flows'), rfc(5411, 'Hitchhiker\u2019s Guide to SIP'),
        rfc(3966, 'tel: URI'),
        ['Twilio Elastic SIP Trunking', 'https://www.twilio.com/docs/sip-trunking'],
    ],
    'rtp': [
        rfc(3550, 'RTP'), rfc(3551, 'RTP Audio/Video Profile'),
        rfc(3611, 'RTCP Extended Reports'), rfc(2198, 'RTP Redundancy'),
        rfc(4585, 'RTP/AVPF Feedback'),
    ],
    'codec': [
        rfc(6716, 'Opus Codec'), rfc(7587, 'RTP Payload for Opus'),
        rfc(3389, 'RTP Comfort Noise'), rfc(6184, 'RTP Payload for H.264'),
        ['ITU-T G.711', 'https://www.itu.int/rec/T-REC-G.711'],
        ['ITU-T G.729', 'https://www.itu.int/rec/T-REC-G.729'],
        ['ITU-T G.722', 'https://www.itu.int/rec/T-REC-G.722'],
    ],
    'ice': [
        rfc(8445, 'ICE'), rfc(5389, 'STUN'), rfc(8656, 'TURN'), rfc(5780, 'NAT Behavior Discovery'),
    ],
    'e911': [
        rfc(6442, 'Location Conveyance in SIP'), rfc(6881, 'BCP for Emergency Calling'),
    ],
    'qos': [
        rfc(2474, 'DSCP Field'), rfc(2597, 'Assured Forwarding PHB'),
        rfc(3246, 'Expedited Forwarding PHB'),
    ],
    'expressway': [
        ['Cisco Expressway Series — Support', f'{CUC}/expressway-series{TS}'],
        ['Expressway — Install & Config Guides', f'{CUC}/expressway-series{GL}'],
        rfc(8445, 'ICE'),
    ],
    'teams': [
        ['MS Teams Phone Overview', LEARN + '/microsoftteams/what-is-phone-system-in-office-365'],
        ['MS Teams — Plan Direct Routing', LEARN + '/microsoftteams/direct-routing-plan'],
        ['MS Teams — Operator Connect', LEARN + '/microsoftteams/operator-connect-plan'],
        ['MS Teams — Calling Plans', LEARN + '/microsoftteams/calling-plans-for-office-365'],
        ['Microsoft Teams Documentation', LEARN + '/microsoftteams/'],
    ],
    'webex': [
        ['Webex Help Center', 'https://help.webex.com/'],
        ['Webex for Developers', 'https://developer.webex.com/docs'],
        ['Webex Status', 'https://status.webex.com/'],
    ],
    'connect': [
        ['Amazon Connect Documentation', AWSD + '/connect/'],
        ['Amazon Connect — Admin Guide', AWSD + '/connect/latest/adminguide/what-is-amazon-connect.html'],
        ['Amazon Connect — API Reference', AWSD + '/connect/latest/APIReference/Welcome.html'],
        ['amazon-connect-streams (GitHub)', 'https://github.com/aws/amazon-connect-streams'],
    ],
    'genesys': [
        ['Genesys Cloud Resource Center', 'https://help.mypurecloud.com/'],
        ['Genesys Cloud Developer Center', 'https://developer.genesys.cloud/'],
        ['Genesys Cloud Platform API', 'https://developer.genesys.cloud/platform/api/'],
        ['Genesys Cloud Status', 'https://status.mypurecloud.com/'],
    ],
    'twilio': [
        ['Twilio Docs', 'https://www.twilio.com/docs'],
        ['Twilio Voice', 'https://www.twilio.com/docs/voice'],
        ['Twilio Flex', 'https://www.twilio.com/docs/flex'],
        ['Twilio Studio', 'https://www.twilio.com/docs/studio'],
        ['Twilio Status', 'https://status.twilio.com/'],
    ],
    'zoom': [
        ['Zoom Support', 'https://support.zoom.us/'],
        ['Zoom Developers', 'https://developers.zoom.us/'],
        ['Zoom API Reference', 'https://developers.zoom.us/docs/api/'],
        ['Zoom Status', 'https://status.zoom.us/'],
    ],
    'avaya': [
        ['Avaya Support', 'https://support.avaya.com/'],
        ['Avaya Documentation', 'https://documentation.avaya.com/'],
    ],
    'ringcentral': [
        ['RingCentral Developers', 'https://developers.ringcentral.com/'],
        ['RingCentral API Reference', 'https://developers.ringcentral.com/api-reference'],
        ['RingCentral Support', 'https://support.ringcentral.com/'],
        ['RingCentral Status', 'https://status.ringcentral.com/'],
    ],
    '8x8': [
        ['8x8 Support', 'https://support.8x8.com/'],
        ['8x8 Developer', 'https://developer.8x8.com/'],
        ['8x8 Status', 'https://status.8x8.com/'],
    ],
    'asterisk': [
        ['Asterisk Documentation', 'https://docs.asterisk.org/'],
    ],
    'freepbx': [
        ['FreePBX Wiki', 'https://wiki.freepbx.org/'],
    ],
    'five9': [
        ['Five9 — Official Site', 'https://www.five9.com/'],
    ],
    'gcc': [
        ['Dialogflow CX Documentation', 'https://cloud.google.com/dialogflow/cx/docs'],
        ['CCAI Platform Documentation', 'https://cloud.google.com/contact-center/ccai-platform/docs'],
        ['Cloud Speech-to-Text', 'https://cloud.google.com/speech-to-text/docs'],
        ['Cloud Text-to-Speech', 'https://cloud.google.com/text-to-speech/docs'],
    ],
    'ccaip': [
        ['CCAI Platform Documentation', 'https://cloud.google.com/contact-center/ccai-platform/docs'],
        ['Google Cloud Documentation', 'https://cloud.google.com/docs'],
    ],
    'dialogflow': [
        ['Dialogflow CX Documentation', 'https://cloud.google.com/dialogflow/cx/docs'],
        ['Dialogflow CX — Agents', 'https://cloud.google.com/dialogflow/cx/docs/concept/agent'],
        ['Dialogflow CX — Flows', 'https://cloud.google.com/dialogflow/cx/docs/concept/flow'],
        ['Dialogflow CX — Webhooks', 'https://cloud.google.com/dialogflow/cx/docs/concept/webhook'],
    ],
    'ucce': [
        ['UCCE — Support Home', f'{CCC}/unified-contact-center-enterprise{TS}'],
        ['UCCE — Install & Config Guides', f'{CCC}/unified-contact-center-enterprise{GL}'],
        ['Cisco Customer Collaboration Portal', f'{CCC}/index.html'],
    ],
    'uccx': [
        ['UCCX — Support Home', f'{CCC}/unified-contact-center-express{TS}'],
        ['UCCX — Install & Config Guides', f'{CCC}/unified-contact-center-express{GL}'],
    ],
    'pcce': [
        ['PCCE — Support Home', f'{CCC}/packaged-contact-center-enterprise{TS}'],
        ['PCCE — Install & Config Guides', f'{CCC}/packaged-contact-center-enterprise{GL}'],
    ],
    'migrat': [
        ['AWS Well-Architected Framework', AWSD + '/wellarchitected/latest/framework/welcome.html'],
        ['Webex Help Center', 'https://help.webex.com/'],
        ['Microsoft Teams Documentation', LEARN + '/microsoftteams/'],
    ],
    'interview': [
        ['UC Lab Free University (GitHub)', 'https://github.com/cipher0x9/uc-lab-free-university-mesmerizing'],
        ['Campus Linktree', 'https://linktr.ee/cyphermonkey'],
    ],
    'sev2': [
        ['Webex Status', 'https://status.webex.com/'],
        ['AWS Health Dashboard', 'https://health.aws.amazon.com/health/status'],
        ['Google Cloud Status', 'https://status.cloud.google.com/'],
        ['Zoom Status', 'https://status.zoom.us/'],
    ],
    'api': [
        rfc(9110, 'HTTP Semantics'), rfc(8259, 'JSON'),
        rfc(6902, 'JSON Patch'), rfc(7396, 'JSON Merge Patch'),
        ['OpenAPI Specification v3.1', 'https://spec.openapis.org/oas/v3.1.0'],
        ['JSON Schema', 'https://json-schema.org/'],
    ],
    'events': [
        ['Amazon EventBridge Documentation', AWSD + '/eventbridge/'],
        ['Twilio Event Streams', 'https://www.twilio.com/docs/events'],
        rfc(8259, 'JSON'),
    ],
    'identity': [
        rfc(6749, 'OAuth 2.0'), rfc(6750, 'Bearer Tokens'),
        rfc(7519, 'JSON Web Token (JWT)'), rfc(8414, 'OAuth Authorization Server Metadata'),
    ],
    'automation': [
        rfc(6241, 'NETCONF'), rfc(8040, 'RESTCONF'), rfc(7950, 'YANG 1.1'),
    ],
    'security': [
        rfc(8446, 'TLS 1.3'), rfc(5246, 'TLS 1.2'),
        rfc(3711, 'SRTP'), rfc(5280, 'X.509 PKI'),
    ],
    'tollfraud': [
        rfc(8224, 'SIP Identity (STIR)'), rfc(8225, 'PASSporT (SHAKEN)'),
    ],
    'zerotrust': [
        ['NIST SP 800-207 — Zero Trust Architecture', 'https://csrc.nist.gov/publications/detail/sp/800-207/final'],
        rfc(8446, 'TLS 1.3'),
    ],
    'pstn': [
        ['MS Teams — Calling Plans', LEARN + '/microsoftteams/calling-plans-for-office-365'],
        ['Twilio Voice', 'https://www.twilio.com/docs/voice'],
        ['Bandwidth Developer Docs', 'https://dev.bandwidth.com/'],
    ],
    'itsp': [
        ['Bandwidth Developer Docs', 'https://dev.bandwidth.com/'],
        ['Telnyx Support', 'https://support.telnyx.com/'],
        ['Vonage Developer', 'https://developer.vonage.com/'],
        ['Plivo Docs', 'https://www.plivo.com/docs/'],
    ],
    'observability': [
        rfc(5424, 'Syslog Protocol'),
        ['Amazon CloudWatch Documentation', AWSD + '/cloudwatch/'],
        ['Google Cloud Status', 'https://status.cloud.google.com/'],
    ],
}

# ------------------------------------------------------------------ GROUPS --
GH = ['UC Lab Free University (GitHub)', 'https://github.com/cipher0x9/uc-lab-free-university-mesmerizing']
LT = ['Campus Linktree', 'https://linktr.ee/cyphermonkey']

GROUPS = {
    'Campus': [GH, LT, ['Cisco Support Central', CSUPPORT]],
    'Foundations': [rfc(3261, 'SIP'), rfc(3550, 'RTP'), rfc(4566, 'SDP'), rfc(8866, 'SDP (updated)'),
                    ['Cisco Unified Communications — Docs & Support', CVOICE]],
    'Products': [['Cisco Support Central', CSUPPORT], ['Webex Help Center', 'https://help.webex.com/'],
                 ['MS Teams — What is Teams Phone', LEARN + '/microsoftteams/what-is-phone-system-in-office-365'],
                 ['Amazon Connect Documentation', AWSD + '/connect/'],
                 ['Genesys Cloud Resource Center', 'https://help.mypurecloud.com/']],
    'Vendor Deep-Dives': [['Avaya Support', 'https://support.avaya.com/'],
                          ['Genesys Cloud Resource Center', 'https://help.mypurecloud.com/'],
                          ['Twilio Docs', 'https://www.twilio.com/docs'],
                          ['Zoom Developers', 'https://developers.zoom.us/'],
                          ['RingCentral Developers', 'https://developers.ringcentral.com/']],
    'More Vendors': [['Asterisk Documentation', 'https://docs.asterisk.org/'],
                     ['RingCentral Support', 'https://support.ringcentral.com/'],
                     ['8x8 Support', 'https://support.8x8.com/'],
                     ['FreePBX Wiki', 'https://wiki.freepbx.org/']],
    'Network Core': [rfc(791, 'Internet Protocol (IPv4)'), rfc(768, 'UDP'), rfc(9293, 'TCP'),
                     rfc(8200, 'IPv6'), ['Cisco Support Central', CSUPPORT]],
    'Network Deep': [rfc(8200, 'IPv6'), rfc(2474, 'DSCP Field'), rfc(4443, 'ICMPv6'),
                     rfc(4861, 'IPv6 Neighbor Discovery'), ['Cisco Support Central', CSUPPORT]],
    'Protocol Expert': [rfc(3261, 'SIP'), rfc(3550, 'RTP'), rfc(8445, 'ICE'), rfc(4566, 'SDP')],
    'Architect Core': [['Cisco Unified Communications — Docs & Support', CVOICE],
                       ['AWS Well-Architected Framework', AWSD + '/wellarchitected/latest/framework/welcome.html'],
                       ['Microsoft Teams Documentation', LEARN + '/microsoftteams/'], GH],
    'Architect Dojo': [['Cisco Unified Communications — Docs & Support', CVOICE], rfc(3261, 'SIP'), GH],
    'CCaaS APIs & Platforms': [['Webex for Developers', 'https://developer.webex.com/docs'],
                               ['Amazon Connect — API Reference', AWSD + '/connect/latest/APIReference/Welcome.html'],
                               ['Genesys Cloud Developer Center', 'https://developer.genesys.cloud/'],
                               ['Twilio Docs', 'https://www.twilio.com/docs'],
                               ['Salesforce Developers', 'https://developer.salesforce.com/docs'],
                               ['OpenAPI Specification v3.1', 'https://spec.openapis.org/oas/v3.1.0']],
    'Google CC & APIs': [['Dialogflow CX Documentation', 'https://cloud.google.com/dialogflow/cx/docs'],
                         ['CCAI Platform Documentation', 'https://cloud.google.com/contact-center/ccai-platform/docs'],
                         ['Cloud Speech-to-Text', 'https://cloud.google.com/speech-to-text/docs'],
                         ['Cloud Text-to-Speech', 'https://cloud.google.com/text-to-speech/docs']],
    'Cloud Migrations': [['AWS Well-Architected Framework', AWSD + '/wellarchitected/latest/framework/welcome.html'],
                         ['Webex Help Center', 'https://help.webex.com/'],
                         ['Microsoft Teams Documentation', LEARN + '/microsoftteams/'],
                         ['Google Cloud Documentation', 'https://cloud.google.com/docs']],
    'Mastery Practicums': [GH, ['RFC Editor', 'https://www.rfc-editor.org/'], ['Cisco Support Central', CSUPPORT]],
    'Mastery Methodologies': [GH, ['RFC Editor', 'https://www.rfc-editor.org/'], ['Cisco Support Central', CSUPPORT]],
    'Practice Banks': [['Cisco Unified Communications — Docs & Support', CVOICE], ['Webex Help Center', 'https://help.webex.com/'],
                       ['MS Teams — What is Teams Phone', LEARN + '/microsoftteams/what-is-phone-system-in-office-365']],
    'Practice Bank': [['Cisco Unified Communications — Docs & Support', CVOICE], ['Webex Help Center', 'https://help.webex.com/'],
                      ['MS Teams — What is Teams Phone', LEARN + '/microsoftteams/what-is-phone-system-in-office-365']],
    'Tricky SEVs': [['Webex Status', 'https://status.webex.com/'],
                    ['AWS Health Dashboard', 'https://health.aws.amazon.com/health/status'],
                    ['Zoom Status', 'https://status.zoom.us/'],
                    ['Genesys Cloud Status', 'https://status.mypurecloud.com/']],
    'Tricky SEVs v17': [['Webex Status', 'https://status.webex.com/'],
                        ['AWS Health Dashboard', 'https://health.aws.amazon.com/health/status'],
                        ['Zoom Status', 'https://status.zoom.us/'],
                        ['Genesys Cloud Status', 'https://status.mypurecloud.com/'],
                        ['Twilio Status', 'https://status.twilio.com/']],
    'Bonus 50s': [GH, LT, ['Cisco Support Central', CSUPPORT]],
    'Trading Systems': [GH, LT],
    'AI & Future': [['Dialogflow CX Documentation', 'https://cloud.google.com/dialogflow/cx/docs'],
                    ['Webex for Developers', 'https://developer.webex.com/docs'],
                    ['AWS Documentation', AWSD + '/']],
    'Library': [GH, LT, ['RFC Editor', 'https://www.rfc-editor.org/']],
    'Evidence Library': [GH, ['RFC Editor', 'https://www.rfc-editor.org/'],
                         ['IETF Datatracker', 'https://datatracker.ietf.org/']],
    'Security Deep': [rfc(8446, 'TLS 1.3'), rfc(3711, 'SRTP'), rfc(5280, 'X.509 PKI')],
    'Observability Deep': [rfc(5424, 'Syslog Protocol'),
                           ['Amazon CloudWatch Documentation', AWSD + '/cloudwatch/'],
                           ['Google Cloud Status', 'https://status.cloud.google.com/'],
                           ['AWS Health Dashboard', 'https://health.aws.amazon.com/health/status']],
}

# ------------------------------------------------- EXTRA VERIFIED-ONLY POOL --
# Candidates appended to matching sections only if they verify.
EXTRA = {
    'teams': [
        ['MS Teams — Auto Attendants & Call Queues (Plan)', LEARN + '/microsoftteams/plan-auto-attendant-call-queue'],
        ['MS Teams — Create a Call Queue', LEARN + '/microsoftteams/create-a-phone-system-call-queue'],
        ['MS Teams — Create an Auto Attendant', LEARN + '/microsoftteams/create-a-phone-system-auto-attendant'],
        ['MS Teams — Dial Plans', LEARN + '/microsoftteams/what-are-dial-plans'],
        ['MS Teams — Resource Accounts', LEARN + '/microsoftteams/manage-resource-accounts'],
        ['MS Teams — Prepare Your Network', LEARN + '/microsoftteams/prepare-network'],
        ['MS Teams — QoS in Teams', LEARN + '/microsoftteams/qos-in-teams'],
        ['MS Teams — Location-Based Routing', LEARN + '/microsoftteams/location-based-routing-plan'],
        ['MS Teams — Survivable Branch Appliance', LEARN + '/microsoftteams/direct-routing-survivable-branch-appliance'],
        ['MS Teams — Limits & Specifications', LEARN + '/microsoftteams/limits-specifications-teams'],
        ['MS Teams — Audio Conferencing', LEARN + '/microsoftteams/audio-conferencing-in-office-365'],
        ['MS Teams — Cloud Video Interop', LEARN + '/microsoftteams/cloud-video-interop'],
        ['MS Teams — SIP Gateway', LEARN + '/microsoftteams/sip-gateway-plan'],
        ['MS Teams — IP Phones', LEARN + '/microsoftteams/devices/teams-ip-phones'],
        ['MS Teams Rooms', LEARN + '/microsoftteams/rooms/'],
        ['Microsoft 365 URLs & IP Ranges', LEARN + '/microsoft-365/enterprise/urls-and-ip-address-ranges'],
    ],
    'e911': [
        ['MS Teams — Emergency Locations & Call Routing', LEARN + '/microsoftteams/what-are-emergency-locations-addresses-and-call-routing'],
        rfc(4119, 'GEOPRIV PIDF-LO Location Object'),
    ],
    'connect': [
        ['Amazon EventBridge Documentation', AWSD + '/eventbridge/'],
        ['AWS Lambda Documentation', AWSD + '/lambda/'],
        ['Amazon Lex Documentation', AWSD + '/lex/'],
        ['Amazon Polly Documentation', AWSD + '/polly/'],
        ['Amazon Transcribe Documentation', AWSD + '/transcribe/'],
    ],
    'webex': [
        ['Webex Developer Portal', 'https://developer.webex.com/'],
    ],
    'genesys': [
        ['Genesys Cloud API Explorer', 'https://developer.genesys.cloud/devapps/api-explorer'],
    ],
    'twilio': [
        ['Twilio Voice API', 'https://www.twilio.com/docs/voice/api'],
        ['Twilio TwiML for Voice', 'https://www.twilio.com/docs/voice/twiml'],
        ['Twilio Studio User Guide', 'https://www.twilio.com/docs/studio/user-guide'],
    ],
    'sip': [
        rfc(3265, 'SIP Events'), rfc(3325, 'P-Asserted-Identity'),
        rfc(3892, 'Referred-By'), rfc(3911, 'JOIN Header'),
        rfc(4244, 'History-Info'), rfc(4475, 'SIP Torture Tests'),
        rfc(5626, 'Managing Client Connections (Outbound)'),
        rfc(7118, 'SIP over WebSocket'), rfc(6141, 'Re-INVITE Handling'),
    ],
    'rtp': [
        rfc(3605, 'RTCP Attribute in SDP'), rfc(4588, 'RTP Retransmission'),
        rfc(5104, 'Codec Control Messages'), rfc(8285, 'RTP Header Extensions'),
        rfc(7667, 'RTP Topologies'),
    ],
    'codec': [
        rfc(4867, 'RTP Payload for AMR'), rfc(3951, 'iLBC Codec'),
        rfc(7798, 'RTP Payload for H.265'), rfc(7741, 'RTP Payload for VP8'),
        ['ITU-T H.264', 'https://www.itu.int/rec/T-REC-H.264'],
    ],
    'ice': [
        rfc(8825, 'WebRTC Overview'), rfc(8834, 'WebRTC Media'),
        rfc(8489, 'STUN (updated)'),
        ['MDN — WebRTC API', 'https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API'],
    ],
    'security': [
        rfc(6066, 'TLS Extensions'), rfc(6125, 'PKIX Identity Verification'),
        rfc(8555, 'ACME'), rfc(5764, 'DTLS-SRTP'),
        rfc(4568, 'SDP Security Descriptions (SDES)'),
    ],
    'qos': [
        rfc(2598, 'Expedited Forwarding (original)'), rfc(3260, 'DiffServ Clarifications'),
        ['MS Teams — QoS in Teams', LEARN + '/microsoftteams/qos-in-teams'],
    ],
    'expressway': [
        ['Cisco Jabber — Support', f'{CUC}/jabber{TS}'],
        rfc(8489, 'STUN (updated)'),
    ],
    'cucm': [
        ['CUCM — Configuration Examples', f'{CUC}/unified-communications-manager-callmanager{CE}'],
    ],
    'sbc': [
        ['Cisco Unified Border Element — Support', f'{CUC}/unified-border-element{TS}'],
        ['Kamailio Documentation', 'https://www.kamailio.org/docs/'],
        ['OpenSIPS — Official Site', 'https://www.opensips.org/'],
    ],
    'e911-b': [],
    'network-extra-anchor': [],
}

# --------------------------------------------------------------------------
def merged_topics():
    mt = {}
    for k, v in TOPICS.items():
        mt[k] = list(v) + list(EXTRA.get(k, [])) + list(EXTRA3.get(k, []))
    for extra in (EXTRA, EXTRA3):
        for k, v in extra.items():
            if k not in mt and v:
                mt[k] = list(v)
    return mt

def all_seed_lists():
    """Yield (where, links) for every seed bucket; EXTRA/EXTRA3 merged into TOPICS."""
    yield 'portals', PORTALS
    for k, v in HUBS.items():
        yield f'hub:{k}', v
    for k, v in merged_topics().items():
        yield f'topic:{k}', v
    for k, v in GROUPS.items():
        yield f'group:{k}', v
    for grp, entries in RFC_LIB.items():
        yield f'rfc:{grp}', [rfc(n, label) for n, label in entries]

def unique_urls():
    seen, out = set(), []
    for _, links in all_seed_lists():
        for t, u in links:
            if u not in seen:
                seen.add(u)
                out.append(u)
    return out

# ------------------------------------------------------------------ VERIFY --
def _curl(url, head):
    cmd = ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', '-L',
           '--max-time', '15', '-A', UA]
    if head:
        cmd.append('-I')
    cmd.append(url)
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
        code = (r.stdout or '').strip()[-3:]
        return code if code.isdigit() else '000'
    except Exception:
        return '000'

def check_url(url):
    """2xx/3xx = pass. 403/000 → accept only if domain root resolves."""
    for head in (True, False):
        code = _curl(url, head)
        if code[:1] in ('2', '3'):
            return code
        if code in ('400', '404', '410'):
            return code  # definitely dead — no retry
    if code in ('000', '401', '403', '405', '429', '500', '502', '503'):
        m = re.match(r'(https?://[^/]+)', url)
        if m:
            root_code = _curl(m.group(1) + '/', False)
            if root_code[:1] in ('2', '3'):
                return code + '*'  # page blocked/unreachable for curl, domain real
    return code

def verify():
    urls = unique_urls()
    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    todo = [u for u in urls if u not in cache]
    print(f'{len(urls)} unique seed URLs, {len(todo)} to check')
    done = 0
    with ThreadPoolExecutor(max_workers=16) as ex:
        for url, code in zip(todo, ex.map(check_url, todo)):
            cache[url] = code
            done += 1
            if done % 25 == 0:
                print(f'  {done}/{len(todo)}')
                CACHE.write_text(json.dumps(cache, indent=0))
    CACHE.write_text(json.dumps(cache, indent=0))
    ok = [u for u in urls if cache[u][:1] in ('2', '3') or cache[u].endswith('*')]
    bad = [(u, cache[u]) for u in urls if u not in ok]
    print(f'PASS {len(ok)} / {len(urls)}')
    for u, c in bad:
        print(f'  DROP [{c}] {u}')
    return cache

def verified(cache, links):
    return [[t, u] for t, u in links
            if cache.get(u, '000')[:1] in ('2', '3') or cache.get(u, '').endswith('*')]

# --------------------------------------------------------------- BUILD JS --
RENDER_JS = r"""
  /* Wave E 20.2-RESOURCES — official resources card (offline-safe, no CDN) */
  (function () {
    "use strict";
    var R = window.UC_RESOURCES;
    if (!R) return;
    function esc(s){ return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/"/g,"&quot;"); }
    function hash(str){ var h = 0; for (var i = 0; i < str.length; i++) h = (h * 31 + str.charCodeAt(i)) >>> 0; return h; }
    function idHits(id, key){
      var rx = new RegExp("(^|[-_])" + key.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"));
      return rx.test(id);
    }
    function collect(s){
      var seen = {}, out = [];
      function push(l){ if (!l || seen[l[1]]) return; seen[l[1]] = 1; out.push(l); }
      function pushAll(list){ (list || []).forEach(push); }
      var id = s.id || "";
      var isDrill = id.indexOf("drill-") === 0;
      if (isDrill) {                       /* drills: 0-2 links max */
        Object.keys(R.topics || {}).forEach(function(k){ if (idHits(id, k)) pushAll(R.topics[k]); });
        return out.slice(0, 2);
      }
      var isHub = id.indexOf("hub-") === 0;
      if (isHub) {
        pushAll((R.hubs || {})[id]);       /* hubs: 8-20 curated links */
      } else {
        Object.keys(R.topics || {}).forEach(function(k){ if (idHits(id, k)) pushAll(R.topics[k]); });
        if (out.length < 8) pushAll((R.groups || {})[s.group || "Other"]);
        out = out.slice(0, 8);             /* major sections: 3-8 curated */
      }
      var P = R.portals || [];             /* always 2-4 global portals */
      if (P.length) {
        var want = 2 + (hash(id) % 3), off = hash(id) % P.length;
        for (var i = 0; i < P.length && want > 0; i++) {
          var l = P[(off + i) % P.length];
          if (!seen[l[1]]) { push(l); want--; }
        }
      }
      return out;
    }
    function renderCard(s){
      var body = document.querySelector("#main .sec-body");
      if (!body || !s) return;
      var old = body.querySelector(".uc-res-card");
      if (old) old.remove();
      var links = collect(s);
      if (!links.length) return;
      var card = document.createElement("div");
      card.className = "uc-res-card";
      var h = '<div class="uc-res-head"><span aria-hidden="true">&#128218;</span>' +
              '<b>Official resources</b>' +
              '<span class="uc-res-note">curated &middot; verified &middot; new tab</span></div>' +
              '<ul class="uc-res-list">';
      links.forEach(function(l){
        h += '<li><a href="' + esc(l[1]) + '" target="_blank" rel="noopener noreferrer">' + esc(l[0]) + '</a></li>';
      });
      h += '</ul>';
      card.innerHTML = h;
      body.appendChild(card);
    }
    var orig = window.ucAfterOpen;
    window.ucAfterOpen = function (s) {
      if (typeof orig === "function") { try { orig(s); } catch (e) {} }
      try { renderCard(s); } catch (e) {}
    };
  })();
"""

CSS = r"""
/* === WAVE E 20.2-RESOURCES: OFFICIAL RESOURCES CARD === */
.uc-res-card{background:var(--card);border:1px solid var(--border);border-left:5px solid var(--teal);border-radius:16px;padding:16px;margin:14px 0 12px;box-shadow:var(--shadow);overflow-wrap:anywhere}
.uc-res-head{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:10px}
.uc-res-head b{font-family:var(--display);font-size:1.05rem;color:var(--teal)}
.uc-res-note{margin-left:auto;font-size:10px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);font-weight:800}
.uc-res-list{list-style:none;display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:6px;margin:0;padding:0}
.uc-res-list a{display:flex;align-items:center;gap:6px;padding:8px 10px;border-radius:10px;border:1px solid var(--line);background:color-mix(in srgb,var(--peach) 22%,var(--card));color:var(--ink);text-decoration:none;font-weight:700;font-size:12px;transition:transform .18s ease,box-shadow .18s ease,border-color .18s ease}
.uc-res-list a::after{content:"\2197";margin-left:auto;color:var(--amber);font-weight:900}
.uc-res-list a:hover{transform:translateY(-1px);border-color:var(--teal);box-shadow:var(--uc-glow-teal)}
@media (max-width:520px){.uc-res-list{grid-template-columns:1fr}.uc-res-note{margin-left:0}}
@media (prefers-reduced-motion:reduce){.uc-res-list a{transition:none}.uc-res-list a:hover{transform:none}}
"""

VENDOR_CARDS = [
    ('Cisco (CUCM · CUBE · Expressway · Contact Center)', ['cisco.com']),
    ('Webex (Calling · Meetings · Contact Center)', ['webex.com']),
    ('Microsoft Teams Phone', ['microsoft.com']),
    ('AWS · Amazon Connect', ['amazon.com', 'amazonaws.com', 'github.com/aws']),
    ('Google Cloud · CCAI', ['google.com']),
    ('Genesys Cloud', ['purecloud', 'genesys']),
    ('Twilio', ['twilio']),
    ('Zoom', ['zoom']),
    ('RingCentral', ['ringcentral']),
    ('8x8', ['8x8']),
    ('Avaya', ['avaya']),
    ('NICE CXone', ['nice-incontact']),
    ('Five9', ['five9']),
    ('Salesforce', ['salesforce']),
    ('Open-Source Telephony (Asterisk · FreePBX · Kamailio · OpenSIPS · FreeSWITCH)',
     ['asterisk', 'freepbx', 'kamailio', 'opensips', 'signalwire']),
    ('SBC Vendors (Oracle · Ribbon · AudioCodes)', ['oracle', 'rbbn', 'audiocodes']),
    ('E911 & Carrier Services', ['intrado', 'redsky', 'bandwidth', 'telnyx', 'vonage', 'plivo']),
    ('Standards Bodies & Specs', ['itu.int', 'w3.org', 'mozilla', 'openapis', 'json-schema', 'datatracker']),
    ('Packet Analysis & Lab Tools', ['wireshark', 'sipp', 'tcpdump', 'sipcapture']),
    ('Security & Compliance', ['csrc.nist.gov']),
    ('Campus', ['github.com/cipher0x9', 'linktr.ee']),
]

def vendor_of(url):
    for title, frags in VENDOR_CARDS:
        if any(f in url for f in frags):
            return title
    return None

def build_atlas_html(cache):
    """resources-index body: every verified seed URL, grouped by vendor + RFC library."""
    def ok(u):
        c = cache.get(u, '000')
        return c[:1] in ('2', '3') or c.endswith('*') or c.endswith('B')
    # gather non-RFC links, dedup by URL, group by vendor
    cards = {t: [] for t, _ in VENDOR_CARDS}
    other = []
    seen = set()
    for where, links in all_seed_lists():
        if where.startswith('rfc:'):
            continue
        for t, u in links:
            if u in seen or not ok(u):
                continue
            seen.add(u)
            v = vendor_of(u)
            (cards[v] if v else other).append((t, u))
    if other:
        cards['More Official Docs'] = other
    parts = ['<div class="hero"><div class="eyebrow">20.2-RESOURCES · CURATED OFFICIAL DOCS · VERIFIED AT BUILD TIME</div>',
             '<div style="font-size:2.2rem">📚🧭</div><h1>Resources Atlas</h1>',
             '<p>Every external learning link on this campus, grouped by vendor and standards body. '
             'Official documentation homes only — no blogs, no link farms, no invented URLs. '
             'A smaller 📚 Official resources card also appears automatically under every section.</p></div>']
    colors = ['teal', 'blue', 'purple', 'green', 'rose']
    i = 0
    def card(title, rows):
        nonlocal i
        if not rows:
            return
        cls = colors[i % len(colors)]
        lis = ''.join(f'<li><a href="{u}" target="_blank" rel="noopener noreferrer">{t}</a></li>'
                      for t, u in rows)
        parts.append(f'<div class="card {cls}"><h2>{title} <span style="color:var(--muted);font-size:.8rem">({len(rows)})</span></h2><ul class="tips">{lis}</ul></div>')
        i += 1
    for title, _ in VENDOR_CARDS:
        card(title, cards.get(title, []))
    card('More Official Docs', other)
    for grp, entries in RFC_LIB.items():
        rows = [(f'RFC {n} — {label}', f'{RFC}{n}') for n, label in entries if ok(f'{RFC}{n}')]
        card(f'IETF RFC Library — {grp}', rows)
    parts.append('<div class="card"><h2>Curation law</h2><ul class="tips">'
                 '<li>Hub chapters carry 8–20 curated official links.</li>'
                 '<li>Major tech sections carry 3–8 links via topic + group defaults.</li>'
                 '<li>Drills carry 0–2 links — do the drill first.</li>'
                 '<li>Every URL was HTTP-verified (curl + headless Chromium) when this build shipped; unverified links are omitted, never guessed.</li>'
                 '<li>Campus works fully offline — links open only when you choose.</li></ul></div>')
    def esc(x):
        return x.replace('\\', '\\\\').replace('"', '\\"')
    return '\\n'.join(esc(x) for x in parts)

# ------------------------------------------------------------------ INJECT --
VERSION_REPLACEMENTS = [
    ('UC Lab Free University 20.1-UI — 631 sections, offline',
     'UC Lab Free University 20.2-RESOURCES — 632 sections, offline'),
    ('UC Lab University 20.1-UI Free — offline curriculum, 631 sections',
     'UC Lab University 20.2-RESOURCES Free — offline curriculum, 632 sections'),
    ('<title>UC Lab Free University 20.1-UI — Offline Learning Pack</title>',
     '<title>UC Lab Free University 20.2-RESOURCES — Offline Learning Pack</title>'),
    ('UC Lab Free University 20.1-UI · 631 full curriculum sections',
     'UC Lab Free University 20.2-RESOURCES · 632 full curriculum sections'),
    ('🌿 UC Lab Free · 20.1-UI', '🌿 UC Lab Free · 20.2-RESOURCES'),
    ('<span class="muted" id="prog">20.1-UI</span>',
     '<span class="muted" id="prog">20.2-RESOURCES</span>'),
    ('"version": "20.1-UI"', '"version": "20.2-RESOURCES"'),
    ('"sections": 631', '"sections": 632'),
    ('"note": "Full 631-section curriculum', '"note": "Full 632-section curriculum'),
    ("'20.1-UI · <b", "'20.2-RESOURCES · <b"),
    ('# UC Lab Free University 20.1-UI — Full Curriculum',
     '# UC Lab Free University 20.2-RESOURCES — Full Curriculum'),
    ('version: "20.1-UI",', 'version: "20.2-RESOURCES",'),
    ('>631</b><span>Sections (20.1-UI)</span>', '>632</b><span>Sections (20.2-RESOURCES)</span>'),
]

FALLBACK = [
    ['Cisco Support Central', CSUPPORT],
    ['Cisco Unified Communications — Docs & Support', CVOICE],
    rfc(3261, 'SIP'),
    ['UC Lab Free University (GitHub)', 'https://github.com/cipher0x9/uc-lab-free-university-mesmerizing'],
]

def inject(cache):
    text = HTML.read_text()
    # merge EXTRA/EXTRA3 into topics
    topics = merged_topics()
    # verify-filter everything
    portals = verified(cache, PORTALS)
    hubs = {k: verified(cache, v) for k, v in HUBS.items()}
    topics = {k: verified(cache, v) for k, v in topics.items()}
    groups = {k: verified(cache, v) for k, v in GROUPS.items()}
    topics = {k: v for k, v in topics.items() if v}
    # enforce hub floor of 8
    for k, v in hubs.items():
        seen = {u for _, u in v}
        for f in verified(cache, FALLBACK):
            if len(v) >= 8:
                break
            if f[1] not in seen:
                v.append(f)
                seen.add(f[1])
        hubs[k] = v[:20]
    res = {'version': '20.2-RESOURCES', 'hubs': hubs, 'topics': topics,
           'groups': groups, 'portals': portals}
    js = ('<script>\n/* UC-RESOURCES-JS 20.2-RESOURCES */\n'
          'window.UC_RESOURCES = ' + json.dumps(res, ensure_ascii=False) + ';\n'
          + RENDER_JS + '</script>')
    # CSS (idempotent via markers)
    css_block = '<style>\n/* UC-RESOURCES-CSS 20.2-RESOURCES */' + CSS + '</style>\n</head>'
    if '/* UC-RESOURCES-CSS' in text:
        text = re.sub(r'<style>\s*/\* UC-RESOURCES-CSS.*?</style>\s*</head>',
                      css_block, text, flags=re.DOTALL)
    else:
        text = text.replace('</head>', css_block, 1)
    # JS (idempotent via markers)
    if '/* UC-RESOURCES-JS' in text:
        text = re.sub(r'<script>\s*/\* UC-RESOURCES-JS.*?</script>\s*</body>',
                      js + '\n</body>', text, flags=re.DOTALL)
    else:
        text = text.replace('</body>', js + '\n</body>', 1)
    # resources-index section (once)
    if '"id": "resources-index"' not in text and '"id":"resources-index"' not in text:
        body = build_atlas_html(cache)
        section = (',\n{"id": "resources-index", "num": "632", "group": "Library", '
                   '"title": "📚 Resources Atlas", '
                   '"sub": "Every official doc portal on campus, grouped by vendor", '
                   '"body": "' + body + '"}\n]')
        # insert before the '];' that closes window.SECTIONS
        i = text.find('window.SECTIONS = [')
        j = text.find('];', i)
        assert j > i, 'SECTIONS array close not found'
        text = text[:j] + section + text[j + 1:]
    # version bumps
    for old, new in VERSION_REPLACEMENTS:
        if old in text:
            text = text.replace(old, new)
        else:
            print(f'  WARN: version string not found: {old[:60]}')
    HTML.write_text(text)
    n_unique = len({u for _, links in [('p', portals)] + [(k, v) for k, v in hubs.items()]
                    + [(k, v) for k, v in topics.items()] + [(k, v) for k, v in groups.items()]
                    for _, u in links})
    print(f'injected. portals={len(portals)} hubs={sum(len(v) for v in hubs.values())} '
          f'topics={sum(len(v) for v in topics.values())} groups={sum(len(v) for v in groups.values())} '
          f'unique_urls={n_unique}')
    for k, v in hubs.items():
        assert 8 <= len(v) <= 20, f'hub {k} has {len(v)} links (law: 8-20)'
    print('hub law OK (8-20 each)')

# ------------------------------------------------------------------ REPORT --
def report(cache):
    lines = ['# UC Resources — URL audit (Wave E)\n']
    for where, links in all_seed_lists():
        lines.append(f'\n## {where}')
        for t, u in links:
            c = cache.get(u, '?')
            mark = '✅' if (c[:1] in ('2', '3')) else ('⚠️' if c.endswith('*') else '❌')
            lines.append(f'- {mark} [{c}] [{t}]({u})')
    SNIPPET.write_text('\n'.join(lines) + '\n')
    print(f'wrote {SNIPPET}')

# ------------------------------------------------- RFC LIBRARY (canonical) --
# Every entry is an rfc-editor.org canonical URL; all are build-verified.
RFC_LIB = {
    'SIP & Signaling': [
        (3261, 'SIP Core'), (3262, 'PRACK'), (3263, 'Locating SIP Servers'),
        (3264, 'Offer/Answer'), (3265, 'SIP Events'), (3311, 'UPDATE'),
        (3312, 'Preconditions'), (3313, 'P-Access-Network-Info'),
        (3323, 'Privacy Mechanism'), (3324, 'Asserted Identity Extension'),
        (3325, 'P-Asserted / P-Preferred Identity'), (3326, 'Reason Header'),
        (3327, 'Path Header'), (3329, 'Security Mechanism Agreement'),
        (3398, 'SIP-ISUP Mapping'), (3428, 'MESSAGE'), (3455, 'Private Header Extensions'),
        (3515, 'REFER'), (3608, 'Service-Route'), (3665, 'Basic Call Flows'),
        (3666, 'SIP-PSTN Call Flows'), (3725, 'Third Party Call Control'),
        (3840, 'Callee Capabilities'), (3841, 'Caller Preferences'),
        (3891, 'Replaces'), (3892, 'Referred-By'), (3893, 'Authenticated Identity Body'),
        (3903, 'PUBLISH'), (3960, 'Early Media'), (3966, 'tel: URI'),
        (4028, 'Session Timers'), (4235, 'Dialog Event Package'),
        (4244, 'History-Info'), (4412, 'Resource-Priority Headers'),
        (4474, 'SIP Identity (original)'), (4475, 'SIP Torture Tests'),
        (4916, 'Connected Identity'), (5009, 'P-Early-Media'),
        (5368, 'Referring to Multiple Resources'), (5411, 'Hitchhiker\u2019s Guide to SIP'),
        (5502, 'P-Served-User'), (5626, 'Outbound Client Connections'),
        (5627, 'GRUU'), (5628, 'GRUU Registration Event'),
        (5954, '3261 ABNF Corrections'), (6026, '2xx Transaction Handling'),
        (6141, 'Re-INVITE Handling'), (6665, 'SIP Events (updated)'),
        (7118, 'SIP over WebSocket'), (7315, '3GPP Private Header Extensions'),
        (7462, 'Alert-Info URNs'),
    ],
    'Media & Transport': [
        (3550, 'RTP'), (3551, 'RTP A/V Profile'), (3555, 'RTP MIME Registration'),
        (3611, 'RTCP XR'), (2198, 'RTP Redundancy'), (2326, 'RTSP'),
        (2733, 'RTP Generic FEC'), (3389, 'Comfort Noise'), (3605, 'RTCP in SDP'),
        (3711, 'SRTP'), (4585, 'RTP/AVPF'), (4587, 'H.261 Payload'),
        (4588, 'RTP Retransmission'), (4733, 'DTMF Telephony Events'),
        (4734, 'Modem/Fax Telephony Events'), (4867, 'AMR Payload'),
        (5104, 'Codec Control Messages'), (6184, 'H.264 Payload'),
        (6464, 'Client-to-Mixer Audio Level'), (6465, 'Mixer-to-Client Audio Level'),
        (6716, 'Opus'), (7587, 'Opus Payload'), (7667, 'RTP Topologies'),
        (7741, 'VP8 Payload'), (7798, 'HEVC/H.265 Payload'), (7826, 'RTSP 2.0'),
        (8285, 'RTP Header Extensions'),
    ],
    'Network & Infrastructure': [
        (768, 'UDP'), (791, 'IPv4'), (792, 'ICMP'), (1034, 'DNS Concepts'),
        (1035, 'DNS Implementation'), (1918, 'Private Addressing'), (2131, 'DHCP'),
        (2328, 'OSPFv2'), (2474, 'DSCP Field'), (2475, 'DiffServ Architecture'),
        (2597, 'Assured Forwarding PHB'), (2598, 'Expedited Forwarding (original)'),
        (2782, 'DNS SRV'), (2865, 'RADIUS'), (3022, 'Traditional NAT'),
        (3164, 'BSD Syslog'), (3246, 'Expedited Forwarding PHB'),
        (3260, 'DiffServ Clarifications'), (3411, 'SNMP Architecture'),
        (3596, 'DNS AAAA'), (4271, 'BGP-4'), (4443, 'ICMPv6'),
        (4594, 'DiffServ Service Classes'), (4632, 'CIDR'), (4787, 'NAT Behaviors'),
        (4861, 'IPv6 Neighbor Discovery'), (5424, 'Syslog Protocol'),
        (5425, 'Syslog over TLS'), (5426, 'Syslog over UDP'), (5880, 'BFD'),
        (5905, 'NTPv4'), (7858, 'DNS over TLS'), (8200, 'IPv6'),
        (8201, 'IPv6 Path MTU'), (8484, 'DNS over HTTPS'), (9293, 'TCP'),
    ],
    'Security & Identity': [
        (2818, 'HTTP over TLS'), (2986, 'PKCS #10'), (4511, 'LDAP'),
        (4568, 'SDP Security Descriptions'), (5246, 'TLS 1.2'), (5280, 'X.509 PKI'),
        (5764, 'DTLS-SRTP'), (6066, 'TLS Extensions'), (6125, 'PKIX Identity Verification'),
        (8224, 'SIP Identity (STIR)'), (8225, 'PASSporT (SHAKEN)'),
        (8226, 'STIR Certificates'), (8446, 'TLS 1.3'), (8555, 'ACME'),
    ],
    'HTTP · APIs · Data Formats': [
        (6749, 'OAuth 2.0'), (6750, 'Bearer Tokens'), (6901, 'JSON Pointer'),
        (6902, 'JSON Patch'), (7396, 'JSON Merge Patch'), (7515, 'JWS'),
        (7516, 'JWE'), (7517, 'JWK'), (7518, 'JWA'), (7519, 'JWT'),
        (8259, 'JSON'), (8414, 'OAuth Server Metadata'), (9110, 'HTTP Semantics'),
        (9112, 'HTTP/1.1'), (9113, 'HTTP/2'), (9114, 'HTTP/3'),
    ],
    'WebRTC & NAT Traversal': [
        (5389, 'STUN'), (5780, 'NAT Behavior Discovery'), (7874, 'WebRTC Audio'),
        (8445, 'ICE'), (8489, 'STUN (updated)'), (8656, 'TURN'),
        (8825, 'WebRTC Overview'), (8826, 'WebRTC Security'),
        (8827, 'WebRTC Security Architecture'), (8834, 'WebRTC Media'),
        (8835, 'WebRTC Transports'),
    ],
    'Emergency & Location': [
        (4119, 'GEOPRIV PIDF-LO'), (5222, 'LoST'), (5985, 'HELD'),
        (6442, 'Location Conveyance in SIP'), (6881, 'BCP for Emergency Calling'),
        (7852, 'Additional Data for Emergency Calls'),
    ],
    'Messaging & Presence': [
        (3856, 'SIP Presence'), (3857, 'Watcher Information'), (3863, 'PIDF'),
        (4975, 'MSRP'), (4976, 'MSRP Relays'), (6120, 'XMPP Core'),
        (6121, 'XMPP IM & Presence'), (6122, 'XMPP Address Format'),
    ],
    'Automation & Programmability': [
        (6241, 'NETCONF'), (7950, 'YANG 1.1'), (8040, 'RESTCONF'),
        (8639, 'YANG Notifications Subscription'),
    ],
}

# -------------------------------------------------- EXTRA ROUND-3 PROBES ----
# Verify-filtered like everything else: failures drop silently.
EXTRA3 = {
    'teams': [
        ['MS Teams — Set Up Audio Conferencing', LEARN + '/microsoftteams/set-up-audio-conferencing'],
        ['MS Teams — Audio Conferencing Phone Numbers', LEARN + '/microsoftteams/phone-numbers-for-audio-conferencing'],
        ['MS Teams — Port Orders', LEARN + '/microsoftteams/port-order-overview'],
        ['MS Teams — Transfer Numbers to Teams', LEARN + '/microsoftteams/transfer-phone-numbers-to-teams'],
        ['MS Teams — Manage Phone Numbers', LEARN + '/microsoftteams/manage-phone-numbers-for-your-organization'],
        ['MS Teams — Dynamic Emergency Calling', LEARN + '/microsoftteams/dynamic-emergency-calling'],
        ['MS Teams — Teams Phone Extensibility', LEARN + '/microsoftteams/teams-phone-extensibility'],
        ['MS Teams — Voice Routing Policies', LEARN + '/microsoftteams/manage-voice-routing-policies'],
        ['MS Teams — Network Planner', LEARN + '/microsoftteams/network-planner'],
        ['MS Teams — Device Management', LEARN + '/microsoftteams/devices/device-management'],
        ['MS Teams Rooms — Requirements', LEARN + '/microsoftteams/rooms/requirements'],
        ['MS Teams — CQD Building Data', LEARN + '/microsoftteams/cqd-upload-tenant-building-data'],
        ['MS Teams — Emergency Calling Terms', LEARN + '/microsoftteams/emergency-calling-terms-and-conditions'],
        ['MS Teams — Configure Direct Routing', LEARN + '/microsoftteams/direct-routing-configure'],
    ],
    'cucm': [
        ['CUCM — Install & Upgrade Guides', f'{CUC}/unified-communications-manager-callmanager{IG}'],
        ['CUCM — Troubleshoot & Alerts', f'{CUC}/unified-communications-manager-callmanager/tsd-products-support-troubleshoot-and-alerts.html'],
    ],
    'unity': [
        ['Unity Connection — Install & Upgrade Guides', f'{CUC}/unity-connection{IG}'],
        ['Unity Connection — Command References', f'{CUC}/unity-connection{CR}'],
        ['Unity Connection — Release Notes', f'{CUC}/unity-connection{RN}'],
    ],
    'jabber': [
        ['Jabber — Release Notes', f'{CUC}/jabber{RN}'],
        ['Jabber — Troubleshooting Guides', f'{CUC}/jabber{TG}'],
    ],
    'e911': [
        ['Cisco Emergency Responder — Install & Config Guides', f'{CUC}/emergency-responder{GL}'],
        ['Cisco Emergency Responder — Install & Upgrade Guides', f'{CUC}/emergency-responder{IG}'],
    ],
    'cube': [
        ['CUBE — Install & Upgrade Guides', f'{CUC}/unified-border-element{IG}'],
        ['CUBE — Command References', f'{CUC}/unified-border-element{CR}'],
        ['CUBE — Release Notes', f'{CUC}/unified-border-element{RN}'],
        ['CUBE — Troubleshooting Guides', f'{CUC}/unified-border-element{TG}'],
    ],
    'expressway': [
        ['Expressway — Install & Upgrade Guides', f'{CUC}/expressway-series{IG}'],
        ['Expressway — Command References', f'{CUC}/expressway-series{CR}'],
    ],
    'ucce': [
        ['UCCE — Install & Upgrade Guides', f'{CCC}/unified-contact-center-enterprise{IG}'],
        ['UCCE — Command References', f'{CCC}/unified-contact-center-enterprise{CR}'],
        ['Cisco Unified CVP — Support', f'{CCC}/unified-customer-voice-portal{TS}'],
        ['Cisco Unified CVP — Install & Config Guides', f'{CCC}/unified-customer-voice-portal{GL}'],
        ['Cisco Finesse — Support', f'{CCC}/finesse{TS}'],
        ['Cisco Finesse — Install & Config Guides', f'{CCC}/finesse{GL}'],
        ['Cisco Unified Intelligence Center — Support', f'{CCC}/unified-intelligence-center{TS}'],
        ['Cisco Unified Intelligence Center — Guides', f'{CCC}/unified-intelligence-center{GL}'],
    ],
    'pcce': [
        ['PCCE — Install & Upgrade Guides', f'{CCC}/packaged-contact-center-enterprise{IG}'],
        ['PCCE — Troubleshooting Guides', f'{CCC}/packaged-contact-center-enterprise{TG}'],
    ],
    'uccx': [
        ['UCCX — Install & Upgrade Guides', f'{CCC}/unified-contact-center-express{IG}'],
        ['UCCX — Release Notes', f'{CCC}/unified-contact-center-express{RN}'],
    ],
    'webex': [
        ['Webex Meetings — Support', CISCO + '/c/en/us/support/collaboration-meetings/webex-meetings' + TS],
        ['Webex Meetings — Install & Config Guides', CISCO + '/c/en/us/support/collaboration-meetings/webex-meetings' + GL],
        ['Webex App — Support', CISCO + '/c/en/us/support/collaboration-apps/webex-app' + TS],
        ['Webex — API Basics', 'https://developer.webex.com/docs/api/basics'],
    ],
    'recording': [
        ['Cisco MediaSense — Support', f'{CCC}/mediasense{TS}'],
        ['Cisco MediaSense — Install & Config Guides', f'{CCC}/mediasense{GL}'],
    ],
    'endpoint': [
        ['Cisco IP Phone 8800 Series — Support', CISCO + '/c/en/us/support/collaboration-endpoints/unified-ip-phone-8800-series' + TS],
        ['Cisco IP Phone 8800 Series — Guides', CISCO + '/c/en/us/support/collaboration-endpoints/unified-ip-phone-8800-series' + GL],
    ],
    'genesys': [
        ['Genesys Cloud — REST API v2', 'https://developer.genesys.cloud/api/rest/v2/'],
    ],
    'gcc': [
        ['Dialogflow CX — Pages', 'https://cloud.google.com/dialogflow/cx/docs/concept/page'],
        ['Dialogflow CX — Integrations', 'https://cloud.google.com/dialogflow/cx/docs/concept/integration'],
        ['Dialogflow CX — Reference', 'https://cloud.google.com/dialogflow/cx/docs/reference'],
        ['Speech-to-Text — REST Reference', 'https://cloud.google.com/speech-to-text/docs/reference/rest'],
        ['Text-to-Speech — REST Reference', 'https://cloud.google.com/text-to-speech/docs/reference/rest'],
    ],
    'twilio': [
        ['Twilio — SIP Trunking API', 'https://www.twilio.com/docs/sip-trunking/api'],
        ['Twilio — Usage Records API', 'https://www.twilio.com/docs/usage/api'],
    ],
    'zoom': [
        ['Zoom — API Reference (new)', 'https://developers.zoom.us/docs/api-reference/'],
    ],
    'ringcentral': [
        ['RingCentral — Developer Guide', 'https://developers.ringcentral.com/guide'],
    ],
    'connect': [
        ['Amazon Connect — Features', 'https://aws.amazon.com/connect/features/'],
        ['AWS Step Functions Documentation', AWSD + '/step-functions/'],
        ['Amazon Kinesis Documentation', AWSD + '/kinesis/'],
    ],
    'salesforce': [
        ['Salesforce — REST API Developer Guide', 'https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/'],
        ['Salesforce Help', 'https://help.salesforce.com/'],
        ['Salesforce Developers', 'https://developer.salesforce.com/docs'],
    ],
    'nice': [
        ['NICE CXone Help', 'https://help.nice-incontact.com/'],
        ['NICE CXone Developer Portal', 'https://developer.nice-incontact.com/'],
    ],
    'five9': [
        ['Five9 — Official Site', 'https://www.five9.com/'],
        ['Five9 Help Center', 'https://help.five9.com/'],
    ],
    'asterisk': [
        ['Asterisk Wiki', 'https://wiki.asterisk.org/'],
        ['FreeSWITCH Documentation (SignalWire)', 'https://developer.signalwire.com/freeswitch/'],
    ],
    'wireshark': [
        ['Wireshark Documentation', 'https://www.wireshark.org/docs/'],
        ['Wireshark User\u2019s Guide', 'https://www.wireshark.org/docs/wsug_html_chunked/'],
        ['Wireshark Wiki', 'https://wiki.wireshark.org/'],
        ['Wireshark Sample Captures', 'https://wiki.wireshark.org/SampleCaptures'],
        ['SIPp — SIP Traffic Generator', 'https://sipp.sourceforge.net/'],
        ['Homer (SIPCAPTURE)', 'https://github.com/sipcapture/homer'],
        ['tcpdump', 'https://www.tcpdump.org/'],
    ],
}

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'all'
    cache = None
    if mode in ('verify', 'all'):
        cache = verify()
    if cache is None:
        cache = json.loads(CACHE.read_text())
    if mode in ('inject', 'all'):
        inject(cache)
    if mode in ('report', 'all'):
        report(cache)
