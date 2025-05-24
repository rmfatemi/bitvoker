import React, { useMemo } from 'react';
import YamlEditor from './YamlEditor';

function RuleEditor({ rules, updateConfig }) {
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
`- name: 'custom-rule-1'                                             # unique rule identifier
  enabled: true                                                     # enable or disable this rule (true/false)
  preprompt: 'Summarize this technical log message in 20 word: '    # if not empty string ('') runs through model
  match:                                                            # rule matching conditions
    source: '192.168.20.112'                                        # sender identifier, ip, or hostname, empty string ('') to match all
    og_text_regex: ''                                               # match regex against original text, empty string ('') to match all
    ai_text_regex: ''                                               # match regex against ai-processed text, empty string ('') to match all
  notify:
    destinations: ["Telegram", "Slack"]                             # destinations, empty array ([]) to send to all configured and enabled channels
    original_message:                                               # original message version
      enabled: true                                                 # enable/disable including original text in the notification
      match_regex: ''                                               # only send if this regex matches, empty string ('') to always send
    ai_summary:                                                     # ai-processed version
      enabled: true                                                 # enable/disable including ai summary text in the notification
      match_regex: ''                                               # only send if this regex matches, empty string ('') to always send`;

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
