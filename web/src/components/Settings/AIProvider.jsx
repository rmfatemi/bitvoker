import React from 'react';
import {
    Box,
    Typography,
    Radio,
    RadioGroup,
    FormControl,
    FormLabel,
    FormControlLabel,
    styled,
    Paper,
    TextField
} from '@mui/material';

const StyledPaper = styled(Paper)(() => ({
    padding: '20px',
    border: '1px solid var(--border-color)',
    backgroundColor: 'var(--card-bg)',
    marginBottom: '20px'
}));

const StyledTextField = styled(TextField)(() => ({
    marginBottom: '15px',
    '& .MuiInputBase-root': {
        backgroundColor: 'var(--input-bg)',
    }
}));

function AIProvider({aiProvider, ollamaUrl, ollamaModel, updateConfig}) {
    const handleProviderChange = (e) => {
        const newProvider = e.target.value;
        updateConfig(prev => ({
            ...prev,
            ai: {
                ...prev.ai,
                provider: newProvider
            }
        }));
    };

    const handleOllamaConfigChange = (e) => {
        const {name, value} = e.target;
        updateConfig(prev => ({
            ...prev,
            ai: {
                ...prev.ai,
                ollama: {
                    ...prev.ai.ollama,
                    [name]: value
                }
            }
        }));
    };

    return (
        <StyledPaper>
            <Typography variant="h6" component="h2" sx={{mb: 2}}>
                AI Provider Configuration
            </Typography>
            <FormControl component="fieldset">
                <FormLabel component="legend">Select AI Provider</FormLabel>
                <RadioGroup
                    name="provider"
                    value={aiProvider}
                    onChange={handleProviderChange}
                    row
                >
                    <FormControlLabel
                        value="meta_ai"
                        control={<Radio/>}
                        label="Meta AI"
                    />
                    <FormControlLabel
                        value="ollama"
                        control={<Radio/>}
                        label="Ollama"
                    />
                </RadioGroup>
            </FormControl>

            <Box sx={{mt: 2}}>
                <Typography variant="subtitle1" sx={{mb: 1, fontWeight: 'bold'}}>
                    Ollama Configuration
                </Typography>
                <Box sx={{mb: 2}}>
                    <StyledTextField
                        label="Ollama URL"
                        name="url"
                        value={ollamaUrl}
                        onChange={handleOllamaConfigChange}
                        fullWidth
                        margin="normal"
                        disabled={aiProvider !== 'ollama'}
                    />

                    <Typography variant="body2" color="text.secondary">
                        URL for the Ollama provider's API endpoint
                    </Typography>
                </Box>
                <Box>
                    <StyledTextField
                        label="Ollama Model"
                        name="model"
                        value={ollamaModel}
                        onChange={handleOllamaConfigChange}
                        fullWidth
                        margin="normal"
                        disabled={aiProvider !== 'ollama'}
                    />

                    <Typography variant="body2" color="text.secondary">
                        The model to use (e.g., gemma3:1b, llama2)
                    </Typography>
                </Box>
            </Box>
        </StyledPaper>
    );
}

export default AIProvider;
