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

// Styled components
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

function DefaultRule({ aiEnabled, showOriginal, preprompt, updateAIEnabled, updateShowOriginal, updatePreprompt }) {
    return (
        <StyledPaper>
            <Typography variant="h6" component="h2" sx={{ mb: 2 }}>
                Default AI Processing
            </Typography>

            <FormControlLabel
                control={
                    <Checkbox
                        checked={aiEnabled}
                        onChange={updateAIEnabled}
                    />
                }
                label="Enable AI Processing (Default Rule)"
                sx={{
                    '& .MuiFormControlLabel-label': {
                        fontWeight: 'bold',
                    }
                }}
            />

            <Box sx={{ ml: 4, mt: -0.5, mb: 2 }}>
                <Typography variant="body2" color="text.secondary">
                    Enables AI processing for the default rule, which applies when no other rules match
                </Typography>
            </Box>

            <Box sx={{ mb: 2 }}>
                <FormControlLabel
                    control={
                        <Checkbox
                            checked={showOriginal}
                            onChange={updateShowOriginal}
                            disabled={!aiEnabled}
                        />
                    }
                    label="Show Original Message (Default Rule)"
                    disabled={!aiEnabled}
                    sx={{
                        '& .MuiFormControlLabel-label': {
                            fontWeight: 'bold',
                            color: !aiEnabled ? 'var(--disabled-text)' : 'inherit',
                        }
                    }}
                />

                <Box sx={{ ml: 4, mt: -0.5 }}>
                    <Typography variant="body2" color="text.secondary">
                        For the default rule: when AI is enabled, appends the original message to the AI summary
                    </Typography>
                </Box>
            </Box>

            <Box sx={{ mt: 4 }}>
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
                    rows={10}
                    value={preprompt}
                    onChange={updatePreprompt}
                    fullWidth
                    disabled={!aiEnabled}
                    placeholder="Instructions for the AI model"
                    inputProps={{ maxLength: 2048 }}
                />

                <Typography variant="body2" color="text.secondary">
                    Instructions that guide how the AI processes messages (max 2048 chars)
                </Typography>
            </Box>
        </StyledPaper>
    );
}

export default DefaultRule;
