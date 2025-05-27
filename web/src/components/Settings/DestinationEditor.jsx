import React from 'react';
import YamlEditor from './YamlEditor';

function DestinationEditor({destinations, updateConfig}) {
    const destinationsReference =
        `- name: 'Telegram'                    # application name (refer to https://github.com/caronc/apprise/wiki for supported applications and how to configure them)
  enabled: false                      # whether destination should be disabled (global setting, overrides custom rules)
  url: 'tgram://{token}/{chat_id}'    # apprise compatible url with tokens e.g. for telegram refer to (https://github.com/caronc/apprise/wiki/Notify_telegram)`;

    const handleDestinationsUpdate = (updatedDestinations) => {
        updateConfig(prev => ({
            ...prev,
            destinations: updatedDestinations
        }));
    };

    return (
        <YamlEditor
            data={destinations}
            updateData={handleDestinationsUpdate}
            referenceText={destinationsReference}
            referenceTitle="Destination Format Reference"
            title="Define your notification destinations in YAML format:"
        />
    );
}

export default DestinationEditor;
