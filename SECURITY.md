# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability, please follow these steps:

1. Do not open a public issue
2. Open a private security advisory or contact the maintainers directly
3. Provide details about the vulnerability
4. Allow time for the issue to be addressed before public disclosure

## Supported Versions

Currently supported versions with security updates:

*   Version 3.0.3 (Ongoing Support)
*   Version 2.32.3 (Limited Support - Patch Updates Only)
*   Version 6.0.11
*   Version 5.0.11
*   Version 1.0.0

## Security Best Practices

*   **API Key Management:**  Never commit API keys directly to the codebase. Use environment variables to store sensitive information.
*   **Input Validation:**  Thoroughly validate all user inputs to prevent injection attacks (e.g., SQL injection, XSS).
*   **Rate Limiting:** Implement rate limiting to prevent brute-force attacks.
*   **HTTPS:**  Always use HTTPS to encrypt communication between the client and server.
*   **Regular Updates:** Keep all dependencies up-to-date to patch security vulnerabilities.
*   **Authentication/Authorization**: Ensure proper authentication and authorization mechanisms are in place to control access to resources.

## Disclosure Policy

Security issues will be handled through a private channel (e.g., a secure messaging service).  The maintainers will acknowledge receipt of the report and provide updates on the progress of remediation.  A public disclosure of vulnerabilities will only occur after the issue has been addressed and a sufficient period has passed for the community to understand and mitigate the risk.  The exact timeline for public disclosure will be communicated transparently.
