# Standard library imports
import argparse
import base64
import configparser
import datetime
import getpass
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import urllib.request
import webbrowser
from collections import Counter

# Third-party imports
import colorama
import requests
import tiktoken
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from packaging import version
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt

# Optional dependencies with graceful fallbacks
try:
    from pyfzf.pyfzf import FzfPrompt
    HAS_FZF = True
except ImportError:
    HAS_FZF = False

try:
    from prompt_toolkit import prompt
    from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
    from prompt_toolkit.completion import Completer, Completion, WordCompleter
    from prompt_toolkit.filters import Condition
    from prompt_toolkit.formatted_text import HTML
    from prompt_toolkit.history import InMemoryHistory
    from prompt_toolkit.key_binding import KeyBindings
    from prompt_toolkit.shortcuts import CompleteStyle
    from prompt_toolkit.styles import Style
    HAS_PROMPT_TOOLKIT = True
except ImportError:
    HAS_PROMPT_TOOLKIT = False

# Initialize cross-platform support
colorama.init()

# ============================================================================
# APPLICATION CONSTANTS
# ============================================================================

# App metadata
APP_NAME = "OrChat"
APP_VERSION = "1.4.1"
REPO_URL = "https://github.com/oop7/OrChat"
API_URL = "https://api.github.com/repos/oop7/OrChat/releases/latest"

# Security & file constraints
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB limit
ALLOWED_FILE_EXTENSIONS = {
    # Text files
    '.txt', '.md', '.json', '.xml', '.csv',
    # Code files  
    '.py', '.js', '.ts', '.java', '.cpp', '.c', '.cs', '.go', '.rb', '.php', '.swift',
    # Web files
    '.html', '.css',
    # Image files
    '.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'
}

# Global state
console = Console()
last_thinking_content = ""
command_history = []

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def clear_terminal():
    """Clear the terminal screen using ANSI escape codes."""
    print("\x1b[2J\x1b[H")

def format_time_delta(delta_seconds: float) -> str:
    """Format time delta into human-readable string."""
    if delta_seconds < 1:
        return f"{delta_seconds*1000:.0f}ms"
    elif delta_seconds < 60:
        return f"{delta_seconds:.1f}s"
    else:
        mins, secs = divmod(delta_seconds, 60)
        return f"{int(mins)}m {secs:.1f}s"

def format_file_size(size_bytes: int) -> str:
    """Format file size into human-readable string."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

# ============================================================================
# COMPLETION CLASSES
# ============================================================================

class OrChatCompleter(Completer):
    """Optimized command completer with descriptions."""
    
    # Static command definitions for better performance
    COMMANDS = {
        'clear': 'Clear the screen and conversation history',
        'chat': 'Manage conversation history. Usage: /chat <list|save|resume> [session_id]',
        'new': 'Start a new conversation',
        'cls': 'Clear terminal screen',
        'clear-screen': 'Clear terminal screen',
        'save': 'Save conversation to file',
        'settings': 'Adjust model settings',
        'tokens': 'Show token usage statistics',
        'model': 'Change the AI model',
        'temperature': 'Adjust temperature (0.0-2.0)',
        'system': 'View or change system instructions',
        'speed': 'Show response time statistics',
        'theme': 'Change the color theme',
        'about': 'Show information about OrChat',
        'update': 'Check for updates',
        'thinking': 'Show last AI thinking process',
        'thinking-mode': 'Toggle thinking mode on/off',
        'help': 'Show available commands'
    }
    
    def get_completions(self, document, complete_event):
        """Generate command completions efficiently."""
        text = document.text_before_cursor
        if not text.startswith('/'):
            return
            
        command_part = text[1:].lower()
        for cmd, description in self.COMMANDS.items():
            if cmd.startswith(command_part):
                yield Completion(
                    cmd,
                    start_position=-len(command_part),
                    display_meta=description
                )

class FilePickerCompleter(Completer):
    """Optimized file picker completer for @ symbol."""
    
    # File type icons (static for performance)
    FILE_ICONS = {
        '.py': '🐍', '.js': '📜', '.ts': '📜', '.java': '☕', '.cpp': '⚙️', '.c': '⚙️',
        '.cs': '💙', '.go': '🐹', '.rb': '💎', '.php': '🐘', '.swift': '🍃',
        '.txt': '📄', '.md': '📝', '.json': '📋', '.xml': '📋', '.html': '🌐',
        '.css': '🎨', '.csv': '📊', '.jpg': '🖼️', '.jpeg': '🖼️', '.png': '🖼️',
        '.gif': '🖼️', '.webp': '🖼️', '.bmp': '🖼️'
    }
    
    def get_files_in_directory(self, directory: str = ".", filter_text: str = "") -> list:
        """Get filtered files with size checking and icons."""
        try:
            files = []
            full_path = os.path.abspath(directory)
            if not os.path.exists(full_path):
                return files
                
            for item in os.listdir(full_path):
                # Skip hidden files unless specifically requested
                if item.startswith('.') and not filter_text.startswith('.'):
                    continue
                # Apply case-insensitive filter
                if filter_text and filter_text.lower() not in item.lower():
                    continue
                
                item_path = os.path.join(full_path, item)
                
                if os.path.isfile(item_path):
                    file_ext = os.path.splitext(item)[1].lower()
                    if file_ext in ALLOWED_FILE_EXTENSIONS:
                        file_size = os.path.getsize(item_path)
                        icon = self.FILE_ICONS.get(file_ext, '📄')
                        size_str = format_file_size(file_size)
                        
                        if file_size > MAX_FILE_SIZE:
                            display = f"{icon} {item} ({size_str}) [TOO LARGE]"
                            files.append((item, display, False))
                        else:
                            display = f"{icon} {item} ({size_str})"
                            files.append((item, display, True))
                            
                elif os.path.isdir(item_path):
                    files.append((item + "/", f"📁 {item}/", True))
                    
            # Sort: directories first, then files alphabetically
            files.sort(key=lambda x: (not x[0].endswith('/'), x[0].lower()))
            return files
            
        except (OSError, PermissionError):
            return []
    
    def get_completions(self, document, complete_event):
        """Generate file completions for @ symbol anywhere in text."""
        text = document.text
        cursor_pos = document.cursor_position
        text_before = text[:cursor_pos]
        at_index = text_before.rfind('@')
        
        if at_index == -1:
            return
            
        path_part = text_before[at_index + 1:]
        # Stop if whitespace found (separate word)
        if ' ' in path_part or '\t' in path_part:
            return
        
        # Parse directory and filter
        if '/' in path_part:
            directory = os.path.dirname(path_part)
            filter_text = os.path.basename(path_part)
        else:
            directory = "."
            filter_text = path_part
        
        # Generate completions
        for filename, display_text, selectable in self.get_files_in_directory(directory, filter_text):
            if selectable:
                completion = f"{directory}/{filename}" if directory != "." else filename
                yield Completion(
                    completion,
                    start_position=-len(path_part),
                    display=display_text
                )

class CombinedCompleter(Completer):
    """Efficient combined completer for commands and files."""
    
    def __init__(self):
        self.command_completer = OrChatCompleter()
        self.file_completer = FilePickerCompleter()
    
    def get_completions(self, document, complete_event):
        """Route to appropriate completer based on context."""
        text = document.text
        cursor_pos = document.cursor_position
        
        if text.startswith('/'):
            yield from self.command_completer.get_completions(document, complete_event)
        elif '@' in text[:cursor_pos]:
            yield from self.file_completer.get_completions(document, complete_event)

def create_command_completer():
    """Create a combined completer for OrChat"""
    if not HAS_PROMPT_TOOLKIT:
        return None
    
    return CombinedCompleter()

def get_user_input_with_completion(history=None):
    """Get user input with command auto-completion and history support"""
    if not HAS_PROMPT_TOOLKIT:
        return input("> ")
    
    try:
        completer = create_command_completer()
        
        # Use provided history or create a new one
        if history is None:
            history = InMemoryHistory()
        
        # Create auto-suggest from history
        auto_suggest = AutoSuggestFromHistory()
        
        # Create key bindings for automatic completion and multiline support
        bindings = KeyBindings()
        
        # Track multiline mode
        multiline_mode = [False]  # Use list to allow modification in nested functions
        
        @bindings.add('@')
        def _(event):
            """Auto-trigger file picker completion when '@' is typed"""
            event.app.current_buffer.insert_text('@')
            # Force completion menu to show
            event.app.current_buffer.start_completion()
        
        @bindings.add('/')
        def _(event):
            """Auto-trigger completion when '/' is typed"""
            event.app.current_buffer.insert_text('/')
            # Force completion menu to show
            event.app.current_buffer.start_completion()
        
        # Add bindings for letters to keep completion active after / or #
        for char in 'abcdefghijklmnopqrstuvwxyz.-_0123456789':
            @bindings.add(char)
            def _(event, char=char):
                """Keep completion active while typing after / or @"""
                event.app.current_buffer.insert_text(char)
                # Trigger completion if we're typing after a '/' or have '@' in the text
                text = event.app.current_buffer.text
                cursor_pos = event.app.current_buffer.cursor_position
                
                # Check for command completion
                if text.startswith('/') and len(text) > 1:
                    event.app.current_buffer.start_completion()
                # Check for file picker completion (@ anywhere before cursor)
                elif '@' in text[:cursor_pos]:
                    # Find the last @ before cursor
                    text_before_cursor = text[:cursor_pos]
                    at_index = text_before_cursor.rfind('@')
                    if at_index != -1:
                        # Check if we're still in the file path (no spaces after @)
                        path_part = text_before_cursor[at_index + 1:]
                        if ' ' not in path_part and '\t' not in path_part:
                            event.app.current_buffer.start_completion()
        
        # Add binding for backspace to retrigger completion
        @bindings.add('backspace')
        def _(event):
            """Handle backspace and retrigger completion if needed"""
            if event.app.current_buffer.text:
                event.app.current_buffer.delete_before_cursor()
                # Retrigger completion if we still have / at start or @ anywhere
                text = event.app.current_buffer.text
                cursor_pos = event.app.current_buffer.cursor_position
                
                if text.startswith('/'):
                    event.app.current_buffer.start_completion()
                elif '@' in text[:cursor_pos]:
                    # Find the last @ before cursor
                    text_before_cursor = text[:cursor_pos]
                    at_index = text_before_cursor.rfind('@')
                    if at_index != -1:
                        # Check if we're still in the file path (no spaces after @)
                        path_part = text_before_cursor[at_index + 1:]
                        if ' ' not in path_part and '\t' not in path_part:
                            event.app.current_buffer.start_completion()
        
        # Add binding for Ctrl+Space to manually trigger completion
        @bindings.add('c-space')
        def _(event):
            """Manually trigger completion"""
            event.app.current_buffer.start_completion()
        
        # Add binding for Esc+Enter to toggle multiline mode
        @bindings.add('escape', 'enter')
        def _(event):
            """Toggle multiline mode with Esc+Enter"""
            multiline_mode[0] = not multiline_mode[0]
            if multiline_mode[0]:
                event.app.current_buffer.insert_text('\n')
                # Show indicator that we're in multiline mode
                event.app.invalidate()
            else:
                # Exit multiline mode and submit
                event.app.exit(result=event.app.current_buffer.text)
        
        # Custom prompt function to show multiline indicator
        def get_prompt():
            if multiline_mode[0]:
                return HTML('> <style fg="yellow">[Multi-line] </style>')
            return "> "
        
        result = prompt(
            get_prompt,
            completer=completer,
            complete_while_typing=True,
            complete_style="multi-column",
            history=history,
            auto_suggest=auto_suggest,
            enable_history_search=True,
            multiline=Condition(lambda: multiline_mode[0]),
            wrap_lines=True,
            key_bindings=bindings
        )
        return result
    except (KeyboardInterrupt, EOFError):
        raise
    except Exception as e:
        # Fallback to regular input if anything goes wrong
        print(f"[Auto-completion error: {e}]")
        return input("> ")

# ============================================================================
# SECURITY & CONFIGURATION MANAGEMENT
# ============================================================================

def generate_key() -> bytes:
    """Generate a key for encryption."""
    return Fernet.generate_key()

def encrypt_api_key(api_key: str, key: bytes) -> bytes:
    """Encrypt API key using Fernet symmetric encryption."""
    return Fernet(key).encrypt(api_key.encode())

def decrypt_api_key(encrypted_key: bytes, key: bytes) -> str:
    """Decrypt API key using Fernet symmetric encryption."""
    try:
        return Fernet(key).decrypt(encrypted_key).decode()
    except Exception:
        return None

def get_or_create_master_key() -> bytes:
    """Get or create master encryption key with secure file permissions."""
    key_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.key')
    
    if os.path.exists(key_file):
        with open(key_file, 'rb') as f:
            return f.read()
    
    # Create new key with secure permissions
    key = generate_key()
    with open(key_file, 'wb') as f:
        f.write(key)
    
    # Set restrictive permissions on Unix-like systems
    if os.name != 'nt':
        os.chmod(key_file, 0o600)
    
    return key

def validate_api_key_format(api_key: str) -> bool:
    """Validate API key format and warn about incorrect format."""
    if not api_key or len(api_key) < 20:
        return False
    
    if not api_key.startswith('sk-or-'):
        console.print("[yellow]Warning: API key doesn't match expected OpenRouter format[/yellow]")
    
    return True

def secure_input_api_key() -> str:
    """Securely input API key without echoing to console."""
    try:
        api_key = getpass.getpass("Enter your OpenRouter API key (input hidden): ")
        if not validate_api_key_format(api_key):
            console.print("[red]Invalid API key format[/red]")
            return None
        return api_key
    except KeyboardInterrupt:
        console.print("\n[yellow]API key input cancelled[/yellow]")
        return None

def load_config() -> dict:
    """Load configuration from .env file and/or config.ini with optimized handling."""
    # Load from environment first
    load_dotenv()
    api_key = os.getenv("OPENROUTER_API_KEY")

    # Default configuration
    defaults = {
        'api_key': api_key,
        'model': "",
        'temperature': 0.7,
        'system_instructions': "",
        'theme': 'default',
        'max_tokens': 0,
        'autosave_interval': 300,
        'streaming': True,
        'thinking_mode': False
    }

    # Try to load from config.ini
    config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
    if not os.path.exists(config_file):
        return defaults

    config = configparser.ConfigParser()
    config.read(config_file)

    # Load API key (encrypted or plaintext)
    if 'API' in config:
        if 'OPENROUTER_API_KEY_ENCRYPTED' in config['API']:
            try:
                encrypted_key_b64 = config['API']['OPENROUTER_API_KEY_ENCRYPTED']
                encrypted_key = base64.b64decode(encrypted_key_b64)
                master_key = get_or_create_master_key()
                decrypted_key = decrypt_api_key(encrypted_key, master_key)
                if decrypted_key:
                    defaults['api_key'] = decrypted_key
                else:
                    console.print("[yellow]Warning: Could not decrypt API key. Please re-enter it.[/yellow]")
            except Exception as e:
                console.print(f"[yellow]Warning: Error decrypting API key: {e}[/yellow]")
        elif 'OPENROUTER_API_KEY' in config['API'] and config['API']['OPENROUTER_API_KEY']:
            defaults['api_key'] = config['API']['OPENROUTER_API_KEY']

    # Load settings
    if 'SETTINGS' in config:
        settings = config['SETTINGS']
        defaults.update({
            'model': settings.get('MODEL', ''),
            'temperature': settings.getfloat('TEMPERATURE', 0.7),
            'system_instructions': settings.get('SYSTEM_INSTRUCTIONS', ''),
            'theme': settings.get('THEME', 'default'),
            'max_tokens': settings.getint('MAX_TOKENS', 0),
            'autosave_interval': settings.getint('AUTOSAVE_INTERVAL', 300),
            'streaming': settings.getboolean('STREAMING', True),
            'thinking_mode': settings.getboolean('THINKING_MODE', False)
        })

    return defaults

def save_config(config_data: dict) -> None:
    """Save configuration to config.ini with encrypted API key."""
    config = configparser.ConfigParser()
    
    # Handle API key encryption
    if 'OPENROUTER_API_KEY' not in os.environ and config_data.get('api_key'):
        try:
            master_key = get_or_create_master_key()
            encrypted_key = encrypt_api_key(config_data['api_key'], master_key)
            encrypted_key_b64 = base64.b64encode(encrypted_key).decode('utf-8')
            config['API'] = {'OPENROUTER_API_KEY_ENCRYPTED': encrypted_key_b64}
        except Exception as e:
            console.print(f"[yellow]Warning: Could not encrypt API key: {e}. Saving in plaintext.[/yellow]")
            config['API'] = {'OPENROUTER_API_KEY': config_data['api_key']}
    elif 'OPENROUTER_API_KEY' not in os.environ:
        config['API'] = {'OPENROUTER_API_KEY': config_data['api_key']}
    
    # Save settings
    config['SETTINGS'] = {
        'MODEL': config_data['model'],
        'TEMPERATURE': str(config_data['temperature']),
        'SYSTEM_INSTRUCTIONS': config_data['system_instructions'],
        'THEME': config_data['theme'],
        'MAX_TOKENS': str(config_data['max_tokens']),
        'AUTOSAVE_INTERVAL': str(config_data['autosave_interval']),
        'STREAMING': str(config_data['streaming']),
        'THINKING_MODE': str(config_data['thinking_mode'])
    }

    config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
    
    try:
        with open(config_file, 'w', encoding="utf-8") as f:
            config.write(f)
        
        # Set restrictive permissions on Unix-like systems
        if os.name != 'nt':
            os.chmod(config_file, 0o600)
            
    except Exception as e:
        console.print(f"[red]Error saving configuration: {e}[/red]")
        
        console.print("[green]Configuration saved successfully![/green]")
    except Exception as e:
        console.print(f"[red]Error saving configuration: {str(e)}[/red]")

def count_tokens(text, model_name="cl100k_base"):
    """Counts the number of tokens in a given text string using tiktoken."""
    try:
        # tiktoken.encoding_for_model will raise a KeyError if the model is not found.
        encoding = tiktoken.encoding_for_model(model_name)
    except KeyError:
        # Fallback to a default encoding for unknown models
        encoding = tiktoken.get_encoding("cl100k_base")

    tokens = encoding.encode(text)
    return len(tokens)

def get_available_models():
    """Fetch available models from OpenRouter API"""
    try:
        config = load_config()
        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json",
        }

        with console.status("[bold green]Fetching available models..."):
            response = requests.get("https://openrouter.ai/api/v1/models", headers=headers)

        if response.status_code == 200:
            models_data = response.json()
            return models_data["data"]
        console.print(f"[red]Error fetching models: {response.status_code}[/red]")
        return []
    except Exception as e:
        console.print(f"[red]Error fetching models: {str(e)}[/red]")
        return []

def get_model_info(model_id):
    """Get model information of all models"""
    models = get_available_models()
    
    try:
        for model in models:
            if model["id"] == model_id:
                return model
        
        console.print(f"[yellow]Warning: Could not find info for model '{model_id}'.[/yellow]")
        return None
    except Exception as e:
        console.print(f"[red] Failed to fetch model info: {str(e)}[/red]")
        return None

def get_enhanced_models():
    """Fetch enhanced model data from OpenRouter frontend API with detailed capabilities"""
    try:
        config = load_config()
        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json",
        }

        with console.status("[bold green]Fetching enhanced model data..."):
            response = requests.get("https://openrouter.ai/api/frontend/models", headers=headers)

        if response.status_code == 200:
            models_data = response.json()
            return models_data.get("data", [])
        else:
            console.print(f"[red]Error fetching enhanced models: {response.status_code}[/red]")
            # Fallback to standard models API
            return get_available_models()
    except Exception as e:
        console.print(f"[red]Error fetching enhanced models: {str(e)}[/red]")
        # Fallback to standard models API
        return get_available_models()

def get_models_by_capability(capability_filter="all"):
    """Get models filtered by specific capabilities using the enhanced frontend API"""
    try:
        enhanced_models = get_enhanced_models()
        
        if capability_filter == "all":
            return enhanced_models
        
        filtered_models = []
        
        for model in enhanced_models:
            # Skip None models
            if model is None:
                continue
                
            # Extract capability information from the endpoint data
            endpoint = model.get('endpoint', {})
            if endpoint is None:
                continue
            
            if capability_filter == "reasoning":
                # Check if model supports reasoning/thinking
                supports_reasoning = endpoint.get('supports_reasoning', False)
                reasoning_config = model.get('reasoning_config') or endpoint.get('reasoning_config')
                if supports_reasoning or reasoning_config:
                    filtered_models.append(model)
                    
            elif capability_filter == "multipart":
                # Check if model supports multipart (images/files)
                supports_multipart = endpoint.get('supports_multipart', False)
                input_modalities = model.get('input_modalities', [])
                if supports_multipart or ('image' in input_modalities):
                    filtered_models.append(model)
                    
            elif capability_filter == "tools":
                # Check if model supports tool parameters
                supports_tools = endpoint.get('supports_tool_parameters', False)
                supported_params = endpoint.get('supported_parameters', [])
                if supported_params is None:
                    supported_params = []
                if supports_tools or 'tools' in supported_params:
                    filtered_models.append(model)
                    
            elif capability_filter == "free":
                # Check if model is free
                is_free = endpoint.get('is_free', False)
                pricing = endpoint.get('pricing', {})
                if pricing is None:
                    pricing = {}
                prompt_price = float(pricing.get('prompt', '0'))
                if is_free or prompt_price == 0:
                    filtered_models.append(model)
                    
        return filtered_models
        
    except Exception as e:
        console.print(f"[red]Error filtering models by capability: {str(e)}[/red]")
        # Fallback to standard models
        return get_available_models()

def get_models_by_group():
    """Get models organized by their groups using enhanced API"""
    try:
        enhanced_models = get_enhanced_models()
        groups = {}
        
        for model in enhanced_models:
            # Skip None models
            if model is None:
                continue
                
            group = model.get('group', 'Other')
            if group not in groups:
                groups[group] = []
            groups[group].append(model)
        
        return groups
        
    except Exception as e:
        console.print(f"[red]Error grouping models: {str(e)}[/red]")
        return {}

def get_models_by_provider():
    """Get models organized by their providers using enhanced API"""
    try:
        enhanced_models = get_enhanced_models()
        providers = {}
        
        for model in enhanced_models:
            # Skip None models
            if model is None:
                continue
                
            endpoint = model.get('endpoint', {})
            if endpoint is None:
                continue
                
            provider = endpoint.get('provider_name', 'Unknown')
            if provider not in providers:
                providers[provider] = []
            providers[provider].append(model)
        
        return providers
        
    except Exception as e:
        console.print(f"[red]Error organizing models by provider: {str(e)}[/red]")
        return {}

def get_models_by_categories(categories):
    """Fetch models by categories from OpenRouter API using the find endpoint"""
    try:
        config = load_config()
        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json",
        }

        # Convert categories list to comma-separated string for the API
        categories_param = ",".join(categories) if isinstance(categories, list) else categories
        
        with console.status(f"[bold green]Fetching models for categories: {categories_param}..."):
            response = requests.get(
                f"https://openrouter.ai/api/frontend/models/find?categories={categories_param}",
                headers=headers
            )

        if response.status_code == 200:
            models_data = response.json()
            # Extract model slugs from the response
            if "data" in models_data and "models" in models_data["data"]:
                return [model["slug"] for model in models_data["data"]["models"]]
            return []
        else:
            console.print(f"[red]Error fetching models by categories: {response.status_code}[/red]")
            return []
    except Exception as e:
        console.print(f"[red]Error fetching models by categories: {str(e)}[/red]")
        return []

def get_dynamic_task_categories():
    """Get dynamic task categories by fetching models from specific OpenRouter categories"""
    # Map our task types to OpenRouter categories and fallback model patterns
    category_mapping = {
        "creative": {
            "openrouter_categories": ["Programming", "Technology"],  # OpenRouter categories that might contain creative models
            "fallback_patterns": ["claude-3", "gpt-4", "llama", "gemini"]  # Fallback to original patterns
        },
        "coding": {
            "openrouter_categories": ["Programming", "Technology"],
            "fallback_patterns": ["claude-3-opus", "gpt-4", "deepseek-coder", "qwen-coder", "devstral", "codestral"]
        },
        "analysis": {
            "openrouter_categories": ["Science", "Academia"],
            "fallback_patterns": ["claude-3-opus", "gpt-4", "mistral", "qwen"]
        },
        "chat": {
            "openrouter_categories": ["Programming"],  # General chat category
            "fallback_patterns": ["claude-3-haiku", "gpt-3.5", "gemini-pro", "llama"]
        }
    }

    dynamic_categories = {}
    
    for task_type, config in category_mapping.items():
        try:
            # Try to get models from OpenRouter categories first
            category_models = get_models_by_categories(config["openrouter_categories"])
            
            if category_models:
                # Filter to get relevant models based on fallback patterns for better accuracy
                filtered_models = []
                for model_slug in category_models:
                    if any(pattern in model_slug.lower() for pattern in config["fallback_patterns"]):
                        filtered_models.append(model_slug)
                
                # If we found filtered models, use them, otherwise use all category models
                dynamic_categories[task_type] = filtered_models if filtered_models else category_models[:10]  # Limit to 10 for performance
            else:
                # Fallback to pattern-based filtering with all available models
                all_models = get_available_models()
                fallback_models = []
                for model in all_models:
                    model_id = model.get('id', '').lower()
                    if any(pattern in model_id for pattern in config["fallback_patterns"]):
                        fallback_models.append(model['id'])
                
                dynamic_categories[task_type] = fallback_models[:10]  # Limit to 10 for performance
                        
        except Exception as e:
            console.print(f"[yellow]Warning: Failed to get dynamic categories for {task_type}: {str(e)}[/yellow]")
            # Use fallback patterns in case of error
            dynamic_categories[task_type] = config["fallback_patterns"]
    
    return dynamic_categories

def select_model(config):
    """Simplified model selection interface"""
    all_models = get_available_models()

    if not all_models:
        console.print("[red]No models available. Please check your API key and internet connection.[/red]")
        return None

    # Option to directly enter a model name
    console.print("[bold green]Model Selection[/bold green]")
    console.print("\n[bold magenta]Options:[/bold magenta]")
    console.print("[bold]1[/bold] - View all available models")
    console.print("[bold]2[/bold] - Show free models only")
    console.print("[bold]3[/bold] - Enter model name directly")
    console.print("[bold]4[/bold] - Browse models by task category")
    console.print("[bold]5[/bold] - Browse by capabilities (enhanced)")
    console.print("[bold]6[/bold] - Browse by model groups")
    console.print("[bold]q[/bold] - Cancel selection")

    choice = Prompt.ask("Select an option", choices=["1", "2", "3", "4", "5", "6", "q"], default="1")

    if choice == "q":
        return None

    elif choice == "3":
        # Direct model name entry
        console.print("[yellow]Enter the exact model name (e.g., 'anthropic/claude-3-opus')[/yellow]")
        model_name = Prompt.ask("Model name")

        # Validate the model name
        model_exists = any(model["id"] == model_name for model in all_models)
        if model_exists:
            # Auto-detect thinking mode support first
            try:
                auto_detect_thinking_mode(config, model_name)
            except Exception as e:
                console.print(f"[yellow]Error auto-detecting thinking mode: {str(e)}. Using default settings.[/yellow]")
            return model_name

        console.print("[yellow]Warning: Model not found in available models. Using anyway.[/yellow]")
        confirm = Prompt.ask("Continue with this model name? (y/n)", default="y")
        if confirm.lower() == "y":
            # Auto-detect thinking mode support first
            try:
                auto_detect_thinking_mode(config, model_name)
            except Exception as e:
                console.print(f"[yellow]Error auto-detecting thinking mode: {str(e)}. Using default settings.[/yellow]")
            return model_name
        return select_model(config)  # Start over

    elif choice == "1":
        # All models, simple numbered list
        console.print("[bold green]All Available Models:[/bold green]")

        if HAS_FZF:
            try:
                fzf = FzfPrompt()
                model_choice = fzf.prompt([ model['id']  for  model in all_models ])
                if not model_choice:
                    console.print("[red]No model selected. Exiting...[/red]")
                    return select_model(config)
                else:
                    try:
                        auto_detect_thinking_mode(config, model_choice[0])
                    except Exception as e:
                        console.print(f"[yellow]Error auto-detecting thinking mode: {str(e)}. Using default settings.[/yellow]")
                    return model_choice[0]
            except Exception as e:
                console.print(f"[yellow]FZF not available: {str(e)}. Falling back to numbered list.[/yellow]")
                # Fall through to the numbered list below

        with console.pager(styles=True):
            for i, model in enumerate(all_models, 1):
                # Highlight free models
                if model['id'].endswith(":free"):
                    console.print(f"[bold]{i}.[/bold] {model['id']} [green](FREE)[/green]")
                else:
                    console.print(f"[bold]{i}.[/bold] {model['id']}")

        model_choice = Prompt.ask("Enter model number or 'b' to go back", default="1")

        if model_choice.lower() == 'b':
            return select_model(config)

        try:
            index = int(model_choice) - 1
            if 0 <= index < len(all_models):
                selected_model = all_models[index]['id']
                # Auto-detect thinking mode support
                try:
                    auto_detect_thinking_mode(config, selected_model)
                except Exception as e:
                    console.print(f"[yellow]Error auto-detecting thinking mode: {str(e)}. Using default settings.[/yellow]")
                return selected_model
            else:
                console.print("[red]Invalid selection[/red]")
                return select_model(config)
        except ValueError:
            console.print("[red]Please enter a valid number[/red]")
            return select_model(config)

    elif choice == "2":
        # Show only free models
        free_models = [model for model in all_models if model['id'].endswith(":free")]

        if not free_models:
            console.print("[yellow]No free models found.[/yellow]")
            Prompt.ask("Press Enter to continue")
            return select_model(config)

        console.print("[bold green]Free Models:[/bold green]")
        for i, model in enumerate(free_models, 1):
            console.print(f"[bold]{i}.[/bold] {model['id']} [green](FREE)[/green]")

        model_choice = Prompt.ask("Enter model number or 'b' to go back", default="1")

        if model_choice.lower() == 'b':
            return select_model(config)

        try:
            index = int(model_choice) - 1
            if 0 <= index < len(free_models):
                selected_model = free_models[index]['id']
                # Auto-detect thinking mode support
                try:
                    auto_detect_thinking_mode(config, selected_model)
                except Exception as e:
                    console.print(f"[yellow]Error auto-detecting thinking mode: {str(e)}. Using default settings.[/yellow]")
                return selected_model
            console.print("[red]Invalid selection[/red]")
            Prompt.ask("Press Enter to continue")
            return select_model(config)
        except ValueError:
            console.print("[red]Please enter a valid number[/red]")
            Prompt.ask("Press Enter to continue")
            return select_model(config)

    elif choice == "4":
        # Browse models by task category using dynamic categories
        console.print("[bold green]Browse Models by Task Category:[/bold green]")
        console.print("[dim]Using dynamic categories from OpenRouter API[/dim]\n")
        
        # Available task categories
        task_categories = ["creative", "coding", "analysis", "chat"]
        
        console.print("[bold magenta]Available Categories:[/bold magenta]")
        for i, category in enumerate(task_categories, 1):
            console.print(f"[bold]{i}.[/bold] {category.title()}")
        console.print("[bold]b[/bold] - Go back to main menu")
        
        category_choice = Prompt.ask("Select a category", choices=["1", "2", "3", "4", "b"], default="1")
        
        if category_choice.lower() == 'b':
            return select_model(config)
        
        try:
            category_index = int(category_choice) - 1
            if 0 <= category_index < len(task_categories):
                selected_category = task_categories[category_index]
                
                # Get models for the selected category using dynamic categories
                console.print(f"[cyan]Loading {selected_category} models...[/cyan]")
                try:
                    dynamic_categories = get_dynamic_task_categories()
                    category_models = dynamic_categories.get(selected_category, [])
                    
                    if not category_models:
                        console.print(f"[yellow]No models found for {selected_category} category.[/yellow]")
                        Prompt.ask("Press Enter to continue")
                        return select_model(config)
                    
                    # Get full model details for display
                    all_models = get_available_models()
                    detailed_models = []
                    for model in all_models:
                        if model['id'] in category_models:
                            detailed_models.append(model)
                    
                    if not detailed_models:
                        console.print(f"[yellow]No detailed model information found for {selected_category} category.[/yellow]")
                        Prompt.ask("Press Enter to continue")
                        return select_model(config)
                    
                    console.print(f"[bold green]{selected_category.title()} Models:[/bold green]")
                    console.print(f"[dim]Found {len(detailed_models)} models optimized for {selected_category} tasks[/dim]\n")
                    
                    for i, model in enumerate(detailed_models, 1):
                        # Highlight free models and show pricing info
                        if model['id'].endswith(":free"):
                            console.print(f"[bold]{i}.[/bold] {model['id']} [green](FREE)[/green]")
                        else:
                            # Try to show pricing if available
                            pricing = ""
                            if 'pricing' in model and 'prompt' in model['pricing']:
                                try:
                                    prompt_price = float(model['pricing']['prompt'])
                                    if prompt_price > 0:
                                        pricing = f" [dim](${prompt_price:.6f}/token)[/dim]"
                                except:
                                    pass
                            console.print(f"[bold]{i}.[/bold] {model['id']}{pricing}")
                    
                    console.print(f"\n[bold]b[/bold] - Go back to category selection")
                    
                    model_choice = Prompt.ask("Enter model number or 'b' to go back", default="1")
                    
                    if model_choice.lower() == 'b':
                        return select_model(config)
                    
                    try:
                        model_index = int(model_choice) - 1
                        if 0 <= model_index < len(detailed_models):
                            selected_model = detailed_models[model_index]['id']
                            console.print(f"[green]Selected {selected_model} for {selected_category} tasks[/green]")
                            
                            # Auto-detect thinking mode support
                            try:
                                auto_detect_thinking_mode(config, selected_model)
                            except Exception as e:
                                console.print(f"[yellow]Error auto-detecting thinking mode: {str(e)}. Using default settings.[/yellow]")
                            return selected_model
                        else:
                            console.print("[red]Invalid selection[/red]")
                            Prompt.ask("Press Enter to continue")
                            return select_model(config)
                    except ValueError:
                        console.print("[red]Please enter a valid number[/red]")
                        Prompt.ask("Press Enter to continue")
                        return select_model(config)
                        
                except Exception as e:
                    console.print(f"[red]Error loading dynamic categories: {str(e)}[/red]")
                    console.print("[yellow]Falling back to standard model selection[/yellow]")
                    Prompt.ask("Press Enter to continue")
                    return select_model(config)
            else:
                console.print("[red]Invalid category selection[/red]")
                return select_model(config)
        except ValueError:
            console.print("[red]Please enter a valid number[/red]")
            return select_model(config)

    elif choice == "5":
        # Browse models by capabilities using enhanced API
        console.print("[bold green]Browse Models by Capabilities:[/bold green]")
        console.print("[dim]Using enhanced OpenRouter frontend API data[/dim]\n")
        
        # Available capability filters
        capabilities = [
            ("reasoning", "Models with thinking/reasoning support"),
            ("multipart", "Models that support images and files"),
            ("tools", "Models with tool/function calling support"),
            ("free", "Free models (no cost)")
        ]
        
        console.print("[bold magenta]Available Capabilities:[/bold magenta]")
        for i, (cap, desc) in enumerate(capabilities, 1):
            console.print(f"[bold]{i}.[/bold] {desc}")
        console.print("[bold]b[/bold] - Go back to main menu")
        
        cap_choice = Prompt.ask("Select a capability", choices=["1", "2", "3", "4", "b"], default="1")
        
        if cap_choice.lower() == 'b':
            return select_model(config)
        
        try:
            cap_index = int(cap_choice) - 1
            if 0 <= cap_index < len(capabilities):
                selected_capability, description = capabilities[cap_index]
                
                # Get models with the selected capability
                console.print(f"[cyan]Loading models with {description.lower()}...[/cyan]")
                try:
                    capability_models = get_models_by_capability(selected_capability)
                    
                    if not capability_models:
                        console.print(f"[yellow]No models found with {description.lower()}.[/yellow]")
                        Prompt.ask("Press Enter to continue")
                        return select_model(config)
                    
                    console.print(f"[bold green]{description}:[/bold green]")
                    console.print(f"[dim]Found {len(capability_models)} models[/dim]\n")
                    
                    for i, model in enumerate(capability_models, 1):
                        # Skip None models in display
                        if model is None:
                            continue
                            
                        # Show enhanced model information
                        endpoint = model.get('endpoint', {}) if model else {}
                        # Try multiple fields for model name
                        model_name = model.get('slug') or model.get('name') or model.get('short_name', 'Unknown') if model else 'Unknown'
                        
                        # Show capability-specific information
                        extra_info = ""
                        if selected_capability == "reasoning":
                            reasoning_config = model.get('reasoning_config') or endpoint.get('reasoning_config') if model and endpoint else None
                            if reasoning_config:
                                start_token = reasoning_config.get('start_token', '<thinking>')
                                end_token = reasoning_config.get('end_token', '</thinking>')
                                extra_info = f" [dim]({start_token}...{end_token})[/dim]"
                        elif selected_capability == "multipart":
                            input_modalities = model.get('input_modalities', []) if model else []
                            if input_modalities:
                                extra_info = f" [dim]({', '.join(input_modalities)})[/dim]"
                        elif selected_capability == "tools":
                            supported_params = endpoint.get('supported_parameters', []) if endpoint else []
                            if supported_params is None:
                                supported_params = []
                            tool_params = [p for p in supported_params if 'tool' in p.lower()]
                            if tool_params:
                                extra_info = f" [dim]({', '.join(tool_params)})[/dim]"
                        elif selected_capability == "free":
                            provider = endpoint.get('provider_name', 'Unknown') if endpoint else 'Unknown'
                            extra_info = f" [green](FREE via {provider})[/green]"
                        
                        console.print(f"[bold]{i}.[/bold] {model_name}{extra_info}")
                    
                    console.print(f"\n[bold]b[/bold] - Go back to capability selection")
                    
                    model_choice = Prompt.ask("Enter model number or 'b' to go back", default="1")
                    
                    if model_choice.lower() == 'b':
                        return select_model(config)
                    
                    try:
                        model_index = int(model_choice) - 1
                        if 0 <= model_index < len(capability_models):
                            selected_model_obj = capability_models[model_index]
                            if selected_model_obj:
                                selected_model = selected_model_obj.get('slug') or selected_model_obj.get('name') or selected_model_obj.get('short_name', 'Unknown')
                            else:
                                selected_model = 'Unknown'
                            console.print(f"[green]Selected {selected_model} with {description.lower()}[/green]")
                            
                            # Auto-detect thinking mode support
                            try:
                                auto_detect_thinking_mode(config, selected_model)
                            except Exception as e:
                                console.print(f"[yellow]Error detecting thinking mode: {str(e)}. Using default settings.[/yellow]")
                            return selected_model
                        else:
                            console.print("[red]Invalid selection[/red]")
                            Prompt.ask("Press Enter to continue")
                            return select_model(config)
                    except ValueError:
                        console.print("[red]Please enter a valid number[/red]")
                        Prompt.ask("Press Enter to continue")
                        return select_model(config)
                        
                except Exception as e:
                    console.print(f"[red]Error loading capability models: {str(e)}[/red]")
                    console.print("[yellow]Falling back to standard model selection[/yellow]")
                    Prompt.ask("Press Enter to continue")
                    return select_model(config)
            else:
                console.print("[red]Invalid capability selection[/red]")
                return select_model(config)
        except ValueError:
            console.print("[red]Please enter a valid number[/red]")
            return select_model(config)

    elif choice == "6":
        # Browse models by groups using enhanced API
        console.print("[bold green]Browse Models by Groups:[/bold green]")
        console.print("[dim]Using enhanced OpenRouter frontend API data[/dim]\n")
        
        try:
            groups = get_models_by_group()
            
            if not groups:
                console.print("[yellow]No model groups found.[/yellow]")
                Prompt.ask("Press Enter to continue")
                return select_model(config)
            
            # Sort groups by name and display
            sorted_groups = sorted(groups.keys())
            console.print("[bold magenta]Available Model Groups:[/bold magenta]")
            for i, group in enumerate(sorted_groups, 1):
                model_count = len(groups[group])
                console.print(f"[bold]{i}.[/bold] {group} [dim]({model_count} models)[/dim]")
            console.print("[bold]b[/bold] - Go back to main menu")
            
            group_choice = Prompt.ask("Select a group", default="1")
            
            if group_choice.lower() == 'b':
                return select_model(config)
            
            try:
                group_index = int(group_choice) - 1
                if 0 <= group_index < len(sorted_groups):
                    selected_group = sorted_groups[group_index]
                    group_models = groups[selected_group]
                    
                    console.print(f"[bold green]{selected_group} Models:[/bold green]")
                    console.print(f"[dim]Found {len(group_models)} models in this group[/dim]\n")
                    
                    for i, model in enumerate(group_models, 1):
                        # Skip None models in display
                        if model is None:
                            continue
                            
                        endpoint = model.get('endpoint', {}) if model else {}
                        model_name = model.get('slug') or model.get('name') or model.get('short_name', 'Unknown') if model else 'Unknown'
                        provider = endpoint.get('provider_name', 'Unknown') if endpoint else 'Unknown'
                        
                        # Show pricing info
                        pricing_info = ""
                        if endpoint and endpoint.get('is_free', False):
                            pricing_info = " [green](FREE)[/green]"
                        elif endpoint:
                            pricing = endpoint.get('pricing', {})
                            if pricing:
                                prompt_price = pricing.get('prompt', '0')
                                try:
                                    if float(prompt_price) > 0:
                                        pricing_info = f" [dim](${prompt_price}/token)[/dim]"
                                except:
                                    pass
                        
                        console.print(f"[bold]{i}.[/bold] {model_name} [dim]({provider})[/dim]{pricing_info}")
                    
                    console.print(f"\n[bold]b[/bold] - Go back to group selection")
                    
                    model_choice = Prompt.ask("Enter model number or 'b' to go back", default="1")
                    
                    if model_choice.lower() == 'b':
                        return select_model(config)
                    
                    try:
                        model_index = int(model_choice) - 1
                        if 0 <= model_index < len(group_models):
                            selected_model_obj = group_models[model_index]
                            if selected_model_obj:
                                selected_model = selected_model_obj.get('slug') or selected_model_obj.get('name') or selected_model_obj.get('short_name', 'Unknown')
                            else:
                                selected_model = 'Unknown'
                            console.print(f"[green]Selected {selected_model} from {selected_group} group[/green]")
                            
                            # Auto-detect thinking mode support
                            try:
                                auto_detect_thinking_mode(config, selected_model)
                            except Exception as e:
                                console.print(f"[yellow]Error detecting thinking mode: {str(e)}. Using default settings.[/yellow]")
                            return selected_model
                        else:
                            console.print("[red]Invalid selection[/red]")
                            Prompt.ask("Press Enter to continue")
                            return select_model(config)
                    except ValueError:
                        console.print("[red]Please enter a valid number[/red]")
                        Prompt.ask("Press Enter to continue")
                        return select_model(config)
                else:
                    console.print("[red]Invalid group selection[/red]")
                    return select_model(config)
            except ValueError:
                console.print("[red]Please enter a valid number[/red]")
                return select_model(config)
                
        except Exception as e:
            console.print(f"[red]Error loading model groups: {str(e)}[/red]")
            console.print("[yellow]Falling back to standard model selection[/yellow]")
            Prompt.ask("Press Enter to continue")
            return select_model(config)

def auto_detect_thinking_mode(config, selected_model):
    """Automatically detect if the selected model supports thinking mode"""
    # Make sure the thinking_mode key exists in config
    if 'thinking_mode' not in config:
        config['thinking_mode'] = False  # Default to disabled

    try:
        # Get enhanced models to check if this model supports reasoning
        enhanced_models = get_enhanced_models()
        
        for model in enhanced_models:
            if model is None:
                continue
                
            # Check if this is the selected model
            model_slug = model.get('slug') or model.get('name') or model.get('short_name', '')
            if model_slug == selected_model:
                # Check if model supports reasoning/thinking
                endpoint = model.get('endpoint', {})
                supports_reasoning = endpoint.get('supports_reasoning', False) if endpoint else False
                reasoning_config = model.get('reasoning_config') or (endpoint.get('reasoning_config') if endpoint else None)
                
                if supports_reasoning or reasoning_config:
                    config['thinking_mode'] = True
                    console.print("[green]🧠 Thinking mode automatically enabled for this reasoning model.[/green]")
                    if reasoning_config:
                        start_token = reasoning_config.get('start_token', '<thinking>')
                        end_token = reasoning_config.get('end_token', '</thinking>')
                        console.print(f"[dim]Uses reasoning tags: {start_token}...{end_token}[/dim]")
                else:
                    config['thinking_mode'] = False
                    console.print("[dim]Thinking mode disabled - this model doesn't support reasoning.[/dim]")
                return
        
        # If model not found in enhanced models, disable thinking mode
        config['thinking_mode'] = False
        console.print("[dim]Thinking mode disabled - unable to verify reasoning support.[/dim]")
        
    except Exception as e:
        # If there's an error, keep current setting or default to disabled
        config['thinking_mode'] = config.get('thinking_mode', False)
        console.print(f"[yellow]Could not auto-detect thinking mode: {str(e)}[/yellow]")
        console.print(f"[dim]Keeping current setting: {'enabled' if config['thinking_mode'] else 'disabled'}[/dim]")

def get_model_pricing_info(model_name):
    """Get pricing information for a specific model"""
    try:
        enhanced_models = get_enhanced_models()
        
        for model in enhanced_models:
            if model is None:
                continue
                
            # Check if this is the selected model
            model_slug = model.get('slug') or model.get('name') or model.get('short_name', '')
            if model_slug == model_name:
                endpoint = model.get('endpoint', {})
                if endpoint:
                    api_is_free = endpoint.get('is_free', False)
                    pricing = endpoint.get('pricing', {})
                    
                    # Check if the model name explicitly indicates it's free
                    is_explicitly_free = model_name and (model_name.endswith(':free') or ':free' in model_name)
                    
                    # For explicitly free models, always return free pricing regardless of API data
                    if is_explicitly_free:
                        return {
                            'is_free': True,
                            'prompt_price': 0.0,
                            'completion_price': 0.0,
                            'display': 'FREE (OpenRouter)',
                            'provider': endpoint.get('provider_name', 'Unknown')
                        }
                    elif pricing:
                        prompt_price = float(pricing.get('prompt', '0'))
                        completion_price = float(pricing.get('completion', '0'))
                        
                        if prompt_price == 0 and completion_price == 0:
                            # Model has 0 pricing but may still require credits
                            # Don't trust 0-pricing for non-explicit free models
                            return {
                                'is_free': False,
                                'prompt_price': 0.0,
                                'completion_price': 0.0,
                                'display': 'Requires credits',
                                'provider': endpoint.get('provider_name', 'Unknown')
                            }
                        else:
                            # Format prices for display
                            if prompt_price * 1000 < 0.001:
                                prompt_display = f"${prompt_price * 1000:.4f}"
                            else:
                                prompt_display = f"${prompt_price * 1000:.3f}"
                                
                            if completion_price * 1000 < 0.001:
                                completion_display = f"${completion_price * 1000:.4f}"
                            else:
                                completion_display = f"${completion_price * 1000:.3f}"
                                
                            return {
                                'is_free': False,
                                'prompt_price': prompt_price,
                                'completion_price': completion_price,
                                'display': f"{prompt_display}/1K prompt, {completion_display}/1K completion",
                                'provider': endpoint.get('provider_name', 'Unknown')
                            }
        
        # Model not found in enhanced models - check if it's a free model by name
        if model_name and (model_name.endswith(':free') or ':free' in model_name):
            return {
                'is_free': True,
                'prompt_price': 0.0,
                'completion_price': 0.0,
                'display': 'FREE',
                'provider': 'OpenRouter'
            }
        
        # Model not found in enhanced models and not obviously free
        return {
            'is_free': False,
            'prompt_price': 0.0,
            'completion_price': 0.0,
            'display': 'Pricing unknown - may require credits',
            'provider': 'Unknown'
        }
        
    except Exception as e:
        return {
            'is_free': False,
            'prompt_price': 0.0,
            'completion_price': 0.0,
            'display': 'Pricing unknown - may require credits',
            'provider': 'Unknown'
        }

def calculate_session_cost(total_prompt_tokens, total_completion_tokens, pricing_info):
    """Calculate the total cost for the current session"""
    if pricing_info['is_free']:
        return 0.0
    
    prompt_cost = total_prompt_tokens * pricing_info['prompt_price']
    completion_cost = total_completion_tokens * pricing_info['completion_price']
    
    return prompt_cost + completion_cost



def setup_wizard():
    """Interactive setup wizard for first-time users"""
    console.print(Panel.fit(
        "[bold blue]Welcome to the OrChat Setup Wizard![/bold blue]\n"
        "Let's configure your chat settings.",
        title="Setup Wizard"
    ))

    if "OPENROUTER_API_KEY" not in os.environ:
        console.print("[bold yellow]🔐 API Key Setup[/bold yellow]")
        console.print("[dim]Your API key will be encrypted and stored securely[/dim]")
        
        # Loop until we get a valid API key or user explicitly cancels
        while True:
            api_key = secure_input_api_key()
            if not api_key:
                console.print("[red]Invalid API key provided.[/red]")
                retry = Prompt.ask("Would you like to try again? (y/n)", default="y")
                if retry.lower() != 'y':
                    console.print("[red]Setup cancelled - no valid API key provided[/red]")
                    return None
                continue  # Ask for API key again
            else:
                break  # Valid API key received, exit loop
    else:
        api_key = os.getenv("OPENROUTER_API_KEY")

    # Save API key temporarily to allow model fetching
    temp_config = {'api_key': api_key, 'thinking_mode': False}  # Default to disabled

    # Use the simplified model selection
    console.print("[bold]Select an AI model to use:[/bold]")
    model = ""
    thinking_mode = False  # Default value - disabled
    try:
        with console.status("[bold green]Connecting to OpenRouter...[/bold green]"):
            # Small delay to ensure the API key is registered
            time.sleep(1)

        selected_model = select_model(temp_config)
        if selected_model:
            model = selected_model
            # Use the thinking_mode value that was set during model selection
            thinking_mode = temp_config.get('thinking_mode', False)
        else:
            console.print("[yellow]Model selection cancelled. You can set a model later.[/yellow]")
    except Exception as e:
        console.print(f"[yellow]Error during model selection: {str(e)}. You can set a model later.[/yellow]")

    temperature = float(Prompt.ask("Set temperature (0.0-2.0)", default="0.7"))
    if temperature > 1.0:
        console.print("[yellow]Warning: High temperature values (>1.0) may cause erratic or nonsensical responses.[/yellow]")
        confirm = Prompt.ask("Are you sure you want to use this high temperature? (y/n)", default="n")
        if confirm.lower() != 'y':
            temperature = float(Prompt.ask("Enter a new temperature value (0.0-1.0)", default="0.7"))

    console.print("[bold]Enter system instructions (guide the AI's behavior)[/bold]")
    console.print("[dim]Press Enter twice to finish[/dim]")
    lines = []
    empty_line_count = 0
    while True:
        line = input()
        if not line:
            empty_line_count += 1
            if empty_line_count >= 2:  # Exit after two consecutive empty lines
                break
        else:
            empty_line_count = 0  # Reset counter if non-empty line
            lines.append(line)

    # If no instructions provided, use a default value
    if not lines:
        system_instructions = "You are a helpful AI assistant."
        console.print("[yellow]No system instructions provided. Using default instructions.[/yellow]")
    else:
        system_instructions = "\n".join(lines)

    # Add theme selection
    available_themes = ['default', 'dark', 'light', 'hacker']
    console.print("[green]Available themes:[/green]")
    for theme in available_themes:
        console.print(f"- {theme}")
    theme_choice = Prompt.ask("Select theme", choices=available_themes, default="default")

    # We already asked about thinking mode during model selection, so we'll use that value
    # Only ask if model selection failed or was cancelled
    if not model:
        # Enhanced thinking mode explanation
        console.print(Panel.fit(
            "[yellow]Thinking Mode:[/yellow]\n\n"
            "Thinking mode shows the AI's reasoning process between <thinking> and </thinking> tags.\n"
            "This reveals how the AI approaches your questions and can help you understand its thought process.\n\n"
            "[dim]Note: Not all models support this feature. If you notice issues with responses, you can disable it later with /thinking-mode[/dim]",
            title="🧠 AI Reasoning Process",
            border_style="yellow"
        ))

        thinking_mode = Prompt.ask(
            "Enable thinking mode?",
            choices=["y", "n"],
            default="n"
        ).lower() == "y"

    config_data = {
        'api_key': api_key,
        'model': model,
        'temperature': temperature,
        'system_instructions': system_instructions,
        'theme': theme_choice,
        'max_tokens': 0,
        'autosave_interval': 300,
        'streaming': True,
        'thinking_mode': thinking_mode
    }

    save_config(config_data)
    return config_data

def format_time_delta(delta_seconds):
    """Format time delta in a human-readable format"""
    if delta_seconds < 1:
        return f"{delta_seconds*1000:.0f}ms"
    elif delta_seconds < 60:
        return f"{delta_seconds:.2f}s"
    else:
        minutes = int(delta_seconds // 60)
        seconds = delta_seconds % 60
        return f"{minutes}m {seconds:.2f}s"

def format_file_size(size_bytes):
    """Format file size in a human-readable way"""
    if size_bytes < 1024:
        return f"{size_bytes} bytes"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

def stream_response(response, start_time, thinking_mode=False):
    """Stream the response from the API with proper text formatting"""
    console.print("\n[bold green]Assistant[/bold green]")

    # Full content accumulates everything
    full_content = ""
    # For thinking detection
    thinking_content = ""
    in_thinking = False
    # For capturing usage information
    usage_info = None

    # Create a temporary file to collect all content
    # This avoids terminal display issues
    collected_content = []

    # For debugging purposes
    global last_thinking_content

    try:
        for chunk in response.iter_lines():
            if not chunk:
                continue

            chunk_text = chunk.decode('utf-8', errors='replace')

            if "OPENROUTER PROCESSING" in chunk_text:
                continue

            if chunk_text.startswith('data:'):
                chunk_text = chunk_text[5:].strip()

            if chunk_text == "[DONE]":
                continue

            try:
                chunk_data = json.loads(chunk_text)
                
                # Capture usage information if present
                if 'usage' in chunk_data:
                    usage_info = chunk_data['usage']
                
                if 'choices' in chunk_data and chunk_data['choices']:
                    delta = chunk_data['choices'][0].get('delta', {})
                    content = delta.get('content', delta.get('text', ''))

                    if content:
                        # Add to full content
                        full_content += content

                        # Only process thinking tags if thinking mode is enabled
                        if thinking_mode:
                            # Check for thinking tags
                            if "<thinking>" in content:
                                in_thinking = True
                                # Extract content after the tag
                                thinking_part = content.split("<thinking>", 1)[1]
                                thinking_content += thinking_part
                                # Skip this chunk - don't display the <thinking> tag
                                continue

                            if "</thinking>" in content:
                                in_thinking = False
                                # Extract content before the tag
                                thinking_part = content.split("</thinking>", 1)[0]
                                thinking_content += thinking_part
                                # Skip this chunk - don't display the </thinking> tag
                                continue

                            if in_thinking:
                                thinking_content += content
                                continue

                        # Not in thinking mode or model doesn't support thinking, collect for display
                        collected_content.append(content)
            except json.JSONDecodeError:
                # For non-JSON chunks, quietly ignore
                pass
    except Exception as e:
        console.print(f"\n[red]Error during streaming: {str(e)}[/red]")

    # More robust thinking extraction - uses regex pattern to look for any thinking tags in the full content
    thinking_section = ""
    thinking_pattern = re.compile(r'<thinking>(.*?)</thinking>', re.DOTALL)
    thinking_matches = thinking_pattern.findall(full_content)

    if thinking_mode and thinking_matches:
        thinking_section = "\n".join(thinking_matches)
        # Update the global thinking content variable
        last_thinking_content = thinking_section

        # Display thinking content immediately if found
        console.print(Panel.fit(
            Markdown(last_thinking_content),
            title="🧠 AI Thinking Process",
            border_style="yellow"
        ))
    else:
        # Also check if thinking_content has any content from our incremental collection
        if thinking_content.strip():
            last_thinking_content = thinking_content

            # Display thinking content immediately if found
            console.print(Panel.fit(
                Markdown(last_thinking_content),
                title="🧠 AI Thinking Process",
                border_style="yellow"
            ))

    # Clean the full content - only if model supports thinking
    cleaned_content = full_content
    if thinking_mode and "<thinking>" in full_content:
        # Remove the thinking sections with a more robust pattern
        try:
            # Use a non-greedy match to handle multiple thinking sections
            cleaned_content = re.sub(r'<thinking>.*?</thinking>', '', full_content, flags=re.DOTALL)
            cleaned_content = cleaned_content.strip()
        except:
            # Fallback to simpler method
            parts = full_content.split("</thinking>")
            if len(parts) > 1:
                cleaned_content = parts[-1].strip()

    # If after cleaning we have nothing, use a default response
    if not cleaned_content.strip():
        cleaned_content = "Hello! I'm here to help you."

    if cleaned_content:
        console.print(Markdown(cleaned_content))
    else:
        console.print("Hello! I'm here to help you.")

    response_time = time.time() - start_time
    return cleaned_content, response_time, usage_info

def save_conversation(conversation_history, filename, fmt="markdown"):
    """Save conversation to file in various formats"""
    if fmt == "markdown":
        with open(filename, 'w', encoding="utf-8") as f:
            f.write("# OrChat Conversation\n\n")
            f.write(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            for msg in conversation_history:
                if msg['role'] == 'system':
                    f.write(f"## System Instructions\n\n{msg['content']}\n\n")
                else:
                    f.write(f"## {msg['role'].capitalize()}\n\n{msg['content']}\n\n")
    elif fmt == "json":
        with open(filename, 'w', encoding="utf-8") as f:
            json.dump(conversation_history, f, indent=2)
    elif fmt == "html":
        with open(filename, 'w', encoding="utf-8") as f:
            f.write("<!DOCTYPE html>\n<html>\n<head>\n")
            f.write("<title>OrChat Conversation</title>\n")
            f.write("<style>\n")
            f.write("body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }\n")
            f.write(".system { background-color: #f0f0f0; padding: 10px; border-radius: 5px; }\n")
            f.write(".user { background-color: #e1f5fe; padding: 10px; border-radius: 5px; margin: 10px 0; }\n")
            f.write(".assistant { background-color: #f1f8e9; padding: 10px; border-radius: 5px; margin: 10px 0; }\n")
            f.write("</style>\n</head>\n<body>\n")
            f.write("<h1>OrChat Conversation</h1>\n")
            f.write(f"<p>Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>\n")

            for msg in conversation_history:
                f.write(f"<div class='{msg['role']}'>\n")
                f.write(f"<h2>{msg['role'].capitalize()}</h2>\n")
                content_html = msg['content'].replace('\n', '<br>')
                f.write(f"<p>{content_html}</p>\n")
                f.write("</div>\n")

            f.write("</body>\n</html>")

    return filename

def load_conversation(session_id):
    """Load conversation from a session directory"""
    sessions_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sessions")
    session_path = os.path.join(sessions_dir, session_id)
    
    if not os.path.exists(session_path):
        return None, "Session not found"
    
    # Look for JSON file first (preferred for resume)
    json_files = [f for f in os.listdir(session_path) if f.endswith('.json')]
    if json_files:
        json_file = os.path.join(session_path, json_files[0])
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                conversation_history = json.load(f)
            return conversation_history, None
        except Exception as e:
            return None, f"Error loading JSON file: {str(e)}"
    
    # Fallback to parsing markdown file
    md_files = [f for f in os.listdir(session_path) if f.endswith('.md')]
    if md_files:
        md_file = os.path.join(session_path, md_files[0])
        try:
            conversation_history = []
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Simple markdown parser for conversation format
            sections = content.split('## ')
            for section in sections[1:]:  # Skip header
                lines = section.strip().split('\n', 1)
                if len(lines) >= 2:
                    role = lines[0].lower()
                    if role == 'system instructions':
                        role = 'system'
                    content_text = lines[1].strip()
                    conversation_history.append({"role": role, "content": content_text})
            
            return conversation_history, None
        except Exception as e:
            return None, f"Error parsing markdown file: {str(e)}"
    
    return None, "No conversation files found in session"

def generate_conversation_summary(conversation_history):
    """Generate a short summary of the conversation using a lightweight model"""
    try:
        # Extract meaningful content (skip system messages)
        user_messages = [msg['content'] for msg in conversation_history if msg['role'] == 'user']
        assistant_messages = [msg['content'] for msg in conversation_history if msg['role'] == 'assistant']
        
        if not user_messages:
            return "empty_conversation"
        
        # Create a condensed version for summarization
        conversation_text = ""
        for i, (user_msg, assistant_msg) in enumerate(zip(user_messages[:3], assistant_messages[:3])):  # Only first 3 exchanges
            conversation_text += f"User: {user_msg[:100]}...\n"
            if assistant_msg:
                conversation_text += f"Assistant: {assistant_msg[:100]}...\n"
        
        # Use a lightweight free model for summarization
        summary_prompt = f"""Create a very short (2-4 words) topic summary for this conversation. Use lowercase with underscores, no spaces. Examples: "python_coding", "travel_advice", "cooking_tips", "math_help", "job_interview".

Conversation:
{conversation_text}

Summary:"""

        # Make API call with lightweight model
        data = {
            "model": "meta-llama/llama-3.3-8b-instruct:free",
            "messages": [{"role": "user", "content": summary_prompt}],
            "temperature": 0.3,
            "max_tokens": 20
        }
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                "Content-Type": "application/json"
            },
            json=data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                summary = result['choices'][0]['message']['content'].strip()
                # Clean up the summary - remove quotes, ensure it's valid
                summary = summary.replace('"', '').replace("'", "").replace(' ', '_').lower()
                # Limit length and ensure it's alphanumeric + underscores
                summary = re.sub(r'[^a-z0-9_]', '', summary)[:20]
                return summary if summary else "conversation"
        
        # Fallback to simple topic detection
        combined_text = " ".join(user_messages[:2]).lower()
        if any(word in combined_text for word in ['code', 'program', 'python', 'javascript', 'html']):
            return "coding_help"
        elif any(word in combined_text for word in ['travel', 'trip', 'vacation', 'visit']):
            return "travel_advice"
        elif any(word in combined_text for word in ['cook', 'recipe', 'food', 'eat']):
            return "cooking_tips"
        elif any(word in combined_text for word in ['work', 'job', 'career', 'interview']):
            return "career_advice"
        else:
            return "general_chat"
            
    except Exception as e:
        # Fallback to timestamp if everything fails
        return datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

def save_session_metadata(session_dir, summary):
    """Save session metadata including the human-readable summary"""
    metadata = {
        "summary": summary,
        "created": datetime.datetime.now().isoformat(),
        "session_id": os.path.basename(session_dir)
    }
    metadata_file = os.path.join(session_dir, "metadata.json")
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)

def get_session_summary(session_dir):
    """Get the human-readable summary for a session"""
    metadata_file = os.path.join(session_dir, "metadata.json")
    if os.path.exists(metadata_file):
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            return metadata.get('summary', os.path.basename(session_dir))
        except:
            pass
    return os.path.basename(session_dir)  # Fallback to directory name

def manage_context_window(conversation_history, max_tokens=8000, model_name="cl100k_base"):
    """Manage the context window to prevent exceeding token limits"""
    # Always keep the system message
    system_message = conversation_history[0]

    # Count total tokens in the conversation
    total_tokens = sum(count_tokens(msg["content"], model_name) for msg in conversation_history)

    # If we're under the limit, no need to trim
    if total_tokens <= max_tokens:
        return conversation_history, 0

    # We need to trim the conversation
    # Start with just the system message
    trimmed_history = [system_message]
    current_tokens = count_tokens(system_message["content"], model_name)

    # Add messages from the end (most recent) until we approach the limit
    # Leave room for the next user message
    messages_to_consider = conversation_history[1:]
    trimmed_count = 0

    for msg in reversed(messages_to_consider):
        msg_tokens = count_tokens(msg["content"], model_name)
        if current_tokens + msg_tokens < max_tokens - 1000:  # Leave 1000 tokens buffer
            trimmed_history.insert(1, msg)  # Insert after system message
            current_tokens += msg_tokens
        else:
            trimmed_count += 1

    # Add a note about trimmed messages if any were removed
    if trimmed_count > 0:
        note = {"role": "system", "content": f"Note: {trimmed_count} earlier messages have been removed to stay within the context window."}
        trimmed_history.insert(1, note)

    return trimmed_history, trimmed_count

def validate_file_security(file_path):
    """Validate file for security concerns before processing"""
    try:
        # Check if file exists and is readable
        if not os.path.exists(file_path):
            return False, "File does not exist"
        
        if not os.path.isfile(file_path):
            return False, "Path is not a file"
        
        # Check file size
        file_size = os.path.getsize(file_path)
        if file_size > MAX_FILE_SIZE:
            return False, f"File too large ({format_file_size(file_size)}). Maximum allowed: {format_file_size(MAX_FILE_SIZE)}"
        
        # Check file extension
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext not in ALLOWED_FILE_EXTENSIONS:
            return False, f"File type '{file_ext}' not allowed. Allowed types: {', '.join(sorted(ALLOWED_FILE_EXTENSIONS))}"
        
        # Basic path traversal prevention
        normalized_path = os.path.normpath(file_path)
        if '..' in normalized_path:
            return False, "Invalid file path detected"
        
        # Check for executable files (additional security)
        dangerous_extensions = {'.exe', '.bat', '.cmd', '.com', '.scr', '.pif', '.vbs', '.jar', '.sh'}
        if file_ext in dangerous_extensions:
            return False, f"Executable file type '{file_ext}' not allowed for security reasons"
        
        return True, "File validation passed"
    
    except Exception as e:
        return False, f"File validation error: {str(e)}"

def process_file_upload(file_path, conversation_history):
    """Process a file upload and add its contents to the conversation"""
    try:
        # Validate file security first
        is_valid, validation_message = validate_file_security(file_path)
        if not is_valid:
            return False, f"Security validation failed: {validation_message}"

        # Read file with proper encoding handling
        try:
            with open(file_path, 'r', encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            # Try with different encoding for non-UTF8 files
            with open(file_path, 'r', encoding="latin-1") as f:
                content = f.read()
        
        # Limit content size for processing
        max_content_length = 50000  # 50KB of text content
        if len(content) > max_content_length:
            content = content[:max_content_length] + "\n\n[Content truncated due to size limit]"

        file_ext = os.path.splitext(file_path)[1].lower()
        file_name = os.path.basename(file_path)

        # Sanitize file name to prevent issues
        safe_file_name = re.sub(r'[<>:"/\\|?*]', '_', file_name)

        # Determine file type and create appropriate message
        if file_ext in ['.py', '.js', '.java', '.cpp', '.c', '.cs', '.go', '.rb', '.php', '.ts', '.swift']:
            file_type = "code"
            message = f"I'm uploading a code file named '{safe_file_name}'. Please analyze it:\n\n```{file_ext[1:]}\n{content}\n```"
        elif file_ext in ['.txt', '.md', '.csv', '.json', '.xml', '.html', '.css']:
            file_type = "text"
            message = f"I'm uploading a text file named '{safe_file_name}'. Here are its contents:\n\n{content}"
        else:
            file_type = "unknown"
            message = f"I'm uploading a file named '{safe_file_name}'. Here are its contents:\n\n{content}"

        # Add to conversation history
        conversation_history.append({"role": "user", "content": message})
        return True, f"File '{safe_file_name}' uploaded successfully as {file_type}."
    except Exception as e:
        console.print(f"[red]File processing error: {str(e)}[/red]")
        return False, f"Error processing file: {str(e)}"

def handle_attachment(file_path, conversation_history):
    """Enhanced file attachment handling with preview and metadata"""
    try:
        # Validate file security first
        is_valid, validation_message = validate_file_security(file_path)
        if not is_valid:
            return False, f"Security validation failed: {validation_message}"

        # Get file information
        file_name = os.path.basename(file_path)
        file_ext = os.path.splitext(file_path)[1].lower()
        file_size = os.path.getsize(file_path)
        file_size_formatted = format_file_size(file_size)

        # Sanitize file name
        safe_file_name = re.sub(r'[<>:"/\\|?*]', '_', file_name)

        # Determine file type and create appropriate message
        file_type, content = extract_file_content(file_path, file_ext)

        # Create a message that includes metadata about the attachment
        message = f"I'm sharing a file: **{safe_file_name}** ({file_type}, {file_size_formatted})\n\n"

        if file_type == "image":
            # For images, validate and process safely
            if file_size > 5 * 1024 * 1024:  # 5MB limit for images
                return False, "Image file too large (max 5MB)"
            
            try:
                with open(file_path, 'rb') as img_file:
                    image_data = img_file.read()
                    # Basic image validation (check for image headers)
                    if not (image_data.startswith(b'\xff\xd8') or  # JPEG
                           image_data.startswith(b'\x89PNG') or  # PNG
                           image_data.startswith(b'GIF8') or     # GIF
                           image_data.startswith(b'RIFF')):     # WebP
                        return False, "Invalid or corrupted image file"
                    
                    base64_image = base64.b64encode(image_data).decode('utf-8')

                # Add to messages with proper format for multimodal models
                conversation_history.append({
                    "role": "user",
                    "content": [
                        {"type": "text", "text": message},
                        {"type": "image_url", "image_url": {"url": f"data:image/{file_ext[1:]};base64,{base64_image}"}}
                    ]
                })
                return True, f"Image '{safe_file_name}' attached successfully."
            except Exception as e:
                return False, f"Error processing image: {str(e)}"
        else:
            # For other file types, add content to the message
            message += content
            conversation_history.append({"role": "user", "content": message})
            return True, f"File '{safe_file_name}' attached successfully as {file_type}."

    except Exception as e:
        console.print(f"[red]Attachment processing error: {str(e)}[/red]")
        return False, f"Error processing attachment: {str(e)}"

def extract_file_content(file_path, file_ext):
    """Extract and format content from different file types"""
    # Determine file type based on extension
    if file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']:
        return "image", ""

    elif file_ext in ['.pdf']:
        # Basic PDF handling - just mention it's a PDF
        return "PDF document", "[PDF content not displayed in chat, but AI can analyze the document]"

    elif file_ext in ['.py', '.js', '.java', '.cpp', '.c', '.cs', '.go', '.rb', '.php', '.ts', '.swift']:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        return "code", f"```{file_ext[1:]}\n{content}\n```"

    elif file_ext in ['.txt', '.md', '.csv']:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        return "text", content

    elif file_ext in ['.json', '.xml']:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        return "data", f"```{file_ext[1:]}\n{content}\n```"

    elif file_ext in ['.html', '.css']:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        return "web", f"```{file_ext[1:]}\n{content}\n```"

    elif file_ext in ['.zip', '.tar', '.gz', '.rar']:
        return "archive", "[Archive content not displayed in chat]"

    else:
        # Try to read as text, but handle binary files
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            return "unknown", content
        except:
            return "binary", "[Binary content not displayed in chat]"



def show_about():
    """Display information about OrChat"""
    console.print(Panel.fit(
        f"[bold blue]Or[/bold blue][bold green]Chat[/bold green] [dim]v{APP_VERSION}[/dim]\n\n"
        "A powerful CLI for chatting with AI models through OpenRouter.\n\n"
        f"[link={REPO_URL}]{REPO_URL}[/link]\n\n"
        "Created by OOP7\n"
        "Licensed under MIT License",
        title="ℹ️ About OrChat",
        border_style="blue"
    ))

# Add this function to check for updates
def check_for_updates(silent=False):
    """Check GitHub for newer versions of OrChat"""
    if not silent:
        console.print("[bold cyan]Checking for updates...[/bold cyan]")
    try:
        with urllib.request.urlopen(API_URL) as response:
            if response.getcode() == 200:
                data = json.loads(response.read().decode('utf-8'))
                latest_version = data.get('tag_name', 'v0.0.0').lstrip('v')

                if version.parse(latest_version) > version.parse(APP_VERSION):
                    console.print(Panel.fit(
                        f"[yellow]A new version of OrChat is available![/yellow]\n"
                        f"Current version: [cyan]{APP_VERSION}[/cyan]\n"
                        f"Latest version: [green]{latest_version}[/green]\n\n"
                        f"Update at: {REPO_URL}/releases",
                        title="📢 Update Available",
                        border_style="yellow"
                    ))

                    if silent:
                        update_choice = Prompt.ask("Would you like to update now?", choices=["y", "n"], default="n")
                        if update_choice.lower() == "y":
                            try:
                                console.print("[cyan]Attempting to update via pip...[/cyan]")
                                result = subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "orchat"], 
                                                      capture_output=True, text=True)
                                if result.returncode == 0:
                                    console.print("[green]Update successful! Please restart OrChat.[/green]")
                                    sys.exit(0)
                                else:
                                    console.print(f"[yellow]Update failed: {result.stderr}[/yellow]")
                                    open_browser = Prompt.ask("Open release page for manual update?", choices=["y", "n"], default="y")
                                    if open_browser.lower() == "y":
                                        webbrowser.open(f"{REPO_URL}/releases")
                            except Exception as e:
                                console.print(f"[yellow]Auto-update failed: {str(e)}[/yellow]")
                                open_browser = Prompt.ask("Open release page for manual update?", choices=["y", "n"], default="y")
                                if open_browser.lower() == "y":
                                    webbrowser.open(f"{REPO_URL}/releases")
                    else:
                        open_browser = Prompt.ask("Open release page in browser?", choices=["y", "n"], default="n")
                        if open_browser.lower() == "y":
                            webbrowser.open(f"{REPO_URL}/releases")
                    return True  # Update available
                else:
                    if not silent:
                        console.print("[green]You are using the latest version of OrChat![/green]")
                    return False  # No update available
            else:
                if not silent:
                    console.print("[yellow]Could not check for updates. Server returned status "
                                f"code {response.getcode()}[/yellow]")
                return False
    except Exception as e:
        if not silent:
            console.print(f"[yellow]Could not check for updates: {str(e)}[/yellow]")
        return False



def chat_with_model(config, conversation_history=None):
    """ Main chat loop with model interaction """
    if conversation_history is None:
        # Use user's thinking mode preference instead of model detection
        if config['thinking_mode']:
            # Make the thinking instruction more explicit and mandatory
            thinking_instruction = (
                f"{config['system_instructions']}\n\n"
                "CRITICAL INSTRUCTION: For EVERY response without exception, you MUST first explain your "
                "thinking process between <thinking> and </thinking> tags, even for simple greetings or short "
                "responses. This thinking section should explain your reasoning and approach. "
                "After the thinking section, provide your final response. Example format:\n"
                "<thinking>Here I analyze what to say, considering context and appropriate responses...</thinking>\n"
                "This is my actual response to the user."
            )
        else:
            # Use standard instructions without thinking tags
            thinking_instruction = config['system_instructions']

        conversation_history = [
            {"role": "system", "content": thinking_instruction}
        ]

    # Initialize command history for session
    if HAS_PROMPT_TOOLKIT:
        session_history = InMemoryHistory()
    else:
        session_history = None
    
    # Initialize double CTRL+C exit tracking
    ctrl_c_count = 0
    last_ctrl_c_time = 0

    headers = {
        "Authorization": f"Bearer {config['api_key']}",
        "Content-Type": "application/json",
    }

    # Check if temperature is too high and warn the user
    if config['temperature'] > 1.0:
        console.print(Panel.fit(
            f"[yellow]Warning: High temperature setting ({config['temperature']}) may cause erratic responses.[/yellow]\n"
            f"Consider using a value between 0.0 and 1.0 for more coherent outputs.",
            title="⚠️ High Temperature Warning",
            border_style="yellow"
        ))

    # Get pricing information for the model
    pricing_info = get_model_pricing_info(config['model'])
    pricing_display = f"[cyan]Pricing:[/cyan] {pricing_info['display']}"
    if pricing_info['is_free']:
        pricing_display += f" [green]({pricing_info['provider']})[/green]"
    else:
        pricing_display += f" [dim]({pricing_info['provider']})[/dim]"

    console.print(Panel.fit(
        f"[bold blue]Or[/bold blue][bold green]Chat[/bold green] [dim]v{APP_VERSION}[/dim]\n"
        f"[cyan]Model:[/cyan] {config['model']}\n"
        f"[cyan]Temperature:[/cyan] {config['temperature']}\n"
        f"[cyan]Thinking mode:[/cyan] {'[green]✓ Enabled[/green]' if config['thinking_mode'] else '[yellow]✗ Disabled[/yellow]'}\n"
        f"{pricing_display}\n"
        f"[cyan]Session started:[/cyan] {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"Type your message or use commands: /help for available commands\n"
        f"[dim]Press Ctrl+C again to exit[/dim]",
        title="🤖 Chat Session Active",
        border_style="green"
    ))

    # Add session tracking
    session_start_time = time.time()
    total_tokens_used = 0
    total_prompt_tokens = 0
    total_completion_tokens = 0
    response_times = []
    message_count = 0
    max_tokens = config.get('max_tokens')
    
    if not max_tokens or max_tokens == 0:
        model_info = get_model_info(config['model'])
        if model_info and 'context_length' in model_info and model_info['context_length']:
            max_tokens = model_info['context_length']
            console.print(f"[dim]Using model's context length: {max_tokens:,} tokens[/dim]")
        else:
            max_tokens = 8192
            console.print(f"[yellow]Could not determine model's context length. Using default: {max_tokens:,} tokens[/yellow]")
    else:
        console.print(f"[dim]Using user-defined max tokens: {max_tokens:,}[/dim]")

    # Create a session directory for saving files
    session_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    session_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sessions", session_id)
    os.makedirs(session_dir, exist_ok=True)

    # Auto-save conversation periodically
    last_autosave = time.time()
    autosave_interval = config['autosave_interval']

    # Check if we need to trim the conversation history
    conversation_history, trimmed_count = manage_context_window(conversation_history, max_tokens=max_tokens, model_name=config['model'])
    if trimmed_count > 0:
        console.print(f"[yellow]Note: Removed {trimmed_count} earlier messages to stay within the context window.[/yellow]")

    while True:
        try:
            # Display user input panel similar to assistant style
            console.print("\n")
            console.print(Panel.fit(
                "Enter your message",
                title="👤 You",
                border_style="blue"
            ))
            
            # Use auto-completion if available, otherwise fallback to regular input
            if HAS_PROMPT_TOOLKIT:
                user_input = get_user_input_with_completion(session_history)
            else:
                print("> ", end="")
                user_input = input()

            # Ignore empty or whitespace-only input
            if not user_input.strip():
                continue

            # Reset CTRL+C counter when user provides valid input
            ctrl_c_count = 0

            # Handle special commands and file picker
            # Check if input starts with a command OR contains file picker
            if user_input.startswith('/'):
                # Handle regular commands starting with /
                command = user_input.lower()
            elif user_input.startswith('@'):
                # Handle file picker with @
                file_path = user_input[1:].strip()
                
                if not file_path:
                    console.print("[yellow]Please select a file using the file picker.[/yellow]")
                    console.print("[dim]Type @ to browse files in the current directory[/dim]")
                    continue
                
                # Handle relative paths - make them absolute
                if not os.path.isabs(file_path):
                    file_path = os.path.abspath(file_path)
                
                # Check if file exists
                if not os.path.exists(file_path):
                    console.print(f"[red]File not found: {file_path}[/red]")
                    console.print("[dim]Make sure the file path is correct and the file exists.[/dim]")
                    continue

                # Show attachment preview
                file_name = os.path.basename(file_path)
                file_ext = os.path.splitext(file_path)[1].lower()
                file_size = os.path.getsize(file_path)
                file_size_formatted = format_file_size(file_size)

                console.print(Panel.fit(
                    f"File: [bold]{file_name}[/bold]\n"
                    f"Type: {file_ext[1:].upper() if file_ext else 'Unknown'}\n"
                    f"Size: {file_size_formatted}",
                    title="📎 Attachment Preview",
                    border_style="cyan"
                ))

                # Process the file attachment
                success, message = handle_attachment(file_path, conversation_history)
                if success:
                    console.print(f"[green]{message}[/green]")
                else:
                    console.print(f"[red]{message}[/red]")
                    continue
                
                # Continue to get user's actual message about the file
                console.print("\n[dim]The file has been attached. Now enter your message about this file:[/dim]")
                
                # Get user input for the message about the file
                if HAS_PROMPT_TOOLKIT:
                    user_message = get_user_input_with_completion(session_history)
                else:
                    print("> ", end="")
                    user_message = input()
                
                if user_message.strip():
                    user_input = user_message  # Use the message as the actual input
                else:
                    continue  # Skip if no message provided
            
            elif '@' in user_input:
                # Handle file picker anywhere in the message
                parts = user_input.split('@', 1)
                if len(parts) == 2:
                    message_part = parts[0].strip()
                    file_and_rest = parts[1].strip()
                    
                    if file_and_rest:
                        # Parse filename and any additional text after it
                        # Split by whitespace to separate filename from additional text
                        file_tokens = file_and_rest.split()
                        file_part = file_tokens[0] if file_tokens else ""
                        additional_text = " ".join(file_tokens[1:]) if len(file_tokens) > 1 else ""
                        
                        if file_part:
                            # Handle relative paths - make them absolute
                            if not os.path.isabs(file_part):
                                file_part = os.path.abspath(file_part)
                            
                            # Check if file exists
                            if not os.path.exists(file_part):
                                console.print(f"[red]File not found: {file_part}[/red]")
                                console.print("[dim]Make sure the file path is correct and the file exists.[/dim]")
                                continue

                        # Show attachment preview
                        file_name = os.path.basename(file_part)
                        file_ext = os.path.splitext(file_part)[1].lower()
                        file_size = os.path.getsize(file_part)
                        file_size_formatted = format_file_size(file_size)

                        console.print(Panel.fit(
                            f"File: [bold]{file_name}[/bold]\n"
                            f"Type: {file_ext[1:].upper() if file_ext else 'Unknown'}\n"
                            f"Size: {file_size_formatted}",
                            title="📎 Attachment Preview",
                            border_style="cyan"
                        ))

                        # Process the file attachment
                        success, attachment_message = handle_attachment(file_part, conversation_history)
                        if success:
                            console.print(f"[green]{attachment_message}[/green]")
                            # Combine message part with any additional text after filename
                            combined_message = ""
                            if message_part:
                                combined_message = message_part
                            if additional_text:
                                if combined_message:
                                    combined_message += " " + additional_text
                                else:
                                    combined_message = additional_text
                            
                            if combined_message:
                                user_input = combined_message
                            else:
                                console.print("\n[dim]File attached. Enter your message about this file:[/dim]")
                                if HAS_PROMPT_TOOLKIT:
                                    user_input = get_user_input_with_completion(session_history)
                                else:
                                    print("> ", end="")
                                    user_input = input()
                        else:
                            console.print(f"[red]{attachment_message}[/red]")
                            continue
            
            # Process commands if we have one
            if user_input.startswith('/'):
                command = user_input.lower()

                if command == '/help':
                    help_text = "/new - Start a new conversation\n" \
                               "/clear - Clear conversation history\n" \
                               "/cls or /clear-screen - Clear terminal screen\n" \
                               "/save - Save conversation to file\n" \
                               "/chat <list|save|resume> [session_id] - Manage conversation history\n" \
                               "/settings - Adjust model settings\n" \
                               "/tokens - Show token usage statistics\n" \
                               "/model - Change the AI model\n" \
                               "/temperature <0.0-2.0> - Adjust temperature\n" \
                               "/system - View or change system instructions\n" \
                               "/speed - Show response time statistics\n" \
                               "/theme <theme> - Change the color theme\n" \
                               "/about - Show information about OrChat\n" \
                               "/update - Check for updates\n" \
                               "/thinking - Show last AI thinking process\n" \
                               "/thinking-mode - Toggle thinking mode on/off\n" \
                               "@ - Browse and attach files (can be used anywhere in your message)\n" \
                               "[yellow]Press Ctrl+C twice to exit[/yellow]"
                    
                    if HAS_PROMPT_TOOLKIT:
                        help_text += "\n\n[dim]💡 Interactive Features:[/dim]\n"
                        help_text += "[dim]• Command auto-completion: Type '/' and all commands appear instantly[/dim]\n"
                        help_text += "[dim]• File picker: Type '#' anywhere to browse and select files[/dim]\n"
                        help_text += "[dim]• Continue typing to filter commands/files (e.g., '/c' or '#main'[/dim]\n"
                        help_text += "[dim]• Press ↑/↓ arrow keys to navigate through previous prompts[/dim]\n"
                        help_text += "[dim]• Press Ctrl+R to search through prompt history[/dim]\n"
                        help_text += "[dim]• Press Esc+Enter to toggle multi-line input mode[/dim]\n"
                        help_text += "[dim]• Auto-suggestions: Previous prompts appear as grey text while typing[/dim]"
                    
                    console.print(Panel.fit(
                        help_text,
                        title="Available Commands"
                    ))
                    continue

                elif command == '/clear':
                    conversation_history = [{"role": "system", "content": config['system_instructions']}]
                    console.print("[green]Conversation history cleared![/green]")
                    continue

                elif command == '/new':
                    # Check if there's any actual conversation to save
                    if len(conversation_history) > 1:
                        save_prompt = Prompt.ask(
                            "Would you like to save the current conversation before starting a new one?",
                            choices=["y", "n"],
                            default="n"
                        )

                        if save_prompt.lower() == "y":
                            # Auto-generate a filename with timestamp
                            filename = f"conversation_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                            filepath = os.path.join(session_dir, filename)
                            save_conversation(conversation_history, filepath, "markdown")
                            console.print(f"[green]Conversation saved to {filepath}[/green]")

                    # Reset conversation
                    conversation_history = [{"role": "system", "content": config['system_instructions']}]

                    # Reset session tracking variables
                    total_tokens_used = 0
                    response_times = []
                    message_count = 0
                    last_autosave = time.time()

                    # Create a new session directory
                    session_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    session_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sessions", session_id)
                    os.makedirs(session_dir, exist_ok=True)

                    console.print(Panel.fit(
                        "[green]New conversation started![/green]\n"
                        "Previous conversation history has been cleared.",
                        title="🔄 New Conversation",
                        border_style="green"
                    ))
                    continue

                elif command == '/save':
                    parts = user_input.split(' ', 1)
                    if len(parts) > 1:
                        filename = parts[1]
                    else:
                        filename = Prompt.ask("Enter filename to save conversation",
                                            default=f"conversation_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md")

                    format_options = ["markdown", "json", "html"]
                    format_choice = Prompt.ask("Choose format", choices=format_options, default="markdown")

                    if not filename.endswith(f".{format_choice.split('.')[-1]}"):
                        if format_choice == "markdown":
                            filename += ".md"
                        elif format_choice == "json":
                            filename += ".json"
                        elif format_choice == "html":
                            filename += ".html"

                    filepath = os.path.join(session_dir, filename)
                    save_conversation(conversation_history, filepath, format_choice)
                    console.print(f"[green]Conversation saved to {filepath}[/green]")
                    continue

                elif command == '/settings':
                    console.print(Panel.fit(
                        f"Current Settings:\n"
                        f"Model: {config['model']}\n"
                        f"Temperature: {config['temperature']}\n"
                        f"System Instructions: {config['system_instructions'][:50]}...",
                        title="Settings"
                    ))
                    continue

                elif command == '/tokens':
                    # Calculate session statistics
                    session_duration = time.time() - session_start_time
                    session_cost = calculate_session_cost(total_prompt_tokens, total_completion_tokens, pricing_info)
                    
                    # Create detailed token statistics
                    stats_text = f"[bold cyan]📊 Session Statistics[/bold cyan]\n\n"
                    stats_text += f"[cyan]Model:[/cyan] {config['model']}\n"
                    stats_text += f"[cyan]Session duration:[/cyan] {format_time_delta(session_duration)}\n"
                    stats_text += f"[cyan]Messages exchanged:[/cyan] {message_count}\n\n"
                    
                    stats_text += f"[bold]Token Usage:[/bold]\n"
                    stats_text += f"[cyan]Prompt tokens:[/cyan] {total_prompt_tokens:,}\n"
                    stats_text += f"[cyan]Completion tokens:[/cyan] {total_completion_tokens:,}\n"
                    stats_text += f"[cyan]Total tokens:[/cyan] {total_tokens_used:,}\n"
                    stats_text += f"[dim]Token counts from OpenRouter API (accurate)[/dim]\n\n"
                    
                    if pricing_info['is_free']:
                        stats_text += f"[green]💰 Cost: FREE[/green]\n"
                    else:
                        if session_cost < 0.01:
                            cost_display = f"${session_cost:.6f}"
                        else:
                            cost_display = f"${session_cost:.4f}"
                        stats_text += f"[cyan]💰 Session cost:[/cyan] {cost_display}\n"
                        stats_text += f"[dim]{pricing_info['display']}[/dim]\n"
                    
                    if response_times:
                        avg_time = sum(response_times) / len(response_times)
                        stats_text += f"\n[cyan]⏱️ Avg response time:[/cyan] {format_time_delta(avg_time)}"
                        
                        if total_completion_tokens > 0 and avg_time > 0:
                            tokens_per_second = total_completion_tokens / sum(response_times)
                            stats_text += f"\n[cyan]⚡ Speed:[/cyan] {tokens_per_second:.1f} tokens/second"
                    
                    console.print(Panel.fit(
                        stats_text,
                        title="📈 Token Statistics",
                        border_style="cyan"
                    ))
                    continue

                elif command == '/speed':
                    if not response_times:
                        console.print("[yellow]No response time data available yet.[/yellow]")
                    else:
                        avg_time = sum(response_times) / len(response_times)
                        min_time = min(response_times)
                        max_time = max(response_times)
                        console.print(Panel.fit(
                            f"Response Time Statistics:\n"
                            f"Average: {format_time_delta(avg_time)}\n"
                            f"Fastest: {format_time_delta(min_time)}\n"
                            f"Slowest: {format_time_delta(max_time)}\n"
                            f"Total responses: {len(response_times)}",
                            title="Speed Statistics"
                        ))
                    continue

                elif command.startswith('/model'):
                    selected_model = select_model(config)
                    if selected_model:
                        config['model'] = selected_model
                        save_config(config)
                        console.print(f"[green]Model changed to {config['model']}[/green]")
                    else:
                        console.print("[yellow]Model selection cancelled[/yellow]")
                    continue

                elif command.startswith('/temperature'):
                    parts = command.split()
                    if len(parts) > 1:
                        try:
                            temp = float(parts[1])
                            if 0 <= temp <= 2:
                                if temp > 1.0:
                                    console.print("[yellow]Warning: High temperature values (>1.0) may cause erratic or nonsensical responses.[/yellow]")
                                    confirm = Prompt.ask("Are you sure you want to use this high temperature? (y/n)", default="n")
                                    if confirm.lower() != 'y':
                                        continue

                                config['temperature'] = temp
                                save_config(config)
                                console.print(f"[green]Temperature set to {temp}[/green]")
                            else:
                                console.print("[red]Temperature must be between 0 and 2[/red]")
                        except ValueError:
                            console.print("[red]Invalid temperature value[/red]")
                    else:
                        new_temp = Prompt.ask("Enter new temperature (0.0-2.0)", default=str(config['temperature']))
                        try:
                            temp = float(new_temp)
                            if 0 <= temp <= 2:
                                if temp > 1.0:
                                    console.print("[yellow]Warning: High temperature values (>1.0) may cause erratic or nonsensical responses.[/yellow]")
                                    confirm = Prompt.ask("Are you sure you want to use this high temperature? (y/n)", default="n")
                                    if confirm.lower() != 'y':
                                        continue

                                config['temperature'] = temp
                                save_config(config)
                                console.print(f"[green]Temperature set to {temp}[/green]")
                            else:
                                console.print("[red]Temperature must be between 0 and 2[/red]")
                        except ValueError:
                            console.print("[red]Invalid temperature value[/red]")
                    continue

                elif command.startswith('/system'):
                    parts = user_input.split(' ', 1)
                    if len(parts) > 1:
                        config['system_instructions'] = parts[1]
                        conversation_history[0] = {"role": "system", "content": config['system_instructions']}
                        save_config(config)
                        console.print("[green]System instructions updated![/green]")
                    else:
                        console.print(Panel(config['system_instructions'], title="Current System Instructions"))
                        change = Prompt.ask("Update system instructions? (y/n)", default="n")
                        if change.lower() == 'y':
                            console.print("[bold]Enter new system instructions (guide the AI's behavior)[/bold]")
                            console.print("[dim]Press Enter twice to finish[/dim]")
                            lines = []
                            empty_line_count = 0
                            while True:
                                line = input()
                                if not line:
                                    empty_line_count += 1
                                    if empty_line_count >= 2:  # Exit after two consecutive empty lines
                                        break
                                else:
                                    empty_line_count = 0  # Reset counter if non-empty line
                                    lines.append(line)
                            system_instructions = "\n".join(lines)
                            config['system_instructions'] = system_instructions
                            conversation_history[0] = {"role": "system", "content": config['system_instructions']}
                            save_config(config)
                            console.print("[green]System instructions updated![/green]")
                    continue

                elif command.startswith('/theme'):
                    parts = command.split()
                    available_themes = ['default', 'dark', 'light', 'hacker']
                    
                    if len(parts) > 1:
                        theme = parts[1].lower()
                        if theme in available_themes:
                            config['theme'] = theme
                            save_config(config)
                            console.print(f"[green]Theme changed to {theme}[/green]")
                        else:
                            console.print(f"[red]Invalid theme. Available themes: {', '.join(available_themes)}[/red]")
                    else:
                        console.print(f"[cyan]Current theme:[/cyan] {config['theme']}")
                        console.print(f"[cyan]Available themes:[/cyan] {', '.join(available_themes)}")
                        new_theme = Prompt.ask("Select theme", choices=available_themes, default=config['theme'])
                        config['theme'] = new_theme
                        save_config(config)
                        console.print(f"[green]Theme changed to {new_theme}[/green]")
                    continue

                elif command == '/about':
                    show_about()
                    continue

                elif command == '/update':
                    check_for_updates(silent=False)
                    continue

                elif command == '/thinking':
                    if last_thinking_content:
                        console.print(Panel.fit(
                            last_thinking_content,
                            title="🧠 Last Thinking Process",
                            border_style="yellow"
                        ))
                    else:
                        console.print("[yellow]No thinking content available from the last response.[/yellow]")
                    continue

                elif command == '/thinking-mode':
                    # Toggle thinking mode
                    config['thinking_mode'] = not config['thinking_mode']
                    save_config(config)

                    # Update the system prompt for future messages
                    if len(conversation_history) > 0 and conversation_history[0]['role'] == 'system':
                        original_instructions = config['system_instructions']
                        if config['thinking_mode']:
                            thinking_instruction = (
                                f"{original_instructions}\n\n"
                                "CRITICAL INSTRUCTION: For EVERY response without exception, you MUST first explain your "
                                "thinking process between <thinking> and </thinking> tags, even for simple greetings or short "
                                "responses. This thinking section should explain your reasoning and approach. "
                                "After the thinking section, provide your final response. Example format:\n"
                                "<thinking>Here I analyze what to say, considering context and appropriate responses...</thinking>\n"
                                "This is my actual response to the user."
                            )
                            conversation_history[0]['content'] = thinking_instruction
                        else:
                            # Revert to original instructions without thinking tags
                            conversation_history[0]['content'] = original_instructions

                    console.print(f"[green]Thinking mode is now {'enabled' if config['thinking_mode'] else 'disabled'}[/green]")
                    continue

                elif command in ('/cls', '/clear-screen'):

                    # Clear the terminal
                    clear_terminal()

                    # After clearing, redisplay the session header for context
                    # Re-get pricing info for display
                    current_pricing_info = get_model_pricing_info(config['model'])
                    pricing_display = f"[cyan]Pricing:[/cyan] {current_pricing_info['display']}"
                    if not current_pricing_info['is_free']:
                        pricing_display += f" [dim]({current_pricing_info['provider']})[/dim]"
                    else:
                        pricing_display += f" [green]({current_pricing_info['provider']})[/green]"
                        
                    console.print(Panel.fit(
                        f"[bold blue]Or[/bold blue][bold green]Chat[/bold green] [dim]v{APP_VERSION}[/dim]\n"
                        f"[cyan]Model:[/cyan] {config['model']}\n"
                        f"[cyan]Temperature:[/cyan] {config['temperature']}\n"
                        f"[cyan]Thinking mode:[/cyan] {'[green]✓ Enabled[/green]' if config['thinking_mode'] else '[yellow]✗ Disabled[/yellow]'}\n"
                        f"{pricing_display}\n"
                        f"[cyan]Session started:[/cyan] {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                        f"Type your message or use commands: /help for available commands",
                        title="🤖 Chat Session Active",
                        border_style="green"
                    ))
                    console.print("[green]Terminal screen cleared. Chat session continues.[/green]")
                    continue

                elif command.startswith('/chat'):
                    parts = user_input.split()
                    if len(parts) < 2:
                        console.print("[yellow]Usage: /chat <list|save|resume> [session_id][/yellow]")
                        continue
                    
                    action = parts[1].lower()
                    session_id = parts[2] if len(parts) > 2 else None
                    
                    if action == 'list':
                        # List saved conversations with human-readable summaries
                        sessions_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sessions")
                        if os.path.exists(sessions_dir):
                            sessions = [d for d in os.listdir(sessions_dir) if os.path.isdir(os.path.join(sessions_dir, d))]
                            if sessions:
                                session_list = []
                                for session in sorted(sessions, reverse=True):  # Most recent first
                                    session_path = os.path.join(sessions_dir, session)
                                    summary = get_session_summary(session_path)
                                    session_list.append(f"{summary} ({session})")
                                
                                console.print(Panel.fit(f"Saved sessions:\n" + "\n".join(session_list), title="Chat History"))
                            else:
                                console.print("[yellow]No saved conversations found.[/yellow]")
                        else:
                            console.print("[yellow]No sessions directory found.[/yellow]")
                    elif action == 'save':
                        # Generate a meaningful summary for this conversation
                        console.print("[cyan]Generating conversation summary...[/cyan]")
                        summary = generate_conversation_summary(conversation_history)
                        
                        # Save both markdown and JSON for resume capability
                        md_filepath = os.path.join(session_dir, f"{summary}.md")
                        json_filepath = os.path.join(session_dir, f"{summary}.json")
                        save_conversation(conversation_history, md_filepath, "markdown")
                        save_conversation(conversation_history, json_filepath, "json")
                        
                        # Save metadata with summary
                        save_session_metadata(session_dir, summary)
                        
                        console.print(f"[green]Conversation saved as '{summary}'[/green]")
                    elif action == 'resume':
                        if not session_id:
                            console.print("[yellow]Please specify a session ID to resume. Use '/chat list' to see available sessions.[/yellow]")
                        else:
                            # If user provides a summary name, find the corresponding session
                            sessions_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sessions")
                            target_session = session_id
                            
                            # Check if it's a summary name by looking through all sessions
                            if os.path.exists(sessions_dir):
                                for session in os.listdir(sessions_dir):
                                    session_path = os.path.join(sessions_dir, session)
                                    if os.path.isdir(session_path):
                                        summary = get_session_summary(session_path)
                                        if summary == session_id:
                                            target_session = session
                                            break
                            
                            loaded_history, error = load_conversation(target_session)
                            if error:
                                console.print(f"[red]Error loading conversation: {error}[/red]")
                            else:
                                conversation_history.clear()
                                conversation_history.extend(loaded_history)
                                console.print(f"[green]Conversation resumed from session {target_session}![/green]")
                                # Show a brief summary
                                msg_count = len([msg for msg in conversation_history if msg['role'] in ['user', 'assistant']])
                                console.print(f"[cyan]Loaded {msg_count} messages from previous conversation.[/cyan]")
                    else:
                        console.print("[yellow]Unknown chat action. Use: list, save, or resume[/yellow]")
                    continue

                else:
                    console.print("[yellow]Unknown command. Type /help for available commands.[/yellow]")
                    continue

            # Count tokens in user input
            # Estimate input tokens for display purposes (will be replaced by API data if available)
            estimated_input_tokens = count_tokens(user_input)
            input_tokens = estimated_input_tokens
            total_prompt_tokens += input_tokens

            # Add user message to conversation history
            conversation_history.append({"role": "user", "content": user_input})

            # Get model max tokens
            model_info = get_model_info(config['model'])
            if model_info and 'context_length' in model_info:
                # This is just for display, max_tokens for management is set at the start
                display_max_tokens = model_info['context_length']
            else:
                display_max_tokens = max_tokens

            # Check if we need to trim the conversation history
            conversation_history, trimmed_count = manage_context_window(conversation_history, max_tokens=max_tokens, model_name=config['model'])
            if trimmed_count > 0:
                console.print(f"[yellow]Note: Removed {trimmed_count} earlier messages to stay within the context window.[/yellow]")

            # Clean conversation history for API - remove any messages with invalid fields
            clean_conversation = []
            for msg in conversation_history:
                clean_msg = {
                    "role": msg["role"],
                    "content": msg["content"]
                }
                # Handle models that don't support system messages (like Gemma)
                if clean_msg["role"] == "system":
                    # Check if this is a Gemma model that doesn't support system messages
                    if "gemma" in config['model'].lower():
                        # Convert system message to user message with instructions
                        if clean_msg["content"] and clean_msg["content"].strip():
                            clean_msg["role"] = "user"
                            clean_msg["content"] = f"Please follow these instructions: {clean_msg['content']}"
                        else:
                            # Skip empty system messages
                            continue
                    else:
                        # Keep system message for models that support it
                        pass
                
                # Only include valid roles for OpenRouter API
                if clean_msg["role"] in ["system", "user", "assistant"]:
                    clean_conversation.append(clean_msg)

            # Update the API call to use streaming
            data = {
                "model": config['model'],
                "messages": clean_conversation,
                "temperature": config['temperature'],
                "stream": True,
            }

            # Start timing the response
            start_time = time.time()
            timer_display = console.status("[bold cyan]⏱️ Waiting for response...[/bold cyan]")
            timer_display.start()

            try:
                # Make streaming request
                response = requests.post(
                    url="https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=data,
                    stream=True,
                    timeout=60  # Add a timeout
                )

                if response.status_code == 200:
                    # Pass config['thinking_mode'] to stream_response
                    message_content, response_time, usage_info = stream_response(response, start_time, config['thinking_mode'])

                    # Only add to history if we got actual content
                    if message_content:
                        response_times.append(response_time)

                        # Add assistant response to conversation history
                        conversation_history.append({"role": "assistant", "content": message_content})

                        # Use API-provided token counts if available, otherwise fallback to tiktoken
                        if usage_info:
                            actual_prompt_tokens = usage_info.get('prompt_tokens', 0)
                            actual_completion_tokens = usage_info.get('completion_tokens', 0)
                            actual_total_tokens = usage_info.get('total_tokens', actual_prompt_tokens + actual_completion_tokens)
                            
                            total_prompt_tokens += actual_prompt_tokens
                            total_completion_tokens += actual_completion_tokens
                            total_tokens_used += actual_total_tokens
                            
                            input_tokens = actual_prompt_tokens
                            response_tokens = actual_completion_tokens
                        else:
                            # Fallback to tiktoken estimation
                            response_tokens = count_tokens(message_content)
                            total_tokens_used += input_tokens + response_tokens
                            total_completion_tokens += response_tokens

                        # Calculate cost for this exchange
                        exchange_cost = calculate_session_cost(input_tokens, response_tokens, pricing_info)

                        # Display speed and token information
                        formatted_time = format_time_delta(response_time)
                        console.print(f"[dim]⏱️ Response time: {formatted_time}[/dim]")
                        
                        # Enhanced token display with cost and accuracy indicator
                        token_source = "API" if usage_info else "estimated"
                        token_display = f"[dim]Tokens: {input_tokens} (input) + {response_tokens} (response) = {input_tokens + response_tokens} (total) [{token_source}]"
                        if exchange_cost > 0:
                            if exchange_cost < 0.01:
                                token_display += f" | Cost: ${exchange_cost:.6f}"
                            else:
                                token_display += f" | Cost: ${exchange_cost:.4f}"
                        token_display += "[/dim]"
                        console.print(token_display)
                        
                        if max_tokens:
                            console.print(f"[dim]Total Tokens: {total_tokens_used:,} / {display_max_tokens:,}[/dim]")
                        
                        # Increment message count for successful exchanges
                        message_count += 1
                    else:
                        # If we didn't get content but status was 200, something went wrong with streaming
                        console.print("[red]Error: Received empty response from API[/red]")
                        # Remove the user's last message since we didn't get a response
                        if conversation_history and conversation_history[-1]["role"] == "user":
                            conversation_history.pop()
                else:
                    # Try to get error details from response
                    try:
                        error_data = response.json()
                        error_message = error_data.get('error', {}).get('message', str(response.text))
                        
                        # Special handling for insufficient credits error (402)
                        if response.status_code == 402:
                            suggestions_text = (
                                f"[yellow]Solutions:[/yellow]\n"
                                f"• Add credits at: [link=https://openrouter.ai/settings/credits]https://openrouter.ai/settings/credits[/link]\n"
                                f"• Browse free models: [cyan]/model[/cyan] → [cyan]2[/cyan] (Show free models only)\n"
                                f"• Try the free version if available: [cyan]{config['model']}:free[/cyan]\n"
                                f"\n[dim]Original error: {error_message}[/dim]"
                            )
                            
                            console.print(Panel.fit(
                                f"[red]💳 Insufficient Credits[/red]\n\n"
                                f"The model '[cyan]{config['model']}[/cyan]' requires credits to use.\n\n"
                                f"{suggestions_text}",
                                title="⚠️ Payment Required",
                                border_style="red"
                            ))
                        else:
                            console.print(f"[red]API Error ({response.status_code}): {error_message}[/red]")
                    except Exception:
                        console.print(f"[red]API Error: Status code {response.status_code}[/red]")
                        console.print(f"[red]{response.text}[/red]")

                    # Remove the user's last message since we didn't get a response
                    if conversation_history and conversation_history[-1]["role"] == "user":
                        conversation_history.pop()
            except requests.exceptions.RequestException as e:
                console.print(f"[red]Network error: {str(e)}[/red]")
                # Remove the user's last message since we didn't get a response
                if conversation_history and conversation_history[-1]["role"] == "user":
                    conversation_history.pop()
            except Exception as e:
                console.print(f"[red]Error: {str(e)}[/red]")
                # Remove the user's last message since we didn't get a response
                if conversation_history and conversation_history[-1]["role"] == "user":
                    conversation_history.pop()
            finally:
                timer_display.stop()

        except KeyboardInterrupt:
            current_time = time.time()
            # Check if this is a double CTRL+C (within 2 seconds)
            if ctrl_c_count > 0 and (current_time - last_ctrl_c_time) <= 2.0:
                console.print("\n[yellow]Exiting chat...[/yellow]")
                break
            else:
                # First CTRL+C or too much time passed since last one
                ctrl_c_count = 1
                last_ctrl_c_time = current_time
                console.print("\n[yellow]Press Ctrl+C again to exit.[/yellow]")
                continue
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")

def create_chat_ui():
    """Creates a modern, attractive CLI interface using rich components"""
    console.print(Panel.fit(
        f"[bold blue]Or[/bold blue][bold green]Chat[/bold green] [dim]v{APP_VERSION}[/dim]\n"
        "[dim]A powerful CLI for AI models via OpenRouter[/dim]",
        title="🚀 Welcome",
        border_style="green",
        padding=(1, 2)
    ))

    # Display a starting tip
    console.print(Panel(
        "Type [bold green]/help[/bold green] for commands\n"
        "[bold cyan]/model[/bold cyan] to change AI models\n"
        "[bold yellow]/theme[/bold yellow] to customize appearance",
        title="Quick Tips",
        border_style="blue",
        width=40
    ))

def get_model_recommendations(task_type=None, budget=None):
    """Recommends models based on task type and budget constraints using dynamic OpenRouter categories"""
    all_models = get_available_models()

    if not task_type:
        return all_models

    # Get dynamic task categories from OpenRouter API instead of hardcoded ones
    try:
        task_categories = get_dynamic_task_categories()
        console.print(f"[dim]Using dynamic categories for task: {task_type}[/dim]")
    except Exception as e:
        console.print(f"[yellow]Warning: Failed to get dynamic categories, using fallback patterns: {str(e)}[/yellow]")
        # Fallback to basic patterns if API fails
        task_categories = {
            "creative": ["claude-3", "gpt-4", "llama", "gemini"],
            "coding": ["claude-3-opus", "gpt-4", "deepseek-coder", "qwen-coder", "devstral", "codestral"],
            "analysis": ["claude-3-opus", "gpt-4", "mistral", "qwen"],
            "chat": ["claude-3-haiku", "gpt-3.5", "gemini-pro", "llama"]
        }

    recommended = []
    task_model_patterns = task_categories.get(task_type, [])
    
    for model in all_models:
        model_id = model.get('id', '').lower()
        # Check if model matches any of the task-specific patterns/slugs
        if any(pattern.lower() in model_id for pattern in task_model_patterns):
            # Filter by budget if specified
            if budget == "free" and ":free" in model['id']:
                recommended.append(model)
            elif budget is None or budget != "free":
                recommended.append(model)

    return recommended or all_models

def main():
    parser = argparse.ArgumentParser(description="OrChat - AI chat powered by OpenRouter")
    parser.add_argument("--setup", action="store_true", help="Run the setup wizard")
    parser.add_argument("--model", type=str, help="Specify model to use")
    parser.add_argument("--task", type=str, choices=["creative", "coding", "analysis", "chat"],
                        help="Optimize for specific task type")
    parser.add_argument("--image", type=str, help="Path to image file to analyze")
    args = parser.parse_args()

    # Check if config exists
    config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
    env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')

    if args.setup or (not os.path.exists(config_file) and not os.path.exists(env_file)):
        config = setup_wizard()
        if config is None:
            console.print("[red]Setup failed. Cannot continue without proper configuration. Exiting.[/red]")
            sys.exit(1)
    else:
        config = load_config()

    # Show welcome UI
    create_chat_ui()

    # Auto-check for updates on startup
    try:
        check_for_updates(silent=True)
    except Exception:
        pass  # Silently ignore update check failures

    # Check if API key is set
    if not config['api_key'] or config['api_key'] == "<YOUR_OPENROUTER_API_KEY>":
        console.print("[red]API key not found or not set correctly.[/red]")
        setup_choice = Prompt.ask("Would you like to run the setup wizard? (y/n)", default="y")
        if setup_choice.lower() == 'y':
            config = setup_wizard()
            if config is None:
                console.print("[red]Setup failed. Cannot continue without a valid API key. Exiting.[/red]")
                sys.exit(1)
        else:
            console.print("[red]Cannot continue without a valid API key. Exiting.[/red]")
            sys.exit(1)

    # Handle task-specific model recommendation
    if args.task:
        recommended_models = get_model_recommendations(args.task)
        if recommended_models:
            console.print(Panel.fit(
                f"[bold green]Recommended models for {args.task} tasks:[/bold green]\n" +
                "\n".join([f"- {model['id']}" for model in recommended_models[:5]]),
                title="🎯 Task Optimization"
            ))

            use_recommended = Prompt.ask(
                "Would you like to use one of these recommended models?",
                choices=["y", "n"],
                default="y"
            )

            if use_recommended.lower() == 'y':
                # Let user select from recommended models
                for i, model in enumerate(recommended_models[:5], 1):
                    console.print(f"[bold]{i}.[/bold] {model['id']}")

                choice = Prompt.ask("Select model number", default="1")
                try:
                    index = int(choice) - 1
                    if 0 <= index < len(recommended_models[:5]):
                        config['model'] = recommended_models[index]['id']
                        save_config(config)
                except ValueError:
                    pass

    # Check if model is set or specified via command line
    if args.model:
        config['model'] = args.model
        save_config(config)
    elif not config['model']:
        console.print("[yellow]No model selected. Please choose a model.[/yellow]")
        selected_model = select_model(config)
        if selected_model:
            config['model'] = selected_model
            save_config(config)
        else:
            console.print("[red]Cannot continue without a valid model. Exiting.[/red]")
            sys.exit(1)

    # Check if system instructions are set - make sure we don't prompt again after setup
    if not config['system_instructions']:
        # Only prompt for system instructions if they weren't already set during setup
        # Set a default value without prompting
        config['system_instructions'] = "You are a helpful AI assistant."
        console.print("[yellow]No system instructions set. Using default instructions.[/yellow]")
        save_config(config)

    # Handle image analysis if provided
    conversation_history = None
    if args.image:
        conversation_history = [
            {"role": "system", "content": config['system_instructions']}
        ]
        success, message = handle_attachment(args.image, conversation_history)
        if success:
            console.print(f"[green]{message}[/green]")
        else:
            console.print(f"[red]{message}[/red]")

    # Start chat
    chat_with_model(config, conversation_history)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting application...")
    except Exception as e:
        console.print(f"[red]Critical error: {str(e)}[/red]")
        sys.exit(1)
