# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability, please follow these steps:

1.  Do not open a public issue
2.  Open a private security advisory or contact the maintainers directly
3.  Provide details about the vulnerability
4.  Allow time for the issue to be addressed before public disclosure

## Supported Versions

Currently supported versions with security updates:

*   **Version 1.0:**  Ongoing security updates.
*   **Version 1.1:**  Security updates until Q4 2024.
*   **Future Releases:**  All future releases will be actively maintained with security updates.

## Security Best Practices

*   **API Key Protection:** Never expose API keys in the client-side code. Utilize a backend server for authentication and authorization. Store API keys securely as environment variables on the server.
*   **Input Validation:** Implement robust input validation on all API endpoints to prevent SQL injection and other vulnerabilities.
*   **Rate Limiting:** Implement rate limiting on API endpoints to prevent abuse and denial-of-service attacks.
*   **Data Sanitization:** Sanitize all user-generated content to prevent Cross-Site Scripting (XSS) attacks.
*   **Secure Communication:** Use HTTPS for all communication to encrypt data in transit.
*   **Regular Updates:** Keep all software components (Python, Flask, database drivers, etc.) up to date with the latest security patches.

## Disclosure Policy

Security vulnerabilities will be addressed promptly.  The maintainers will acknowledge reports within 24-48 hours and commit to a remediation plan.  A timeline for resolution will be provided based on the severity of the vulnerability.  Details of the vulnerability and the remediation steps will be shared with the reporter on a need-to-know basis.  Public disclosure of vulnerabilities will only occur after the issue has been fully addressed and a public statement has been prepared.
