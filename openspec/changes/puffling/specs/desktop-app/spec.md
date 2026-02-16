## ADDED Requirements

### Requirement: Tauri wraps frontend and backend into a single desktop application
The system SHALL use Tauri v2 to bundle the Next.js static export as a WebView and spawn FastAPI as a sidecar process, producing a single executable for Linux and Windows.

#### Scenario: Application starts successfully
- **WHEN** the user launches the Puffling desktop application
- **THEN** Tauri spawns the FastAPI sidecar process
- **AND** waits for the health check at `/api/health` to respond HTTP 200
- **AND** loads the frontend in the WebView pointing at the sidecar's localhost port

#### Scenario: Health check timeout shows error
- **WHEN** the FastAPI sidecar fails to respond to the health check within a timeout period
- **THEN** the application displays an error message indicating the backend failed to start

### Requirement: Graceful shutdown terminates sidecar
The system SHALL gracefully terminate the FastAPI sidecar process when the desktop window is closed.

#### Scenario: User closes the application
- **WHEN** the user closes the Tauri window
- **THEN** the system sends SIGTERM to the FastAPI sidecar process
- **AND** waits for graceful shutdown before exiting

### Requirement: Sidecar uses bundled Python environment
The system SHALL bundle a self-contained Python environment with the sidecar so users do not need Python installed separately.

#### Scenario: Application runs without system Python
- **WHEN** the user runs the Puffling executable on a machine without Python installed
- **THEN** the application starts successfully using the bundled Python environment

### Requirement: Desktop app targets Linux and Windows
The system SHALL produce distributable builds for Linux and Windows platforms.

#### Scenario: Linux build produces executable
- **WHEN** the build pipeline runs for Linux
- **THEN** it produces a distributable package (AppImage or .deb)

#### Scenario: Windows build produces executable
- **WHEN** the build pipeline runs for Windows
- **THEN** it produces a distributable package (.msi or .exe installer)
