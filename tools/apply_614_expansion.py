#!/usr/bin/env python3
"""Re-apply the 12-section expert expansion (IDs 603-614) to v17-UNIVERSITY.html."""
import json, re
from pathlib import Path

ROOT = Path('/Users/cypher0x9/Documents/01_🎓_UC_AI_FREE_UNIVERSITY_CAMPUS/_github-publish')
HTML = ROOT / 'university' / 'v17-UNIVERSITY.html'
REPORT = Path('/Users/cypher0x9/Desktop/uc-w5-kimi-content-report.md')

def now():
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).astimezone().isoformat()

def append_report(line):
    with open(REPORT, 'a', encoding='utf-8') as f:
        f.write(line + '\n')

def expert_body(title, eyebrow, lead, tabs):
    body_lines = ['<section class="expert-section">',
        '<style>.expert-section .tab-pane{margin:1rem 0;padding:1rem;border:1px solid var(--border);border-radius:14px}.expert-section table{width:100%;border-collapse:collapse}.expert-section th,.expert-section td{padding:.55rem;border:1px solid var(--border);vertical-align:top}.expert-section th{background:color-mix(in srgb,var(--blue) 14%,transparent);text-align:left}.expert-section details{margin:.5rem 0;padding:.7rem;border-left:4px solid var(--purple);background:color-mix(in srgb,var(--card) 94%,var(--purple))}.expert-section .ans{color:var(--green);font-weight:700}.expert-section svg{width:100%;height:auto}</style>',
        f'<div class="hero"><div class="eyebrow">{eyebrow}</div><h1>{title}</h1><p class="lead">{lead}</p></div>',
        '<div class="tabs"><div class="tab-bar">']
    for i, (tid, tlabel, _) in enumerate(tabs):
        active = ' active' if i == 0 else ''
        body_lines.append(f'<button type="button" class="tab-btn{active}" data-tab="{tid}">{tlabel}</button>')
    body_lines.append('</div>')
    for i, (tid, _, content) in enumerate(tabs):
        active = ' active' if i == 0 else ''
        body_lines.append(f'<div class="tab-pane{active}" id="{tid}">{content}</div>')
    body_lines.append('</div></section>')
    return '\n'.join(body_lines)

def sev_body(title, eyebrow, scenario, tabs):
    body_lines = ['<section class="sev-section">',
        '<style>.sev-section .tab-pane{margin:1rem 0;padding:1rem;border:1px solid var(--border);border-radius:14px}.sev-section table{width:100%;border-collapse:collapse}.sev-section th,.sev-section td{padding:.55rem;border:1px solid var(--border);vertical-align:top}.sev-section th{background:color-mix(in srgb,var(--red) 14%,transparent);text-align:left}.sev-section details{margin:.5rem 0;padding:.7rem;border-left:4px solid var(--red);background:color-mix(in srgb,var(--card) 94%,var(--red))}.sev-section .ans{color:var(--green);font-weight:700}.sev-section .clock{font-size:1.1rem;font-weight:800;color:var(--red)}.sev-section svg{width:100%;height:auto}</style>',
        f'<div class="hero"><div class="eyebrow">{eyebrow}</div><h1>{title}</h1><p class="lead">{scenario}</p><p class="clock">⏱️ 15-minute war-room clock</p></div>',
        '<div class="tabs"><div class="tab-bar">']
    for i, (tid, tlabel, _) in enumerate(tabs):
        active = ' active' if i == 0 else ''
        body_lines.append(f'<button type="button" class="tab-btn{active}" data-tab="{tid}">{tlabel}</button>')
    body_lines.append('</div>')
    for i, (tid, _, content) in enumerate(tabs):
        active = ' active' if i == 0 else ''
        body_lines.append(f'<div class="tab-pane{active}" id="{tid}">{content}</div>')
    body_lines.append('</div></section>')
    return '\n'.join(body_lines)

def tabs(*pairs):
    return [(f'tab-{i}', label, content) for i, (label, content) in enumerate(pairs)]

# ---------- 12 new sections ----------
new_sections = []

# 603 Microsoft Teams Phone PSTN
t603 = tabs(
    ("📘 Overview", """<ul><li><b>Teams Phone System</b> license enables cloud PBX features: auto-attendant, call queues, voicemail, transfer, hold.</li><li><b>PSTN choices:</b> Microsoft Calling Plan (carrier-managed), Operator Connect (partner-managed SBC), Direct Routing (customer-managed SBC).</li><li><b>Emergency:</b> dynamic E911 with civic address validation and LIS (Location Information Service).</li><li><b>Media path:</b> ICE/STUN/TURN; Teams client to SBC for Direct Routing; Microsoft network for Calling Plan.</li></ul>"""),
    ("🏛️ Architecture", """<p><b>Direct Routing:</b> certified SBC → Microsoft Teams SIP proxy → Teams client. Requires:</p><ul><li>Public IP, FQDN, TLS 1.2 certificate on SBC.</li><li>SIP OPTIONS ping for health monitoring.</li><li>Voice Routing Policy + PSTN Usage + Route + SBC association.</li></ul><p><b>Operator Connect:</b> partner provisions trunk in Teams Admin Center; no customer SBC.</p><p><b>Calling Plan:</b> Microsoft assigns numbers; simplest but least flexible.</p>"""),
    ("⚙️ Configuration", """<ol><li>Assign <b>Teams Phone Standard</b> or E5 license.</li><li>Acquire/provision numbers (port, request, or assign).</li><li>Create emergency addresses in TAC → validate civic address.</li><li>Assign numbers to users/resource accounts (AA/CQ).</li><li>For Direct Routing: add SBC, create voice routes, assign Voice Routing Policy.</li><li>Enable location-based routing if regulatory requirement exists.</li></ol><pre><code>Set-CsPhoneNumberAssignment -Identity user@domain.com -PhoneNumber +15551234567 -PhoneNumberType DirectRouting
New-CsOnlineVoiceRoute -Identity 'US-Route' -NumberPattern '^\\+1' -OnlinePstnGatewayList sbc.contoso.com -Priority 1</code></pre>"""),
    ("🛠️ Troubleshoot", """<table><tr><th>Symptom</th><th>LICC evidence</th><th>Fix</th></tr><tr><td>No dial tone</td><td>Get-CsPhoneNumberAssignment returns blank</td><td>Assign number + Phone System license</td></tr><tr><td>Calls fail to PSTN</td><td>SBC SIP logs: 403 Forbidden</td><td>Check voice route pattern and PSTN usage</td></tr><tr><td>One-way audio</td><td>Client media logs; SBC RTP port blocked</td><td>Open UDP 10000-20000; verify ICE candidate</td></tr><tr><td>E911 misroute</td><td>Get-CsOnlineLisLocation / civic address mismatch</td><td>Reassign emergency location</td></tr></table>"""),
    ("🎤 Interview", """<details><summary>When do you choose Direct Routing over Operator Connect?</summary><p class='ans'>Direct Routing when you need full control over SBC, legacy PBX/PSTN integration, least-cost routing, or specialized compliance. Operator Connect when you want partner-managed SBC with faster provisioning and lower ops overhead.</p></details><details><summary>How does Teams handle emergency location for remote workers?</summary><p class='ans'>Dynamic E911 uses LIS with network identifiers (subnet/WiFi BSSID/switch port) to map the endpoint to a validated civic address; calls route to the appropriate PSAP.</p></details>""")
)
new_sections.append({"id":"ms-teams-phone-pstn","num":"603","group":"Vendor Deep-Dives","title":"📞 Microsoft Teams Phone PSTN","sub":"Teams Phone System with Calling Plan, Operator Connect, Direct Routing, and emergency calling deep-dive.","body":expert_body("Microsoft Teams Phone PSTN","VENDOR DEEP-DIVE · MODULE 603 · ms-teams-phone-pstn","Teams Phone becomes a full PBX only when PSTN connectivity is architected correctly. Compare Calling Plan, Operator Connect, Direct Routing, and Teams Phone Mobile for voice, resilience, and compliance.",t603)})

# 604 Webex Calling Advanced
t604 = tabs(
    ("📘 Overview", """<ul><li><b>Webex Calling</b> multi-tenant: shared cloud, fastest provisioning, Control Hub management.</li><li><b>Dedicated Instance</b>: single-tenant UC in Webex cloud for regulatory/performance needs.</li><li><b>Local Gateway (LGW)</b>: CUBE-based SBC connecting Webex Calling to on-prem PSTN/PBX.</li><li><b>Advanced routing:</b> route lists, route groups, hunt groups, call queues, executive assistant.</li></ul>"""),
    ("🏛️ Architecture", """<p><b>Dedicated Instance → on-prem:</b> Expressway-C/E for MRA, LGW for PSTN, AD/LDAP sync for directory.</p><p><b>Multi-tenant PSTN:</b></p><ul><li>Webex Calling PSTN (Cisco PSTN)</li><li>Cloud Connected PSTN (partner)</li><li>Local Gateway (customer)</li></ul><p><b>Redundancy:</b> redundant LGWs, DNS SRV for SBC failover, multiple trunks in route list.</p>"""),
    ("⚙️ Configuration", """<ol><li>Provision location in Control Hub with PSTN choice.</li><li>For LGW: configure CUBE with Webex Calling SIP profile, TLS cert, trunk group.</li><li>Create route groups, route lists, and assign to locations.</li><li>Configure hunt groups / call queues with overflow, fallback, and business hours.</li><li>Enable call recording or Webex Contact Center integration.</li></ol><pre><code>voice service voip
 sip
  registrar server
 voice class sip-profiles 100
  rule 1 request INVITE peer-header sip-to copy "(.*)" sip-to
 dial-peer voice 100 voip
  session protocol sipv2
  session target ipv4:10.0.0.1
  destination-pattern 9[2-9]......</code></pre>"""),
    ("🛠️ Troubleshoot", """<table><tr><th>Symptom</th><th>Evidence</th><th>Fix</th></tr><tr><td>Registration rejected</td><td>LGW logs 401 Unauthorized</td><td>Verify TLS cert, Webex trunk credentials</td></tr><tr><td>Route not used</td><td>Route list priority / time-of-day</td><td>Check route group membership and selection order</td></tr><tr><td>Queue overflow fails</td><td>Call distribution policy</td><td>Configure fallback destination and max wait</td></tr><tr><td>MRA no service</td><td>Expressway diagnostics</td><td>Verify _collab-edge DNS SRV, NAT, certs</td></tr></table>"""),
    ("🎤 Interview", """<details><summary>Differentiate Webex Calling Multi-Tenant vs Dedicated Instance.</summary><p class='ans'>Multi-tenant shares cloud infrastructure for cost and speed. Dedicated Instance provides isolated UC resources, deeper CUCM-like feature parity, and meets strict data residency/compliance.</p></details><details><summary>How do you design PSTN resilience?</summary><p class='ans'>Use redundant Local Gateways in a route group with top-down or round-robin selection, dual Internet/MPLS paths, DNS SRV failover, and monitor SIP OPTIONS health.</p></details>""")
)
new_sections.append({"id":"webex-calling-advanced","num":"604","group":"Vendor Deep-Dives","title":"☁️ Webex Calling Advanced","sub":"Dedicated Instance, Multi-Tenant, Local Gateway, Route Lists, Hunt/Call Queue, and Control Hub automation.","body":expert_body("Webex Calling Advanced","VENDOR DEEP-DIVE · MODULE 604 · webex-calling-advanced","Go beyond basic Webex Calling. Architect dedicated instances, PSTN local gateways, route lists, call queues, and automate with Control Hub APIs.",t604)})

# 605 AWS Connect Migration
t605 = tabs(
    ("📘 Overview", """<ul><li><b>Amazon Connect</b> is AWS cloud contact center: IVR, ACD, routing, analytics, ML (Contact Lens).</li><li><b>Migration patterns:</b> greenfield, parallel run, phased cutover, big-bang.</li><li><b>Key risks:</b> number porting timing, flow parity, agent desktop integration, recording compliance.</li></ul>"""),
    ("🏗️ Migration Plan", """<ol><li><b>Discovery:</b> document current queues, skills, flows, prompts, reports, integrations.</li><li><b>Design:</b> instance/region, telephony (Claimed/Direct Connect/SIP trunk), flows, routing profiles, security profiles.</li><li><b>Build:</b> Contact Flows, Lambda integrations, Lex bots, agent whisper.</li><li><b>Pilot:</b> small queue, shadow routing, validate recording.</li><li><b>Cutover:</b> port DIDs, update forwarding, run hypercare.</li></ol>"""),
    ("⚙️ Configuration", """<ul><li>Claim or port numbers in Connect admin.</li><li>Create Contact Flows with Set queue, Transfer to queue, Play prompt, Invoke Lambda.</li><li>Build Routing Profiles mapping queues + channels to agents.</li><li>Enable Contact Lens for transcription/sentiment.</li><li>Integrate CRM via Streams API + Lambda.</li></ul><pre><code>// Connect Streams init
connect.core.initCCP(container, {
  ccpUrl: 'https://instance.my.connect.aws/ccp-v2/',
  loginPopup: true,
  softphone: { allowFramedSoftphone: true }
});</code></pre>"""),
    ("🛠️ Troubleshoot", """<table><tr><th>Symptom</th><th>Evidence</th><th>Fix</th></tr><tr><td>Calls not reaching flow</td><td>CloudWatch Logs / contact trace</td><td>Check phone number → flow association</td></tr><tr><td>Lambda invoke fails</td><td>CloudWatch error / IAM role</td><td>Grant connect:InvokeLambdaFunction, check timeout</td></tr><tr><td>Agent status stuck</td><td>Streams event logs</td><td>Clear browser cache, check CCP permissions</td></tr><tr><td>Recording missing</td><td>S3 bucket / encryption KMS key</td><td>Verify recording enablement and IAM S3 access</td></tr></table>"""),
    ("🎤 Interview", """<details><summary>How do you minimize risk during an Amazon Connect cutover?</summary><p class='ans'>Run parallel operation with split-DN forwarding, keep legacy active as rollback, validate end-to-end call flows with synthetic tests, and stage number ports in waves.</p></details>""")
)
new_sections.append({"id":"aws-connect-migration","num":"605","group":"Cloud Migrations","title":"☁️ AWS Connect Migration","sub":"Lift-and-shift or refactor voice/contact center from legacy ACD/PBX into Amazon Connect.","body":expert_body("AWS Connect Migration","CLOUD MIGRATIONS · MODULE 605 · aws-connect-migration","Move enterprise contact center workloads into Amazon Connect: assess, pilot, port numbers, rebuild flows, integrate CRM, and run parallel validation.",t605)})

# 606 Azure Communication Services
t606 = tabs(
    ("📘 Overview", """<ul><li><b>Azure Communication Services (ACS)</b> cloud-native APIs/SDKs for voice, video, chat, SMS, email.</li><li><b>PSTN:</b> buy numbers, use Direct Routing, or Teams interop.</li><li><b>Identity:</b> serverless Azure AD or ACS identity tokens.</li><li><b>Events:</b> Event Grid hooks for call state, SMS delivery, recording.</li></ul>"""),
    ("🏛️ Architecture", """<p>Typical flow:</p><ol><li>App backend exchanges Azure AD token for ACS access token.</li><li>Client SDK joins a <b>Call</b> or <b>Chat</b> thread.</li><li>PSTN call placed via <b>CallAutomation</b> or client SDK.</li><li>Media/Recording routed to Azure Blob via managed identities.</li></ol><p><b>Teams interop:</b> Azure Bot + Teams meeting ID allows external users to join Teams calls.</p>"""),
    ("⚙️ Configuration", """<ol><li>Create ACS resource in Azure portal.</li><li>Provision phone numbers (Geo/ Toll-free) and assign capabilities.</li><li>Configure Event Grid subscription for call/SMS events.</li><li>Set up managed identity and storage for call recording.</li><li>Deploy client app with ACS Calling/Web UI library.</li></ol><pre><code>// Node.js server token
const { CommunicationIdentityClient } = require('@azure/communication-identity');
const client = new CommunicationIdentityClient(connectionString);
const user = await client.createUser();
const token = await client.getToken(user, ['voip']);</code></pre>"""),
    ("🛠️ Troubleshoot", """<table><tr><th>Symptom</th><th>Evidence</th><th>Fix</th></tr><tr><td>Token expired</td><td>401 on SDK init</td><td>Refresh access token server-side</td></tr><tr><td>One-way media</td><td>SDK logs / TURN relay failure</td><td>Open UDP 3478; allow TURN relays</td></tr><tr><td>SMS blocked</td><td>Delivery receipt failed</td><td>Check sender ID, content filtering, country rules</td></tr><tr><td>Recording not stored</td><td>Storage auth error</td><td>Verify managed identity Storage Blob Contributor</td></tr></table>"""),
    ("🎤 Interview", """<details><summary>When would you choose ACS over Teams Phone?</summary><p class='ans'>ACS for embedded/custom communication experiences in apps, IoT, or service-to-service calls. Teams Phone for user-centric PBX replacement with native Teams client.</p></details>""")
)
new_sections.append({"id":"azure-communication-services","num":"606","group":"Cloud Migrations","title":"🔷 Azure Communication Services","sub":"Build PSTN, SMS, Teams interop, and programmable voice/video apps on Azure.","body":expert_body("Azure Communication Services","CLOUD MIGRATIONS · MODULE 606 · azure-communication-services","ACS provides managed communication primitives—PSTN, SMS, video, chat, email—tightly integrated with Azure identity, events, and AI services.",t606)})

# 607 GCP CCAI Migration
t607 = tabs(
    ("📘 Overview", """<ul><li><b>CCAI</b> suite: Dialogflow CX (virtual agent), Agent Assist, Insights, Conversational Search.</li><li><b>Telephony integration:</b> AudioCodes/SBC → Dialogflow CX phone gateway or partner connector.</li><li><b>Data:</b> conversation data exported to BigQuery for analytics.</li></ul>"""),
    ("🏗️ Migration Plan", """<ol><li>Map current IVR intents and utterances to Dialogflow CX flows.</li><li>Design entities, parameters, webhook fulfillment, escalation paths.</li><li>Connect telephony partner via CCAI Connector or Dialogflow phone gateway.</li><li>Enable Agent Assist with knowledge bases and smart reply.</li><li>Run A/B test: legacy IVR vs Dialogflow, measure containment and CSAT.</li></ol>"""),
    ("⚙️ Configuration", """<ul><li>Create Dialogflow CX agent with flows, pages, routes.</li><li>Build fulfillment webhook (Cloud Functions/Run) for backend lookups.</li><li>Configure CCAI Insights with conversation profile and BigQuery export.</li><li>Integrate partner telephony using Session ID and StreamingDetectIntent.</li></ul><pre><code>// StreamingDetectIntent audio config
const request = {
  session: sessionPath,
  queryInput: { audio: { config: { encoding: 'AUDIO_ENCODING_MULAW', sampleRateHertz: 8000, languageCode: 'en-US' } } }
};</code></pre>"""),
    ("🛠️ Troubleshoot", """<table><tr><th>Symptom</th><th>Evidence</th><th>Fix</th></tr><tr><td>Intent not matched</td><td>Dialogflow history / training phrases</td><td>Add utterances, tune ML classification threshold</td></tr><tr><td>High latency</td><td>Webhook execution time</td><td>Move fulfillment closer, cache, reduce payload</td></tr><tr><td>Agent Assist blank</td><td>Knowledge base coverage</td><td>Index docs, verify FAQ articles</td></tr><tr><td>Audio garbled</td><td>Codec mismatch μ-law/A-law</td><td>Match telephony codec with Dialogflow config</td></tr></table>"""),
    ("🎤 Interview", """<details><summary>How do you measure CCAI success?</summary><p class='ans'>Containment rate, escalation accuracy, average handle time reduction, CSAT delta, intent match confidence, and cost per automated contact.</p></details>""")
)
new_sections.append({"id":"gcp-ccai-migration","num":"607","group":"Cloud Migrations","title":"🔶 GCP CCAI Migration","sub":"Migrate contact center to Google Cloud CCAI: Dialogflow CX, Agent Assist, Insights, and telephony integration.","body":expert_body("GCP CCAI Migration","CLOUD MIGRATIONS · MODULE 607 · gcp-ccai-migration","Google Cloud Contact Center AI (CCAI) adds conversational AI, live agent assist, and analytics on top of telco/telephony partners (Genesys, Avaya, Cisco, Twilio).",t607)})

# 608 Hybrid CUCM→Webex Calling Cutover
t608 = tabs(
    ("📘 Overview", """<ul><li><b>Hybrid Calling</b> lets Webex app register to CUCM as a softphone while user prepares for cloud move.</li><li><b>Cutover waves:</b> pilot → site/department waves → full migration.</li><li><b>PSTN options:</b> keep CUBE as Local Gateway, use Webex Calling PSTN, or partner Cloud Connected PSTN.</li></ul>"""),
    ("🏗️ Cutover Plan", """<ol><li><b>Discovery:</b> export DNs, partitions, CSS, devices, firmware, dependencies.</li><li><b>Dial plan normalization:</b> ensure +E.164 consistency; map CUCM partitions to Webex locations.</li><li><b>Provision:</b> Webex org, locations, users, devices in Control Hub.</li><li><b>Configure Local Gateway</b> with CUCM and Webex trunks for inter-cluster.</li><li><b>Pilot:</b> migrate test users, validate voicemail, AA, CQ, emergency.</li><li><b>Waves:</b> migrate by site, update route patterns, port DIDs.</li></ol>"""),
    ("⚙️ Configuration", """<ul><li>CUCM: build SIP trunk to LGW; route patterns for Webex DNs.</li><li>LGW/CUBE: two dial-peers—one to CUCM, one to Webex Calling.</li><li>Webex: assign licenses, configure locations, assign numbers/devices.</li><li>Unity Connection: enable single inbox or migrate to Webex voicemail.</li></ul><pre><code>// CUCM route pattern to Webex via LGW
Pattern: 8.XXXXX
Partition: PT-Webex
Gateway/Route List: RL-LGW
Called Party Transform: strip prefix 8</code></pre>"""),
    ("🛠️ Troubleshoot", """<table><tr><th>Symptom</th><th>Evidence</th><th>Fix</th></tr><tr><td>Calls between CUCM and Webex fail</td><td>LGW SIP 404 / no route</td><td>Check called-party transforms and dial-peer destination</td></tr><tr><td>Voicemail conflict</td><td>Same DN in Unity and Webex</td><td>Disable CUCM mailbox, migrate to Webex voicemail</td></tr><tr><td>Emergency call from Webex misroutes</td><td>E911 location missing</td><td>Assign emergency address per location</td></tr><tr><td>Device not registering</td><td>Webex device activation URL</td><td>Verify MAC, network access, activation code</td></tr></table>"""),
    ("🎤 Interview", """<details><summary>How do you maintain dial plan during hybrid coexistence?</summary><p class='ans'>Use a Local Gateway as a SIP tandem between CUCM and Webex; normalize all numbers to +E.164; build route patterns/partitions that route inter-platform calls transparently.</p></details>""")
)
new_sections.append({"id":"cucm-webex-calling-cutover","num":"608","group":"Cloud Migrations","title":"🔀 Hybrid CUCM → Webex Calling Cutover","sub":"Parallel operation, directory number mapping, PSTN planning, and safe user migration from CUCM to Webex Calling.","body":expert_body("Hybrid CUCM → Webex Calling Cutover","CLOUD MIGRATIONS · MODULE 608 · cucm-webex-calling-cutover","Migrate enterprise CUCM estates to Webex Calling without losing dial plan integrity. Use hybrid calling, call forwarding, and wave-based cutover.",t608)})

# 609 Webex CC Flow Designer
t609 = tabs(
    ("📘 Overview", """<ul><li><b>Flow Designer</b> replaces traditional IVR scripting with visual nodes.</li><li>Supports voice, email, chat, social, and WhatsApp channels.</li><li><b>Nodes:</b> Play Message, Menu, Collect Digits, HTTP Request, Queue Contact, Agent Request, Sub-flow.</li><li><b>Integrations:</b> Salesforce, ServiceNow, MS Dynamics, custom REST via HTTP node.</li></ul>"""),
    ("🏛️ Architecture", """<p>Flow triggers:</p><ul><li><b>Entry Point (DNIS)</b> → flow published to entry point.</li><li><b>API-triggered flow</b> for digital channels.</li><li><b>Sub-flow</b> reusable modules for authentication, routing logic.</li></ul><p>Data: flow variables, custom variables, ANI/DNIS, CRM lookup results. Analytics: Flow Execution Records exported to WxCC Analyzer.</p>"""),
    ("⚙️ Configuration", """<ol><li>Create flow from template or blank.</li><li>Add nodes: Play Message → Menu → Queue Contact.</li><li>Configure Queue node with skill-based or profile-based routing.</li><li>Add HTTP node to fetch customer context from CRM.</li><li>Set flow-level variables and error handling.</li><li>Validate, publish, and map to Entry Point.</li></ol><pre><code>// HTTP node JSON path example
{{customer.value.firstName}}
{{apiResponse.data.accountTier}}</code></pre>"""),
    ("🛠️ Troubleshoot", """<table><tr><th>Symptom</th><th>Evidence</th><th>Fix</th></tr><tr><td>Flow not triggered</td><td>Entry point mapping</td><td>Publish flow and attach to entry point</td></tr><tr><td>HTTP node fails</td><td>Flow debug logs / 4xx 5xx</td><td>Check URL, auth header, timeout, SSL cert</td></tr><tr><td>Long queue waits</td><td>Analyzer queue metrics</td><td>Add callback, overflow queue, staffing forecast</td></tr><tr><td>Variable blank</td><td>Flow variable scope</td><td>Declare variable, set before use, check case</td></tr></table>"""),
    ("🎤 Interview", """<details><summary>How do you version and rollback flows?</summary><p class='ans'>Flow Designer keeps published versions. Rollback by republishing a previous version; test new flows in a sandbox entry point before production mapping.</p></details>""")
)
new_sections.append({"id":"webex-cc-flow-designer","num":"609","group":"CCaaS APIs & Platforms","title":"🎛️ Webex CC Flow Designer","sub":"Design IVR, routing, bots, and agent workflows in Webex Contact Center Flow Designer.","body":expert_body("Webex CC Flow Designer","CCaaS APIs & PLATFORMS · MODULE 609 · webex-cc-flow-designer","Webex Contact Center Flow Designer is a low-code canvas for building voice/chat flows, integrating CRM, and orchestrating AI-powered customer journeys.",t609)})

# 610 Amazon Connect Contact Flows
t610 = tabs(
    ("📘 Overview", """<ul><li><b>Contact Flow</b> blocks: Set Voice, Play Prompt, Get Customer Input, Set Queue, Transfer to Queue, Invoke AWS Lambda, Disconnect.</li><li><b>Types:</b> Inbound, Outbound whisper, Transfer to agent/queue, Customer queue, Hold.</li><li><b>Lex integration:</b> speech and DTMF input with slot filling.</li></ul>"""),
    ("🏛️ Architecture", """<p>Flow lifecycle:</p><ol><li>Phone number → Contact Flow (ARN).</li><li>Play prompt / Get customer input (DTMF or Lex).</li><li>Invoke Lambda for CRM lookup, authentication.</li><li>Set queue based on intent/attributes.</li><li>Transfer to queue; agent accepts via CCP.</li><li>Post-contact: CTR to S3, Contact Lens analysis.</li></ol>"""),
    ("⚙️ Configuration", """<ol><li>Create contact flow from template.</li><li>Add Set Logging Behavior and Set Voice blocks.</li><li>Get Customer Input with Lex bot or DTMF.</li><li>Invoke Lambda function; parse $.External attributes.</li><li>Set working queue and transfer.</li><li>Publish and associate with phone number.</li></ol><pre><code>// Lambda response attributes for Connect
{
  "Attributes": {
    "accountTier": "Gold",
    "preferredAgent": "agent1"
  }
}</code></pre>"""),
    ("🛠️ Troubleshoot", """<table><tr><th>Symptom</th><th>Evidence</th><th>Fix</th></tr><tr><td>Lex not hearing</td><td>Audio logs / barge-in setting</td><td>Enable barge-in, check grammar/language</td></tr><tr><td>Lambda timeout</td><td>CloudWatch logs</td><td>Increase function timeout, optimize query</td></tr><tr><td>Queue never selected</td><td>Contact trace flow path</td><td>Check branch conditions and attribute names</td></tr><tr><td>No CTR data</td><td>S3 lifecycle / IAM</td><td>Enable contact records, verify S3 bucket policy</td></tr></table>"""),
    ("🎤 Interview", """<details><summary>How do you handle sensitive data in Contact Flows?</summary><p class='ans'>Mark attributes as sensitive to mask in logs/CTR, use KMS encryption, avoid logging PII in Lex, and route sensitive flows to secure queues.</p></details>""")
)
new_sections.append({"id":"amazon-connect-contact-flows","num":"610","group":"CCaaS APIs & Platforms","title":"📞 Amazon Connect Contact Flows","sub":"IVR design, Lex bots, Lambda integration, queue routing, and analytics in Amazon Connect.","body":expert_body("Amazon Connect Contact Flows","CCaaS APIs & PLATFORMS · MODULE 610 · amazon-connect-contact-flows","Amazon Connect Contact Flows orchestrate the customer journey with drag-and-drop blocks, Lex NLU, Lambda backends, and real-time analytics.",t610)})

# 611 Twilio Studio & Elastic SIP
t611 = tabs(
    ("📘 Overview", """<ul><li><b>Twilio Studio</b> visual builder for IVR, bots, notifications, surveys.</li><li><b>Twilio Functions</b> serverless runtime for custom logic.</li><li><b>Elastic SIP Trunking</b>: global PSTN connectivity with PAYG pricing.</li><li><b>Super Network:</b> carrier redundancy and dynamic routing.</li></ul>"""),
    ("🏛️ Architecture", """<p><b>Studio Flow trigger:</b> Incoming Message / Call / API Request / Subflow.</p><p><b>Common widgets:</b> Say/Play, Gather Input, Split Based On, Run Function, Send to Flex, Connect Call To.</p><p><b>Elastic SIP:</b> Twilio Termination (outbound) + Origination (inbound) URIs, IP ACL, credential lists, secure trunking (TLS/SRTP).</p>"""),
    ("⚙️ Configuration", """<ol><li>Buy phone number in Twilio Console.</li><li>Create Studio Flow; configure widgets and transitions.</li><li>Assign number → Studio Flow.</li><li>For SIP trunk: create trunk, add termination/origination URIs, whitelist IPs, configure CNAME.</li><li>Integrate Flex or custom contact center via TaskRouter.</li></ol><pre><code>// Twilio Function to route by VIP flag
exports.handler = function(context, event, callback) {
  const response = new Twilio.twiml.VoiceResponse();
  if (event.vip === 'true') {
    response.dial('+18005551234');
  } else {
    response.redirect('https://handler.twilio.com/...');
  }
  callback(null, response);
};</code></pre>"""),
    ("🛠️ Troubleshoot", """<table><tr><th>Symptom</th><th>Evidence</th><th>Fix</th></tr><tr><td>Flow not starting</td><td>Number configuration</td><td>Point number to Studio Flow webhook</td></tr><tr><td>SIP 403</td><td>Trunk ACL / credential list</td><td>Add customer IP, verify auth</td></tr><tr><td>No audio</td><td>Codec mismatch / firewall</td><td>Allow Twilio IP ranges, use G.711</td></tr><tr><td>High latency</td><td>Edge location</td><td>Use closest Twilio edge location</td></tr></table>"""),
    ("🎤 Interview", """<details><summary>When is Twilio Elastic SIP preferred over a regional telco?</summary><p class='ans'>When you need rapid global scale, API-driven provisioning, elastic capacity, and built-in redundancy without long-term commitments.</p></details>""")
)
new_sections.append({"id":"twilio-studio-elastic-sip","num":"611","group":"CCaaS APIs & Platforms","title":"🔷 Twilio Studio & Elastic SIP","sub":"Visual IVR with Twilio Studio, programmable voice, and Elastic SIP Trunking for global PSTN.","body":expert_body("Twilio Studio & Elastic SIP","CCaaS APIs & PLATFORMS · MODULE 611 · twilio-studio-elastic-sip","Twilio combines low-code Studio flows with powerful APIs and Elastic SIP Trunking for rapid, global communication apps.",t611)})

# 612 Principal Architect Interview Deep-Dive
t612 = tabs(
    ("📘 Overview", """<ul><li><b>Scope:</b> design reviews, migration strategy, cost modeling, risk management, team leadership.</li><li><b>Frameworks:</b> LICC proof grammar, RFP scoring, TCO/ROI, RACI, rollback planning.</li><li><b>Delivery:</b> whiteboard architecture, present to C-level, defend decisions under challenge.</li></ul>"""),
    ("🧠 Question Bank", """<details><summary>Design a global UCaaS rollout for 50k users across 40 countries.</summary><p class='ans'>Key axes: data residency, PSTN strategy per country, identity federation, network readiness, pilot waves, training, support tiering, and compliance. Use regional hubs, redundant Internet/MPLS, SBCs, and phased cutover.</p></details><details><summary>How do you decide build vs buy for a contact-center AI feature?</summary><p class='ans'>Compare time-to-market, total cost of ownership, data privacy, integration depth, and in-house ML capability. Buy when commodity; build when differentiation or strict data control is required.</p></details><details><summary>Explain a major outage you led recovery for.</summary><p class='ans'>Use STAR: Situation (SEV-1 symptoms), Task (restore service + protect data), Action (LICC evidence, rollback, war-room communication), Result (MTTR, RCA, preventive measures).</p></details>"""),
    ("📊 Scoring Rubric", """<table><tr><th>Dimension</th><th>Strong</th><th>Weak</th></tr><tr><td>Technical depth</td><td>First-principles explanation with protocols/counters</td><td>Vague buzzwords</td></tr><tr><td>Business acumen</td><td>TCO, risk, compliance, stakeholder trade-offs</td><td>Tech-only answer</td></tr><tr><td>Communication</td><td>Structured, audience-calibrated</td><td>Jargon dump</td></tr><tr><td>Delivery</td><td>Pilot waves, rollback, success metrics</td><td>Big-bang without validation</td></tr></table>"""),
    ("📝 Mock Panel", """<ol><li>Whiteboard: hybrid CUCM→Teams migration.</li><li>Cost estimate: 5-year TCO of cloud vs on-prem.</li><li>Risk register: top 5 risks and mitigations.</li><li>Stakeholder map: CIO, CISO, legal, regional ops.</li><li>Architecture decision record: why Direct Routing vs Operator Connect.</li></ol>""")
)
new_sections.append({"id":"principal-architect-interview","num":"612","group":"Practice Banks","title":"🎤 Principal Architect Interview Deep-Dive","sub":"Executive-level design, cost, risk, stakeholder, and delivery questions for UC/CC principal architect roles.","body":expert_body("Principal Architect Interview Deep-Dive","PRACTICE BANKS · MODULE 612 · principal-architect-interview","Prepare for principal-level interviews where the focus shifts from config commands to business outcomes, architectural trade-offs, and leading multi-vendor programs.",t612)})

# 613 Ghost calls SEV
t613 = tabs(
    ("🚨 SEV Brief", """<ul><li><b>Impact:</b> user disruption, potential toll fraud, security incident.</li><li><b>Hypotheses:</b> phone exposed on public IP, SBC ACL missing, SIP ALG mangling, rogue registration.</li><li><b>Safety:</b> do not block legitimate PSAP/emergency traffic.</li></ul>"""),
    ("🔍 Diagnose", """<ol><li>Capture INVITE at phone or edge: <code>show sip-ua calls</code>, packet capture.</li><li>Check source IP and User-Agent. Legitimate source? Spoofed?</li><li>Verify phone is on public IP or NAT with SIP ALG.</li><li>Review SBC/CUBE firewall rules for UDP 5060 open to world.</li><li>Check CDR for 1-second calls or 4xx responses.</li></ol><pre><code>// CUBE: show current sip calls from unknown source
show sip-ua calls brief
show voice call status</code></pre>"""),
    ("🛡️ Mitigate", """<table><tr><th>Control</th><th>Implementation</th></tr><tr><td>ACL</td><td>Allow SIP only from carrier/SBC IPs</td></tr><tr><td>NAT + no public IP</td><td>Place phones behind firewall; disable DMZ</td></tr><tr><td>SIP ALG off</td><td>Disable on edge firewall to prevent rewriting</td></tr><tr><td>Authentication</td><td>Digest auth on registrations; reject anonymous</td></tr><tr><td>Rate limiting</td><td>Throttle INVITE rate at SBC</td></tr></table>"""),
    ("✅ Verify", """<ul><li>No phantom calls for 24h after ACL deployment.</li><li>SIP capture shows only authorized sources.</li><li>Legitimate inbound/outbound calls still complete.</li><li>Document IOCs and close SEV with RCA.</li></ul>""")
)
new_sections.append({"id":"sev-ghost-calls","num":"613","group":"Tricky SEVs v17","title":"👻 Ghost Calls / Phantom SIP INVITEs","sub":"Phones ring with no caller, dead air, or random INVITEs from the Internet. SEV response with LICC proof.","body":sev_body("Ghost Calls / Phantom SIP INVITEs","TRICKY SEVs v17 · MODULE 613 · sev-ghost-calls","Desk phones ring at odd hours with no audio, calling number 100, 1000, or blank. Root cause: SIP endpoints exposed to Internet receiving scanned/spoofed INVITEs.",t613)})

# 614 DSP exhaustion SEV
t614 = tabs(
    ("🚨 SEV Brief", """<ul><li><b>Impact:</b> new calls rejected, conference bridges collapse, prompts/MoH cut out.</li><li><b>Hypotheses:</b> DSP farm undersized, codec mismatch forcing transcoding, hung DSP sessions, hardware failure.</li><li><b>Safety:</b> preserve emergency calling capacity.</li></ul>"""),
    ("🔍 Diagnose", """<ol><li><code>show dspfarm profile</code> — active sessions vs max.</li><li><code>show voice dsp detailed</code> — channel state, errors.</li><li>Identify codec mismatches (e.g., G.729↔G.711) forcing transcoding.</li><li>Check for stuck calls: <code>show call active voice brief</code>.</li><li>Review recent config changes to MRGL, regions, codec preferences.</li></ol><pre><code>// IOS-XE DSP checks
show dspfarm profile 1
show voice dsp group all
show dspfarm sessions</code></pre>"""),
    ("🛡️ Mitigate", """<table><tr><th>Action</th><th>When</th></tr><tr><td>Add DSPs / PVDM</td><td>Chronic over-subscription</td></tr><tr><td>Align codec policy</td><td>Reduce transcoding by preferring G.711 end-to-end</td></tr><tr><td>Restart hung session</td><td>Clear stuck call or reset DSP farm</td></tr><tr><td>Offload conferencing</td><td>Use software bridge or cloud mixer</td></tr><tr><td>Capacity alert</td><td>SNMP trap at 80% DSP utilization</td></tr></table>"""),
    ("✅ Verify", """<ul><li>DSP utilization below 70% during peak.</li><li>Test calls across codec boundaries succeed.</li><li>Conference bridge joins complete.</li><li>Monitoring alert configured for future exhaustion.</li></ul>""")
)
new_sections.append({"id":"sev-dsp-exhaustion","num":"614","group":"Tricky SEVs v17","title":"🔥 DSP Exhaustion / Transcoder Failure","sub":"Calls fail mid-conversation, conference drops, or MoH breaks. DSP resource exhaustion SEV.","body":sev_body("DSP Exhaustion / Transcoder Failure","TRICKY SEVs v17 · MODULE 614 · sev-dsp-exhaustion","Voice gateway runs out of DSP channels for transcoding, conferencing, or media termination. Symptoms include fast-busy, one-way audio, or failed conference joins.",t614)})

def main():
    print('Reading HTML...')
    text = HTML.read_text(encoding='utf-8')
    match = re.search(r'window\.SECTIONS\s*=\s*(\[.*?\]);', text, re.DOTALL)
    if not match:
        raise RuntimeError('Could not find window.SECTIONS array')
    arr_text = match.group(1)
    sections = json.loads(arr_text)
    print(f'Loaded {len(sections)} sections')

    sections.extend(new_sections)
    print(f'New count: {len(sections)}')

    new_arr_text = json.dumps(sections, ensure_ascii=False)
    new_js = f'window.SECTIONS = {new_arr_text};'
    text = text[:match.start()] + new_js + text[match.end():]

    text = re.sub(
        r'window\.STATS\s*=\s*\{[^}]+\};',
        'window.STATS = {"version": "19.1-UI", "built": "2026-08-01T06:07:54Z", "sections": 614, "note": "Full 614-section curriculum · mobile drawer nav · safe boot · browser-friendly"};',
        text,
        count=1
    )

    # After json.dumps, the home body string has escaped quotes; handle both forms.
    text = text.replace('<b id=\\"st-sec\\">602</b>', '<b id=\\"st-sec\\">614</b>')
    text = text.replace('<b id="st-sec">602</b>', '<b id="st-sec">614</b>')

    HTML.write_text(text, encoding='utf-8')
    print(f'Wrote {HTML}')
    append_report(f'EDITED re-applied 12 expert sections (603-614) and updated STATS to 614 / version 19.1-UI / hero counter — {now()}')

if __name__ == '__main__':
    main()
