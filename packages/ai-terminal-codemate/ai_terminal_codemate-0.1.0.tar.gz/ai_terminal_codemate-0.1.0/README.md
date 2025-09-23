# AI Terminal CodeMate

An AI-powered terminal that combines traditional command execution with natural language processing for intuitive command generation.

## Features

- **Natural Language Commands**: Type commands in plain English and get AI-generated shell commands
- **Traditional Command Support**: Full support for standard terminal commands
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **AI-Powered**: Uses Google Gemini AI for intelligent command translation

## Installation

```bash
pip install ai-terminal-codemate
```

## Usage

After installation, run:

```bash
aiterminal
```

### Examples

**Natural Language:**
- "create a file called test.txt" → `touch test.txt`
- "show me the files in this directory" → `ls`
- "make a folder called projects" → `mkdir projects`
- "show CPU usage" → `top`
- "how much memory is free" → `free`

**Traditional Commands:**
- `ls` - list files
- `mkdir folder_name` - create directory
- `rm file_name` - remove file
- `cp source dest` - copy file
- `mv source dest` - move file
- `cat file_name` - display file contents

## Available Commands

### File Operations
- `mkdir <dir>` - Create directory
- `ls [path]` - List files and folders
- `rm <file>` - Remove file
- `cp <src> <dst>` - Copy file
- `mv <src> <dst>` - Move/rename file
- `cat <file>` - Display file contents
- `touch <file>` - Create empty file

### System Information
- `top` - Show CPU usage
- `free` - Show memory usage
- `df` - Show disk usage
- `ps` - List running processes

### Navigation
- `pwd` - Print current directory
- `clear` - Clear terminal

## Configuration

The AI features require a Google Gemini API key. Create a `.env` file in your project directory:

```
GENAI_API_KEY=your_gemini_api_key_here
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.