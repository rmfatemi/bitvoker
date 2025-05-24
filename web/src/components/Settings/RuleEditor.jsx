import React from 'react';
import YamlEditor from './YamlEditor';

function RuleEditor({ rules, updateRules }) {
  const rulesReference =
`- name: "custom-rule"                                    # clear rule identifier
enabled: true                                            # toggle rule on/off
preprompt: "summarize this technical message briefly"    # if not empty runs through model
match:                                                   # rule matching conditions
  source: ""                                             # source identifier, empty matches any
  og_text_regex: ""                                      # match against original text, empty to match all
  ai_text_regex: ""                                      # match against ai-processed text, empty to match all
notify:
  destinations: []                                       # destinations, empty for all
  original_message:                                      # original message version
    enabled: true                                        # enable/disable original text
    match_regex: ""                                      # only send if this matches, empty for always
  ai_summary:                                            # ai-processed version
    enabled: true                                        # explicitly control sending
    match_regex: ""                                      # only send if this matches, empty for always`;
  return (
    <YamlEditor
      data={rules}
      updateData={updateRules}
      referenceText={rulesReference}
      title="Define your rules in YAML format:"
      referenceTitle="Rule Format Reference"
      editorHeight="40vh"
    />
  );
}

export default RuleEditor;
