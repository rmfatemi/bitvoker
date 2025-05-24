import React, { useMemo } from 'react';
import YamlEditor from './YamlEditor';

function RuleEditor({ rules, updateRules }) {
  const displayRules = useMemo(() => {
    return rules.filter(rule => rule.name !== "default-rule");
  }, [rules]);

  const handleRuleUpdate = (updatedDisplayRules) => {
    const defaultRule = rules.find(rule => rule.name === "default-rule");
    const newRules = defaultRule
      ? [defaultRule, ...updatedDisplayRules]
      : updatedDisplayRules;
    updateRules(newRules);
  };

  const rulesReference =
`- name: "custom-rule"                                               # rule identifier
  enabled: false                                                    # toggle rule on/off
  preprompt: "summarize this technical message briefly"             # if not empty runs through model
  match:                                                            # rule matching conditions
    source: ""                                                      # source identifier, empty matches any
    og_text_regex: ""                                               # match against original text, empty to match all
    ai_text_regex: ""                                               # match against ai-processed text, empty to match all
  notify:
    destinations: []                                                # destinations, empty for all
    original_message: # original message version
      enabled: true                                                 # enable/disable original text
      match_regex: ""                                               # only send if this matches, empty for always
    ai_summary: # ai-processed version
      enabled: true                                                 # explicitly control sending
      match_regex: ""                                               # only send if this matches, empty for always`;

  return (
    <YamlEditor
      data={displayRules}
      updateData={handleRuleUpdate}
      referenceText={rulesReference}
      title="Define your custom rules in YAML format:"
      referenceTitle="Rule Format Reference (all keys are mandatory)"
    />
  );
}

export default RuleEditor;
