import React from 'react';

function ChannelCard({ channel, config, updateConfig, icon, title, fields }) {
  return (
    <div className="channel-config-card" id={`${channel}-channel`}>
      <input type="hidden" name={`channel_${channel}_type`} value={channel} />
      <h4 style={{textAlign: 'left', display: 'flex', alignItems: 'center', justifyContent: 'space-between'}}>
        <div style={{display: 'flex', alignItems: 'center'}}>
          {icon}
          <span>{title}</span>
        </div>
        <label>
          <input
            type="checkbox"
            name={`channel_${channel}_enabled`}
            checked={config.enabled}
            onChange={(e) => updateConfig(channel, 'enabled', e.target.checked)}
          /> Enabled
        </label>
      </h4>

      {fields.map((field) => (
        <React.Fragment key={field.id}>
          <label htmlFor={field.id}>{field.label}</label>
          <input
            type={field.type || "text"}
            id={field.id}
            name={`${channel}_config_${field.key}`}
            value={config[field.key] || ''}
            placeholder={field.placeholder}
            autoComplete={field.autoComplete || "on"}
            disabled={!config.enabled}
            onChange={(e) => updateConfig(channel, field.key, e.target.value)}
          />
        </React.Fragment>
      ))}
    </div>
  );
}

export default ChannelCard;
