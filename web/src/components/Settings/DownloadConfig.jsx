import React from 'react';
import { Button } from '@mui/material';
import FileDownloadIcon from '@mui/icons-material/FileDownload';
import yaml from 'js-yaml';

const DownloadConfig = ({ configData }) => {
    const downloadConfigYaml = () => {
        try {
            const yamlContent = yaml.dump(configData);
            const blob = new Blob([yamlContent], { type: 'text/yaml' });
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = 'config.yaml';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
        } catch (error) {
            console.error('Error downloading config:', error);
        }
    };

    return (
        <Button
            variant="outlined"
            size="large"
            startIcon={<FileDownloadIcon />}
            onClick={downloadConfigYaml}
        >
            Download Config
        </Button>
    );
};

export default DownloadConfig;
