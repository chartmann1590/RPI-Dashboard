# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability, please follow these steps:

1.  Do not open a public issue.
2.  Open a private security advisory or contact the maintainers directly.
3.  Provide details about the vulnerability.
4.  Allow time for the issue to be addressed before public disclosure

## Supported Versions

Currently supported versions with security updates:

*   Version 1.0 - Ongoing Support
*   Version 1.1 (Released 2024-01-26) - Ongoing Support

## Security Best Practices

*   **API Key Protection:** Never hardcode API keys directly into the source code. Store them securely as environment variables.
*   **Input Validation:**  Thoroughly validate all user inputs to prevent injection attacks (e.g., SQL injection, XSS).
*   **Rate Limiting:** Implement rate limiting to protect against denial-of-service attacks.
*   **HTTPS:** Ensure that the application is served over HTTPS to encrypt traffic.
*   **Regular Updates:** Keep the application and its dependencies up-to-date with the latest security patches.

## Disclosure Policy

Security vulnerabilities will be addressed promptly. The maintainers will acknowledge reports within 24 hours and provide an estimated timeline for resolution.  A public announcement will be made once the vulnerability has been fully addressed.  The maintainers reserve the right to coordinate with security researchers and law enforcement authorities as necessary.
