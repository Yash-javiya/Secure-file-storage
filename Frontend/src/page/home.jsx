import React, { useEffect, useState } from "react";
import {
	Alert,
	Button,
	CircularProgress,
	Container,
	TextField,
	Typography,
	Collapse,
	IconButton,
} from "@mui/material";
import { useNavigate } from "react-router-dom";
import {
	fetchFiles,
	handleFileDownload,
	handleFileUpload,
	removeFile,
} from "../utils/fileUtils";

import {
	CloudDownload,
	CloudUpload,
	Delete,
	Logout,
	Close,
} from "@mui/icons-material";

export const Home = () => {
	const [file, setFile] = useState(null);
	const [fileName, setFileName] = useState("");
	const [errorMessage, setErrorMessage] = useState("");
	const [successMessage, setSuccessMessage] = useState("");
	const [userName, setUserName] = useState("");
	const [fileList, setFileList] = useState([]);
	const [uploading, setUploading] = useState(false);
	const [downloading, setDownloading] = useState(false);
	const [removing, setRemoving] = useState(false);
	const [selectedFile, setSelectedFile] = useState("");
	const [showSuccessAlert, setShowSuccessAlert] = useState(false);
	const [showErrorAlert, setShowErrorAlert] = useState(false);
	const [open, setOpen] = useState(true);
	const navigate = useNavigate();

	const handleFileChange = (event) => {
		const selectedFile = event.target.files[0];
		setFile(selectedFile);
		setFileName(selectedFile.name);
	};

	const handleFileUploadWrapper = () => {
		setUploading(true);
		setErrorMessage(""); // Clear the error message before attempting to upload
		handleFileUpload(
			file,
			fileName,
			userName,
			setErrorMessage,
			(message) => {
				setSuccessMessage(message);
				setShowSuccessAlert(true);
				setUploading(false);
			},
			() => {
				fetchFilesWrapper();
				setUploading(false);
			}
		);
	};

	const handleFileDownloadWrapper = (fileName) => {
		setDownloading(true);
		setErrorMessage(""); // Clear the error message before attempting to download
		handleFileDownload(userName, fileName, setErrorMessage).finally(() =>
			setDownloading(false)
		);
	};

	const handleFileRemoveConfirm = () => {
		setRemoving(true);
		setErrorMessage(""); // Clear the error message before attempting to remove
		removeFile(userName, selectedFile, setErrorMessage, () => {
			setRemoving(false);
			fetchFilesWrapper();
			setSuccessMessage("File removed successfully.");
			setShowSuccessAlert(true);
		}).catch((error) => {
			setRemoving(false);
			setErrorMessage(error.data.error);
			setShowErrorAlert(true);
		});
		setSelectedFile("");
	};

	const handleLogout = () => {
		sessionStorage.removeItem("jwtToken");
		setUserName("");
		setFileList([]);
		setSuccessMessage("Logged out successfully.");
		setErrorMessage("");
		navigate("/login");
	};

	const fetchFilesWrapper = () => {
		fetchFiles(userName, setFileList, setErrorMessage);
	};

	useEffect(() => {
		if (userName && userName.trim() !== "") {
			fetchFilesWrapper();
		}
	}, [userName]);

	useEffect(() => {
		const storedToken = sessionStorage.getItem("jwtToken");
		if (!storedToken) {
			navigate("/forbidden");
		} else {
			const decodedToken = JSON.parse(atob(storedToken.split(".")[1]));

			const username = decodedToken.username;
			setUserName(username);
		}
	}, [navigate, userName]);

	// Function to automatically hide the success and error alerts after 2 seconds
	useEffect(() => {
		if (showSuccessAlert || showErrorAlert) {
			const timer = setTimeout(() => {
				setShowSuccessAlert(false);
				setShowErrorAlert(false);
			}, 2000);

			return () => clearTimeout(timer);
		}
	}, [showSuccessAlert, showErrorAlert]);

	const handleFileRemove = (fileName) => {
		setSelectedFile(fileName);
	};

	return (
		<Container
			component='main'
			maxWidth='xs'
			className='page-container'
			sx={{
				display: "flex",
				flexDirection: "column",
				alignItems: "center",
			}}
		>
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
			<Typography variant='h6' component='h6' align='center' sx={{ mt: 2 }}>
				{userName}
			</Typography>

			<Button
				variant='contained'
				color='secondary'
				onClick={handleLogout}
				startIcon={<Logout />}
				sx={{ mt: 2 }}
			>
				Logout
			</Button>

			{errorMessage && showSuccessAlert && (
				<Alert severity='success' sx={{ mt: 2, width: "100%" }}>
					{errorMessage}
				</Alert>
			)}

			{errorMessage && showErrorAlert && (
				<Alert severity='error' sx={{ mt: 2, width: "100%" }}>
					{errorMessage}
				</Alert>
			)}

			<div
				className='upload-section'
				style={{ width: "100%", marginTop: "20px" }}
			>
				<Typography variant='h5' component='h3' sx={{ mt: 2 }}>
					Upload a File:
				</Typography>
				<TextField type='file' onChange={handleFileChange} sx={{ mt: 2 }} />
				<Button
					variant='contained'
					color='primary'
					onClick={handleFileUploadWrapper}
					startIcon={<CloudUpload />}
					sx={{ mt: 2 }}
					disabled={uploading}
				>
					{uploading ? "Uploading..." : "Upload"}
				</Button>
			</div>

			<Typography variant='h5' component='h3' sx={{ mb: 2 }}>
				List of Files:
			</Typography>

			{selectedFile && (
				<div>
					<Typography variant='body1' sx={{ mt: 2 }}>
						Are you sure you want to remove "{selectedFile}"?
					</Typography>
					<Button
						variant='contained'
						color='primary'
						onClick={handleFileRemoveConfirm}
						disabled={removing}
						startIcon={<Delete />}
						sx={{ mt: 2 }}
					>
						{removing ? "Removing..." : "Confirm Remove"}
					</Button>
				</div>
			)}

			{fileList.length > 0 ? (
				<div
					className='file-list-section'
					style={{ width: "100%", marginTop: "20px" }}
				>
					{fileList.map((filePath) => {
						const parts = filePath.split("/");
						const fileName = parts.pop();
						return (
							<div className='file-item' key={filePath}>
								<Typography variant='body1' sx={{ flex: 1 }}>
									{fileName}
								</Typography>
								<Button
									variant='contained'
									color='secondary'
									onClick={() => handleFileDownloadWrapper(fileName)}
									disabled={downloading}
									startIcon={<CloudDownload />}
								>
									{downloading ? "Downloading..." : "Download"}
								</Button>
								<Button
									variant='contained'
									color='error'
									onClick={() => handleFileRemove(fileName)}
									disabled={removing}
									startIcon={<Delete />}
								>
									{removing ? "Removing..." : "Remove"}
								</Button>
							</div>
						);
					})}
				</div>
			) : (
				<Typography variant='body1' sx={{ mt: 2 }}>
					No files present on the server.
				</Typography>
			)}
		</Container>
	);
};
