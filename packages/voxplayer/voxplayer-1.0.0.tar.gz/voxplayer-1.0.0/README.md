# 🎬 VoxPlayer v1.0.0

> **VoxPlayer** - A modern, ultra-compact media player for Windows with professional file association support. Built with PyQt6 and designed for simplicity and performance.

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/voxhash/voxplayer)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://python.org/)
[![PyQt6](https://img.shields.io/badge/pyqt6-6.0+-blue.svg)](https://pypi.org/project/PyQt6/)

## ✨ Features

### 🎬 **Core Media Playback**
- **Universal Format Support**: MP4, AVI, MKV, MOV, WMV, FLV, WebM, M4V, MP3, FLAC, WAV, OGG, M4A, AAC, WMA
- **Ultra-Compact Design**: Minimalist interface with maximum functionality
- **True Volume Amplification**: Up to 200% volume boost for quiet media
- **Professional File Associations**: Double-click any media file to open with VoxPlayer
- **Command-Line Support**: Open files directly from command line

### 🎵 **Advanced Playlist Management**
- **Smart Playlist Behavior**: No auto-clearing, persistent playlist
- **Drag & Drop Support**: Files and folders from Windows Explorer
- **Real-Time Search**: Instant filtering and search within playlists
- **Import/Export**: M3U, PLS, XSPF, and text format support
- **Individual Item Control**: Remove specific items with X buttons
- **Visual Selection**: Clear indication of current playing item

### 🚀 **Professional Features**
- **Torrent Streaming**: qBittorrent integration for streaming
- **Auto-Update System**: GitHub-based update checking
- **Audio Device Selection**: Default or manual audio output
- **Fullscreen Mode**: Auto-hiding controls for immersive viewing
- **Timeline Preview**: Hover and drag preview on timeline
- **SRT Subtitle Support**: Built-in subtitle display
- **Snapshot Functionality**: Capture frames from videos

### 🎨 **User Experience**
- **Dark Theme**: Professional dark interface
- **Keyboard Shortcuts**: 15+ shortcuts for efficient control
- **Context Menus**: Right-click options for advanced features
- **Resume Positions**: Automatic playback position memory
- **Settings Persistence**: Remembers all user preferences

## 🚀 Quick Start

### Prerequisites
- Windows 10/11
- Python 3.8+ (for development)
- PyQt6 and dependencies

### Installation

#### Method 1: Download Executable (Recommended)

**Windows:**
1. **Download**: Get `VoxPlayer.exe` from [Releases](https://github.com/voxhash/voxplayer/releases)
2. **Run**: Double-click `VoxPlayer.exe` to start
3. **File Associations**: Run `register_file_associations.bat` as Administrator

**macOS:**
1. **Download**: Get `VoxPlayer-1.0.0-macOS.dmg` from [Releases](https://github.com/voxhash/voxplayer/releases)
2. **Install**: Double-click the DMG and drag VoxPlayer.app to Applications
3. **Run**: Launch VoxPlayer from Applications folder

**Linux:**
- **Debian/Ubuntu**: Download `voxplayer_1.0.0_amd64.deb` and run `sudo dpkg -i voxplayer_1.0.0_amd64.deb`
- **Fedora/CentOS/RHEL**: Download `voxplayer-1.0.0-1.x86_64.rpm` and run `sudo dnf install voxplayer-1.0.0-1.x86_64.rpm`
- **Arch Linux**: Download `voxplayer-1.0.0-1-x86_64.pkg.tar.zst` and run `sudo pacman -U voxplayer-1.0.0-1-x86_64.pkg.tar.zst`

#### Method 2: Python Installation
1. **Clone Repository**
```bash
   git clone https://github.com/voxhash/voxplayer.git
   cd voxplayer
   ```

2. **Install Dependencies**
   ```bash
pip install -r requirements.txt
   ```

3. **Run VoxPlayer**
   ```bash
python app.py
   # Or with a file
   python app.py "path/to/video.mp4"
   ```

#### Method 3: Source Distribution
1. **Download**: Get `VoxPlayer-1.0.0.tar.gz` from [Releases](https://github.com/voxhash/voxplayer/releases)
2. **Install**: `pip install VoxPlayer-1.0.0.tar.gz`
3. **Run**: `voxplayer`

### File Associations Setup

1. **Run as Administrator**: Right-click `register_file_associations.bat` → "Run as administrator"
2. **Verify**: Double-click any media file - VoxPlayer should open automatically
3. **Remove**: Run `unregister_file_associations.bat` to remove associations

## 🎯 Usage

### Opening Media Files

#### Method 1: Double-Click (File Associations)
- **Setup**: Run `register_file_associations.bat` as Administrator
- **Use**: Double-click any supported media file in Windows Explorer
- **Result**: VoxPlayer opens and plays the file automatically

#### Method 2: Command Line
```bash
# Open specific file
python app.py "C:\Videos\movie.mp4"

# Open from current directory
python app.py "video.mp4"
```

#### Method 3: Drag & Drop
1. **Open VoxPlayer**
2. **Drag media files** from Windows Explorer
3. **Drop onto VoxPlayer window**
4. **Files are added to playlist** and first file starts playing

### Playlist Management

#### Adding Files
- **File Menu**: File → Open File(s) or Open Folder
- **Drag & Drop**: Drag files/folders from Windows Explorer
- **Command Line**: `python app.py "file.mp4"`

#### Playlist Controls
- **Search**: Type in search box to filter playlist
- **Remove Items**: Click X button next to any item
- **Clear All**: File → Clear Playlist (with confirmation)
- **Import/Export**: File → Import/Export Playlist

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Space` | Play/Pause |
| `Left/Right` | Seek backward/forward |
| `Up/Down` | Volume up/down |
| `M` | Mute/Unmute |
| `F` | Toggle fullscreen |
| `Ctrl+O` | Open file(s) |
| `Ctrl+F` | Open folder |
| `Ctrl+S` | Save playlist |
| `Ctrl+L` | Load playlist |
| `Ctrl+Q` | Quit |
| `Ctrl+,` | Settings |
| `Ctrl+H` | Help |

## 🔧 Configuration

### Settings Menu
Access via **File → Settings** or `Ctrl+,`:

- **Audio Output**: Default or Manual device selection
- **Volume**: Master volume level
- **Theme**: Dark theme (default)
- **Auto-Update**: Enable/disable update checking
- **Update Channel**: Stable or Beta updates

### File Associations
- **Register**: `register_file_associations.bat` (run as Administrator)
- **Unregister**: `unregister_file_associations.bat`
- **Test**: `test_file_associations.bat`

## 📁 Supported Formats

### Video Files
- **MP4** - Most common video format
- **AVI** - Classic video format  
- **MKV** - High-quality video container
- **MOV** - Apple QuickTime format
- **WMV** - Windows Media Video
- **FLV** - Flash Video
- **WebM** - Web-optimized video
- **M4V** - iTunes video format

### Audio Files
- **MP3** - Most common audio format
- **FLAC** - Lossless audio
- **WAV** - Uncompressed audio
- **OGG** - Open source audio
- **M4A** - iTunes audio format
- **AAC** - Advanced Audio Coding
- **WMA** - Windows Media Audio

## 🛠️ Development

### Building from Source

1. **Clone Repository**
   ```bash
   git clone https://github.com/voxhash/voxplayer.git
   cd voxplayer
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install pyinstaller
   ```

3. **Build Executable**

**Windows:**
   ```bash
   # Simple build
   .\build_simple.bat
   
   # Full release build
   .\create_release.bat
   
   # Installer build
   .\build_installer.bat
   
   # Build all platforms (Windows only)
   .\build_all_platforms.bat
   ```

**macOS:**
   ```bash
   # macOS DMG build
   ./build_macos.sh
   
   # Build all platforms
   ./build_all.sh
   ```

**Linux:**
   ```bash
   # Debian/Ubuntu .deb package
   ./build_debian.sh
   
   # Fedora/CentOS/RHEL .rpm package
   ./build_rpm.sh
   
   # Arch Linux pacman package
   ./build_arch.sh
   
   # Source distribution
   ./build_source.sh
   
   # Build all platforms
   ./build_all.sh
   ```

### Project Structure
```
voxplayer/
├── app.py                    # Main application (2,458 lines)
├── requirements.txt          # Python dependencies
├── voxplayer.spec           # PyInstaller configuration
├── version_info.txt         # Windows version info
├── VoxPlayer_Installer.iss  # Inno Setup installer script
├── icon.ico                 # Application icon
├── build_simple.bat         # Windows simple build script
├── create_release.bat       # Windows full release build
├── build_installer.bat      # Windows installer build script
├── build_macos.sh           # macOS DMG build script
├── build_debian.sh          # Debian/Ubuntu .deb build script
├── build_rpm.sh             # Fedora/CentOS/RHEL .rpm build script
├── build_arch.sh            # Arch Linux pacman build script
├── build_source.sh          # Source distribution build script
├── build_all.sh             # Cross-platform build script (Linux/macOS)
├── build_all_platforms.bat  # Cross-platform build script (Windows)
├── register_file_associations.bat    # File association setup
├── unregister_file_associations.bat  # File association removal
├── test_file_associations.bat       # Test file associations
├── test.py                  # Test suite
├── run.py                   # Python launcher
├── run.bat                  # Windows launcher
├── README.md                # Project overview
├── CHANGELOG.md             # Version history
├── CONTRIBUTING.md          # Contribution guidelines
├── ROADMAP.md               # Development roadmap
├── DEVELOPMENT_GOALS.md     # Development goals
├── GITHUB_TOPICS.md         # GitHub topics
└── LICENSE                  # MIT License
```

## 🔧 Troubleshooting

### Common Issues

**File associations not working:**
- Run `register_file_associations.bat` as Administrator
- Check Windows Defender settings
- Restart Windows Explorer

**Audio not playing:**
- Check audio device settings in File → Settings
- Verify file format is supported
- Check system volume levels

**Video not displaying:**
- Update graphics drivers
- Check file format compatibility
- Try different video file

**Application won't start:**
- Install Python 3.8+ and PyQt6
- Check Windows version compatibility
- Run from command line to see error messages

### Getting Help

- **Issues**: [GitHub Issues](https://github.com/voxhash/voxplayer/issues)
- **Discussions**: [GitHub Discussions](https://github.com/voxhash/voxplayer/discussions)
- **Creator**: VoxHash

## 📋 Changelog

See [CHANGELOG.md](CHANGELOG.md) for detailed version history and upcoming features.

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📚 Documentation

- **[Changelog](CHANGELOG.md)** - Version history and upcoming features
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute to VoxPlayer
- **[Roadmap](ROADMAP.md)** - Development roadmap and future plans
- **[Development Goals](DEVELOPMENT_GOALS.md)** - Detailed development objectives
- **[GitHub Topics](GITHUB_TOPICS.md)** - Repository topics and tags

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎉 Acknowledgments

- **PyQt6** - Cross-platform GUI framework
- **FFmpeg** - Media processing backend
- **qBittorrent** - Torrent streaming integration
- **Inno Setup** - Professional Windows installer
- **Community** - Feedback and contributions

---

**Made with ❤️ by VoxHash**

*VoxPlayer - Professional media playback made simple!* 🎬✨
