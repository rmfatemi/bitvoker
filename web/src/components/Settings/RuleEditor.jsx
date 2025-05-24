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
`- name: 'custom-rule-1'                                             # rule identifier
  enabled: true                                                     # default rule is always enabled
  preprompt: 'summarize this technical message briefly and clearly' # if not empty string ('') runs through model
  match:                                                            # rule matching conditions
    source: ''                                                      # source identifier, empty string ('') matches any
    og_text_regex: ''                                               # match regex against original text, empty string ('') to match all
    ai_text_regex: ''                                               # match regex against ai-processed text, empty string ('') to match all
  notify:
    destinations: []                                                # destinations, empty array ([]) for all
    original_message:                                               # original message version
      enabled: true                                                 # enable/disable original text
      match_regex: ''                                               # only send if this regex matches, empty string ('') for always
    ai_summary:                                                     # ai-processed version
      enabled: true                                                 # explicitly control sending
      match_regex: ''                                               # only send if this regex matches, empty string ('') for always`;

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
