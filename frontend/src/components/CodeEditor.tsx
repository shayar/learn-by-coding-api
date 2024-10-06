import React, { useState } from 'react';
import axios from 'axios';

const CodeEditor = () => {
	const [code, setCode] = useState('');
	const [output, setOutput] = useState('');
	const [explanation, setExplanation] = useState('');
	const [diff, setDiff] = useState('');
	const [oldCode, setOldCode] = useState('');

	const apiUrl = process.env.REACT_APP_API_URL;

	const runCode = async () => {
		try {
			const response = await axios.post(`${apiUrl}/run`, { code });
			setOutput(response.data.output || response.data.error);
		} catch (error) {
			setOutput('Error executing code.');
		}
	};

	const explainCode = async () => {
		try {
			const response = await axios.post(`${apiUrl}/dynamic-explain`, {
				new_code: code,
			});
			setExplanation(response.data.explanation);
		} catch (error) {
			setExplanation('Error generating explanation.');
		}
	};

	const compareCode = async () => {
		try {
			const response = await axios.post(`${apiUrl}/explain-impact`, {
				old_code: oldCode,
				new_code: code,
			});
			setDiff(response.data.diff);
			setExplanation(response.data.impact);
		} catch (error) {
			setDiff('Error comparing code.');
		}
	};

	return (
		<div>
			<h1>Python Code Editor</h1>
			<textarea
				value={code}
				onChange={(e) => setCode(e.target.value)}
				rows={10}
				cols={50}
				placeholder='Write Python code here...'
			/>
			<br />
			<button onClick={runCode}>Run Code</button>
			<button onClick={explainCode}>Explain Code</button>
			<button onClick={compareCode}>Compare with Previous</button>
			<pre>Output: {output}</pre>
			<pre>Explanation: {explanation}</pre>
			<pre>Difference: {diff}</pre>
			<br />
			<button onClick={() => setOldCode(code)}>
				Set Current Code as Previous
			</button>
		</div>
	);
};

export default CodeEditor;
