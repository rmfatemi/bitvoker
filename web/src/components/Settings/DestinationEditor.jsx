import React from 'react';
import YamlEditor from './YamlEditor';

function DestinationEditor({ destinations, updateConfig }) {
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

    const validateDestinations = (data) => {
        if (data === null || data === undefined) {
             return "YAML content cannot be empty.";
        }
        if (!Array.isArray(data)) {
            return "Invalid format: The root element must be a YAML list (array).";
        }
        for (const dest of data) {
            if (dest === null) {
                return "Invalid structure: Contains a null entry. Please define the destination or remove the hyphen.";
            }
            if (typeof dest !== 'object') {
                return "Invalid structure: All list items must be objects.";
            }
            if (!dest.name || !dest.url) {
                return "Invalid structure: Every destination must have 'name' and 'url' properties.";
            }
        }
        return '';
    };

    return (
        <YamlEditor
            data={destinations}
            updateData={handleDestinationsUpdate}
            validateData={validateDestinations}
            referenceText={destinationsReference}
            referenceTitle="Destination Format Reference"
            title="Define your notification destinations in YAML format:"
        />
    );
}

export default DestinationEditor;
