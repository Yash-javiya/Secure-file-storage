import React from "react";
import { Container, Typography, Button } from "@mui/material";
import { Link } from "react-router-dom"; // Import Link from react-router-dom

export const Forbidden = () => {
  return (
    <Container component="main" maxWidth="xs" sx={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
      <Typography component="h1" variant="h5" align="center">
        403 Forbidden
      </Typography>
      <Typography variant="body1" align="center">
        You don't have permission to access this page.
      </Typography>
      <Button
        component={Link}
        to="/login"
        variant="contained"
        color="primary"
        fullWidth
        sx={{ mt: 3 }}
      >
        Go to Login
      </Button>
    </Container>
  );
};

export default Forbidden;
