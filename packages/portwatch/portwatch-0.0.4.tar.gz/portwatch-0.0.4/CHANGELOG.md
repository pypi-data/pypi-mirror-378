# PortWatch Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [0.1.0] - 2025-04-05

### Added
- Initial release of PortWatch TUI app
- Real-time process and port monitoring
- Built-in UI for managing dev ports (no manual `.portconfig` editing)
- Desktop notifications for port conflicts (cross-platform)
- Filter by “All”, “New”, or “Conflict” processes
- One-click process kill with confirmation modal
- Auto-generated `.portconfig` with default dev ports
- Notification disabled alert modal

### Changed
- Removed support for manual `.portconfig` editing — must use UI
- Improved UI with modern layout, active filter states, and hover effects
- Notifications now include process name and port number

### Fixed
- CSS styling for DataTable headers and cells
- Notification system fallback for unsupported platforms
- Button alignment and spacing in filter bar

### Removed
- Manual YAML config editing — replaced with secure UI config modal

---