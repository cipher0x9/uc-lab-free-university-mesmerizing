/*!
 * UC Lab Free University — Resources Registry
 * ---------------------------------------------------------------------------
 * Curated, real, official/primary-source reference links only. No invented
 * URLs. Every entry below was fetched and verified to resolve (HTTP 200 or a
 * clean redirect to a live page) during Wave E.
 *
 * Design:
 *  - window.UC_RESOURCES.bySection[id]  -> array of links specific to a
 *    section id (used mainly for the 13 hub-* chapter landing sections).
 *  - window.UC_RESOURCES.byGroup[group] -> array of links shared by every
 *    section in a curriculum group (reused, not duplicated per-section).
 *  - window.UC_RESOURCES.registry       -> flat de-duplicated master list
 *    (for the Resources Index section / audits).
 *
 * Maintainer source for the Official Resources drawer. The flagship file
 * university/v17-UNIVERSITY.html ships with window.UC_RESOURCES inlined so
 * the one-file campus stays offline. This sibling file is not loaded by
 * the flagship at boot. Rebuild via tools/build_uc_resources.py.
 * ---------------------------------------------------------------------------
 */
(function () {
  "use strict";

  // ---- Vendor/topic link pools (reused across sections) --------------------
  var CUCM = [
    { title: "CUCM (CallManager) Support Series", url: "https://www.cisco.com/c/en/us/support/unified-communications/unified-communications-manager-callmanager/series.html", vendor: "Cisco", why: "Official CUCM support home — releases, docs, downloads" },
    { title: "CUCM Installation Guides", url: "https://www.cisco.com/c/en/us/support/unified-communications/unified-communications-manager-callmanager/products-installation-guides-list.html", vendor: "Cisco", why: "Official install guide index across CUCM releases" },
    { title: "CUCM Maintenance Guides", url: "https://www.cisco.com/c/en/us/support/unified-communications/unified-communications-manager-callmanager/products-maintenance-guides-list.html", vendor: "Cisco", why: "Official maintain/administer guide index" },
    { title: "CUCM Release Notes", url: "https://www.cisco.com/c/en/us/support/unified-communications/unified-communications-manager-callmanager/products-release-notes-list.html", vendor: "Cisco", why: "Track version-specific fixes and known issues" }
  ];
  var CUBE = [
    { title: "Cisco Unified Border Element (CUBE) Support Series", url: "https://www.cisco.com/c/en/us/support/unified-communications/unified-border-element/series.html", vendor: "Cisco", why: "Official CUBE/SBC support home" },
    { title: "CUBE Configuration Guide (IOS XE Voice)", url: "https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/voice/cube/ios-xe/config/ios-xe-book.html", vendor: "Cisco", why: "Primary IOS-XE CUBE configuration reference" }
  ];
  var SIP_RFC = [
    { title: "RFC 3261 — SIP: Session Initiation Protocol", url: "https://www.rfc-editor.org/rfc/rfc3261", vendor: "IETF", why: "The core SIP specification" },
    { title: "RFC 3550 — RTP: A Transport Protocol for Real-Time Applications", url: "https://www.rfc-editor.org/rfc/rfc3550", vendor: "IETF", why: "RTP media transport fundamentals" },
    { title: "RFC 3551 — RTP Profile for Audio and Video Conferences", url: "https://www.rfc-editor.org/rfc/rfc3551", vendor: "IETF", why: "Audio/video payload profile companion to RTP" },
    { title: "RFC 3711 — The Secure Real-time Transport Protocol (SRTP)", url: "https://www.rfc-editor.org/rfc/rfc3711", vendor: "IETF", why: "Media encryption baseline for modern UC" },
    { title: "RFC 4566 — SDP: Session Description Protocol", url: "https://www.rfc-editor.org/rfc/rfc4566", vendor: "IETF", why: "Media negotiation format used by SIP/WebRTC" },
    { title: "RFC 3264 — Offer/Answer Model with SDP", url: "https://www.rfc-editor.org/rfc/rfc3264", vendor: "IETF", why: "Explains SDP offer/answer call setup" },
    { title: "RFC 3323 — Privacy Mechanism for SIP", url: "https://www.rfc-editor.org/rfc/rfc3323", vendor: "IETF", why: "Basis for Privacy/anonymous calling headers" },
    { title: "RFC 3325 — P-Asserted-Identity for Trusted Networks", url: "https://www.rfc-editor.org/rfc/rfc3325", vendor: "IETF", why: "Used constantly in CUBE/SBC trunk troubleshooting" },
    { title: "RFC 2833 — RTP Payload for DTMF Digits (obsoleted by 4733)", url: "https://www.rfc-editor.org/rfc/rfc2833", vendor: "IETF", why: "Legacy DTMF relay reference, still seen in configs" },
    { title: "RFC 4733 — RTP Payload for DTMF Digits, Tones and Signals", url: "https://www.rfc-editor.org/rfc/rfc4733", vendor: "IETF", why: "Current DTMF relay spec (rfc2833 successor)" },
    { title: "RFC 3428 — SIP Extension for Instant Messaging", url: "https://www.rfc-editor.org/rfc/rfc3428", vendor: "IETF", why: "SIP MESSAGE method reference" },
    { title: "RFC 3515 — The SIP REFER Method", url: "https://www.rfc-editor.org/rfc/rfc3515", vendor: "IETF", why: "Call transfer signaling reference" },
    { title: "RFC 5389 — STUN: Session Traversal Utilities for NAT", url: "https://www.rfc-editor.org/rfc/rfc5389", vendor: "IETF", why: "NAT traversal building block for MRA/WebRTC" },
    { title: "RFC 8445 — ICE: Interactive Connectivity Establishment", url: "https://www.rfc-editor.org/rfc/rfc8445", vendor: "IETF", why: "Modern NAT traversal used by Expressway/WebRTC" },
    { title: "IANA SIP Parameters Registry", url: "https://www.iana.org/assignments/sip-parameters/sip-parameters.xhtml", vendor: "IANA", why: "Authoritative registry of SIP headers, methods, response codes" },
    { title: "W3C WebRTC 1.0 Specification", url: "https://www.w3.org/TR/webrtc/", vendor: "W3C", why: "Browser real-time media API standard behind Webex/Teams web clients" }
  ];
  var QOS = [
    { title: "RFC 2474 — DiffServ Field in IPv4/IPv6 Headers", url: "https://www.rfc-editor.org/rfc/rfc2474", vendor: "IETF", why: "Foundation of DSCP marking used in UC QoS" },
    { title: "RFC 4594 — Configuration Guidelines for DiffServ Classes", url: "https://www.rfc-editor.org/rfc/rfc4594", vendor: "IETF", why: "Reference class model (EF/AF) applied to voice/video QoS" },
    { title: "RFC 3246 — An Expedited Forwarding PHB", url: "https://www.rfc-editor.org/rfc/rfc3246", vendor: "IETF", why: "Defines EF, the DSCP class voice traffic typically uses" }
  ];
  var UCCE = [
    { title: "UCCE Support Series", url: "https://www.cisco.com/c/en/us/support/customer-collaboration/unified-contact-center-enterprise/series.html", vendor: "Cisco", why: "Official UCCE/ICM support home" },
    { title: "UCCE Installation Guides", url: "https://www.cisco.com/c/en/us/support/customer-collaboration/unified-contact-center-enterprise/products-installation-guides-list.html", vendor: "Cisco", why: "Official install guide index" },
    { title: "UCCE Maintenance Guides", url: "https://www.cisco.com/c/en/us/support/customer-collaboration/unified-contact-center-enterprise/products-maintenance-guides-list.html", vendor: "Cisco", why: "Official maintenance/administration guide index" },
    { title: "UCCE Implementation & Design Guides", url: "https://www.cisco.com/c/en/us/support/customer-collaboration/unified-contact-center-enterprise/products-implementation-design-guides-list.html", vendor: "Cisco", why: "Design-guide index for solution architects" },
    { title: "Solution Design Guide for UCCE 15.0(1)", url: "https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cust_contact/contact_center/icm_enterprise/icm_enterprise_15_0_1/design/guide/ucce_b_ucce_soldg-for-unified-cce-1501.html", vendor: "Cisco", why: "Current reference design/sizing guide" }
  ];
  var PCCE = [
    { title: "PCCE Support Series", url: "https://www.cisco.com/c/en/us/support/customer-collaboration/packaged-contact-center-enterprise/series.html", vendor: "Cisco", why: "Official Packaged CCE support home, install/upgrade docs" }
  ];
  var WEBEX = [
    { title: "Webex Help Center", url: "https://help.webex.com/en-us/", vendor: "Cisco", why: "End-user and admin help articles for all Webex apps" },
    { title: "Webex Calling Overview", url: "https://help.webex.com/en-us/landing/ld-o91qrfb-CiscoWebexMeetings/Webex-Calling", vendor: "Cisco", why: "Cloud calling admin/setup landing page" },
    { title: "Webex Contact Center Admin Setup Guide", url: "https://help.webex.com/en-us/article/n1qbbmp/Webex-Contact-Center-Set-Up-Guide-for-Administrators", vendor: "Cisco", why: "Official CC provisioning walkthrough" },
    { title: "Webex Developer Docs", url: "https://developer.webex.com/docs", vendor: "Cisco", why: "APIs, SDKs and webhooks for Webex integrations" },
    { title: "Webex Developer Getting Started", url: "https://developer.webex.com/docs/api/getting-started", vendor: "Cisco", why: "Auth + first API call walkthrough" },
    { title: "Webex Calling Product Page", url: "https://www.webex.com/suite/enterprise-cloud-calling.html", vendor: "Cisco", why: "Product overview and licensing tiers" },
    { title: "Webex Contact Center Product Page", url: "https://www.webex.com/us/en/products/customer-experience/contact-center.html", vendor: "Cisco", why: "CCaaS platform overview" }
  ];
  var CONNECT = [
    { title: "Amazon Connect Documentation Home", url: "https://docs.aws.amazon.com/connect/", vendor: "AWS", why: "Root doc index for Amazon Connect" },
    { title: "Amazon Connect Administrator Guide", url: "https://docs.aws.amazon.com/connect/latest/adminguide/what-is-amazon-connect.html", vendor: "AWS", why: "Core admin/architecture concepts" },
    { title: "Amazon Connect API Reference", url: "https://docs.aws.amazon.com/connect/latest/APIReference/welcome.html", vendor: "AWS", why: "Full REST API reference for automation/integrations" },
    { title: "Amazon Connect Instances Guide", url: "https://docs.aws.amazon.com/connect/latest/adminguide/connect-instances.html", vendor: "AWS", why: "Instance provisioning and multi-region design" },
    { title: "Contact Lens API Reference", url: "https://docs.aws.amazon.com/contact-lens/latest/APIReference/Welcome.html", vendor: "AWS", why: "Call analytics/sentiment API for CX quality programs" },
    { title: "Amazon Connect FAQs", url: "https://aws.amazon.com/connect/faqs/", vendor: "AWS", why: "Pricing, scaling and capability Q&A" }
  ];
  var E911 = [
    { title: "Cisco Emergency Responder Product Page", url: "https://www.cisco.com/c/en/us/products/unified-communications/emergency-responder/index.html", vendor: "Cisco", why: "CER overview and PSAP routing concept" },
    { title: "Cisco Emergency Responder Administration Guide (R15)", url: "https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cer/15/english/administration/guide/cer0_b_cisco-emergency-responder-administration-guide-15/cer0_m_preface.html", vendor: "Cisco", why: "Current CER admin/configuration reference" },
    { title: "FCC Kari's Law & RAY BAUM's Act — Small Entity Compliance Guide", url: "https://docs.fcc.gov/public/attachments/DA-20-431A1.pdf", vendor: "FCC", why: "Federal direct-911-dial + dispatchable-location compliance rules" }
  ];
  var EXPRESSWAY = [
    { title: "Expressway Support Series", url: "https://www.cisco.com/c/en/us/support/unified-communications/expressway-series/series.html", vendor: "Cisco", why: "Official Expressway/MRA support home" },
    { title: "Expressway Installation & Configuration Guides", url: "https://www.cisco.com/c/en/us/support/unified-communications/expressway-series/products-installation-and-configuration-guides-list.html", vendor: "Cisco", why: "MRA deployment guide index (select your X-version)" }
  ];
  var MIGRATIONS = [
    { title: "Microsoft Teams Phone: Direct Routing Overview", url: "https://learn.microsoft.com/en-us/microsoftteams/direct-routing-landing-page", vendor: "Microsoft", why: "SBC-to-Teams trunking pattern used in most UC migrations" },
    { title: "Microsoft Teams Phone System Features", url: "https://learn.microsoft.com/en-us/microsoftteams/here-s-what-you-get-with-phone-system", vendor: "Microsoft", why: "What Teams Phone actually replaces from legacy PBX/CUCM" },
    { title: "Plan Microsoft Teams Direct Routing", url: "https://learn.microsoft.com/en-us/microsoftteams/direct-routing-plan", vendor: "Microsoft", why: "Capacity/SBC planning checklist for cutover projects" },
    { title: "Microsoft 365 Network Connectivity Principles", url: "https://learn.microsoft.com/en-us/microsoft-365/enterprise/microsoft-365-network-connectivity-principles", vendor: "Microsoft", why: "Network readiness guidance for cloud voice migrations" },
    { title: "Azure Communication Services Overview", url: "https://learn.microsoft.com/en-us/azure/communication-services/overview", vendor: "Microsoft", why: "Programmable comms platform relevant to hybrid migrations" },
    { title: "AWS Overview Whitepaper", url: "https://docs.aws.amazon.com/whitepapers/latest/aws-overview/aws-overview.html", vendor: "AWS", why: "Cloud fundamentals for teams migrating CC workloads to AWS" },
    { title: "Google Cloud Architecture Framework", url: "https://cloud.google.com/architecture/framework", vendor: "Google Cloud", why: "Design principles applicable to CCAI/GCP migrations" },
    { title: "Google Dialogflow CX Documentation", url: "https://cloud.google.com/dialogflow/cx/docs", vendor: "Google Cloud", why: "Conversational IVR platform used in Google CC migrations" },
    { title: "Google CCAI Platform Documentation", url: "https://cloud.google.com/contact-center/ccai-platform/docs", vendor: "Google Cloud", why: "Google's CCaaS platform docs for migration scoping" }
  ];
  var SEV = [
    { title: "Cisco Worldwide Support Contacts", url: "https://www.cisco.com/c/en/us/support/web/tsd-cisco-worldwide-contacts.html", vendor: "Cisco", why: "Escalation path for SEV1/SEV2 TAC cases" },
    { title: "Cisco Support & Downloads Home", url: "https://www.cisco.com/c/en/us/support/index.html", vendor: "Cisco", why: "Central entry point to bugs, docs, and software downloads" }
  ];
  var TWILIO = [
    { title: "Twilio Docs Home", url: "https://www.twilio.com/docs", vendor: "Twilio", why: "Root of all Twilio product documentation" },
    { title: "Twilio Voice Docs", url: "https://www.twilio.com/docs/voice", vendor: "Twilio", why: "Programmable Voice API reference" },
    { title: "Twilio Elastic SIP Trunking Docs", url: "https://www.twilio.com/docs/sip-trunking", vendor: "Twilio", why: "SIP trunk interconnect used in CUBE-to-Twilio designs" },
    { title: "Twilio Usage API", url: "https://www.twilio.com/docs/usage/api", vendor: "Twilio", why: "Programmatic usage/billing records" },
    { title: "Twilio Flex Docs", url: "https://www.twilio.com/docs/flex", vendor: "Twilio", why: "Programmable contact-center platform docs" },
    { title: "Twilio Studio Docs", url: "https://www.twilio.com/docs/studio", vendor: "Twilio", why: "Visual IVR/flow builder used in CC migrations" }
  ];
  var CAMPUS = [
    { title: "UC Lab Free University — GitHub Repo", url: "https://github.com/cipher0x9/uc-lab-free-university-mesmerizing", vendor: "GitHub", why: "Source repo for this campus — issues, releases, downloads" }
  ];

  // ---- Group defaults: shared across every section in a curriculum group --
  var byGroup = {
    "Vendor Deep-Dives": [].concat(CUCM.slice(0, 2), CUBE, WEBEX.slice(0, 2)),
    "Cloud Migrations": MIGRATIONS,
    "CCaaS APIs & Platforms": [].concat(CONNECT.slice(0, 3), WEBEX.slice(3, 5), TWILIO),
    "Google CC & APIs": [MIGRATIONS[7], MIGRATIONS[8], MIGRATIONS[6]],
    "Network Core": [].concat(SIP_RFC.slice(0, 6), QOS),
    "Protocol Expert": SIP_RFC,
    "Tricky SEVs v17": SEV,
    "Tricky SEVs": SEV,
    "More Vendors": [].concat(CUCM.slice(2), UCCE.slice(0, 2), PCCE),
    "Products": [].concat(CUCM.slice(0, 1), WEBEX.slice(0, 1), CONNECT.slice(0, 1)),
    "Architecture + Mastery": [].concat(UCCE.slice(3), EXPRESSWAY, MIGRATIONS.slice(3, 5)),
    "Architect Core": [].concat(UCCE.slice(3, 5), EXPRESSWAY),
    "Foundations": [].concat(SIP_RFC.slice(0, 4), CUCM.slice(0, 1)),
    "Campus": CAMPUS
  };

  // ---- Section-specific (hub landing pages) --------------------------------
  var bySection = {
    "hub-cucm": CUCM,
    "hub-cube-sbc": CUBE.concat(SIP_RFC.slice(6, 8)),
    "hub-sip": SIP_RFC,
    "hub-icm-ucce": UCCE,
    "hub-pcce": PCCE.concat(UCCE.slice(0, 1)),
    "hub-webex-cc": WEBEX,
    "hub-amazon-connect": CONNECT,
    "hub-e911-redsky": E911,
    "hub-qos": QOS,
    "hub-expressway": EXPRESSWAY.concat(SIP_RFC.slice(12, 14)),
    "hub-migrations": MIGRATIONS,
    "hub-sev-troubleshoot": SEV,
    "hub-interview": [].concat(UCCE.slice(3, 4), EXPRESSWAY.slice(0, 1), SIP_RFC.slice(0, 1))
  };

  // ---- Flat de-duplicated master registry (for audits / resources index) --
  var seen = {}, registry = [];
  Object.keys(bySection).concat(Object.keys(byGroup)).forEach(function (k) {
    var list = bySection[k] || byGroup[k] || [];
    list.forEach(function (item) {
      if (!item || !item.url || seen[item.url]) return;
      seen[item.url] = true;
      registry.push(item);
    });
  });

  window.UC_RESOURCES = {
    bySection: bySection,
    byGroup: byGroup,
    registry: registry
  };
})();
