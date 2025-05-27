import React, {useMemo} from 'react';
import YamlEditor from './YamlEditor';

function RuleEditor({rules, updateConfig}) {
    const displayRules = useMemo(() => {
        return rules.filter(rule => rule.name !== "default-rule");
    }, [rules]);

    const handleRuleUpdate = (updatedDisplayRules) => {
        const defaultRule = rules.find(rule => rule.name === "default-rule");
        const newRules = defaultRule
            ? [defaultRule, ...updatedDisplayRules]
            : updatedDisplayRules;

        updateConfig(prev => ({
            ...prev,
            rules: newRules
        }));
    };

    const rulesReference =
        `- name: 'example-rule-1'                      # unique rule identifier
  enabled: true                               # enable or disable this rule (true/false)
  preprompt: 'Summarize logs (20 words max):' # instructions prompt sent to the ai model along with the original text
  match:                                      # rule matching conditions; all conditions must be met to trigger (combined using an AND operator)
    source: ['192.168.20.112', 'pve.home']    # sender identifier; triggers if sender matches any of the listed ips or hostnames, an empty array ([]) matches all senders
    og_text_regex: ''                         # regex to apply to the original received text; an empty string ('') means it will match all text
    ai_text_regex: ''                         # regex to apply to the ai-processed text; an empty string ('') means it will match all text
  notify:                                     # conditions and destinations for sending notifications
    destinations: ['Telegram', 'Slack']       # notification destinations; an empty array ([]) sends to all configured and enabled destinations
    original_message:                         # conditions for sending original message version
      enabled: true                           # enable/disable including original text in the notification
      match_regex: ''                         # only send the original message if this regex matches; an empty string ('') always triggers sending
    ai_processed:                             # conditions for sending ai-processed version
      enabled: true                           # enable/disable including ai-processed text in the notification
      match_regex: ''                         # only send the ai-processed message if this regex matches; an empty string ('') always triggers sending`;

    return (
        <YamlEditor
            data={displayRules}
            updateData={handleRuleUpdate}
            referenceText={rulesReference}
            title="Define your custom rules in YAML format:"
            referenceTitle="Rule Format Reference"
        />
    );
}

export default RuleEditor;
