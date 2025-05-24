import React from 'react';
import YamlEditor from './YamlEditor';

function ChannelEditor({ channels, updateConfig }) {
  const channelsReference =
`- name: 'Telegram'                    # application name (refer to https://github.com/caronc/apprise/wiki for supported applications and how to configure them)
  enabled: false                      # whether channel should be disabled (global setting, overrides custom rules)
  url: 'tgram://{token}/{chat_id}'    # apprise compatible url with tokens e.g. for telegram refer to (https://github.com/caronc/apprise/wiki/Notify_telegram)`;

  const handleChannelsUpdate = (updatedChannels) => {
    updateConfig(prev => ({
      ...prev,
      notification_channels: updatedChannels
    }));
  };

  return (
    <YamlEditor
      data={channels}
      updateData={handleChannelsUpdate}
      referenceText={channelsReference}
      referenceTitle="Channel Format Reference"
      title="Define your notification channels in YAML format:"
    />
  );
}

export default ChannelEditor;
