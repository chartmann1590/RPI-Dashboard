# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability, please follow these steps:

1. Do not open a public issue
2. Open a private security advisory or contact the maintainers directly
3. Provide details about the vulnerability
4. Allow time for the issue to be addressed before public disclosure

## Supported Versions

Currently supported versions with security updates:

*   Version 1.0
*   Version 1.1

## Security Best Practices

*   **API Key Protection:**  Never hardcode API keys directly into the code. Use environment variables to store sensitive information.
*   **Input Validation:**  Thoroughly validate all user inputs to prevent injection attacks (SQL injection, XSS).
*   **HTTPS:**  Ensure all communication is encrypted using HTTPS.
*   **Rate Limiting:** Implement rate limiting to prevent abuse.
*   **Regular Updates:** Keep all dependencies up to date to patch security vulnerabilities.
*   **Secure Storage:** Store sensitive data (e.g., database credentials, session tokens) securely.

## Disclosure Policy

Security vulnerabilities will be addressed promptly.  The maintainers will acknowledge the vulnerability privately and work to develop a patch.  A public announcement will be made once the patch is released.  The maintainers will not disclose the vulnerability to the public until a patch is available. This is to prevent attackers from exploiting the vulnerability before a fix is deployed.
