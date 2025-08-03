---
description: 'Description of the custom chat mode.'
tools: ['changes', 'codebase', 'editFiles', 'extensions', 'fetch', 'findTestFiles', 'githubRepo', 'new', 'openSimpleBrowser', 'problems', 'runCommands', 'runNotebooks', 'runTasks', 'runTests', 'search', 'searchResults', 'terminalLastCommand', 'terminalSelection', 'testFailure', 'usages', 'vscodeAPI', 'pylance mcp server', 'configurePythonEnvironment', 'getPythonEnvironmentInfo', 'getPythonExecutableCommand', 'installPythonPackage', 'configureNotebook', 'installNotebookPackages', 'listNotebookPackages']
---
Always use uv run to run any commands related to python or packaging or building or testing. Only ever build the project using ./build.sh. This ensures that the environment is set up correctly and all dependencies are managed properly.

# JupyterLab Firefox Launcher - Build Considerations
This document outlines the key considerations for building and maintaining the JupyterLab Firefox Launcher extension, including server cleanup, session management, and best practices for development.

## Server Cleanup
- Implement proper cleanup routines for the Firefox profiles and session directories to avoid leftover data from previous sessions.
- Use unique session identifiers (e.g., port numbers) to manage multiple user sessions effectively.

## Session Management
- Ensure that each user session is isolated and does not interfere with others.
- Implement mechanisms to track active sessions and their associated resources (e.g., ports, profiles).

## Development Best Practices
- Follow a modular architecture to separate concerns and improve maintainability.
- Write unit tests for critical components to ensure reliability.
- Document the codebase thoroughly to facilitate onboarding and collaboration.

## Installation and Building
Always use ./build.sh to build the extension, which ensures that all dependencies are correctly installed and the build process is consistent.

## Testing and Debugging
Always use uv run test to run tests, which provides a consistent environment for executing unit tests and integration tests.