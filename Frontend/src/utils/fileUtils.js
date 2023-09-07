import axios from "axios";
import { encryptHandler, decryptHandler } from "./cryptoUtils";

export const handleFileUpload = async (
	file,
	fileName,
	userName,
	setErrorMessage,
	setSuccessMessage,
	fetchFiles
) => {
	if (!file) {
		setErrorMessage("Please select a file to upload.");
		return;
	}

	if (!userName) {
		setErrorMessage("Please enter your user name.");
		return;
	}

	try {
		const fileReader = new FileReader();
		fileReader.onload = async () => {
			const fileContent = fileReader.result; // Read the file content as a string

			// Encrypt the file content
			const encryptedFileData = await encryptHandler(fileContent, userName);

			// Prepare form data for uploading
			const formData = new FormData();
			formData.append("file", encryptedFileData);
			formData.append("username", userName);
			formData.append("filename", fileName);

			// Upload the encrypted file data
			const response = await axios.post("/fileup", formData, {
				headers: {
					"Content-Type": "multipart/form-data",
				},
			});

			if (response.status === 200) {
				setSuccessMessage(
					response.data.file_name + " uploaded and encrypted successfully."
				);

				fetchFiles(); // Fetch files after successful upload
			}
		};

		fileReader.readAsText(file); // Read the file as text
	} catch (error) {
		console.error("File encryption error:", error);
		setErrorMessage("An error occurred while encrypting the file.");
	}
};

// Function to handle file decryption and download
export const handleFileDownload = async (
	userName,
	fileName,
	setErrorMessage
) => {
	if (!userName || !fileName) {
		setErrorMessage(
			"Please enter your user name and select a file to download."
		);
		return;
	}

	try {
		const requestData = {
			username: userName,
			file_name: fileName,
		};

		const response = await axios.post("/filedown", requestData, {
			responseType: "text",
		});

		// Decrypt the downloaded file data
		const decryptedFileData = await decryptHandler(response.data, userName);

		// Create a Blob from the decrypted file data with the appropriate content type
		const blob = new Blob([decryptedFileData], {
			type: "application/octet-stream", // Use the appropriate content type for the decrypted data (e.g., application/octet-stream for binary data)
		});

		// Create a URL for the blob object
		const url = URL.createObjectURL(blob);

		// Create a temporary link and click it to trigger the download
		const link = document.createElement("a");
		link.href = url;
		link.setAttribute("download", fileName);
		document.body.appendChild(link);
		link.click();
		document.body.removeChild(link); // Remove the link from the DOM after clicking

		// Cleanup the URL object
		URL.revokeObjectURL(url);
	} catch (error) {
		console.error("Error downloading the file:", error);
		setErrorMessage("An error occurred while downloading the file.");
	}
};

export const fetchFiles = async (userName, setFileList, setErrorMessage) => {
	try {
		const requestData = {
			username: userName,
		};
		const response = await axios.post("/fileget", requestData);

		if (response.status === 200) {
			const fileList = Object.keys(response.data); // Extract the file names from the response object
			setFileList(fileList);
			setErrorMessage("");
		}
	} catch (error) {
		console.error("Error fetching files:", error);
		setFileList([]);
		setErrorMessage("Error fetching files. Please try again later.");
	}
};

export const removeFile = async (
	userName,
	fileName,
	setErrorMessage,
	fetchFiles,
	setSuccessMessage
) => {
	if (!userName || !fileName) {
		setErrorMessage("Please enter your user name and select a file to remove.");
		return;
	}

	try {
		const requestData = {
			username: userName,
			filename: fileName,
		};

		const response = await axios.post("/filedel", requestData);

		if (response.status === 200) {
			fetchFiles();
			setErrorMessage("");
		}
	} catch (error) {
		console.error("Error removing the file:", error);
		if (error?.response?.data) {
			setErrorMessage(error.response.data); // Set the error message from the response data
		} else {
			setErrorMessage("An error occurred while removing the file.");
		}
	}
};
