import React from 'react';
import YamlEditor from './YamlEditor';

function ChannelEditor({ channels, updateChannels }) {
  const channelsReference =
`- name: "Telegram"                    # application name
  enabled: false                      # whether channel should be disabled (overrides custom rules)
  url: "tgram://{token}/{chat_id}"    # apprise compatible url with tokens (e.g. for Telegram refer to https://github.com/caronc/apprise/wiki/Notify_telegram)
- name: "Slack"
  enabled: false
  url: "slack://{token}/{channel}"
- name: "ntfy"
  enabled: false
  url: "ntfy://{topic}"
- name: "custom apprise"
  enabled: false
  url: ""`;
  return (
    <YamlEditor
      data={channels}
      updateData={updateChannels}
      referenceText={channelsReference}
      title="Define your notification channels in YAML format:"
      referenceTitle="Channel Format Reference"
      editorHeight="40vh"
    />
  );
}

export default ChannelEditor;
