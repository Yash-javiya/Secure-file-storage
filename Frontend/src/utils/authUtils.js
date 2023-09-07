import axios from "axios";

export const validateName = (name) => {
	return name ? "" : "Please enter a name";
};

export const validateEmail = (email) => {
	if (!email) {
		return "Please enter an email";
	} else if (!/\S+@\S+\.\S+/.test(email)) {
		return "Please enter a valid email address";
	} else {
		return "";
	}
};

export const validatePassword = (password) => {
	if (!password) {
		return "Please enter a password";
	} else if (password.length < 8) {
		return "Password must be at least 8 characters long";
	} else if (!/^[a-zA-Z0-9!@#$%^&*]+$/g.test(password)) {
		return "Password can only contain alphanumeric characters and special characters: !@#$%^&*";
	} else {
		return "";
	}
};

export const registerUser = async (name, email, password) => {
	const requestBody = {
		name: name,
		username: email.toLowerCase(),
		password: password,
	};

	try {
		const response = await axios.post("/register", requestBody);

		if (response.status === 200) {
			return response.data.message;
		}
	} catch (error) {
		if (error.response?.data?.error) {
			throw new Error(error.response.data.error);
		} else {
			throw new Error("An error occurred. Please try again later.");
		}
	}
};

export const loginUser = async (email, password) => {
	const requestBody = {
		username: email.toLowerCase(),
		password: password,
	};

	try {
		const response = await axios.post("/login", requestBody);

		if (response.status === 200) {
			const token = response.data.token;

			// Check if the token is null or empty
			if (!token) {
				throw new Error("Empty token received.");
			}

			// Parse the token to extract the username
			const decodedToken = JSON.parse(atob(token.split(".")[1]));
			const usernameInToken = decodedToken.username;

			// Check if the username in the token matches the email
			if (usernameInToken !== email.toLowerCase()) {
				throw new Error("Token username does not match email.");
			}

			// Store the JWT token in the session storage
			sessionStorage.setItem("jwtToken", token);

			// Set the JWT token in Axios headers for future requests
			axios.defaults.headers.common["Authorization"] = token;

			return response.data.message;
		}
	} catch (error) {
		if (error?.response?.data?.error) {
			throw new Error(error.response.data.error);
		} else {
			throw new Error("An error occurred. Please try again later.");
		}
	}
};
