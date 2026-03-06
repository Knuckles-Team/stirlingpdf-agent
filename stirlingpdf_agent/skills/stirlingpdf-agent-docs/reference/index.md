We use essential cookies to make our site work. With your consent, we may also use non-essential cookies to improve user experience and analyze website traffic. By clicking “Accept,” you agree to our website's cookie use as described in our Cookie Policy. You can change your cookie settings at any time by clicking “Preferences.”
PreferencesDeclineAccept
![x](https://static.scarf.sh/a.png?x-pxid=5d074971-2ecb-4c54-8397-30c0f91896b3)
[Skip to main content](https://docs.stirlingpdf.com/#__docusaurus_skipToContent_fallback)
[![Stirling-PDF Logo](https://docs.stirlingpdf.com/img/logo.svg) **Stirling-PDF**](https://docs.stirlingpdf.com/)[Docs](https://docs.stirlingpdf.com/)
[2.0 (Current)](https://docs.stirlingpdf.com/)
  * [2.0 (Current)](https://docs.stirlingpdf.com/)
  * [1.6.0](https://docs.stirlingpdf.com/1.5/)


Search`K`
  * [](https://docs.stirlingpdf.com/)
  * Getting Started


On this page
## Benefits of Stirling-PDF[​](https://docs.stirlingpdf.com/#benefits-of-stirling-pdf "Direct link to Benefits of Stirling-PDF")
  * **Extensive PDF Functionality:** Access 60+ tools, including signing, converting, merging, and more.
  * **Advanced Customization:** Deep customization, themes, and environment variables.
  * **Enterprise Features:** SSO, user management, and permission controls.
  * **Data Security:** Local file processing with automatic deletion post-task.
  * **Scalability & Automation:** Batch processing with Docker and Kubernetes support.
  * **API Integration:** Use APIs for automation and external integrations.
  * **Open-Source:** Community-driven with frequent updates and GitHub support.
  * **Multi-Language Support:** Available in 38+ languages with active translations.


## Welcome to Stirling-PDF[​](https://docs.stirlingpdf.com/#welcome-to-stirling-pdf "Direct link to Welcome to Stirling-PDF")
See the **[Migration Guide](https://docs.stirlingpdf.com/Migration/Overview)** for what's new and how to upgrade smoothly.
Stirling-PDF is a locally hosted web application that allows you to perform various operations on PDF files. With 60+ tools, flexible deployment options, and enterprise features, it's the comprehensive PDF solution for individuals and organizations.
* * *
## What's New in V2[​](https://docs.stirlingpdf.com/#whats-new-in-v2 "Direct link to What's New in V2")
V2 brings major improvements to performance, workflow, and deployment flexibility:
  * **📁 Stateful Processing** - Upload once, use across multiple tools without re-uploading
  * **⏮️ Undo & Redo** - Made a mistake? Just undo it! Full version history included
  * **🖥️ Native Desktop Apps** - Lightning-fast startup, "Open with" integration, offline capable
  * **🔀 Split Deployment** - Scale frontend and backend independently for enterprise use
  * **⚙️ In-App Settings** - Configure everything through the UI, no file editing needed


* * *
## Documentation Guide[​](https://docs.stirlingpdf.com/#documentation-guide "Direct link to Documentation Guide")
### 👤 For Individual Users[​](https://docs.stirlingpdf.com/#-for-individual-users "Direct link to 👤 For Individual Users")
**[Tool Reference](https://docs.stirlingpdf.com/functionality)** Browse all 60+ PDF tools with descriptions and use cases
* * *
### 🏢 For Organizations & IT Teams[​](https://docs.stirlingpdf.com/#-for-organizations--it-teams "Direct link to 🏢 For Organizations & IT Teams")
**[Production Deployment Guide](https://docs.stirlingpdf.com/Production-Deployment-Guide)** Complete walkthrough: installation → configuration → security → monitoring
**[Paid Offerings (Server& Enterprise)](https://docs.stirlingpdf.com/Paid-Offerings)** External databases, Google Drive integration, SSO, advanced monitoring, and priority support
**[Configuration Options](https://docs.stirlingpdf.com/Configuration/Extra-Settings)** All configuration options for Docker and server deployments
* * *
### 🔧 For Developers & Integration[​](https://docs.stirlingpdf.com/#-for-developers--integration "Direct link to 🔧 For Developers & Integration")
**[API Documentation](https://docs.stirlingpdf.com/API)** Integrate Stirling-PDF into your applications and workflows
**[Configuration](https://docs.stirlingpdf.com/Configuration/System%20and%20Security)** SSO, split deployment, certificates, security settings, and more
**[Contribute Guide](https://docs.stirlingpdf.com/Contribute)** Help improve Stirling-PDF - development setup and guidelines
* * *
## Installation[​](https://docs.stirlingpdf.com/#installation "Direct link to Installation")
Choose how you want to run Stirling-PDF based on your needs:
### 🖥️ Desktop Applications[​](https://docs.stirlingpdf.com/#%EF%B8%8F-desktop-applications "Direct link to 🖥️ Desktop Applications")
Native apps with system integration:
Platform | Download | Guide
---|---|---
**Windows** | [Installer](https://files.stirlingpdf.com/win-installer.exe) | [Windows Guide](https://docs.stirlingpdf.com/Installation/Windows%20Installation)
**Mac (Apple Silicon)** | [DMG](https://files.stirlingpdf.com/mac-installer.dmg) | [Mac Guide](https://docs.stirlingpdf.com/Installation/Mac%20Installation)
**Mac (Intel)** | [DMG](https://files.stirlingpdf.com/mac-x86_64-installer.dmg) | [Mac Guide](https://docs.stirlingpdf.com/Installation/Mac%20Installation)
**Linux** | [DEB](https://files.stirlingpdf.com/linux-installer.deb) | [Unix Guide](https://docs.stirlingpdf.com/Installation/Unix%20Installation)
**Features:** Lightning-fast startup, "Open with" integration, sign in with Stirling Cloud or self-hosted server
* * *
### 🐳 Docker Deployment[​](https://docs.stirlingpdf.com/#-docker-deployment "Direct link to 🐳 Docker Deployment")
Recommended for server deployments and organizations:
**Quick Start:**
```
docker run -d \
  -p 8080:8080 \
  -v ./stirling-data:/configs \
  stirlingtools/stirling-pdf:latest

```

**Available versions:**
  * `latest` - Standard version (recommended)
  * `latest-fat` - Includes extra fonts and security features
  * `latest-ultra-lite` - Minimal size for resource-constrained environments


**Full guide:** [Docker Installation Guide](https://docs.stirlingpdf.com/Installation/Docker%20Install)
* * *
### ⚙️ Manual Server Setup[​](https://docs.stirlingpdf.com/#%EF%B8%8F-manual-server-setup "Direct link to ⚙️ Manual Server Setup")
For bare metal installations or environments without Docker:
  1. Download `Stirling-PDF.jar`
  2. Install Java 21+
  3. Install dependencies (LibreOffice, Tesseract for OCR)
  4. Run the JAR file


**Full guide:** [Unix Installation Guide](https://docs.stirlingpdf.com/Installation/Unix%20Installation)
* * *
## Quick Links[​](https://docs.stirlingpdf.com/#quick-links "Direct link to Quick Links")
  * **Questions?** Check our **[FAQ](https://docs.stirlingpdf.com/FAQ)**
  * **Issues?** Report on
  * **Community?** Join our


[Next Production Deployment Guide](https://docs.stirlingpdf.com/Production-Deployment-Guide)
  * [Benefits of Stirling-PDF](https://docs.stirlingpdf.com/#benefits-of-stirling-pdf)
  * [Welcome to Stirling-PDF](https://docs.stirlingpdf.com/#welcome-to-stirling-pdf)
  * [What's New in V2](https://docs.stirlingpdf.com/#whats-new-in-v2)
  * [Documentation Guide](https://docs.stirlingpdf.com/#documentation-guide)
    * [👤 For Individual Users](https://docs.stirlingpdf.com/#-for-individual-users)
    * [🏢 For Organizations & IT Teams](https://docs.stirlingpdf.com/#-for-organizations--it-teams)
    * [🔧 For Developers & Integration](https://docs.stirlingpdf.com/#-for-developers--integration)
  * [Installation](https://docs.stirlingpdf.com/#installation)
    * [🖥️ Desktop Applications](https://docs.stirlingpdf.com/#%EF%B8%8F-desktop-applications)
    * [🐳 Docker Deployment](https://docs.stirlingpdf.com/#-docker-deployment)
    * [⚙️ Manual Server Setup](https://docs.stirlingpdf.com/#%EF%B8%8F-manual-server-setup)
  * [Quick Links](https://docs.stirlingpdf.com/#quick-links)
