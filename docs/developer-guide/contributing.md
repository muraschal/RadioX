# 🤝 Contributing Guide

<div align="center">

![Developer Guide](https://img.shields.io/badge/guide-developer-purple)
![Difficulty](https://img.shields.io/badge/difficulty-beginner-green)
![Time](https://img.shields.io/badge/time-10%20min-orange)

**🚀 Complete guide to contributing to RadioX development**

[🏠 Documentation](../) • [👨‍💻 Developer Guides](../README.md#-developer-guides) • [🏗️ Architecture](architecture.md) • [🔧 Development](development.md)

</div>

---

## 🎯 Overview

We welcome contributions to RadioX! This guide covers **everything you need** to contribute effectively, from code standards to submission workflows.

### ✨ **What You Can Contribute**
- 🐛 **Bug Fixes** - Fix issues and improve stability
- ✨ **New Features** - Add functionality and enhancements
- 📚 **Documentation** - Improve guides and examples
- 🧪 **Tests** - Add test coverage and validation
- 🎨 **UI/UX** - Enhance user experience

---

## 🚀 Quick Start

### **🍴 Fork & Setup**

```bash
# 1. Fork the repository on GitHub
# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/RadioX.git
cd RadioX

# 3. Add upstream remote
git remote add upstream https://github.com/original-org/RadioX.git

# 4. Setup development environment
./setup.sh
cd backend && python cli/cli_master.py test
```

### **🌿 Create Feature Branch**

```bash
# Create and switch to feature branch
git checkout -b feature/amazing-feature

# Or for bug fixes
git checkout -b fix/bug-description
```

---

## 🛡️ Code Standards

### **🏗️ Architectural Guidelines**

RadioX follows **strict architectural principles** - please read our [Development Guide](development.md) for complete details:

#### **✅ DO:**
- Extend existing services instead of creating new files
- Use the Voice Configuration Service (Supabase-based)
- Follow the CLI structure for testing
- Write comprehensive tests
- Document your changes

#### **❌ DON'T:**
- Create temporary helper scripts (`helper_*.py`, `temp_*.py`, etc.)
- Hardcode voice configurations
- Bypass existing service architecture
- Skip testing
- Leave unclean code

### **🎤 Voice Configuration Rules**

```python
# ✅ CORRECT: Use Voice Configuration Service
from src.services.voice_config_service import get_voice_config_service

service = get_voice_config_service()
voice_config = await service.get_voice_config("marcel")

# ❌ WRONG: Hardcoded voices
# voice_config = {"marcel": {"voice_id": "..."}}  # NEVER!
```

### **📁 File Organization**

```bash
# ✅ Extend existing services
src/services/audio_generation.py     # Add audio features here
src/services/broadcast_generation.py # Add broadcast features here

# ✅ Use existing CLI tools
cli/cli_audio.py    # Audio testing
cli/cli_master.py   # Master control

# ❌ NEVER create these patterns
helper_*.py         # Forbidden
temp_*.py          # Forbidden
debug_*.py         # Forbidden
```

---

## 🧪 Testing Requirements

### **🔬 Test Your Changes**

Before submitting, ensure all tests pass:

```bash
# Level 1: Unit tests
python cli/cli_audio.py test
python cli/cli_crypto.py test
python cli/cli_rss.py test

# Level 2: Integration tests
python cli/cli_master.py test

# Level 3: System tests
python production/radiox_master.py --action test_services

# Level 4: Production validation
python production/radiox_master.py --action system_status
```

### **📝 Add Tests for New Features**

```python
# Example: Adding a test to existing service
class AudioGenerationService:
    async def test_new_feature(self) -> bool:
        """Test new audio feature"""
        try:
            # Test implementation
            return True
        except Exception as e:
            print(f"❌ New feature test failed: {e}")
            return False
```

---

## 📝 Commit Guidelines

### **💾 Commit Message Format**

```bash
# Format: <type>(<scope>): <description>
# Examples:
git commit -m "feat(audio): add V3 emotional tags support"
git commit -m "fix(voice): resolve Marcel voice configuration issue"
git commit -m "docs(guide): update voice configuration examples"
git commit -m "test(audio): add ElevenLabs V3 integration tests"
```

### **🎯 Commit Types**

| Type | Description | Example |
|------|-------------|---------|
| `feat` | New feature | `feat(broadcast): add night show style` |
| `fix` | Bug fix | `fix(audio): resolve voice loading issue` |
| `docs` | Documentation | `docs(api): update voice configuration` |
| `test` | Tests | `test(crypto): add Bitcoin API tests` |
| `refactor` | Code refactoring | `refactor(services): optimize data flow` |
| `style` | Code style | `style(cli): improve error messages` |

### **📋 Commit Best Practices**

```bash
# ✅ Good commits
git commit -m "feat(voice): integrate Supabase voice configuration"
git commit -m "fix(audio): handle ElevenLabs quota exceeded error"
git commit -m "test(broadcast): add German language generation tests"

# ❌ Bad commits
git commit -m "fix stuff"
git commit -m "update"
git commit -m "wip"
```

---

## 🔄 Pull Request Process

### **📤 Submission Workflow**

```bash
# 1. Ensure your branch is up to date
git fetch upstream
git rebase upstream/main

# 2. Run complete test suite
python cli/cli_master.py test
python production/radiox_master.py --action test_services

# 3. Push your changes
git push origin feature/amazing-feature

# 4. Create Pull Request on GitHub
```

### **📋 Pull Request Template**

```markdown
## 🎯 Description
Brief description of changes and motivation.

## 🔄 Type of Change
- [ ] 🐛 Bug fix (non-breaking change which fixes an issue)
- [ ] ✨ New feature (non-breaking change which adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] 📚 Documentation update

## 🧪 Testing
- [ ] Unit tests pass (`python cli/cli_master.py test`)
- [ ] Integration tests pass
- [ ] System tests pass (`python production/radiox_master.py --action test_services`)
- [ ] Manual testing completed

## 🛡️ Code Quality
- [ ] Follows architectural guidelines
- [ ] Uses Voice Configuration Service (no hardcoded voices)
- [ ] No temporary/helper scripts created
- [ ] Documentation updated
- [ ] Clean commit history

## 📝 Additional Notes
Any additional information, breaking changes, or migration notes.
```

### **🔍 Review Process**

1. **Automated Checks:** CI/CD pipeline runs tests
2. **Code Review:** Maintainers review code quality
3. **Architecture Review:** Ensure architectural compliance
4. **Testing Validation:** Verify test coverage
5. **Documentation Check:** Ensure docs are updated

---

## 🎨 Documentation Standards

### **📚 Documentation Updates**

When adding features, update relevant documentation:

```bash
# User-facing features
docs/user-guide/show-generation.md
docs/user-guide/voice-configuration.md
docs/user-guide/api-reference.md

# Developer features
docs/developer-guide/architecture.md
docs/developer-guide/development.md
docs/developer-guide/testing.md
```

### **📝 Documentation Style**

```markdown
# Follow existing patterns
## 🎯 Section Title
### **🔧 Subsection**

# Use consistent emojis
🎯 Overview/Purpose
🚀 Quick Start/Actions
🔧 Configuration/Setup
🧪 Testing
💡 Tips/Best Practices
🔗 Related Links
```

---

## 🐛 Bug Reports

### **🚨 Reporting Issues**

Use our [GitHub Issues](https://github.com/your-org/RadioX/issues) with this template:

```markdown
## 🐛 Bug Description
Clear description of the bug.

## 🔄 Steps to Reproduce
1. Run command: `python production/radiox_master.py --action generate_broadcast`
2. Observe error: `ElevenLabs API error`
3. Check logs: `logs/radiox_master_*.log`

## 🎯 Expected Behavior
What should happen.

## 📊 Environment
- OS: Windows 10 / macOS / Linux
- Python: 3.11
- RadioX Version: v3.1
- API Keys: OpenAI ✅, ElevenLabs ❌

## 📝 Additional Context
Logs, screenshots, or additional information.
```

---

## 💡 Feature Requests

### **✨ Suggesting Features**

Use [GitHub Issues](https://github.com/your-org/RadioX/issues) with this template:

```markdown
## 💡 Feature Request
Clear description of the proposed feature.

## 🎯 Use Case
Why is this feature needed? What problem does it solve?

## 📝 Proposed Solution
How should this feature work?

## 🔄 Alternatives Considered
Other approaches you've considered.

## 📊 Additional Context
Mockups, examples, or related features.
```

---

## 🏆 Recognition

### **🎉 Contributors**

We recognize all contributors in:
- 📋 **README.md** - Main contributors list
- 📚 **Documentation** - Guide-specific contributors
- 🏷️ **Releases** - Release notes acknowledgments
- 🐦 **Social Media** - Feature announcements

### **🎖️ Contribution Types**

| 🎯 Type | 🏆 Recognition |
|---------|----------------|
| **Major Features** | Featured in release notes |
| **Bug Fixes** | Mentioned in changelog |
| **Documentation** | Credited in guide headers |
| **Testing** | Acknowledged in test reports |

---

## 🔗 Related Resources

- **🏗️ [Architecture](architecture.md)** - Understand the system design
- **🔧 [Development](development.md)** - Setup development environment
- **🧪 [Testing](testing.md)** - Testing strategies and tools
- **🚀 [Production](../deployment/production.md)** - Deploy your changes

---

<div align="center">

**🤝 Thank you for contributing to RadioX!**

[🏠 Documentation](../) • [🔧 Development Setup](development.md) • [💬 Get Help](../README.md#-support)

</div> 