import React, {useState, useRef, useEffect} from 'react';
import yaml from 'js-yaml';
import AceEditor from 'react-ace';
import 'ace-builds/src-noconflict/mode-yaml';
import 'ace-builds/src-noconflict/theme-merbivore_soft';
import 'ace-builds/src-noconflict/ext-language_tools';
import {TextField, FormHelperText} from '@mui/material';

function YamlEditor({
                        data,
                        updateData,
                        referenceText,
                        title = "Define in YAML format:",
                        referenceTitle = "Format Reference",
                        editorHeight = "52vh"
                    }) {
    const [yamlContent, setYamlContent] = useState(() => {
        try {
            return yaml.dump(data || []);
        } catch (error) {
            return '';
        }
    });

    const [yamlError, setYamlError] = useState('');
    const [isPressed, setIsPressed] = useState(false);
    const [isEditorHovered, setIsEditorHovered] = useState(false);
    const yamlReferenceRef = useRef(null);

    const handleYamlChange = (newValue) => {
        setYamlContent(newValue);

        try {
            yaml.load(newValue);
            setYamlError('');
        } catch (error) {
            setYamlError(`Invalid YAML: ${error.message}`);
        }
    };

    const copyYamlReference = () => {
        if (yamlReferenceRef.current) {
            navigator.clipboard.writeText(yamlReferenceRef.current.value);
            setIsPressed(true);
            setTimeout(() => setIsPressed(false), 200);
        }
    };

    useEffect(() => {
        try {
            const parsedData = yaml.load(yamlContent);
            if (!yamlError && (yamlContent.trim() === '' || parsedData)) {
                updateData(parsedData || []);
            }
        } catch (error) {
            // will be caught by input validation
        }
    }, [yamlContent, yamlError, updateData]);

    return (
        <div className="yaml-editor-container">
            <div
                className="yaml-editor"
                onMouseEnter={() => setIsEditorHovered(true)}
                onMouseLeave={() => setIsEditorHovered(false)}
            >
                <p>{title}</p>

                <div style={{
                    borderRadius: '4px',
                    border: `1px solid ${isEditorHovered ? 'rgba(255, 255, 255, 0.23)' : 'rgba(255, 255, 255, 0.23)'}`,
                    borderColor: isEditorHovered ? 'rgba(255, 255, 255, 0.7)' : 'rgba(255, 255, 255, 0.23)',
                    transition: 'border-color 0.2s'
                }}>
                    <AceEditor
                        mode="yaml"
                        theme="merbivore_soft"
                        onChange={handleYamlChange}
                        value={yamlContent}
                        name="yaml-editor"
                        editorProps={{$blockScrolling: true}}
                        fontSize={12}
                        width="100%"
                        height={editorHeight}
                        showPrintMargin={false}
                        showGutter={true}
                        highlightActiveLine={true}
                        setOptions={{
                            showLineNumbers: true,
                            tabSize: 2,
                            useWorker: false
                        }}
                        style={{
                            borderRadius: '4px',
                        }}
                    />
                </div>

                {yamlError && <div className="error-message">{yamlError}</div>}
            </div>

            <div className="yaml-format-guide" style={{
                marginTop: '15px',
                position: 'relative',
                border: '1px solid var(--border-color)',
                borderRadius: '4px'
            }}>
                <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
                    <h4>{referenceTitle}</h4>
                </div>

                <div style={{position: 'relative'}}>
                    <button
                        type="button"
                        className="action-button"
                        onClick={copyYamlReference}
                        style={{
                            position: 'absolute',
                            right: '10px',
                            top: '10px',
                            zIndex: 1,
                            background: 'transparent',
                            border: '1px solid #606060',
                            cursor: 'pointer',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            width: '30px',
                            height: '30px',
                            borderRadius: '4px',
                            padding: '5px',
                            transform: isPressed ? 'scale(0.95)' : 'scale(1)',
                            transition: 'all 0.1s ease-in-out'
                        }}
                        title="Copy to clipboard"
                    >
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="white" xmlns="http://www.w3.org/2000/svg">
                            <path
                                d="M16 1H4C2.9 1 2 1.9 2 3V17H4V3H16V1ZM19 5H8C6.9 5 6 5.9 6 7V21C6 22.1 6.9 23 8 23H19C20.1 23 21 22.1 21 21V7C21 5.9 20.1 5 19 5ZM19 21H8V7H19V21Z"/>
                        </svg>
                    </button>

                    <TextField
                        inputRef={yamlReferenceRef}
                        multiline
                        fullWidth
                        rows={3}
                        value={referenceText}
                        variant="outlined"
                        InputProps={{
                            readOnly: true,
                        }}
                        sx={{
                            '& .MuiOutlinedInput-root': {
                                backgroundColor: 'var(--input-bg-lighter, #222222)',
                            },
                            '& .MuiInputBase-input': {
                                fontSize: '12px',
                                fontFamily: 'monospace',
                                color: 'white'
                            }
                        }}
                    />
                    <FormHelperText sx={{mt: 0.5}}>
                        YAML configuration reference:
                        All keys are required.
                        Maintain the structure and customize the values.
                        Use single quotes for regex patterns with special-character.
                        Add as many unique entries as needed.
                    </FormHelperText>
                </div>
            </div>
        </div>
    );
}

export default YamlEditor;
