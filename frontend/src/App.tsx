import React from 'react';
import logo from './logo.svg';
import './App.css';
import CodeEditor from './components/CodeEditor';

function App() {
	return (
		<div className='App'>
			<header className='App-header'>
				<CodeEditor />
			</header>
		</div>
	);
}

export default App;
