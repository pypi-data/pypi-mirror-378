# 🤝 Contributing to VoxPlayer

Thank you for your interest in contributing to VoxPlayer! We're excited to work with the community to make VoxPlayer even better! 🎬✨

## 🎯 How to Contribute

### 🐛 Bug Reports
Found a bug? Help us fix it!
1. Check if the issue already exists
2. Use our [bug report template](.github/ISSUE_TEMPLATE/bug_report.md)
3. Provide detailed information about the bug
4. Include steps to reproduce
5. Specify your platform and VoxPlayer version

### ✨ Feature Requests
Have an idea for VoxPlayer? We'd love to hear it!
1. Check if the feature is already requested
2. Use our [feature request template](.github/ISSUE_TEMPLATE/feature_request.md)
3. Describe the feature clearly
4. Explain the use case and benefits
5. Consider if it fits VoxPlayer's ultra-compact design philosophy

### 💻 Code Contributions
Want to contribute code? Awesome! Here's how:

#### 🚀 Getting Started
1. **Fork the repository**
2. **Clone your fork**
   ```bash
   git clone https://github.com/your-username/voxplayer.git
   cd voxplayer
   ```

3. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Make your changes**
6. **Test your changes**
   ```bash
   python app.py
   python test.py
   ```

7. **Commit your changes**
   ```bash
   git commit -m "✨ Add amazing feature"
   ```

8. **Push to your fork**
   ```bash
   git push origin feature/amazing-feature
   ```

9. **Create a Pull Request**

## 📋 Development Guidelines

### 🎨 Code Style
- Use **PEP 8** for Python code formatting
- Follow **PyQt6** best practices
- Use **type hints** where appropriate
- Write **clear, self-documenting code**
- Keep functions focused and small
- Use meaningful variable and function names

### 🧪 Testing
- Test all new features thoroughly
- Test with different media formats
- Test file association functionality
- Test on Windows, macOS, and Linux
- Test with different audio devices
- Test playlist functionality

### 📚 Documentation
- Update documentation for new features
- Add docstrings for new functions
- Update README if needed
- Include examples in your code
- Update changelog for significant changes

### 🎬 Media Player Testing
When contributing, please test:
- [ ] Video playback (MP4, AVI, MKV, MOV, WMV, FLV, WebM, M4V)
- [ ] Audio playback (MP3, FLAC, WAV, OGG, M4A, AAC, WMA)
- [ ] File associations (double-click functionality)
- [ ] Command-line file opening
- [ ] Drag & drop functionality
- [ ] Playlist management
- [ ] Keyboard shortcuts
- [ ] Settings persistence
- [ ] Fullscreen mode
- [ ] Volume controls
- [ ] Timeline seeking

## 🎯 Contribution Areas

### 🔧 Core Development
- Media playback improvements
- File format support
- Performance optimizations
- Bug fixes
- Code refactoring

### 🎨 User Interface
- UI/UX improvements
- Theme enhancements
- Accessibility features
- Responsive design
- Visual improvements

### 🎵 Audio/Video Features
- New format support
- Audio processing
- Video effects
- Subtitle enhancements
- Streaming improvements

### 🗂️ Playlist Management
- Playlist features
- Import/export formats
- Search and filtering
- Drag & drop improvements
- Playlist organization

### 🔗 File Associations
- Cross-platform integration
- Registry management
- Icon system
- Command-line support
- Installation improvements

### 📱 Platform Integration
- Windows features
- macOS features
- Linux features
- System integration
- Auto-update system
- Installer improvements
- Distribution

### 🧠 Advanced Features
- Torrent streaming
- Auto-update system
- Settings management
- Plugin system
- Extensions

### 🌍 Cross-Platform
- Build system improvements
- Platform-specific features
- Package management
- Distribution

## 🏗️ Project Structure

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

## 🧪 Testing Guidelines

### 🔍 Unit Tests
```bash
python test.py
```

### 🎬 Media Player Tests
```bash
# Test with sample files
python app.py "sample_video.mp4"
python app.py "sample_audio.mp3"

# Test file associations
.\test_file_associations.bat
```

### 🔗 File Association Tests
```bash
# Register associations
.\register_file_associations.bat

# Test double-click functionality
# Double-click any media file

# Unregister associations
.\unregister_file_associations.bat
```

### 🏗️ Build Tests
```bash
# Test simple build
.\build_simple.bat

# Test full release build
.\create_release.bat

# Test installer build
.\build_installer.bat

# Test cross-platform builds
.\build_all_platforms.bat
```

## 📝 Commit Convention

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test additions/changes
- `chore`: Build process or auxiliary tool changes

### Examples:
```
feat(playlist): add shuffle mode
fix(audio): resolve volume amplification issue
docs: update README with new features
style: format code with black
refactor(ui): improve timeline component
test: add file association tests
chore: update build scripts
```

## 🎨 VoxPlayer Design Guidelines

When contributing to VoxPlayer's design or features:

### ✅ Do:
- Maintain ultra-compact design philosophy
- Keep interface clean and minimal
- Focus on functionality over decoration
- Ensure professional appearance
- Maintain cross-platform compatibility
- Keep performance as priority

### ❌ Don't:
- Add unnecessary UI elements
- Make interface cluttered
- Remove essential functionality
- Break file associations
- Ignore platform standards
- Compromise performance

## 🚀 Release Process

### 📅 Release Schedule
- **Patch releases**: As needed for bug fixes
- **Minor releases**: Monthly for new features
- **Major releases**: Quarterly for significant changes

### 🏷️ Versioning
We use [Semantic Versioning](https://semver.org/):
- `MAJOR.MINOR.PATCH`
- Example: `1.0.0` → `1.0.1` → `1.1.0`

## 🎉 Recognition

### 🌟 Contributors
- Contributors will be listed in the README
- Special recognition for significant contributions
- VoxPlayer will thank you! 🎬✨

### 🏆 Contribution Levels
- **Bronze**: 1-5 contributions
- **Silver**: 6-15 contributions  
- **Gold**: 16-30 contributions
- **Platinum**: 31+ contributions

## 📞 Getting Help

### 💬 Community
- **GitHub Discussions**: Ask questions and share ideas
- **Issues**: Report bugs and request features
- **Pull Requests**: Submit code contributions

### 📚 Resources
- [README](README.md) - Project overview
- [Changelog](CHANGELOG.md) - Version history
- [Roadmap](ROADMAP.md) - Future plans
- [Development Goals](DEVELOPMENT_GOALS.md) - Development objectives

## 📋 Checklist for Contributors

Before submitting a PR, make sure:

- [ ] Code follows the style guidelines
- [ ] Tests pass locally
- [ ] Documentation is updated
- [ ] Changes are tested with different media formats
- [ ] File associations are tested
- [ ] Cross-platform compatibility is maintained
- [ ] Commit messages follow the convention
- [ ] PR description is clear and detailed
- [ ] Related issues are linked
- [ ] VoxPlayer's design philosophy is maintained

## 🎯 Quick Start for New Contributors

1. **Read the documentation**
2. **Set up the development environment**
3. **Look for "good first issue" labels**
4. **Start with small contributions**
5. **Ask questions if you need help**
6. **Have fun contributing!**

## 🎬 VoxPlayer Philosophy

VoxPlayer is designed with these core principles:

- **Ultra-Compact**: Minimalist interface with maximum functionality
- **Professional**: High-quality implementation and user experience
- **Efficient**: Fast, responsive, and resource-efficient
- **Integrated**: Seamless cross-platform integration and file associations
- **Reliable**: Stable, consistent, and dependable
- **User-Friendly**: Intuitive and easy to use

When contributing, please keep these principles in mind and help us maintain VoxPlayer's high standards!

---

## 🤖 A Message from the VoxPlayer Team

"Hey there, future contributor! We're super excited that you want to help make VoxPlayer even better! Whether you're fixing bugs, adding features, or improving the user experience, every contribution helps us create the best media player possible.

Don't be afraid to ask questions - we're here to help! And remember, coding is like magic... but with more debugging!

Let's build something amazing together! ✨"

---

**Made with ❤️ by VoxHash and the amazing community**

*VoxPlayer is ready to work with you!* 🎬✨
