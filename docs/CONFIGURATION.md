# Configuration Guide

## Environment Variables

*   **DATABASE**
    *   Description: Database file name.
    *   Required/Optional: Required
    *   Default Value: packages.db
*   **NY_TZ**
    *   Description: New York Timezone.
    *   Required/Optional: Required
    *   Default Value: America/New_York
*   **DEBUG**
    *   Description: Enable debug mode.
    *   Required/Optional: Required
    *   Default Value: True
*   **HOST**
    *   Description: Host address to listen on.
    *   Required/Optional: Optional
    *   Default Value: 0.0.0.0
*   **PORT**
    *   Description: Port number to listen on.
    *   Required/Optional: Optional
    *   Default Value: 5000

## Configuration Files

*   None

## Settings

*   **Holiday Theme:**  The code uses a `themes` table in the database to store different holiday themes. The `name`, `particle_type`, `background_gradient`, and `colors` are all retrieved from this table.  The code also supports a `test-holiday` parameter to be passed in the API call to switch between different themes.
