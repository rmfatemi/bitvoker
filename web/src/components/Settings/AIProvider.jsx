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

function AIProvider({ aiProvider, ollamaUrl, ollamaModel, updateAIProvider }) {
    return (
        <StyledPaper>
            <Typography variant="h6" component="h2" sx={{ mb: 2 }}>
                AI Provider Configuration
            </Typography>
            <FormControl component="fieldset">
                <FormLabel component="legend">Select AI Provider</FormLabel>
                <RadioGroup
                    name="provider"
                    value={aiProvider}
                    onChange={updateAIProvider}
                    row
                >
                    <FormControlLabel
                        value="meta_ai"
                        control={<Radio />}
                        label="Meta AI"
                    />
                    <FormControlLabel
                        value="ollama"
                        control={<Radio />}
                        label="Ollama"
                    />
                </RadioGroup>
            </FormControl>

            {/* Ollama fields always visible, but disabled when not selected */}
            <Box sx={{ mt: 2 }}>
                <Typography variant="subtitle1" sx={{ mb: 1, fontWeight: 'bold' }}>
                    Ollama Configuration
                </Typography>
                <Box sx={{ mb: 2 }}>
                    <StyledTextField
                        label="Ollama URL"
                        name="url"
                        value={ollamaUrl}
                        onChange={updateAIProvider}
                        fullWidth
                        margin="normal"
                        disabled={aiProvider !== 'ollama'}
                        placeholder="http://localhost:11434"
                    />
                </Box>
                <Box>
                    <StyledTextField
                        label="Ollama Model"
                        name="model"
                        value={ollamaModel}
                        onChange={updateAIProvider}
                        fullWidth
                        margin="normal"
                        disabled={aiProvider !== 'ollama'}
                        placeholder="gemma:2b"
                    />
                </Box>
            </Box>
        </StyledPaper>
    );
}

export default AIProvider;
