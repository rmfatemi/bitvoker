import React from 'react';
import YamlEditor from './YamlEditor';

function ChannelEditor({ channels, updateChannels }) {
  const channelsReference =
`- name: 'Telegram'                    # application name
  enabled: false                      # whether channel should be disabled (global setting, overrides custom rules)
  url: 'tgram://{token}/{chat_id}'    # apprise compatible url with tokens e.g. for telegram refer to (https://github.com/caronc/apprise/wiki/Notify_telegram)`;

  return (
    <YamlEditor
      data={channels}
      updateData={updateChannels}
      referenceText={channelsReference}
      referenceTitle="Channel Format Reference"
      title="Define your notification channels in YAML format:"
    />
  );
}

export default ChannelEditor;
