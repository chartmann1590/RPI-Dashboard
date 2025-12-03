# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability, please follow these steps:

1. **Do not** open a public issue
2. Open a private security advisory or contact the maintainers directly
3. Provide details about the vulnerability
4. Allow time for the issue to be addressed before public disclosure

## Supported Versions

Currently supported versions with security updates:

*   1.0.0 - 1.0.5 (Ongoing security maintenance)
*   1.0.6 - 1.0.10 (Security maintenance ongoing)
*   1.0.11 - 1.0.15 (Security maintenance ongoing)

## Security Best Practices

*   **API Key Protection:** Never hardcode API keys in your code. Use environment variables to store sensitive information.
*   **Input Validation:** Implement robust input validation to prevent injection attacks and other vulnerabilities.
*   **Database Security:** Secure your database connections and use parameterized queries to prevent SQL injection.
*   **Rate Limiting:** Implement rate limiting on your API endpoints to prevent denial-of-service attacks.
*   **Regular Updates:** Keep your dependencies up-to-date to patch known vulnerabilities.
*   **Logging:** Implement comprehensive logging to track user activity and detect suspicious behavior.

## Disclosure Policy

Security issues will be handled according to the following policy:

1.  **Initial Contact:** Upon discovery of a vulnerability, immediately contact the maintainers via a private security advisory or email. Do not publicly disclose the vulnerability.
2.  **Triage:** The maintainers will acknowledge receipt of the report and initiate a triage process.
3.  **Remediation:** Once the vulnerability is confirmed, the maintainers will prioritize remediation based on its severity.
4.  **Disclosure:** After the fix is deployed and verified, the maintainers will publicly disclose the vulnerability through a security advisory.  The disclosure timeline will be communicated to the reporter.
