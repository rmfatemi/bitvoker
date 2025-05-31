import React, {useMemo, useCallback} from 'react';
import YamlEditor from './YamlEditor';

function RuleEditor({rules, updateConfig}) {
    const displayRules = useMemo(() => {
        return rules.filter(rule => rule && rule.name !== "default-rule");
    }, [rules]);

    const defaultRule = useMemo(() => rules.find(rule => rule.name === "default-rule"), [rules]);

    const handleRuleUpdate = (updatedDisplayRules) => {
        const newRules = defaultRule
            ? [defaultRule, ...updatedDisplayRules]
            : updatedDisplayRules;
        updateConfig(prev => ({
            ...prev,
            rules: newRules
        }));
    };

    const validateRules = useCallback((data) => {
        if (!defaultRule) {
            return "Validation Error: Default rule schema not found. Cannot validate.";
        }
        if (data === null || data === undefined) {
            return "YAML content cannot be empty.";
        }
        if (!Array.isArray(data)) {
            return "Invalid format: The root element must be a YAML list (array).";
        }

        const compareKeysRecursively = (objectToTest, schemaObject, path) => {
            if (typeof objectToTest !== 'object' || objectToTest === null) {
                return `Invalid structure: '${path}' must be an object.`;
            }
            for (const key in schemaObject) {
                if (!(key in objectToTest)) {
                    return `Missing key '${key}' in ${path}`;
                }
                const schemaValue = schemaObject[key];
                const testValue = objectToTest[key];
                if (typeof schemaValue === 'object' && schemaValue !== null && !Array.isArray(schemaValue)) {
                    const nestedError = compareKeysRecursively(testValue, schemaValue, `${path}.${key}`);
                    if (nestedError) {
                        return nestedError;
                    }
                }
            }
            return null;
        };

        for (const [index, rule] of data.entries()) {
            const rulePath = `rule[${index}]`;
            if (rule === null) {
                return `Invalid structure: Entry at ${rulePath} is null.`;
            }
            const error = compareKeysRecursively(rule, defaultRule, rulePath);
            if (error) {
                return error;
            }
        }
        return '';
    }, [defaultRule]);

    const rulesReference =
        `- name: example-rule-1              # unique rule identifier
  enabled: true                     # enable or disable this rule (true/false - overrides all conditions below)
  preprompt: briefly summarize logs # instructions prompt sent to the ai model along with the original received text
  match:                            # rule matching conditions; all conditions must be met to trigger (combined using an AND operator)
    sources:                        # source identifier; triggers if sender matches any of the listed ips or hostnames, leave empty (or null)to match all senders
      - 192.168.20.112              # sample source using ip address
      - pve.home                    # sample source using hostname
    og_text_regex: 10\.0\.0\.\d+        # regex to apply to the original received text; leave empty (or null)to match all text
    ai_text_regex: WARNING          # regex to apply to the ai-processed text; leave empty (or null)to match all text
  notify:                           # conditions and destinations for sending notifications
    destinations:                   # notification destinations; leave empty (or null)to send to all configured and enabled destinations
      - Telegram                    # sample destination (must be enabled in destinations settings to trigger here)
      - Slack                       # sample destination (must be enabled in destinations settings to trigger here)
    send_og_text:                   # conditions for sending original received text
      enabled: false                # enable/disable including original text in the notification (true/false - overrides conditions below it)
      og_text_regex:                # only send the original received text if this regex matches the original received text; leave empty (or null)to always send
      ai_text_regex:                # only send the original received text if this regex matches the ai-processed text; leave empty (or null)to always send
    send_ai_text:                   # conditions for sending ai-processed text
      enabled: true                 # enable/disable including ai-processed text in the notification (true/false - overrides conditions below it)
      og_text_regex: \d+ alerts      # only send the ai-processed text if this regex matches the original received text; leave empty (or null)to always send
      ai_text_regex:                # only send the ai-processed text if this regex matches the ai-processed text; leave empty (or null)to always send`;

    return (
        <YamlEditor
            data={displayRules}
            updateData={handleRuleUpdate}
            validateData={validateRules}
            referenceText={rulesReference}
            title="Define your custom rules in YAML format:"
            referenceTitle="Rule Format Reference"
        />
    );
}

export default RuleEditor;
