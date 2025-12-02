# Usage Guide

## Getting Started

This project simulates a device tracking and monitoring system, providing real-time updates on device status and location. It includes features for scanning devices, tracking packages, archiving old package data, and generating random jokes.

## Basic Usage

**Scanning Devices:**
The `/admin` route displays a list of all scanned devices.  You can add new devices using the `/admin/add_device` route.  A new device is added with its name, IP address, and MAC address. The status is set to "offline" and last seen is set to `NULL`.

**Tracking Packages:**
The system automatically archives packages older than 24 hours.  This archive is represented in the `packages_archive` table.

**Adding Jokes:**
The system occasionally adds a random joke to the `quote_history` table.

## Features

*   **Device Scanning:**  The `/admin` route displays a list of scanned devices, allowing for manual addition.
*   **Package Tracking:**  The system simulates package tracking, archiving old data to maintain a manageable database.
*   **Real-time Updates:**  Simulated device scanning provides real-time updates on device status and last seen.
*   **Random Joke Generation:**  The system provides a random joke as an occasional feature.

## Examples

**Adding a New Device:**

1.  Navigate to the `/admin` route in your browser.
2.  You'll see the `add_device.html` page.
3.  Enter the device's name, IP address, and MAC address.
4.  Submit the form.
5.  The new device will be added to the list in the `/admin` route.

**Viewing Archived Packages:**

1.  Navigate to the `/admin` route in your browser.
2.  The list of archived packages will be displayed, showing their tracking number, carrier, status, last location, and estimated delivery date.

## Tips

*   The system relies on simulated data.
*   The `/admin` route displays a list of all scanned devices.
*   Consider expanding this system with features like map integration, more detailed tracking data, and user authentication.
