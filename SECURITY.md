# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability, please follow these steps:

1. Do not open a public issue
2. Open a private security advisory or contact the maintainers directly
3. Provide details about the vulnerability
4. Allow time for the issue to be addressed before public disclosure

## Supported Versions

The following versions of this project currently receive security updates:

*   Version 1.0.0 - 2024-02-29
*   Version 1.1.0 - 2024-03-01

## Security Best Practices

*   **API Key Management:**  Never hardcode API keys directly into the code. Store them securely using environment variables or a dedicated secrets management solution.
*   **Input Validation:** Always validate user input to prevent injection attacks (e.g., SQL injection, cross-site scripting).
*   **Rate Limiting:** Implement rate limiting to protect against denial-of-service attacks.
*   **Secure Database Connections:** Use secure database connections and follow best practices for database security.
*   **HTTPS:** Ensure that the application is served over HTTPS to encrypt communication between the client and the server.
*   **Regular Updates:** Keep all software components (e.g., Python, Flask, SQLite) up to date with the latest security patches.

## Disclosure Policy

Security vulnerabilities will be handled through a private channel.  If you report a vulnerability, you will be contacted directly by the project maintainers.  We will acknowledge receipt of your report and provide updates on the progress of the investigation and remediation.  We appreciate your help in keeping this project secure.  Public disclosure of vulnerabilities will only occur after the issue has been fully addressed and a security patch has been released.
