import React from 'react';
import {
    Box,
    FormControlLabel,
    Checkbox,
    TextField,
    Paper,
    styled,
    Typography
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

function DefaultRule({aiEnabled, showOriginal, preprompt, updateConfig}) {
    const handleAIEnabledChange = (e) => {
        const enabled = e.target.checked;
        updateConfig(prev => {
            const defaultRule = prev.rules.find(rule => rule.name === "default-rule");
            const showOriginal = defaultRule?.notify?.original_message?.enabled || false;
            const ruleEnabled = enabled || showOriginal;

            return {
                ...prev,
                ai: {
                    ...prev.ai,
                    enabled: enabled
                },
                rules: prev.rules.map(rule =>
                    rule.name === "default-rule"
                        ? {
                            ...rule,
                            enabled: ruleEnabled,
                            notify: {
                                ...rule.notify,
                                original_message: {
                                    ...rule.notify.original_message,
                                    enabled: showOriginal // preserve current value
                                }
                            }
                        }
                        : rule
                )
            };
        });
    };

    const handleShowOriginalChange = (e) => {
        const show = e.target.checked;
        updateConfig(prev => {
            const aiEnabled = prev.ai?.enabled || false;
            const ruleEnabled = aiEnabled || show;
            return {
                ...prev,
                rules: prev.rules.map(rule =>
                    rule.name === "default-rule"
                        ? {
                            ...rule,
                            enabled: ruleEnabled,
                            notify: {
                                ...rule.notify,
                                original_message: {
                                    ...rule.notify.original_message,
                                    enabled: show
                                }
                            }
                        }
                        : rule
                )
            };
        });
    };

    const handlePrepromptChange = (e) => {
        const text = e.target.value;
        updateConfig(prev => ({
            ...prev,
            rules: prev.rules.map(rule =>
                rule.name === "default-rule"
                    ? {...rule, preprompt: text}
                    : rule
            )
        }));
    };

    return (
        <StyledPaper>
            <Typography variant="h6" component="h2" sx={{mb: 2}}>
                Default AI Processing
            </Typography>

            <Box sx={{mb: 2}}>
                <FormControlLabel
                    control={
                        <Checkbox
                            checked={showOriginal}
                            onChange={handleShowOriginalChange}
                        />
                    }
                    label="Show Original Message (Default Rule)"
                    sx={{
                        '& .MuiFormControlLabel-label': {
                            fontWeight: 'bold',
                        }
                    }}
                />

                <Box sx={{ml: 4, mt: -0.5}}>
                    <Typography variant="body2" color="text.secondary">
                        For the default rule: when AI is enabled, includes the original message with the AI processed
                        message
                    </Typography>
                </Box>
            </Box>

            <FormControlLabel
                control={
                    <Checkbox
                        checked={aiEnabled}
                        onChange={handleAIEnabledChange}
                    />
                }
                label="Enable AI Processing (Default Rule)"
                sx={{
                    '& .MuiFormControlLabel-label': {
                        fontWeight: 'bold',
                    }
                }}
            />

            <Box sx={{ml: 4, mt: -0.5, mb: 2}}>
                <Typography variant="body2" color="text.secondary">
                    Enables AI processing for the default rule, which applies when no other rules match
                </Typography>
            </Box>

            <Box sx={{mt: 4}}>
                <Typography
                    variant="subtitle1"
                    component="h3"
                    sx={{
                        fontWeight: 'bold',
                        mb: 1,
                        color: !aiEnabled ? 'var(--disabled-text)' : 'inherit'
                    }}
                >
                    Default Rule AI Preprompt
                </Typography>

                <StyledTextField
                    multiline
                    rows={3.5}
                    value={preprompt}
                    onChange={handlePrepromptChange}
                    fullWidth
                    disabled={!aiEnabled}
                    placeholder="Instructions for the AI model"
                    inputProps={{maxLength: 2048}}
                />

                <Typography variant="body2" color="text.secondary">
                    Instructions that guide how the AI processes messages
                </Typography>
            </Box>
        </StyledPaper>
    );
}

export default DefaultRule;
