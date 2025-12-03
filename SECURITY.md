# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability, please follow these steps:

1.  Do not open a public issue
2.  Open a private security advisory or contact the maintainers directly
3.  Provide details about the vulnerability
4.  Allow time for the issue to be addressed before public disclosure

## Supported Versions

Currently supported:

*   Version 1.0 - Security updates provided until December 31, 2024.
*   Version 1.1 (beta) - Security updates provided until March 31, 2025.

## Security Best Practices

*   **API Key Management:** Never hardcode API keys directly into your code. Use environment variables to securely store sensitive credentials.
*   **Input Sanitization:**  Properly sanitize all user input to prevent cross-site scripting (XSS) attacks.
*   **Rate Limiting:** Implement rate limiting to prevent abuse of API endpoints.
*   **Regular Updates:** Keep all dependencies up-to-date to benefit from the latest security patches.
*   **Secure Data Storage:**  Protect any sensitive data stored within the application. Use encryption where appropriate.

## Disclosure Policy

Security vulnerabilities will be addressed promptly. The maintainers will acknowledge receipt of the vulnerability report and initiate a remediation process.  A timeline for resolution will be provided.  We encourage responsible disclosure and cooperation in the security process.  Public disclosure of vulnerabilities will only occur after a reasonable period has elapsed to allow for remediation.
