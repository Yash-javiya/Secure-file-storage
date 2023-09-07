import {
	Alert,
	Avatar,
	Box,
	Button,
	CircularProgress,
	Collapse,
	Container,
	Grid,
	IconButton,
	Link,
	TextField,
	Typography,
} from "@mui/material";
import React, { useState, useRef } from "react";
import {
	Close,
	LockOutlined,
	Visibility,
	VisibilityOff,
} from "@mui/icons-material";
import {
	validateName,
	validateEmail,
	validatePassword,
	registerUser,
} from "../utils/authUtils";

export const Register = () => {
	const [name, setName] = useState("");
	const [email, setEmail] = useState("");
	const [password, setPassword] = useState("");
	const [errorMessage, setErrorMessage] = useState("");
	const [nameError, setNameError] = useState("");
	const [emailError, setEmailError] = useState("");
	const [passwordError, setPasswordError] = useState("");
	const [successMessage, setSuccessMessage] = useState("");
	const [showPassword, setShowPassword] = useState(false);
	const [open, setOpen] = useState(true);
	const [loading, setLoading] = useState(false); // Added loading state

	const isMounted = useRef(true);

	const handleSubmit = async (e) => {
		e.preventDefault();

		// Reset error messages and loading state
		setNameError("");
		setEmailError("");
		setPasswordError("");
		setErrorMessage("");
		setSuccessMessage("");
		setLoading(true);

		// Validate name
		const nameError = validateName(name);
		setNameError(nameError);
		if (nameError) {
			setLoading(false);
			return;
		}

		// Validate email format
		const emailError = validateEmail(email);
		setEmailError(emailError);
		if (emailError) {
			setLoading(false);
			return;
		}

		// Validate password
		const passwordError = validatePassword(password);
		setPasswordError(passwordError);
		if (passwordError) {
			setLoading(false);
			return;
		}

		try {
			const message = await registerUser(name, email, password);
			setSuccessMessage(message);

			// Clear success message after 5 seconds
			setTimeout(() => {
				if (isMounted.current) {
					setSuccessMessage("");
					window.location.href = "/login";
				}
			}, 2000);
		} catch (error) {
			setErrorMessage(error.message);

			// Clear error message after 5 seconds
			setTimeout(() => {
				if (isMounted.current) {
					setErrorMessage("");
				}
			}, 2000);
		} finally {
			setLoading(false);
		}
	};

	const handleTogglePasswordVisibility = () => {
		setShowPassword(!showPassword);
	};

	return (
		<Container component='main' maxWidth='xs' className='page-container'>
			{errorMessage && (
				<Collapse in={open}>
					<Alert
						action={
							<IconButton
								aria-label='close'
								color='inherit'
								size='small'
								onClick={() => {
									setOpen(false);
								}}
							>
								<Close fontSize='inherit' />
							</IconButton>
						}
						severity='error'
						sx={{ mb: 2 }}
					>
						{errorMessage}
					</Alert>
				</Collapse>
			)}
			{successMessage && (
				<Collapse in={open}>
					<Alert
						action={
							<IconButton
								aria-label='close'
								color='inherit'
								size='small'
								onClick={() => {
									setOpen(false);
								}}
							>
								<Close fontSize='inherit' />
							</IconButton>
						}
						severity='success'
						sx={{ mb: 2 }}
					>
						{successMessage}
					</Alert>
				</Collapse>
			)}
			<Typography variant='h4' component='h2' align='center'>
				Secure Store
			</Typography>
			<Box
				sx={{
					marginTop: 8,
					display: "flex",
					flexDirection: "column",
					alignItems: "center",
				}}
			>
				<Avatar sx={{ m: 1, bgcolor: "secondary.main" }}>
					<LockOutlined />
				</Avatar>
				<Typography component='h1' variant='h5'>
					Sign up
				</Typography>
				<Box component='form' noValidate onSubmit={handleSubmit} sx={{ mt: 3 }}>
					<Grid container spacing={2}>
						<Grid item xs={12}>
							<TextField
								autoComplete='given-name'
								name='Name'
								required
								fullWidth
								id='Name'
								label='Name'
								autoFocus
								onChange={(e) => setName(e.target.value)}
								error={!!nameError}
								helperText={nameError}
							/>
						</Grid>
						<Grid item xs={12}>
							<TextField
								required
								fullWidth
								id='email'
								label='Email Address'
								name='email'
								autoComplete='email'
								onChange={(e) => setEmail(e.target.value)}
								error={!!emailError}
								helperText={emailError}
							/>
						</Grid>
						<Grid item xs={12}>
							<TextField
								required
								fullWidth
								name='password'
								label='Password'
								type={showPassword ? "text" : "password"}
								id='password'
								autoComplete='new-password'
								onChange={(e) => setPassword(e.target.value)}
								error={!!passwordError}
								helperText={passwordError}
								InputProps={{
									endAdornment: (
										<IconButton
											aria-label='toggle password visibility'
											onClick={handleTogglePasswordVisibility}
											edge='end'
										>
											{showPassword ? <VisibilityOff /> : <Visibility />}
										</IconButton>
									),
								}}
							/>
						</Grid>
					</Grid>
					<Button
						type='submit'
						fullWidth
						variant='contained'
						sx={{ mt: 3, mb: 2 }}
						disabled={loading} // Disable the button while loading
					>
						{loading ? <CircularProgress size={24} /> : "Sign Up"}
					</Button>
					<Grid container justifyContent='flex-end'>
						<Grid item>
							<Link href='/login' variant='body2'>
								Already have an account? Sign in
							</Link>
						</Grid>
					</Grid>
				</Box>
			</Box>
		</Container>
	);
};
