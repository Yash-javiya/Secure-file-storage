import React from "react";
import {
	BrowserRouter as Router,
	Route,
	Routes,
	Navigate,
} from "react-router-dom";

import "./App.css";
import { Login } from "./page/login";
import { Register } from "./page/register";
import { Home } from "./page/home";
import { Forbidden } from "./page/forbidden";
import axios from "axios";
import { apiBaseUrl } from './config/commonConfig';

if (!apiBaseUrl) {
	console.error(
		"API base URL is not configured. Please set the REACT_APP_API_BASE_URL environment variable."
	);
}
console.log(apiBaseUrl)
axios.defaults.baseURL = apiBaseUrl;


function App() {
	const jwtToken = sessionStorage.getItem("jwtToken");
	if (jwtToken !== null) {
		axios.interceptors.request.use(function (config) {
			config.headers.Authorization = "Bearer " + jwtToken;
			return config;
		});
	}

	return (
		<div className='App'>
			<div className='container'>
				<Router>
					<Routes>
						<Route path='/login' element={<Login />} />
						<Route path='/register' element={<Register />} />
						<Route path='/home' element={<Home />} />
						<Route path='/' element={<Login />} />
						<Route path='/forbidden' element={<Forbidden />} />
						<Route path='*' element={<Navigate to='/forbidden' />} />
					</Routes>
				</Router>
			</div>
		</div>
	);
}

export default App;
