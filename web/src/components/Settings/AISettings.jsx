import React, { useState } from 'react';
import {
    Box,
    Checkbox,
    FormControlLabel,
    Radio,
    RadioGroup,
    FormControl,
    FormLabel,
    Grid,
    FormHelperText,
    InputLabel,
    Paper,
    TextField,
    styled
} from '@mui/material';

// Custom styled components to match the theme system
const StyledPaper = styled(Paper)(() => ({
    padding: '15px',
    borderRadius: '5px',
    backgroundColor: 'var(--card-bg)',
    height: '100%',
    display: 'flex',
    flexDirection: 'column',
    transition: 'border-color 0.2s'
}));

const StyledTextField = styled(TextField)(() => ({
    marginBottom: '15px',
    '& .MuiInputBase-root': {
        backgroundColor: 'var(--input-bg)',
    },
    '& .MuiOutlinedInput-root': {
        '& fieldset': {
            borderColor: 'var(--input-border)',
        },
        '&:hover fieldset': {
            borderColor: 'var(--primary-color)',
        },
    },
    '& .MuiInputLabel-root': {
        color: 'var(--text-color)',
    },
}));

function AISettings({ settings, toggleAI, handleChange, handleAIProviderChange }) {
    const [leftColumnHovered, setLeftColumnHovered] = useState(false);
    const [rightColumnHovered, setRightColumnHovered] = useState(false);

    // Handle changes for the preprompt field specifically
    const handlePrepromptChange = (e) => {
        handleChange({
            target: {
                name: 'preprompt',
                value: e.target.value
            }
        });
    };

    return (
        <Grid
            container
            spacing={2}
            sx={{
                mb: 3,
                display: 'flex',
                width: '100%'
            }}
        >
            {/* Column 1 - All controls except preprompt */}
            <Grid
                item
                xs={12}
                md={6}
                sx={{
                    display: 'flex',
                    flex: 1
                }}
            >
                <StyledPaper
                    elevation={1}
                    sx={{
                        width: '100%',
                        display: 'flex',
                        flexDirection: 'column',
                        border: '1px solid',
                        borderColor: leftColumnHovered ? 'rgba(255, 255, 255, 0.7)' : 'rgba(255, 255, 255, 0.23)'
                    }}
                    onMouseEnter={() => setLeftColumnHovered(true)}
                    onMouseLeave={() => setLeftColumnHovered(false)}
                >
                    <Box sx={{mb: 2}}>
                        <FormControlLabel
                            control={
                                <Checkbox
                                    id="enable_ai"
                                    name="enable_ai"
                                    checked={settings.enable_ai}
                                    onChange={toggleAI}
                                    sx={{mr: 1}}
                                />
                            }
                            label="Enable AI Processing"
                            sx={{
                                '& .MuiFormControlLabel-label': {
                                    fontWeight: 'bold',
                                }
                            }}
                        />
                        <FormHelperText sx={{ml: 4, mt: -0.5}}>
                            Generated AI summary of received messages processed via <a href="https://www.meta.ai"
                                                                                       target="_blank"
                                                                                       rel="noopener noreferrer">Meta
                            AI</a> or <a href="https://ollama.ai" target="_blank"
                                         rel="noopener noreferrer">Ollama</a>
                        </FormHelperText>
                    </Box>

                    <Box sx={{mb: 2}}>
                        <FormControlLabel
                            control={
                                <Checkbox
                                    id="show_original"
                                    name="show_original"
                                    checked={settings.show_original}
                                    onChange={handleChange}
                                    disabled={!settings.enable_ai}
                                    sx={{mr: 1}}
                                />
                            }
                            label="Show Original Message"
                            disabled={!settings.enable_ai}
                            sx={{
                                '& .MuiFormControlLabel-label': {
                                    fontWeight: 'bold',
                                    color: !settings.enable_ai ? 'var(--disabled-text)' : 'inherit',
                                }
                            }}
                        />
                        <FormHelperText sx={{ml: 4, mt: -0.5}}>
                            If AI is enabled, appends the original to the AI summary. If AI is disabled, this is
                            forced on and the original message is sent.
                        </FormHelperText>
                    </Box>

                    <Box sx={{mb: 2, display: 'flex', alignItems: 'center'}}>
                        <FormLabel
                            sx={{
                                fontWeight: 'bold',
                                color: !settings.enable_ai ? 'var(--disabled-text)' : 'var(--text-color)',
                                mr: 3,
                                minWidth: '80px'
                            }}
                        >
                            AI Provider
                        </FormLabel>

                        <RadioGroup
                            name="type"
                            value={settings.ai_provider.type}
                            onChange={handleAIProviderChange}
                            sx={{flexDirection: 'row'}}
                        >
                            <FormControlLabel
                                value="meta_ai"
                                control={<Radio/>}
                                label="Meta AI"
                                disabled={!settings.enable_ai}
                            />
                            <FormControlLabel
                                value="ollama"
                                control={<Radio/>}
                                label="Ollama"
                                disabled={!settings.enable_ai}
                            />
                        </RadioGroup>
                    </Box>
                    <FormHelperText sx={{ml: 0, mt: -1, mb: 2}}>
                        Select which AI provider to use for message processing
                    </FormHelperText>

                    <Box sx={{mb: 1, display: 'flex', alignItems: 'center'}}>
                        <InputLabel
                            htmlFor="ai_provider_url"
                            sx={{
                                fontWeight: 'bold',
                                color: !settings.enable_ai || settings.ai_provider.type !== "ollama" ? 'var(--disabled-text)' : 'var(--text-color)',
                                mr: 1,
                                minWidth: '55px'
                            }}
                        >
                            URL
                        </InputLabel>
                        <StyledTextField
                            fullWidth
                            id="ai_provider_url"
                            name="url"
                            placeholder="http://{server_ip}:11434"
                            value={settings.ai_provider.url}
                            disabled={!settings.enable_ai || settings.ai_provider.type !== "ollama"}
                            onChange={handleAIProviderChange}
                            variant="outlined"
                            size="small"
                            sx={{mb: 0}}
                        />
                    </Box>
                    <FormHelperText sx={{ml: 0, mb: 2}}>
                        URL for the AI provider's API endpoint
                    </FormHelperText>

                    <Box sx={{mb: 1, display: 'flex', alignItems: 'center'}}>
                        <InputLabel
                            htmlFor="ai_provider_model"
                            sx={{
                                fontWeight: 'bold',
                                color: !settings.enable_ai || settings.ai_provider.type !== "ollama" ? 'var(--disabled-text)' : 'var(--text-color)',
                                mr: 1,
                                minWidth: '55px'
                            }}
                        >
                            Model
                        </InputLabel>
                        <StyledTextField
                            fullWidth
                            id="ai_provider_model"
                            name="model"
                            placeholder="gemma3:1b"
                            value={settings.ai_provider.model}
                            disabled={!settings.enable_ai || settings.ai_provider.type !== "ollama"}
                            onChange={handleAIProviderChange}
                            variant="outlined"
                            size="small"
                            sx={{mb: 0}}
                        />
                    </Box>
                    <FormHelperText sx={{ml: 0, mb: 2}}>
                        The model to use (e.g., gemma3:1b, llama2)
                    </FormHelperText>
                </StyledPaper>
            </Grid>
            {/* Column 2 - Prompt textarea */}
            <Grid
                item
                xs={12}
                md={6}
                sx={{
                    display: 'flex',
                    flex: 1
                }}
            >
                <StyledPaper
                    elevation={1}
                    sx={{
                        width: '100%',
                        display: 'flex',
                        flexDirection: 'column',
                        border: '1px solid',
                        borderColor: rightColumnHovered ? 'rgba(255, 255, 255, 0.7)' : 'rgba(255, 255, 255, 0.23)'
                    }}
                    onMouseEnter={() => setRightColumnHovered(true)}
                    onMouseLeave={() => setRightColumnHovered(false)}
                >
                    <FormControl fullWidth>
                        <InputLabel
                            htmlFor="preprompt"
                            sx={{
                                position: 'relative',
                                fontWeight: 'bold',
                                transform: 'none',
                                color: !settings.enable_ai ? 'var(--disabled-text)' : 'var(--text-color)',
                                mb: 1
                            }}
                        >
                            AI Preprompt
                        </InputLabel>
                        <StyledTextField
                            id="preprompt"
                            name="preprompt"
                            multiline
                            rows={14}
                            placeholder="Instructions for the AI model"
                            inputProps={{maxLength: 2048}}
                            disabled={!settings.enable_ai}
                            value={settings.preprompt}
                            onChange={handlePrepromptChange}
                            variant="outlined"
                            fullWidth
                            sx={{mt: 1}}
                        />
                        <FormHelperText>
                            Instructions that guide how the AI processes messages (max 2048 chars)
                        </FormHelperText>
                    </FormControl>
                </StyledPaper>
            </Grid>
        </Grid>
    );
}

export default AISettings;
