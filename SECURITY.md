# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability, please follow these steps:

1. Do not open a public issue
2. Open a private security advisory or contact the maintainers directly
3. Provide details about the vulnerability
4. Allow time for the issue to be addressed before public disclosure

## Supported Versions

*   **1.0:** (Currently Supported) - Security updates and bug fixes will be provided for this version until December 31, 2024.
*   **0.9:** (End of Life) - No further updates or security fixes will be provided for this version.

## Security Best Practices

*   **API Key Protection:**  Never commit API keys directly to your code repository. Use environment variables instead.
*   **Input Validation:**  Thoroughly validate all user input to prevent injection attacks (e.g., SQL injection, XSS).
*   **Rate Limiting:** Implement rate limiting on API endpoints to mitigate denial-of-service attacks.
*   **HTTPS:** Always use HTTPS to encrypt communication between the client and the server.
*   **Regular Updates:** Keep all dependencies up to date to patch known vulnerabilities.
*   **Secure Coding Practices:** Follow secure coding practices to minimize the risk of vulnerabilities.

## Disclosure Policy

Security vulnerabilities will be handled with utmost priority.  Reported vulnerabilities will be acknowledged promptly and investigated thoroughly.  A timeline for resolution will be provided to the reporter. The maintainers are committed to responsible disclosure and will work with the reporter to ensure a secure resolution.  All security vulnerabilities will be tracked and addressed according to our priority system (Critical, High, Medium, Low). We are committed to transparency and will share updates with the reporter throughout the remediation process.
