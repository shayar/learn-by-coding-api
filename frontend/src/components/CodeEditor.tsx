import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const CodeEditor = () => {
	const [code, setCode] = useState('');
	const [prevCode, setPrevCode] = useState('');
	const [output, setOutput] = useState('');
	const [explanation, setExplanation] = useState('');
	const [difference, setDifference] = useState('');

	const apiUrl = process.env.REACT_APP_API_URL;

	const handleCodeChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
		const newCode = e.target.value;
		setCode(newCode);
	};

	const runCode = async () => {
		try {
			const response = await axios.post(`${apiUrl}/run`, { code });
			setOutput(response.data.output || response.data.error);
		} catch (error) {
			setOutput('Error executing code.');
		}
	};

	const fetchExplanationAndDifference = useCallback(
		async (currentCode: string, previousCode: string) => {
			try {
				const response = await axios.post(`${apiUrl}/dynamic-explain`, {
					new_code: currentCode,
					old_code: previousCode,
				});
				setExplanation(response.data.explanation);
				setDifference(response.data.diff);
			} catch (error) {
				setExplanation('Error generating explanation.');
				setDifference('Error generating difference.');
			}
		},
		[apiUrl]
	);

	useEffect(() => {
		if (code && code !== prevCode) {
			fetchExplanationAndDifference(code, prevCode);
			setPrevCode(code);
		}
	}, [code, prevCode, fetchExplanationAndDifference]);

	return (
		<div
			style={{
				textAlign: 'center',
				color: 'white',
				backgroundColor: '#2f2f2f',
				padding: '20px',
			}}
		>
			<h1>Python Code Editor</h1>
			<textarea
				value={code}
				onChange={handleCodeChange}
				rows={10}
				cols={50}
				placeholder='Write Python code here...'
				style={{
					fontSize: '16px',
					padding: '10px',
					backgroundColor: '#333',
					color: 'white',
					width: '100%',
					height: '150px',
					resize: 'none',
				}}
			/>
			<br />
			<button
				onClick={runCode}
				style={{ margin: '10px', padding: '10px 20px', fontSize: '16px' }}
			>
				Run Code
			</button>
			<div style={{ textAlign: 'left', padding: '20px' }}>
				<h3>Output:</h3>
				<pre>{output}</pre>
				<h3>Explanation:</h3>
				<pre>{explanation}</pre>
				<h3>Difference:</h3>
				<pre>{difference}</pre>
			</div>
		</div>
	);
};

export default CodeEditor;
